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

    def update(self, value_pairs, df, color_col):
        self.df_display = df
        bounds = []
        dimensions= []
        dfg = None
        for key, name in value_pairs:
            values = self.df_display[key]
            up_bound = max(values) 
            low_bound = min(values)
            bounds.append((low_bound, up_bound))
            dimensions.append(dict(range = [low_bound,up_bound],
                        label = name,
                        values = values))

        color_values = self.df_display[color_col]
        
        if self.df_display.dtypes[color_col] not in ('float64','int64'):
            # up_bound = max(color_values) 
            # low_bound = min(color_values)
            # bounds.append((low_bound, up_bound))
            # dimensions.append(dict(range = [low_bound,up_bound],
            #             label = name,
            #             values = values))
            dfg = pd.DataFrame({color_col:self.df_display[color_col].unique()})
            dfg['dummy_'+color_col] = dfg.index
            self.df_display = pd.merge(self.df_display, dfg, on = color_col, how='left')
            color_values = self.df_display['dummy_'+color_col]

            cmin = self.df_display['dummy_'+color_col].min()
            cmax = self.df_display['dummy_'+color_col].max()
        else:
            cmin = self.df_display[color_col].min()
            cmax = self.df_display[color_col].max()
            # cat_dim = dict(range=[0,self.df_display['dummy_'+color_col].max()],
            #         tickvals = dfg['dummy_'+color_col], ticktext = dfg[color_col],
            #         label=name, values=self.df_display['dummy_'+color_col])
            # dimensions.append(cat_dim)

        colorbar = {}
        if dfg is not None:
            colorbar=dict(
                tickvals=dfg['dummy_'+color_col],
                ticktext=dfg[color_col],
            )

        self.fig = go.Figure(data=
            go.Parcoords(
                #line = dict(color = self.df_display[value_pairs[0][0]],
                line = dict(color = color_values,
                        colorscale = 'viridis',
                        showscale = True,
                        cmin = cmin,
                        cmax = cmax,
                        #coloraxis=dict(),
                        colorbar=colorbar),
                
                dimensions = dimensions)
                
                
            # ,layout = dict(plot_bgcolor='rgba(50,0,0,0)')
        )
        
        self.fig.update_layout(
            margin=dict(l=30, r=20, b=20)
        )
        return self.fig
