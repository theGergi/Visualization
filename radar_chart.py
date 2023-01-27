import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


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