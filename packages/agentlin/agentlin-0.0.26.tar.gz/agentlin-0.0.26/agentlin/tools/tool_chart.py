
from abc import abstractmethod, ABC
import httpx
from agentlin.code_interpreter.chart_schema import *


class ChartBackend(ABC):
    @abstractmethod
    async def generate_chart_url(self, chart_type: ChartType, **options) -> str:
        pass


class AntvChartBackend(ChartBackend):
    DEFAULT_CHART_URL = "https://antv-studio.alipay.com/api/gpt-vis"

    async def generate_chart_url(self, chart_type: ChartType, **options) -> str:
        options["type"] = chart_type
        payload = {
            **options,
            "source": "dify-plugin-visualization",
        }
        headers = {
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.DEFAULT_CHART_URL, json=payload, headers=headers)
                data = response.json()
                if not data.get("success"):
                    print(data)
                return data.get("resultObj", "")
        except httpx.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Status code: {response.status_code}")
            print(f"Response content: {response.text}")
            raise
        except httpx.RequestError as e:
            print(f"Request failed: {e}")
            raise
        except Exception as e:
            print(f"An error occurred: {e}")
            raise


from fastmcp import Client

class ClientChartBackend(ChartBackend):
    CHART_TYPE_TO_TOOL = {
        "area": "generate_area_chart",
        "bar": "generate_bar_chart",
        "boxplot": "generate_boxplot_chart",
        "column": "generate_column_chart",
        "district_map": "generate_district_map",
        "dual_axes": "generate_dual_axes_chart",
        "fishbone": "generate_fishbone_diagram",
        "flow": "generate_flow_diagram",
        "funnel": "generate_funnel_chart",
        "histogram": "generate_histogram_chart",
        "line": "generate_line_chart",
        "liquid": "generate_liquid_chart",
        "mind_map": "generate_mind_map",
        "network": "generate_network_graph",
        "organization": "generate_organization_chart",
        "path_map": "generate_path_map",
        "pie": "generate_pie_chart",
        "pin_map": "generate_pin_map",
        "radar": "generate_radar_chart",
        "sankey": "generate_sankey_chart",
        "scatter": "generate_scatter_chart",
        "treemap": "generate_treemap_chart",
        "venn": "generate_venn_chart",
        "violin": "generate_violin_chart",
        "word_cloud": "generate_word_cloud_chart",
    }

    def __init__(self, client: Client):
        self.client = client

    async def generate_chart_url(self, chart_type: ChartType, **options) -> str:
        if chart_type not in self.CHART_TYPE_TO_TOOL:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        tool_name = self.CHART_TYPE_TO_TOOL[chart_type]
        async with self.client:
            result = await self.client.call_tool(tool_name, options)
            url = result.data.get("resultObj")
            return url


# 通用图表生成函数 - 实际实现
async def generate_chart_url(
    chart_type: ChartType,
    **options,
):
    """
    通用图表生成函数，根据chart_type参数生成不同类型的图表

    Args:
        chart_type: 图表类型，支持多种图表格式
        **options: 图表配置参数，根据不同图表类型有不同的参数要求

    Returns:
        生成的图表数据
    """
    backend = AntvChartBackend()
    return await backend.generate_chart_url(chart_type, **options)


# --- Interactive config builder (ECharts) ---
def _ensure_percent(v: NumberType, default_outer: str = "70%") -> Union[str, List[str]]:
    if v is None or v == 0:
        return default_outer
    try:
        # If inner radius is in [0,1], treat as percent
        if 0 < float(v) <= 1:
            inner = f"{int(float(v) * 100)}%"
        else:
            inner = v  # allow px
        return [inner, default_outer]
    except Exception:
        return default_outer


def _title_option(title: str) -> Dict[str, Any]:
    return {"text": title} if title else {}


def _legend_option(enable: bool = True) -> Dict[str, Any]:
    return {"show": enable}


def _tooltip_option(fmt: Optional[str] = None) -> Dict[str, Any]:
    opt: Dict[str, Any] = {"trigger": "item"}
    if fmt:
        opt["formatter"] = fmt
    return opt


def _quantiles(sorted_vals: List[float]) -> tuple[float, float, float, float, float]:
    n = len(sorted_vals)
    if n == 0:
        return (0, 0, 0, 0, 0)
    def q(p: float) -> float:
        # Inclusive method
        if n == 1:
            return sorted_vals[0]
        idx = p * (n - 1)
        lo = int(idx)
        hi = min(lo + 1, n - 1)
        frac = idx - lo
        return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac
    mn = sorted_vals[0]
    q1 = q(0.25)
    med = q(0.5)
    q3 = q(0.75)
    mx = sorted_vals[-1]
    return (mn, q1, med, q3, mx)


def _to_tree_node(node: Dict[str, Any]) -> Dict[str, Any]:
    # normalize keys: expect 'name' and optional 'children'
    name = node.get("name") or node.get("title") or str(node)
    children = node.get("children") or []
    return {"name": name, "children": [
        _to_tree_node(c) if isinstance(c, dict) else {"name": str(c)} for c in children
    ]}


async def generate_chart_config(
    chart_type: ChartType,
    **options,
) -> Dict[str, Any]:
    """
    构建可交互前端渲染所需的 ECharts 配置。

    Returns:
        dict: ECharts option 对象，可直接在前端使用 echartsInstance.setOption(option)。
    """
    title = options.get("title", "")
    axisXTitle = options.get("axisXTitle", "")
    axisYTitle = options.get("axisYTitle", "")

    if chart_type in ("line", "area"):
        data: List[LineChartData] = options.get("data", [])  # type: ignore
        stack: bool = bool(options.get("stack", False))
        # collect categories and groups
        x_vals: List[str] = []
        groups: Dict[Optional[str], List[NumberType]] = {}
        # first pass to maintain order
        for item in data:
            if item["time"] not in x_vals:
                x_vals.append(item["time"])
        # init groups
        group_names: List[Optional[str]] = []
        for item in data:
            g = item.get("group")
            if g not in groups:
                groups[g] = [None] * len(x_vals)  # type: ignore
                group_names.append(g)
        # fill series values aligned to x
        x_index = {x: i for i, x in enumerate(x_vals)}
        for item in data:
            idx = x_index[item["time"]]
            g = item.get("group")
            groups[g][idx] = item["value"]  # type: ignore

        series = []
        for g in group_names:
            s = {
                "name": g or "value",
                "type": "line",
                "data": groups[g],
                "smooth": True,
            }
            if chart_type == "area":
                s["areaStyle"] = {}
            if stack and len(group_names) > 1:
                s["stack"] = "total"
            series.append(s)

        option: Dict[str, Any] = {
            "title": _title_option(title),
            "tooltip": {"trigger": "axis"},
            "legend": _legend_option(len(series) > 1),
            "xAxis": {"type": "category", "name": axisXTitle, "data": x_vals},
            "yAxis": {"type": "value", "name": axisYTitle},
            "series": series,
        }
        return option

    if chart_type in ("column", "bar"):
        data: List[ColumnChartData] = options.get("data", [])  # type: ignore
        group: bool = bool(options.get("group", chart_type == "column"))
        stack: bool = bool(options.get("stack", False))

        categories: List[str] = []
        for d in data:
            if d["category"] not in categories:
                categories.append(d["category"])

        group_names: List[Optional[str]] = []
        values_by_group: Dict[Optional[str], List[NumberType]] = {}
        for d in data:
            g = d.get("group") if group else None
            if g not in values_by_group:
                values_by_group[g] = [0] * len(categories)
                group_names.append(g)
        cat_idx = {c: i for i, c in enumerate(categories)}
        for d in data:
            g = d.get("group") if group else None
            values_by_group[g][cat_idx[d["category"]]] = d["value"]

        series = []
        for g in group_names:
            s = {
                "name": g or "value",
                "type": "bar",
                "data": values_by_group[g],
            }
            if stack and len(group_names) > 1:
                s["stack"] = "total"
            series.append(s)

        # Orientation: column -> x: category, y: value; bar -> x: value, y: category
        if chart_type == "column":
            xAxis = {"type": "category", "name": axisXTitle, "data": categories}
            yAxis = {"type": "value", "name": axisYTitle}
        else:
            xAxis = {"type": "value", "name": axisXTitle}
            yAxis = {"type": "category", "name": axisYTitle, "data": categories}

        return {
            "title": _title_option(title),
            "tooltip": _tooltip_option(),
            "legend": _legend_option(len(series) > 1),
            "xAxis": xAxis,
            "yAxis": yAxis,
            "series": series,
        }

    if chart_type == "scatter":
        points: List[ScatterChartData] = options.get("data", [])  # type: ignore
        xy = [[p["x"], p["y"]] for p in points]
        return {
            "title": _title_option(title),
            "tooltip": _tooltip_option(),
            "xAxis": {"type": "value", "name": axisXTitle},
            "yAxis": {"type": "value", "name": axisYTitle},
            "series": [{"type": "scatter", "data": xy}],
        }

    if chart_type == "pie":
        items: List[PieChartData] = options.get("data", [])  # type: ignore
        innerRadius: NumberType = options.get("innerRadius", 0)
        s: Dict[str, Any] = {
            "type": "pie",
            "data": [{"name": i["category"], "value": i["value"]} for i in items],
        }
        radius = _ensure_percent(innerRadius)
        if isinstance(radius, list):
            s["radius"] = radius
        else:
            s["radius"] = radius
        return {
            "title": _title_option(title),
            "tooltip": _tooltip_option("{b}: {c} ({d}%)"),
            "legend": _legend_option(True),
            "series": [s],
        }

    if chart_type == "funnel":
        items: List[FunnelChartData] = options.get("data", [])  # type: ignore
        return {
            "title": _title_option(title),
            "tooltip": _tooltip_option("{b}: {c}"),
            "legend": _legend_option(True),
            "series": [{
                "type": "funnel",
                "data": [{"name": i["category"], "value": i["value"]} for i in items],
                "label": {"show": True, "formatter": "{b}: {c}"},
            }],
        }

    if chart_type == "histogram":
        nums: List[NumberType] = options.get("data", [])  # type: ignore
        binNumber: Optional[int] = options.get("binNumber")  # type: ignore
        if not nums:
            return {
                "title": _title_option(title),
                "series": [{"type": "bar", "data": []}],
                "xAxis": {"type": "category", "name": axisXTitle, "data": []},
                "yAxis": {"type": "value", "name": axisYTitle},
            }
        mn, mx = float(min(nums)), float(max(nums))
        if mn == mx:
            bins = 1
        else:
            bins = int(binNumber or max(5, min(30, round(len(nums) ** 0.5))))
        width = (mx - mn) / max(bins, 1)
        # Create categories as ranges
        edges = [mn + i * width for i in range(bins + 1)]
        counts = [0] * bins
        for v in nums:
            if v == mx:
                idx = bins - 1
            else:
                idx = int((float(v) - mn) / width) if width > 0 else 0
                idx = max(0, min(bins - 1, idx))
            counts[idx] += 1
        labels = [f"{edges[i]:.2f}~{edges[i+1]:.2f}" for i in range(bins)]
        return {
            "title": _title_option(title),
            "tooltip": _tooltip_option(),
            "xAxis": {"type": "category", "name": axisXTitle, "data": labels},
            "yAxis": {"type": "value", "name": axisYTitle},
            "series": [{"type": "bar", "data": counts}],
        }

    if chart_type == "boxplot":
        # Note: current implementation flattens group into category label if provided.
        items: List[BoxplotChartData] = options.get("data", [])  # type: ignore
        # group by (group, category)
        buckets: Dict[str, List[float]] = {}
        for it in items:
            key = f"{it.get('group') or ''}:{it['category']}"
            buckets.setdefault(key, []).append(float(it["value"]))
        categories = list(buckets.keys())
        series_data = []
        for key in categories:
            vals = sorted(buckets[key])
            series_data.append(list(_quantiles(vals)))
        return {
            "title": _title_option(title),
            "tooltip": _tooltip_option(),
            "xAxis": {"type": "category", "data": categories, "name": axisXTitle},
            "yAxis": {"type": "value", "name": axisYTitle},
            "series": [{"type": "boxplot", "data": series_data}],
        }

    if chart_type == "radar":
        items: List[RadarChartData] = options.get("data", [])  # type: ignore
        # Collect dimensions and group
        dims: List[str] = []
        group_values: Dict[Optional[str], Dict[str, NumberType]] = {}
        for it in items:
            n = it["name"]
            if n not in dims:
                dims.append(n)
            g = it.get("group")
            if g not in group_values:
                group_values[g] = {}
            group_values[g][n] = it["value"]
        indicators = [{"name": d} for d in dims]
        series_data = []
        for g, vals in group_values.items():
            series_data.append({
                "name": g or "value",
                "value": [vals.get(d, 0) for d in dims],
            })
        return {
            "title": _title_option(title),
            "legend": _legend_option(len(series_data) > 1),
            "tooltip": _tooltip_option(),
            "radar": {"indicator": indicators},
            "series": [{"type": "radar", "data": series_data}],
        }

    if chart_type == "liquid":
        percent: NumberType = options.get("percent", 0)  # type: ignore
        shape: str = options.get("shape", "circle")  # type: ignore
        return {
            "title": _title_option(title),
            "series": [{
                "type": "liquidFill",  # requires echarts-liquidfill plugin on frontend
                "data": [percent],
                "shape": shape,
                "outline": {"show": False},
                "label": {"show": True, "formatter": "{a}"},
            }],
        }

    if chart_type == "dual_axes":
        categories: List[str] = options.get("categories", [])  # type: ignore
        series_in: List[DualAxesChartSeries] = options.get("series", [])  # type: ignore
        # Assume first series -> yAxisIndex 0; second -> 1
        y_names = []
        for s in series_in:
            if s.get("axisYTitle") not in y_names:
                y_names.append(s.get("axisYTitle"))
        echarts_series = []
        for idx, s in enumerate(series_in):
            echarts_series.append({
                "name": s.get("axisYTitle") or f"Series {idx+1}",
                "type": "bar" if s.get("type") == "column" else "line",
                "yAxisIndex": 0 if idx == 0 else 1,
                "data": s.get("data", []),
                "smooth": s.get("type") == "line",
            })
        return {
            "title": _title_option(title),
            "legend": _legend_option(True),
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "cross"}},
            "xAxis": {"type": "category", "name": axisXTitle, "data": categories},
            "yAxis": [
                {"type": "value", "name": y_names[0] if len(y_names) > 0 else axisYTitle},
                {"type": "value", "name": y_names[1] if len(y_names) > 1 else ""},
            ],
            "series": echarts_series,
        }

    if chart_type == "mind_map":
        root: MindMapData = options.get("data", {"name": "", "children": []})  # type: ignore
        return {
            "title": _title_option(title),
            "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
            "series": [{
                "type": "tree",
                "data": [_to_tree_node(root)],
                "layout": "radial",
                "symbolSize": 7,
                "label": {"position": "left", "verticalAlign": "middle", "align": "right"},
                "expandAndCollapse": True,
                "animationDuration": 550,
                "animationDurationUpdate": 750,
            }],
        }

    if chart_type == "organization":
        root: OrganizationChartData = options.get("data", {"name": "", "children": []})  # type: ignore
        orient: str = options.get("orient", "vertical")  # type: ignore
        dir_map = {"vertical": "TB", "horizontal": "LR"}
        return {
            "title": _title_option(title),
            "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
            "series": [{
                "type": "tree",
                "data": [_to_tree_node(root)],
                "top": "5%",
                "left": "20%",
                "bottom": "5%",
                "right": "20%",
                "symbolSize": 8,
                "orient": dir_map.get(orient, "TB"),
                "label": {"position": "left", "verticalAlign": "middle", "align": "right"},
                "leaves": {"label": {"position": "right", "verticalAlign": "middle", "align": "left"}},
                "expandAndCollapse": True,
                "animationDuration": 550,
                "animationDurationUpdate": 750,
            }],
        }

    if chart_type == "flow":
        data_in: FlowDiagramData = options.get("data", {"nodes": [], "edges": []})  # type: ignore
        nodes = data_in.get("nodes", [])
        edges = data_in.get("edges", [])
        return {
            "title": _title_option(title),
            "tooltip": {},
            "series": [{
                "type": "graph",
                "layout": "force",
                "data": [{"name": n.get("id") or n.get("name") or str(n), **n} for n in nodes],
                "links": [{"source": e.get("source"), "target": e.get("target"), **e} for e in edges],
                "roam": True,
                "label": {"show": True, "position": "right"},
                "force": {"repulsion": 200, "edgeLength": 80},
            }],
        }

    if chart_type == "fishbone":
        root: FishboneDiagramData = options.get("data", {"name": "", "children": []})  # type: ignore
        # Approximate fishbone using tree LR layout
        return {
            "title": _title_option(title),
            "series": [{
                "type": "tree",
                "data": [_to_tree_node(root)],
                "left": "2%",
                "right": "2%",
                "top": "8%",
                "bottom": "8%",
                "orient": "LR",
                "symbol": "emptyCircle",
                "symbolSize": 6,
                "expandAndCollapse": True,
                "label": {"position": "left", "verticalAlign": "middle", "align": "right"},
                "leaves": {"label": {"position": "right", "verticalAlign": "middle", "align": "left"}},
            }],
        }

    if chart_type == "network":
        data_in: NetworkGraphData = options.get("data", {"nodes": [], "edges": []})  # type: ignore
        nodes = data_in.get("nodes", [])
        edges = data_in.get("edges", [])
        return {
            "title": _title_option(title),
            "tooltip": {},
            "series": [{
                "type": "graph",
                "layout": "force",
                "data": [{"name": n.get("id") or n.get("name") or str(n), **n} for n in nodes],
                "links": [{"source": e.get("source"), "target": e.get("target"), **e} for e in edges],
                "roam": True,
                "label": {"show": True},
                "force": {"repulsion": 400, "edgeLength": [50, 150]},
            }],
        }

    if chart_type == "sankey":
        links: List[SankeyChartData] = options.get("data", [])  # type: ignore
        nodeAlign: str = options.get("nodeAlign", "center")  # type: ignore
        # build node list
        node_names = []
        for l in links:
            for name in (l.get("source"), l.get("target")):
                if name not in node_names:
                    node_names.append(name)  # type: ignore
        nodes = [{"name": n} for n in node_names]
        return {
            "title": _title_option(title),
            "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
            "series": [{
                "type": "sankey",
                "emphasis": {"focus": "adjacency"},
                "nodeAlign": nodeAlign,
                "data": nodes,
                "links": [{"source": l["source"], "target": l["target"], "value": l["value"]} for l in links],
            }],
        }

    if chart_type == "treemap":
        items: List[TreemapChartData] = options.get("data", [])  # type: ignore
        return {
            "title": _title_option(title),
            "tooltip": _tooltip_option(),
            "series": [{
                "type": "treemap",
                "data": items,
                "leafDepth": 2,
                "label": {"show": True, "formatter": "{b}"},
            }],
        }

    if chart_type == "word_cloud":
        items: List[WordCloudChartData] = options.get("data", [])  # type: ignore
        return {
            "title": _title_option(title),
            "series": [{
                "type": "wordCloud",  # requires echarts-wordcloud plugin on frontend
                "shape": "circle",
                "gridSize": 8,
                "sizeRange": [12, 48],
                "rotationRange": [-45, 90],
                "textStyle": {"fontFamily": "sans-serif"},
                "data": [{"name": w["text"], "value": w["value"]} for w in items],
            }],
        }

    # The following types require external map data or complex custom series, leaving as TODO:
    if chart_type in ("district_map", "path_map", "pin_map", "venn", "violin"):
        raise NotImplementedError(
            f"generate_chart_config: '{chart_type}' needs map data or a custom/plugin series. "
            "Consider using generate_chart(...) for a URL, or include the needed frontend plugin and extend this mapper."
        )

    # Not yet supported types -> explicitly notify caller
    raise NotImplementedError(
        f"generate_chart_config does not yet support chart_type='{chart_type}'. "
        "You can still use generate_chart(...) to get an URL, or extend the mapper."
    )
