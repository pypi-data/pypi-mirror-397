"""Stateful Browser Tool

设计要点:
- Search 分页: 通过参数 page, page_size 控制, 在 state 中缓存所有返回结果(一次性获取 max_search_results, 再分页切片)
- Open: 根据 index 打开上一轮搜索结果中的链接, 或直接给 url；支持 view_source 与行区间截取
- Find: 在当前页面中查找关键词, 支持分页返回多个结果
"""

import dataclasses
import functools
import itertools
import re
import textwrap
from typing import Any, TypeVar, Type, Union
from collections import OrderedDict
from urllib.parse import quote, unquote

import tiktoken
from pydantic import BaseModel, Field, ValidationError
from loguru import logger

from agentlin.core.agent_schema import content_to_text
from agentlin.core.types import (
    BaseTool,
    ToolResult,
    FunctionParameters,
    ToolParams,
)
from agentlin.tools.core import tool_result_of_text, tool_result_of_internal_error
from agentlin.tools.stateful_browser.page_contents import Extract, PageContents
from agentlin.tools.stateful_browser.backend import (
    VIEW_SOURCE_PREFIX,
    Backend,
    BackendError,
    ExaBackend,
    maybe_truncate,
)


ENC_NAME = "o200k_base"
FIND_PAGE_LINK_FORMAT = "# 【{idx}†{title}】"
PARTIAL_INITIAL_LINK_PATTERN = re.compile(r"^[^【】]*】")
PARTIAL_FINAL_LINK_PATTERN = re.compile(r"【\d*(?:†(?P<content>[^†】]*)(?:†[^†】]*)?)?$")
LINK_PATTERN = re.compile(r"【\d+†(?P<content>[^†】]+)(?:†[^†】]+)?】")
CITATION_OUTPUT_PATTERN = re.compile(r"【(?P<cursor>\d+)†(?P<content>[^†】]+)(?:†[^†】]+)?】")


T_Params = TypeVar("T_Params", bound="ToolParamsBase")


class ToolParamsBase(BaseModel):
    """参数模型通用基类。

    设计目标:
      1. 统一三种工具(Search/Open/Find)的参数解析入口, 减少重复样板代码。
      2. 通过 Pydantic 校验基础类型与约束, 再通过 ``post_validate`` 补充业务级校验。
      3. 利用 ``normalize`` 对字段做“就地”归一化(例如: 去掉空白 / 范围裁剪 / 大小写折叠)。
      4. 使用泛型精确返回子类类型, 使 IDE 与类型检查器能在分支后正确推断字段。

    生命周期 (成功路径):
        raw(dict/ToolParams)
            -> model_validate (Pydantic 基础类型/范围校验)
            -> post_validate (跨字段/业务逻辑校验, 可提前返回 ToolResult 错误)
            -> normalize (原地归一化, 不改变语义仅改善一致性)
            -> 子类实例

    使用范式::

        args = OpenParams.parse_model(raw_params)
        if isinstance(args, ToolResult):
            return args  # 直接返回错误
        # args 现为 OpenParams, 可安全访问: args.url / args.loc

    可覆写钩子:
        post_validate(self) -> ToolResult | None
            - 适合做跨字段或语义校验; 返回 ToolResult 时将中断并把该结果向上传递。
        normalize(self) -> None
            - 适合做范围裁剪、strip、大小写转换等“纯函数式”变换; 禁止引入副作用。

    注意事项:
        - 若需要外部依赖(如 backend 配置)介入校验, 建议在 tool.execute 中包一层而非在模型内存放引用。
        - 归一化阶段使用 ``object.__setattr__`` 以显式标识属性被修改 (即便未开启 frozen 也保持清晰)。
        - 返回错误时统一通过 ``tool_result_of_internal_error`` 以维持上层错误规范。
    """

    @classmethod
    def parse_model(cls: Type[T_Params], raw: ToolParams) -> Union[T_Params, ToolResult]:
        try:
            inst = cls.model_validate(raw)  # type: ignore[arg-type]
        except ValidationError as ve:
            return tool_result_of_internal_error(f"Parameter validation failed: {ve.errors()[0]['msg']}")
        extra = inst.post_validate()
        if isinstance(extra, ToolResult):
            return extra
        inst.normalize()
        return inst

    def post_validate(self):  # type: ignore[override]
        return None

    def normalize(self):  # type: ignore[override]
        pass


@functools.cache
def _tiktoken_vocabulary_lengths(enc_name: str) -> list[int]:
    encoding = tiktoken.get_encoding(enc_name)
    results = []
    for i in range(encoding.n_vocab):
        try:
            results.append(len(encoding.decode([i])))
        except Exception as e:
            results.append(1)
    return results


@dataclasses.dataclass(frozen=True)
class Tokens:
    tokens: list[int]
    tok2idx: list[int]  # Offsets = running sum of lengths.


@functools.cache
def max_chars_per_token(enc_name: str) -> int:
    """Typical value is 128, but let's be safe."""
    tok_lens = _tiktoken_vocabulary_lengths(enc_name)
    return max(tok_lens)


def get_tokens(text: str, enc_name: str) -> Tokens:
    encoding = tiktoken.get_encoding(enc_name)
    tokens = encoding.encode(text, disallowed_special=())
    _vocabulary_lengths = _tiktoken_vocabulary_lengths(enc_name)
    tok2idx = [0] + list(itertools.accumulate(_vocabulary_lengths[i] for i in tokens))[:-1]
    result = Tokens(tokens=tokens, tok2idx=tok2idx)
    return result


def get_end_loc(
    loc: int,
    num_lines: int,
    total_lines: int,
    lines: list[str],
    view_tokens: int,
    encoding_name: str,
) -> int:
    if num_lines <= 0:
        txt = join_lines(lines[loc:], add_line_numbers=True, offset=loc)
        if len(txt) > view_tokens:
            upper_bound = max_chars_per_token(encoding_name)
            tok2idx = get_tokens(txt[: (view_tokens + 1) * upper_bound], encoding_name).tok2idx
            if len(tok2idx) > view_tokens:
                end_idx = tok2idx[view_tokens]
                num_lines = txt[:end_idx].count("\n") + 1
            else:
                num_lines = total_lines - loc
        else:
            num_lines = total_lines - loc
    else:
        if loc + num_lines > total_lines:
            num_lines = total_lines - loc
    return min(loc + num_lines, total_lines)


def get_page_metadata(
    curr_page: PageContents,
) -> dict[str, str | None | dict[str, str] | list[str]]:
    """Some attributes of the current page."""
    page_metadata: dict[str, str | None | dict[str, str] | list[str]] = {
        "url": curr_page.url,
        "title": curr_page.title,
    }
    return page_metadata


def join_lines(lines: list[str], add_line_numbers: bool = False, offset: int = 0) -> str:
    if add_line_numbers:
        return "\n".join([f"L{i + offset}: {line}" for i, line in enumerate(lines)])
    else:
        return "\n".join(lines)


def wrap_lines(text: str, width: int = 80) -> list[str]:
    lines = text.split("\n")
    wrapped = itertools.chain.from_iterable((textwrap.wrap(line, width=width, replace_whitespace=False, drop_whitespace=False) if line else [""]) for line in lines)  # preserve empty lines
    return list(wrapped)


def strip_links(text: str) -> str:
    text = re.sub(PARTIAL_INITIAL_LINK_PATTERN, "", text)
    text = re.sub(PARTIAL_FINAL_LINK_PATTERN, lambda mo: mo.group("content"), text)
    text = re.sub(LINK_PATTERN, lambda mo: mo.group("content"), text)
    return text


async def run_find_in_page(
    pattern: str,
    page: PageContents,
    max_results: int = 50,
    num_show_lines: int = 4,
) -> PageContents:
    lines = wrap_lines(text=page.text)
    txt = join_lines(lines, add_line_numbers=False)
    without_links = strip_links(txt)
    lines = without_links.split("\n")

    result_chunks, snippets = [], []
    line_idx, match_idx = 0, 0
    while line_idx < len(lines):
        line = lines[line_idx]
        if pattern not in line.lower():
            line_idx += 1
            continue
        snippet = "\n".join(lines[line_idx : line_idx + num_show_lines])
        link_title = FIND_PAGE_LINK_FORMAT.format(idx=f"{match_idx}", title=f"match at L{line_idx}")
        result_chunks.append(f"{link_title}\n{snippet}")
        snippets.append(Extract(url=page.url, text=snippet, title=f"#{match_idx}", line_idx=line_idx))
        if len(result_chunks) == max_results:
            break
        match_idx += 1
        line_idx += num_show_lines

    urls = [page.url for _ in result_chunks]

    if result_chunks:
        display_text = "\n\n".join(result_chunks)
    else:
        display_text = f"No `find` results for pattern: `{pattern}`"

    result_page = PageContents(
        url=f"{page.url}/find?pattern={quote(pattern)}",
        title=f"Find results for text: `{pattern}` in `{page.title}`",
        text=display_text,
        urls={str(i): url for i, url in enumerate(urls)},
        snippets={str(i): snip for i, snip in enumerate(snippets)},
    )
    return result_page


class BrowserSessionState(BaseModel):
    """统一 search/open/find 的会话状态."""

    url2page: OrderedDict[str, PageContents] = Field(default_factory=OrderedDict)
    current_url: str | None = None  # 记录当前激活页面 URL
    max_pages: int = 100  # LRU 容量上限，可由外部初始化时覆盖
    # 搜索缓存
    last_search_query: str | None = None
    last_search_results: list[PageContents] = Field(default_factory=list)
    max_search_results_cached: int = 0
    query_to_search_results: dict[str, list[PageContents]] = Field(default_factory=dict)

    def add_page(self, page: PageContents) -> None:
        # 如果已存在，先删除以便后面插入到末尾（保持最近使用）
        if page.url in self.url2page:
            try:
                del self.url2page[page.url]
            except KeyError:
                pass
        self.url2page[page.url] = page
        self.current_url = page.url
        # LRU 淘汰：超过容量弹出最旧
        while len(self.url2page) > self.max_pages:
            self.url2page.popitem(last=False)

    def get_page(self) -> PageContents | None:
        """返回当前页面；若不存在则返回 None。"""
        if not self.current_url or self.current_url not in self.url2page:
            return None
        page = self.url2page[self.current_url]
        # 触碰刷新 LRU 顺序
        del self.url2page[self.current_url]
        self.url2page[self.current_url] = page
        return page

    def get_page_by_url(self, url: str) -> PageContents | None:
        page = self.url2page.get(url)
        if page is not None:
            # 访问触碰：更新 LRU 顺序
            del self.url2page[url]
            self.url2page[url] = page
        return page

    # 搜索分页: 由 last_search_results 切片
    def get_search_page_slice(self, page: int, page_size: int) -> list[PageContents]:
        start = (page - 1) * page_size
        end = start + page_size
        return self.last_search_results[start:end]

    def clear_search(self):
        self.last_search_query = None
        self.last_search_results = []
        self.max_search_results_cached = 0
        self.query_to_search_results.clear()

    def set_query_results(self, query: str, results: list[PageContents]):
        # 直接缓存列表，保持最小冗余；total 可由 len(results) 外部获取
        self.query_to_search_results[query] = results
        self.last_search_query = query
        self.last_search_results = results
        self.max_search_results_cached = len(results)

    def get_query_results(self, query: str) -> list[PageContents] | None:
        return self.query_to_search_results.get(query)


class _BaseBrowser:
    """提供 search/open/find 公共逻辑的混入基类."""

    def __init__(
        self,
        backend: Backend,
        state: BrowserSessionState | None = None,
        *,
        encoding_name: str = ENC_NAME,
        view_tokens: int = 1024,
        max_search_results: int = 50,
    ):
        self.backend = backend
        self.state = state or BrowserSessionState()
        self.encoding_name = encoding_name
        self.view_tokens = view_tokens
        self.max_search_results = max_search_results

    # 工具公共辅助
    def _page_metadata(self, page: PageContents) -> dict[str, Any]:
        return get_page_metadata(page)

    def _render_browsing_display(self, result: str, summary: str | None = None) -> str:
        # 去掉 cursor 前缀，仅保留摘要 + 正文
        if summary:
            return f"{summary}{result}"
        return result

    def _make_tool_result(self, page: PageContents, body: str, scrollbar: str) -> ToolResult:
        domain = maybe_truncate(unquote(page.url))
        header = f"{page.title}"
        if domain:
            header += f" ({domain})"
        header += f"\n{scrollbar}\n\n"
        text = self._render_browsing_display(body, header)
        return ToolResult(message_content=[{"type": "text", "text": text}], data={**self._page_metadata(page)})

    async def show_page(self, loc: int = 0, num_lines: int = -1) -> ToolResult:
        page = self.state.get_page()
        if page is None:
            return tool_result_of_internal_error("No pages to access!")
        lines = wrap_lines(text=page.text)
        total_lines = len(lines)
        if loc >= total_lines:
            return tool_result_of_internal_error(f"Invalid location parameter: `{loc}`. Cannot exceed page maximum of {total_lines - 1}.")
        end_loc = get_end_loc(loc, num_lines, total_lines, lines, self.view_tokens, self.encoding_name)
        body = join_lines(lines[loc:end_loc], add_line_numbers=True, offset=loc)
        scrollbar = f"viewing lines [{loc} - {end_loc - 1}] of {total_lines - 1}"
        return self._make_tool_result(page, body, scrollbar)

    async def _open_url(self, url: str, direct_url_open: bool) -> PageContents:
        """Use the cache, if available."""
        backend = self.backend
        if not direct_url_open and (page := self.state.get_page_by_url(url)):
            assert page.url == url
            return page

        try:
            page = await backend.fetch(url)
            return page
        except Exception as e:
            msg = maybe_truncate(str(e))
            logger.warning("Error fetching URL in lean browser tool", exc_info=e)
            raise BackendError(f"Error fetching URL `{maybe_truncate(url)}`: {msg}") from e


class BrowserSearchTool(_BaseBrowser, BaseTool):
    """搜索工具: 支持分页返回, 缓存总结果."""

    def __init__(
        self,
        backend: Backend,
        state: BrowserSessionState | None = None,
        *,
        name: str = "browser_search",
        description: str = "Search web pages (paginated).",
        max_search_results: int = 50,
        default_page_size: int = 10,
    ):
        _BaseBrowser.__init__(self, backend, state, max_search_results=max_search_results)
        parameters: FunctionParameters = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "page": {"type": "integer", "minimum": 1, "default": 1},
                "page_size": {"type": "integer", "minimum": 1, "maximum": 50, "default": default_page_size},
            },
            "required": ["query"],
            "additionalProperties": False,
        }
        BaseTool.__init__(self, name=name, title="Browser Search", description=description, parameters=parameters, strict=True)
        self.default_page_size = default_page_size

    class SearchParams(ToolParamsBase):
        """Search 工具参数模型。

        字段说明:
            query (str): 搜索查询语句, 允许包含空格与特殊字符, 但在业务校验中会 strip 后必须非空。
            page (int): 结果页码 (>=1)。若超过最大页数, execute 阶段会回退到最后一页。
            page_size (int): 每页条目数, 1~50; normalize 中二次防御修正非法值。

        业务校验(post_validate):
            - query.strip() 为空则返回错误。

        归一化(normalize):
            - page_size <= 0 -> 10 (安全默认)
            - page_size > 50 -> 50 (上限裁剪)
        """

        query: str
        page: int = Field(1, ge=1)
        page_size: int = Field(10, ge=1, le=50)

        def post_validate(self):  # type: ignore[override]
            if not self.query.strip():
                return tool_result_of_internal_error("Invalid empty query")
            return None

        def normalize(self):  # type: ignore[override]
            # page_size 再保险限制
            if self.page_size <= 0:
                object.__setattr__(self, "page_size", 10)
            if self.page_size > 50:
                object.__setattr__(self, "page_size", 50)

    async def execute(self, params: ToolParams) -> ToolResult:  # type: ignore[override]
        args = self.SearchParams.parse_model(params)
        if isinstance(args, ToolResult):
            return args
        # 额外基于实例属性裁剪 page_size 到 self.max_search_results
        if args.page_size > self.max_search_results:  # type: ignore[attr-defined]
            object.__setattr__(args, "page_size", self.max_search_results)

        query = args.query.strip()
        page = args.page
        page_size = args.page_size
        cached_results = self.state.get_query_results(query)
        if cached_results is None:
            try:
                search_page = await self.backend.search(query=query, topn=self.max_search_results)
            except Exception as e:
                return tool_result_of_internal_error(f"Search failed: {maybe_truncate(str(e))}")
            # 修复: backend.search 返回的 PageContents 可能 url="" (为空字符串)
            # 这会导致 add_page 后 state.current_url 为空, get_page() 判定为无活动页面, 从而触发
            # "No active page available for search results display" 错误。这里为搜索结果页生成一个
            # 稳定的 synthetic URL, 形如 search://<urlencoded_query>，保证其在会话中可被正确识别。
            if not search_page.url.strip():  # 为空或全空白
                synthetic_url = f"search://{quote(query)}"
                try:
                    search_page = search_page.model_copy(update={"url": synthetic_url})  # pydantic v2方式
                except Exception:
                    # 兼容性回退: 若 model_copy 不可用 (极少数情况), 直接赋值
                    try:
                        object.__setattr__(search_page, "url", synthetic_url)  # type: ignore
                    except Exception:
                        pass  # 若仍失败, 不影响后续, 最坏回退原逻辑
            # backend.search 返回的是一个 PageContents (包含多个链接). 我们按之前逻辑: 整个 search page 作为一个 page.
            # 为了分页, 我们暂不拆分链接, 而是分页展示链接子集.
            # 将 search_page 的 urls/snippets 以 id 顺序拆解成 PageContents 的简化条目(每个结果对应一个 Extract snippet)
            results: list[PageContents] = []
            for k, url in (search_page.urls or {}).items():
                snip = (search_page.snippets or {}).get(k)
                title = snip.title if isinstance(snip, Extract) and snip.title else f"Result {k}"
                snippet_text = snip.text if isinstance(snip, Extract) else ""
                pc = PageContents(
                    url=url,
                    title=title,
                    text=snippet_text,
                    urls={},
                    snippets=None,
                )
                results.append(pc)
            # 写入缓存(不清空其它 query)
            self.state.set_query_results(query, results)
            # 把 search_page 也加入页面栈(方便后续引用 cursor) —— 仅当本次真正发起搜索时
            self.state.add_page(search_page)
        else:
            results = cached_results
            # 若缓存来自不同于当前 last_search_query, 同步便捷字段(不影响其它查询)
            self.state.last_search_query = query
            self.state.last_search_results = results
            self.state.max_search_results_cached = len(results)

        total = len(results)
        if total == 0:
            tr_empty = tool_result_of_text(f"No results for query: {query}")
            tr_empty.data = {"query": query}
            return tr_empty
        max_page = (total + page_size - 1) // page_size
        if page > max_page:
            page = max_page
        slice_results = self.state.get_search_page_slice(page, page_size)

        lines = []
        base_index_offset = (page - 1) * page_size
        for _, pc in enumerate(slice_results):
            # 去掉行头数字，只展示标题与链接
            lines.append(f"{pc.title}: {pc.url}\n{pc.text}")
        body = "\n\n".join(lines)
        scrollbar = f"page {page}/{max_page} page_size={page_size} total_pages={max_page} total_results={total}"
        current_page = self.state.get_page()
        if current_page is None:
            return tool_result_of_internal_error("No active page available for search results display")
        tr = self._make_tool_result(current_page, body, scrollbar)
        tr.data = (tr.data or {}) | {
            "query": query,
            "page": page,
            "page_size": page_size,
            "total": total,
            "max_page": max_page,
        }
        return tr


class BrowserOpenTool(_BaseBrowser, BaseTool):
    """打开指定 URL; 不再支持通过搜索结果索引打开。支持 view_source, 指定起始行 loc/行数 num_lines."""

    def __init__(
        self,
        backend: Backend,
        state: BrowserSessionState | None = None,
        *,
        name: str = "browser_open",
        description: str = "Open a previously listed search result or a direct URL.",
    ):
        _BaseBrowser.__init__(self, backend, state)
        parameters: FunctionParameters = {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "必填: 需要打开的 URL"},
                "loc": {"type": "integer", "default": 0, "description": "起始行，默认 0"},
                "num_lines": {"type": "integer", "default": -1, "description": "显示的行数，<=0 表示根据 token 预算自动截断"},
                "view_source": {"type": "boolean", "default": False, "description": "是否查看页面源码(视后端支持情况)"},
            },
            "required": ["url"],
            "additionalProperties": False,
        }
        BaseTool.__init__(self, name=name, title="Browser Open", description=description, parameters=parameters, strict=True)

    class OpenParams(ToolParamsBase):
        """Open 工具参数模型。

        字段:
            url (str): 目标 URL, strip 后必须非空。
            loc (int): 起始行号, 允许传负数; normalize 会将 <0 的值设为 0。
            num_lines (int): 显示行数; <=0 表示由 token 预算自适应截断。
            view_source (bool): 是否使用源码视图 (会在执行时加前缀 ``VIEW_SOURCE_PREFIX``)。

        业务校验:
            - url.strip() 为空报错

        归一化:
            - loc < 0 -> 0
        """

        url: str = Field(..., description="需要打开的URL")
        loc: int = Field(0, description="起始行 (>=0)")
        num_lines: int = Field(-1, description="显示行数, <=0 表示根据 token 预算自动截断")
        view_source: bool = Field(False, description="是否查看源码")

        def post_validate(self):  # type: ignore[override]
            if not self.url.strip():
                return tool_result_of_internal_error("`url` must be a non-empty string")
            return None

        def normalize(self):  # type: ignore[override]
            if self.loc < 0:
                object.__setattr__(self, "loc", 0)

    async def execute(self, params: ToolParams) -> ToolResult:  # type: ignore[override]
        args = self.OpenParams.parse_model(params)
        if isinstance(args, ToolResult):
            return args

        url = f"{VIEW_SOURCE_PREFIX}{args.url}" if args.view_source else args.url  # type: ignore[attr-defined]
        try:
            page = await self._open_url(url, direct_url_open=True)
        except Exception as e:
            return tool_result_of_internal_error(f"Open URL failed: {e}")
        self.state.add_page(page)
        return await self.show_page(loc=args.loc, num_lines=args.num_lines)  # type: ignore[attr-defined]


class BrowserFindTool(_BaseBrowser, BaseTool):
    """在指定 URL(已打开过)页面内查找字符串 pattern 并显示匹配 snippet 列表。强制要求提供 url。"""

    def __init__(
        self,
        backend: Backend,
        state: BrowserSessionState | None = None,
        *,
        name: str = "browser_find",
        description: str = "Find pattern in current opened page.",
    ):
        _BaseBrowser.__init__(self, backend, state)
        parameters: FunctionParameters = {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Lower/upper case insensitive substring to find"},
                "url": {"type": "string", "description": "目标页面 URL (需已通过 browser_open 打开并缓存)"},
                "max_results": {"type": "integer", "default": 50},
                "num_show_lines": {"type": "integer", "default": 4},
            },
            "required": ["pattern", "url"],
            "additionalProperties": False,
        }
        BaseTool.__init__(self, name=name, title="Browser Find", description=description, parameters=parameters, strict=True)

    class FindParams(ToolParamsBase):
        """Find 工具参数模型 (url 为必填)。

        字段:
            pattern (str): 查找的子串(大小写不敏感)。
            url (str): 已打开页面 URL；必须已通过 browser_open 缓存。
            max_results (int): 返回的匹配段上限 (1~200)。
            num_show_lines (int): 每个匹配段展示的行数 (1~50)。

        业务校验:
            - pattern.strip() 为空报错
            - url.strip() 为空报错

        归一化:
            - pattern = pattern.strip()
            - url = url.strip()
        """

        pattern: str = Field(..., description="要查找的子串 (case-insensitive)")
        url: str = Field(..., description="已打开的页面 URL")
        max_results: int = Field(50, ge=1, le=200)
        num_show_lines: int = Field(4, ge=1, le=50)

        def post_validate(self):  # type: ignore[override]
            if not self.pattern.strip():
                return tool_result_of_internal_error("Empty pattern")
            if not self.url.strip():
                return tool_result_of_internal_error("Empty url")
            return None

        def normalize(self):  # type: ignore[override]
            object.__setattr__(self, "pattern", self.pattern.strip())
            object.__setattr__(self, "url", self.url.strip())

    async def execute(self, params: ToolParams) -> ToolResult:  # type: ignore[override]
        args = self.FindParams.parse_model(params)
        if isinstance(args, ToolResult):
            return args

        # 页面解析 (url 已强制要求提供)
        page = self.state.get_page_by_url(args.url)
        if page is None:
            return tool_result_of_internal_error(f"URL not opened yet: {args.url}")
        if page.snippets is not None and page.url.endswith("/find?pattern="):
            return tool_result_of_internal_error("Cannot run find on aggregated search result page")
        try:
            pc = await run_find_in_page(
                pattern=args.pattern.lower(),
                page=page,
                max_results=args.max_results,
                num_show_lines=args.num_show_lines,
            )
        except Exception as e:
            return tool_result_of_internal_error(f"Find failed: {e}")
        self.state.add_page(pc)
        return await self.show_page(loc=0, num_lines=-1)


# 兼容旧引用: 暂保留 normalize_citations 等实用函数, 但不再输出 Message
class LegacyCitationHelper:
    def __init__(self, state: BrowserSessionState):
        self.state = state

    def normalize_citations(self, old_content: str, hide_partial_citations: bool = False):
        has_partial_citations = PARTIAL_FINAL_LINK_PATTERN.search(old_content) is not None
        if hide_partial_citations and has_partial_citations:
            old_content = PARTIAL_FINAL_LINK_PATTERN.sub("", old_content)
        matches = []
        for match in CITATION_OUTPUT_PATTERN.finditer(old_content):
            cursor = match.group("cursor")
            content = match.group("content")
            start_idx = match.start()
            end_idx = match.end()
            matches.append({"cursor": cursor, "content": content, "start": start_idx, "end": end_idx})
        # 由于已移除 page_stack，不再尝试替换为真实 URL，直接返回原文本与空注解
        annotations: list[dict[str, Any]] = []
        return old_content, annotations, has_partial_citations


if __name__ == "__main__":  # 简单演示，不执行真实网络请求(需提供 Backend 实例)

    async def demo():  # pragma: no cover
        backend = ExaBackend(source="demo")  # 需根据实际 backend 初始化
        shared_state = BrowserSessionState()
        search_tool = BrowserSearchTool(backend, state=shared_state)
        open_tool = BrowserOpenTool(backend, state=shared_state)
        find_tool = BrowserFindTool(backend, state=shared_state)

        # 1. 执行搜索(生成一个 synthetic search:// URL 页面)
        res = await search_tool.execute({"query": "python", "page": 1})
        print("[Search Result]\n" + content_to_text(res.message_content))

        # 2. 打开真实页面 URL
        open_url = "https://www.python.org"
        res = await open_tool.execute({"url": open_url})
        print("\n[Open Page]\n" + content_to_text(res.message_content))

        # 3. 在刚才打开的页面中查找关键字 (必须显式提供 url，避免 Field required 错误)
        res = await find_tool.execute({"pattern": "async", "url": open_url})
        print("\n[Find In Page]\n" + content_to_text(res.message_content))

    from dotenv import load_dotenv

    load_dotenv()
    import asyncio

    asyncio.run(demo())
