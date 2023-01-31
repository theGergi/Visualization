import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, dash_table


# def MTPLTgetRadarChartFromAgg(agg_df, range_list):

#     variables = agg_df.columns
#     import Visualization.complex_radar as cr
#     fig = plt.figure(figsize=(6, 6))
#     radar = cr.ComplexRadar(fig, variables, range_list,n_ring_levels=3 ,show_scales=True)

#     custom_colors = ['#F67280', '#6C5B7B', '#355C7D','#f8c16c', '#6c25be']

#     for g,c in zip(agg_df.index, custom_colors[:len(agg_df.index)]):
#         radar.plot(agg_df.loc[g].values, label=f"{g}", color=c, marker='o')
#         radar.fill(agg_df.loc[g].values, alpha=0.5, color=c)
#     radar.use_legend()

#     return fig

def PLgetRadarChart(normalized_df: pd.DataFrame, names: str = None) -> go.Figure:
    fig = go.Figure()
    if normalized_df.empty:
        fig.add_annotation(
            text='No data selected!',
            showarrow=False,
            font= dict(size = 28)        
        )
        fig.update_layout(paper_bgcolor="#1f2630",
                plot_bgcolor="#1f2630",
                font=dict(color="#2cfec1"))
        fig.update_layout
        fig.update_yaxes(visible=False)
        fig.update_xaxes(visible=False)
        return fig
    for key in normalized_df.index:
        print(key)
        fig.add_trace(go.Scatterpolar(
            r = normalized_df.loc[key],
            theta = normalized_df.drop(names, axis=1).columns if names else normalized_df.columns,
            fill ='toself',
            name = normalized_df.loc[key][names] if names else f'{key}' 
        ))
        fig.update_layout(legend = dict(orientation="h"))

    return fig

def normalizeColumns(df: pd.DataFrame) -> pd.DataFrame:
    result_df = pd.DataFrame()
    for col in df.columns: 
        result_df[col] = df[col].rank()
        result_df[col] = (result_df[col]*100) / len(df)
    return result_df

if __name__ == "__main__":
    df = pd.DataFrame()
    df['one'] = [1,2,3,4,5]
    df['two'] = [1,2,2,4,5]
    print(normalizeColumns(df))