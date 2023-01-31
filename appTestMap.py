import math
from dash import Dash, dcc, html, Input, Output, State, dash_table
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff
from dash.exceptions import PreventUpdate
from radar_chart import PLgetRadarChart, normalizeColumns
from jbi100_app.views.parcoords import Parcoords
import numpy as np
import re


VALUE_PAIRS_PCP = [("price","Price"),("service fee","Service fee"),("review rate number","Review rate number"),("Construction year","Construction year"),
("number of reviews","Number of reviews"), ('availability 365','Availability in a year')]
#('host_response_time','Reponse Time'),('host_response_rate','Response rate'),('host_acceptance_rate','Acceptance rate'),('host_is_superhost','Superhost')]

def clean(x):
    x = x.replace("$", "").replace(" ", "")
    if "," in x:
        x = x.replace(",", "")
    return int(x)

def cleanAvailability365(x):
    x = min(x, 365)
    return x

df = pd.read_csv('airbnb_open_data.csv', usecols=['NAME','host id', 'host_identity_verified','host name',
'neighbourhood group','neighbourhood','lat','long',	'country','country code','instant_bookable','cancellation_policy',
'room type','Construction year','price','service fee','minimum nights','number of reviews',	'last review',	
'reviews per month','review rate number','calculated host listings count','availability 365'])
#'host_response_time','host_response_rate','host_acceptance_rate','host_is_superhost']) # Added for parallel coordinates
# df_big = pd.read_csv()
# 'neighbourhood_group_cleansed','latitude','long',
# 'room type','price','service fee','review rate number','availability 365'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

px.set_mapbox_access_token("pk.eyJ1IjoibXJhZmlwaCIsImEiOiJjbGMzdWZ0MTIwNmt5M3B0ODNnbzF1a3d2In0.7VgLitY9OXxhPSxlxJglfQ")

app = Dash(__name__,external_stylesheets=external_stylesheets)

app.config.suppress_callback_exceptions = True

styles = {
    'pre' : {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.title = "Dash Map"

server = app.server

# The first thing we have to do is clean the dataframe

df_clean = df.copy()
df_clean = df_clean.dropna().reset_index(drop=True)
df_clean['price'] = df_clean['price'].apply(clean)
df_clean['service fee'] = df_clean['service fee'].apply(clean)
df_clean['neighbourhood group'] = df_clean['neighbourhood group'].replace('brookln', 'Brooklyn')
df_clean['availability 365'] = df_clean['availability 365'].apply(cleanAvailability365)

plot1 = Parcoords(df_clean)

# Separate these values into different bins
df_clean['bin'] = pd.cut(x=df_clean['service fee'], bins=[0, 10, 60, 120, 180, 240])
df_clean['bin'] = df_clean['bin'].astype(str)
df_clean['bin_price'] = pd.cut(x=df_clean['price'], bins=5, precision=0)
df_clean['bin_price'] = df_clean['bin_price'].astype(str)

# reducing dataset size for faster user experience
df_small = df_clean[:100]
radar_cols = ['price','service fee','minimum nights','number of reviews']
df_normalized = normalizeColumns(df_small[radar_cols])
df_normalized['NAME'] = df_small['NAME']
radar_fig = PLgetRadarChart(pd.DataFrame(), names='NAME')

# Make the layout 
app.layout = html.Div(style={'backgroundColor':"#1f2630", 'color': '#2cfec1'}, children=[
    html.Div(className='row', children=[
        html.Div(className='banner', children =[
            html.H2('Dash - Airbnb Listings'),
            html.Hr()
        ]),
        html.Div(className='row', children = [
            html.Div(className='four columns div-user-controls', children=[
                
                html.P('''Filtering Options'''),
                html.Hr(),
                dcc.Dropdown(
                    [{'label': 'Average Price', 'value': 'price'},
                    {'label': 'Neighbourhood', 'value': 'neighbourhood group'},
                    {'label': 'Room Type', 'value': 'room type'},
                    {'label': 'Availability', 'value': 'availability 365'}],
                    id='dropdown-menu',
                    searchable=False,
                    clearable=False,
                    style={'backgroundColor':"#1f2630"},
                ),
                html.Br(),
                dash_table.DataTable(
                    df_small.to_dict('records'),
                    [{"name": i, "id": i} for i in df_small.columns],
                    row_selectable='multi',
                    id='preview_table',
                    style_table={'height': '300px', 'overflowY': 'auto', 'color': '#2cfec1',},
                    page_size=10,
                    style_data={
                        'color': '#2cfec1',
                        'backgroundColor': "#1f2630"},
                    style_header={
                            'backgroundColor': "#1f2630",
                            'color': '#2cfec1',
                            'fontWeight': 'bold'},
                    ),

                dcc.Graph(figure=radar_fig, 
                    id = 'radar_fig',
                    style={'backgroundColor':"#1f2630"},)
                ],
                    
            ),


            html.Div(className='eight columns div-for-charts-bg-grey', children=[
                html.Div(
                    className="row",
                    children = [
                    html.Div(
                        className="eight columns",
                        children=[
                        dcc.Graph(
                            id='hexbin-mapbox',
                            className='twelve columns',
                            style={'backgroundColor':"#1f2630"}
                            )
                        ]),                  
                        
                    html.Div(className='four columns div-for-charts-bg-grey', 
                        children=[
                            dcc.Graph(
                                id='grouped-bar-chart',
                                style={'backgroundColor':"#1f2630"}
                            )
                        ]),
                    ]
                ),
                
                html.Div(
                    className="row",
                    children=[
                    plot1
                ]),
                
            ])
        ])
    ])
])

# Updates the radar chart
@app.callback(
    Output('radar_fig', "figure"),
    Input('preview_table', 'selected_rows')
)
def select_listings(selected_rows):
    if not selected_rows:
        return PLgetRadarChart(pd.DataFrame(), names='NAME')
    display_df = df_normalized.iloc[selected_rows]
    fig = PLgetRadarChart(display_df, names='NAME')
    fig.update_layout(paper_bgcolor="#1f2630",
                plot_bgcolor="#1f2630",
                font=dict(color="#2cfec1"))
    return fig

# Updates the hexbin map
@app.callback(
    Output('hexbin-mapbox', 'figure'),
    [Input('dropdown-menu', 'value')]
)
def update_hexbin(value):
    if (value == 'Average Price'):
        label = "Average " + value.capitalize()
        fig = ff.create_hexbin_mapbox(
            data_frame=df_clean, lat="lat", lon="long",
            opacity=1.0, labels={"color": label},
            min_count=1, color=value, agg_func=np.mean,
            show_original_data=True,
            original_data_marker=dict(size=4, opacity=0.2, color="deeppink"),
            zoom=8,
        )
    else:
        fig = make_hexbin(df_clean, True)
        

    fig.update_layout(margin=dict(b=0, t=0, l=0, r=0))
    fig.update_layout(paper_bgcolor="#1f2630",
                plot_bgcolor="#1f2630",
                font=dict(color="#2cfec1"))
    return fig

def make_hexbin(df, setOriginalData):
    return ff.create_hexbin_mapbox(
            data_frame=df, lat="lat", lon="long",
            opacity=1.0, labels={"color": "Listings Count"},
            min_count=1, show_original_data=setOriginalData, 
            original_data_marker=dict(size=4, opacity=0.2, color="deeppink"),
            zoom=8, 
    )

# Define interactions Parallel coordinates graph
@app.callback(
    Output(plot1.html_id, 'figure'),
    [Input('dropdown-menu', 'value')]
)
def update_parcoords(value):
    fig = plot1.update(VALUE_PAIRS_PCP, df_clean)
    fig.update_layout(paper_bgcolor="#1f2630",
                plot_bgcolor="#1f2630",
                font=dict(color="#2cfec1"))
    return fig

# Updates the histogram
@app.callback(
    Output('grouped-bar-chart', 'figure'),
    [Input('dropdown-menu', 'value')]
)
def update_histogram(value):
    if value is None:
        return dict(
            data=[dict(x=0, y=0)],
            layout=dict(
                title="Nothing is selected",
                paper_bgcolor="#1f2630",
                plot_bgcolor="#1f2630",
                font=dict(color="#2cfec1"),
            ),
        )
    if (value == 'price'):
        fig_second = px.histogram(df_clean, x='service fee', nbins=10,
                    labels={'service fee':'Service Fee($)'})
    elif (value == 'availability 365'):
        fig_second = px.histogram(df_clean, x='availability 365', nbins=10,
                    labels={'availability 365':'Property Availability(days)'})
    else:
        fig_second = px.histogram(df_clean, x=value, 
                    color=value, labels={'neighbourhood group':'group'})
    fig_second.update_layout(margin = dict(l=0,r=20,b=20,t=0),bargap=0.2)
    fig_second.update_layout(paper_bgcolor="#1f2630",
                plot_bgcolor="#1f2630",
                font=dict(color="#2cfec1"))
    return fig_second
    

if __name__ == '__main__':
    app.run_server(debug=True)
