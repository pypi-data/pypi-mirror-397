---
name: plotly
description: 使用 Plotly 进行数据可视化的内置技能，主要通过 CodeInterpreter 执行 Python 代码来生成交互式图表。
allowed_tools: ["CodeInterpreter"]
---
使用原则：
- 本技能以 CodeInterpreter 为核心，所有绘图逻辑在解释器中执行。
- 返回图表对象而不是调用 fig.show()；直接在代码块末尾返回 fig 对象即可由前端渲染。
- 若需要表格预览，请使用 display_table(df) 而不是 print。
- 在生成技术指标相关图表时，先确保数据完整，必要时补取数据并裁剪缺失区间。
- 当需要同时展示图表或表格到最终回答中，请使用 apply 块，仅填入变量名（例如 fig 或 df）。

最小示例（从已有 DataFrame 绘图）：
<example-code>
import pandas as pd
import plotly.graph_objects as go

dates = ["2025-05-15", "2025-05-16", "2025-05-19", "2025-05-20"]
df = pd.DataFrame({
	"TSLA": [342.82, 349.98, 342.09, 343.82],
	"AAPL": [211.45, 211.26, 208.78, 206.86],
}, index=pd.to_datetime(dates))

fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df["TSLA"], mode="lines", name="TSLA"))
fig.add_trace(go.Scatter(x=df.index, y=df["AAPL"], mode="lines", name="AAPL"))
fig.update_layout(title="TSLA vs AAPL", xaxis_title="Date", yaxis_title="Price")
fig
</example-code>

在回答中内嵌可视化或表格：
- 图表：
<apply>
fig
</apply>
- 表格：
<apply>
df_tsla
</apply>

提示：
- 若需要绘制多子图、添加形状/标注、或叠加事件点，可继续使用 Plotly 的布局与注释 API（layout、add_shape、add_annotation 等）。
- 对于移动端显示，建议将图例设为底部横排、减少留白，并控制曲线与标注数量以保证可读性。
