from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
import numpy as np

class Parcoords(html.Div):
    def __init__(self, name, df):
        self.html_id = name.lower().replace(" ", "-")
        self.df_display = df.head(50)
        # Equivalent to `html.Div([...])`
        super().__init__(
            className="graph_card",
            children=[
                html.H6(name),
                dcc.Graph(id=self.html_id)
            ],
        )

    def update(self, value_pairs):

        dimensions= []
        for key, name in value_pairs:
            values = self.df_display[key]
            up_bound = max(values) 
            low_bound = min(values)
            dimensions.append(dict(range = [low_bound,up_bound],
                        label = name,
                        values = values))
                        

        self.fig = go.Figure(data=
            go.Parcoords(
                line = dict(color = self.df_display['host id'],
                        colorscale = 'Electric',
                        showscale = True,
                        cmin = -4000,
                        cmax = -100),
                dimensions = dimensions
            )
        )

        return self.fig
