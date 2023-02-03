from dash import dcc, html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from plotly.express.colors import sample_colorscale

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

            dfg = pd.DataFrame({color_col:self.df_display[color_col].unique()})

            
            
            color_distribution = np.linspace(0,1,dfg.shape[0]+1)
            colorvals = sample_colorscale('viridis', color_distribution)
            colorscale = []

            for i in range(dfg.shape[0]):
                colorscale.append((color_distribution[i],colorvals[i]))
                colorscale.append((color_distribution[i+1],colorvals[i]))
            
            dummy_values = []
            for i in range(len(color_distribution)-1):
                dummy_values.append( (color_distribution[i+1]+color_distribution[i])/2 )
            dfg['dummy_'+color_col] = dummy_values

            self.df_display = pd.merge(self.df_display, dfg, on = color_col, how='left')
            color_values = self.df_display['dummy_'+color_col]

            cmin = self.df_display['dummy_'+color_col].min()
            cmax = self.df_display['dummy_'+color_col].max()

            

        else:
            cmin = self.df_display[color_col].min()
            cmax = self.df_display[color_col].max()
            colorscale='viridis'
            # cat_dim = dict(range=[0,self.df_display['dummy_'+color_col].max()],
            #         tickvals = dfg['dummy_'+color_col], ticktext = dfg[color_col],
            #         label=name, values=self.df_display['dummy_'+color_col])
            # dimensions.append(cat_dim)

        colorbar = {}
        if dfg is not None:
            colorbar=dict(
                tickvals=dfg['dummy_'+color_col],
                ticktext=dfg[color_col], lenmode="pixels",
            )

        self.fig = go.Figure(data=
            go.Parcoords(
                #line = dict(color = self.df_display[value_pairs[0][0]],
                line = dict(color = color_values,
                        #color_continuous_scale=colorscale,
                        colorscale = colorscale,
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
