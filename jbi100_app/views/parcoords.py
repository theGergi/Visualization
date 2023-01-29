from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
import numpy as np

class Parcoords(html.Div):
    def __init__(self, df):
        self.html_id = 'parcoord'
        self.df_display = df
        # Equivalent to `html.Div([...])`
        super().__init__(
            className="graph_card",
            children=[
                #html.H6(name),
                dcc.Graph(id=self.html_id)
            ],
        )

    def update(self, value_pairs, df):
        self.df_display = df
        bounds = []
        dimensions= []
        for key, name in value_pairs:
            values = self.df_display[key]
            up_bound = max(values) 
            low_bound = min(values)
            bounds.append((low_bound, up_bound))
            dimensions.append(dict(range = [low_bound,up_bound],
                        label = name,
                        values = values))
                        

        self.fig = go.Figure(data=
            go.Parcoords(
                line = dict(color = self.df_display[value_pairs[0][0]],
                        colorscale = 'viridis',
                        showscale = True,
                        cmin = bounds[0][0],
                        cmax = bounds[0][1]),
                
                dimensions = dimensions),
                
            # ,layout = dict(plot_bgcolor='rgba(50,0,0,0)')
        )
        self.fig.update_layout(
            margin=dict(l=20, r=20, b=20)
        )
        return self.fig
