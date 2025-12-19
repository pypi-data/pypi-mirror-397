from typing import TypedDict
from typing_extensions import Any, Literal, Union, Optional
import datetime as dt

import pandas as pd
import numpy as np
from loguru import logger

# Try to import polars if available
try:
    import polars as pl

    POLARS_AVAILABLE = True
except ImportError:
    pl = None
    POLARS_AVAILABLE = False

TABLE_TYPE = Union[
    pd.DataFrame,
    pd.Series,
    list[dict],
    np.ndarray,
    Any,
]

class TableJson(TypedDict):
    columns: list[dict[str, Any]]
    datas: list[dict[str, Any]]
    query: Optional[str]
    text: Optional[str]
    metadata: Optional[dict[str, Any]]

def data_to_table_json(data: TABLE_TYPE) -> dict:
    """
    将各种数据格式转换为表格JSON格式

    Args:
        data: 支持pandas DataFrame/Series、polars DataFrame/Series、numpy数组、字典列表
              空数据也是合法输入，将返回空表格的JSON格式

    Returns:
        dict: 包含uuid、config、data和show_type的字典

    Raises:
        ValueError: 当输入数据为None或不支持的数据类型时
        TypeError: 当数据格式转换失败时
    """
    # Convert data to DataFrame first
    data = data_to_dataframe(data)

    # Generate table JSON from DataFrame
    return dataframe_to_table_json(data)


def data_to_dataframe(data: TABLE_TYPE) -> pd.DataFrame:
    """
    将各种数据格式转换为pandas DataFrame

    Args:
        data: 支持pandas DataFrame/Series、polars DataFrame/Series、numpy数组、字典列表

    Returns:
        pd.DataFrame: 转换后的DataFrame
    """

    # Error handling: Check for None data
    if data is None:
        raise ValueError("Cannot convert None data to table JSON")

    # Handle numpy arrays - convert to DataFrame
    if isinstance(data, (np.ndarray, np.generic)):
        try:
            data = pd.DataFrame(data)  # type: ignore
        except Exception as e:
            raise TypeError(f"Failed to convert numpy array to DataFrame: {e}")

    # Handle list of dictionaries - convert to DataFrame
    if isinstance(data, list):
        try:
            data = pd.DataFrame(data)
        except Exception as e:
            raise TypeError(f"Failed to convert list to DataFrame: {e}")

    # Handle polars DataFrame - convert to pandas DataFrame
    if POLARS_AVAILABLE and pl is not None and isinstance(data, pl.DataFrame):
        try:
            data = data.to_pandas()
        except Exception as e:
            raise TypeError(f"Failed to convert polars DataFrame to pandas: {e}")

    # Handle Series (both pandas and polars) - convert to DataFrame
    if isinstance(data, pd.Series):
        try:
            data = data.to_frame()
        except Exception as e:
            raise TypeError(f"Failed to convert pandas Series to DataFrame: {e}")
    elif POLARS_AVAILABLE and pl is not None and isinstance(data, pl.Series):
        try:
            data = data.to_pandas().to_frame()
        except Exception as e:
            raise TypeError(f"Failed to convert polars Series to DataFrame: {e}")

    # Ensure we have a DataFrame at this point
    if not isinstance(data, pd.DataFrame):
        raise ValueError(f"Unsupported data type: {type(data)}")
    return data



def dataframe_to_table_json(data: pd.DataFrame, include_index: bool=False) -> dict:
    """
    将各种数据格式转换为表格JSON格式

    Args:
        data: pandas DataFrame

    Returns:
        Optional[dict]: 包含 "columns" 和 "datas" 的表格JSON格式数据

    Raises:
        ValueError: 当输入数据为None或不支持的数据类型时
        TypeError: 当数据格式转换失败时
    """
    # Process DataFrame to extract columns and data
    if hasattr(data, "_query_data_"):
        query_data = data._query_data_()  # type: ignore
        if query_data and isinstance(query_data, dict):
            return query_data

    columns = []
    datas = []

    # Include index if it's not a default range index
    include_index = include_index and (not isinstance(data.index, pd.RangeIndex) or data.index.name is not None)

    # Build columns metadata
    if include_index:
        index_name = data.index.name or "index"
        columns.append(
            {
                "index_name": index_name,
                "key": index_name,
                "type": _infer_column_type(data.index.dtype),
            }
        )

    for col in data.columns:
        col_info = {
            "index_name": str(col),
            "key": str(col),
            "type": _infer_column_type(data[col].dtype),
        }

        # Add unit for numeric columns (placeholder logic)
        if col_info["type"] in ["DOUBLE", "LONG"]:
            if any(keyword in str(col).lower() for keyword in ["幅", "率", "percent"]):
                col_info["unit"] = "%"

        columns.append(col_info)

    # Build data rows - Performance optimization: use vectorized operations
    try:
        # Handle empty DataFrame case
        if data.empty:
            datas = []
        else:
            # Convert DataFrame to list of dictionaries efficiently
            if include_index:
                # Reset index to make it a column, then convert to records
                temp_df = data.reset_index()
                if data.index.name is None:
                    temp_df.rename(columns={'index': 'index'}, inplace=True)

                # Apply formatting to all values at once using vectorized operations
                for col in temp_df.columns:
                    temp_df[col] = temp_df[col].apply(_format_value)

                datas = temp_df.to_dict('records')
            else:
                # Apply formatting to all values at once
                formatted_df = data.copy()
                for col in formatted_df.columns:
                    formatted_df[col] = formatted_df[col].apply(_format_value)

                datas = formatted_df.to_dict('records')

    except Exception as e:
        logger.error(f"Failed to convert DataFrame to records: {e}")

    # Build the final JSON structure
    result = {
        "columns": columns,
        "datas": datas,
    }

    return result


def validate_query_data_to_table_json(data: pd.DataFrame, query_data: Optional[dict]=None) -> Optional[dict]:
    """将查询数据转换为表格JSON格式

    Args:
        data: 原始数据DataFrame
        query_data: 来自 FinQuery 带出来的原始数据 schema

    Returns:
        Optional[dict]: 表格JSON格式数据或None
    """
    if not query_data:
        raise ValueError("_query_data_ returns None or empty")
    df_columns = list(data.columns)
    columns = query_data.get("columns")
    datas = query_data.get("datas")
    if columns is None:
        raise ValueError("'columns' is missing in _query_data_")
    if datas is None:
        raise ValueError("'datas' is missing in _query_data_")
    if len(columns) != len(df_columns):
        raise ValueError("Number of columns in _query_data_ does not match DataFrame")
    if len(datas) != len(data):
        raise ValueError("Number of rows in _query_data_ does not match DataFrame")
    return query_data


def _infer_column_type(dtype) -> Literal["STR", "DOUBLE", "DATE", "LONG", "BOOLEAN"]:
    """推断列的数据类型

    Args:
        dtype: pandas数据类型

    Returns:
        str: 推断出的类型字符串
    """
    try:
        if pd.api.types.is_integer_dtype(dtype):
            return "LONG"
        elif pd.api.types.is_float_dtype(dtype):
            return "DOUBLE"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return "DATE"
        elif pd.api.types.is_bool_dtype(dtype):
            return "BOOLEAN"
        else:
            return "STR"
    except Exception:
        # Default to string type if type inference fails
        return "STR"


def _format_value(value) -> str:
    """格式化值为字符串

    Args:
        value: 要格式化的值

    Returns:
        str: 格式化后的字符串
    """
    try:
        if pd.isna(value):
            return ""
        elif isinstance(value, (bool, str)):
            return value
        elif isinstance(value, type(None)):
            return ""
        elif isinstance(value, (int, float)):
            if isinstance(value, float):
                # Handle special float values
                if np.isinf(value):
                    return "∞" if value > 0 else "-∞"
                elif np.isnan(value):
                    return ""
                elif value.is_integer():
                    return int(value)
            return value
        elif isinstance(value, pd.Timestamp):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, pd.Timedelta):
            return str(value)
        elif isinstance(value, dt.datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, dt.date):
            return value.strftime("%Y-%m-%d")
        else:
            return str(value)
    except Exception:
        # Fallback to empty string if formatting fails
        return ""


def dataframe_to_markdown(df: pd.DataFrame, table_json: Optional[dict]=None, query_data: Optional[dict]=None) -> str:
    """将表格JSON格式转换为Markdown格式

    Args:
        df(pd.DataFrame): 要转换的DataFrame
        table_json (Optional[dict]): 可选的表格JSON格式数据
        query_data (Optional[dict]): 可选的查询数据

    Returns:
        str: Markdown格式字符串
    """
    if query_data and "text" in query_data:
        return query_data["text"]
    if not table_json:
        if query_data:
            table_json = validate_query_data_to_table_json(df, query_data)
        else:
            table_json = dataframe_to_table_json(df)

    # Generate Markdown table
    md_lines = []

    if query_data:
        query_id = query_data.get("query_id", None)
        if query_id:
            md_lines.append(f"ID: {query_id}")

        query = query_data.get("query", "")
        if query:
            md_lines.append(f"Query: {query}")
            md_lines.append(f"Results:")

    # Extract columns and data
    columns = table_json.get("columns", [])
    datas = table_json.get("datas", [])

    if len(datas) == 0:
        md_lines.append("No results found.")
        return "\n".join(md_lines)
    if len(datas) > 10:
        md_lines.append(f"{len(datas)} results found. Showing first 5 rows and last 5 rows.")

    # Header
    header = "| " + " | ".join(col.get("key", "") for col in columns) + " |"
    md_lines.append(header)
    md_lines.append("|" + "|".join(["---"] * len(columns)) + "|")

    # Rows
    if len(datas) > 10:
        first_5_rows = datas[:5]
        last_5_rows = datas[-5:]
        for row in first_5_rows:
            md_row = "| " + " | ".join(str(row.get(col.get("key", ""), "")) for col in columns) + " |"
            md_lines.append(md_row)
        md_row = "| " + " | ".join("..." for col in columns) + " |"
        md_lines.append(md_row)
        for row in last_5_rows:
            md_row = "| " + " | ".join(str(row.get(col.get("key", ""), "")) for col in columns) + " |"
            md_lines.append(md_row)
    else:
        for row in datas:
            md_row = "| " + " | ".join(str(row.get(col.get("key", ""), "")) for col in columns) + " |"
            md_lines.append(md_row)

    return "\n".join(md_lines)


def table_json_to_dataframe(table_json: dict) -> pd.DataFrame:
    """将表格JSON格式还原为 pandas DataFrame

    预期输入结构：
    {
        "columns": [
            {"index_name": str, "key": str, "type": "STR"|"DOUBLE"|"INT"|"DATE"[, "is_index": bool]},
            ...
        ],
        "datas": [ { <key>: <value>, ... }, ... ]
    }

    Args:
        table_json (dict): 包含 columns 和 datas 的表格JSON

    Returns:
        pd.DataFrame: 构造的 DataFrame
    """

    if not isinstance(table_json, dict):
        raise ValueError("table_json_to_dataframe: table_json must be a dict")

    columns = table_json.get("columns")
    datas = table_json.get("datas")

    if columns is None or datas is None:
        raise ValueError("table_json_to_dataframe: missing 'columns' or 'datas'")

    if not isinstance(columns, list):
        raise ValueError("table_json_to_dataframe: 'columns' must be a list")
    if not isinstance(datas, list):
        raise ValueError("table_json_to_dataframe: 'datas' must be a list")

    df_columns = set()
    for data in datas:
        df_columns.update(data.keys())
    df = pd.DataFrame(datas, columns=list(df_columns))

    col_name_old2new = {}
    for col in columns:
        if col and col.get("unit") and col.get("key"):
            col_name_old2new[col["key"]] = f"{col['key']}({col['unit']})"
    if col_name_old2new:
        df.rename(columns=col_name_old2new, inplace=True)

    # 除了 STR 类型，其他类型都尝试转换
    for col in columns:
        if not col or "key" not in col or "type" not in col:
            continue
        col_name = col.get("key")
        if col.get("unit"):
            col_name = f"{col_name}({col['unit']})"
        if col_name not in df.columns:
            continue
        col_type = col.get("type")
        try:
            if col_type == "DOUBLE":
                df[col_name] = pd.to_numeric(df[col_name], errors="coerce").astype("float")
            elif col_type == "INT":
                df[col_name] = pd.to_numeric(df[col_name], errors="coerce").astype("Int64")
            elif col_type == "LONG":
                df[col_name] = pd.to_numeric(df[col_name], errors="coerce").astype("Int64")
            elif col_type == "BOOLEAN":
                df[col_name] = df[col_name].map({"True": True, "False": False, True: True, False: False})
            elif col_type == "DATE":
                df[col_name] = pd.to_datetime(df[col_name], errors="coerce")
            # STR 类型不转换
        except Exception as e:
            logger.warning(f"table_json_to_dataframe: failed to convert column '{col_name}' to type '{col_type}': {e}")

    df._query_data_ = lambda: table_json
    markdown = table_json.get("text", None)
    if markdown:
        df._repr_markdown_ = lambda: markdown

    return df


def create_temp_json(data: dict, suffix=".json"):
    """创建临时 JSON 文件并写入数据"""
    # 创建临时文件：文本模式、指定编码、保留文件名、添加.json后缀
    import tempfile
    import json

    with tempfile.NamedTemporaryFile(
        mode='w',          # 文本写入模式
        encoding='utf-8',  # 指定编码（处理中文等字符）
        suffix=suffix,     # 文件后缀为.json，便于识别
        delete=False       # 关闭后不自动删除（需手动清理）
    ) as temp_file:
        # 写入 JSON 数据
        json.dump(data, temp_file, ensure_ascii=False, separators=(',', ':'))
        temp_file_path = temp_file.name  # 获取临时文件路径
        print(f"临时 JSON 文件已创建：{temp_file_path}")
    return temp_file_path

def read_temp_json(file_path: str) -> dict:
    """读取临时 JSON 文件内容"""
    import json
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
