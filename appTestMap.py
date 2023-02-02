import math
import json
from dash import Dash, dcc, html, Input, Output, State, dash_table, State
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff
from dash.exceptions import PreventUpdate
from radar_chart import PLgetRadarChart, normalizeColumns
from jbi100_app.views.parcoords import Parcoords
import numpy as np
import re
from time import perf_counter

#WHAT I DID 
# SELECTING DROPDOWN CHANGES TABLE ORDERING/FILTER
# SELECING DROPDOWN CHANGES MAP COLOR
# SELECTING DROPDOWN CHANGES HIST TYPE

# SELECTING ROW ADDS RADAR
# SELECTING ROW ADD POINT ON MAP

#SELECTING MAP HOOD CHANGES HIST, TABLE AND PCP DATA

#SELECTING HIST CHANGES TABLE AND PCP DATA AND AND MAP COLOR IF HIST CATEGORICAL

VALUE_PAIRS_PCP = [("price","Price"),("service fee","Service fee"),("review rate number","Review rate number"),("Construction year","Construction year"),
("number of reviews","Number of reviews"), ('availability 365','Availability in a year')]

def clean(x):
    x = x.replace("$", "").replace(" ", "")
    if "," in x:
        x = x.replace(",", "")
    return int(x)

def cleanAvailability365(x):
    if x < 0:
        x = abs(x)
    else:
        x = min(x, 365)
    return x

df = pd.read_csv('airbnb_open_data.csv', usecols=['id', 'NAME','host id', 'host_identity_verified','host name',
'neighbourhood group','neighbourhood','lat','long',	'country','country code','instant_bookable','cancellation_policy',
'room type','Construction year','price','service fee','minimum nights','number of reviews',	'last review',	
'reviews per month','review rate number','calculated host listings count','availability 365'])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

px.set_mapbox_access_token("pk.eyJ1IjoibXJhZmlwaCIsImEiOiJjbGMzdWZ0MTIwNmt5M3B0ODNnbzF1a3d2In0.7VgLitY9OXxhPSxlxJglfQ")

app = Dash(__name__,external_stylesheets=external_stylesheets)

app.config.suppress_callback_exceptions = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

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
df_clean['availability 365'] = df_clean['availability 365'].apply(cleanAvailability365)
df_clean['service fee'] = df_clean['service fee'].apply(clean)
df_clean['neighbourhood group'] = df_clean['neighbourhood group'].replace('brookln', 'Brooklyn')
df_clean = df_clean.set_index('id', drop=False)
df_clean['Revenue($)'] = df_clean['price']*(365 - df_clean['availability 365'].astype(int))


plot1 = Parcoords(df_clean)

# reducing dataset size for faster user experience
df_small = df_clean[:100]
radar_cols = ['price','service fee','minimum nights','number of reviews']
df_normalized = normalizeColumns(df_clean[radar_cols])
df_normalized['NAME'] = df_clean['NAME']
df_normalized['id'] = df_clean['id']
df_normalized = df_normalized.set_index('id', drop=False)
radar_fig = PLgetRadarChart(pd.DataFrame(), names='NAME')

with open('datasets/neighbourhoods.geojson') as f:
    hood_geometry = json.load(f)
# should be global
quantitative_columns = ['price','availability 365','Construction year',
            'minimum nights', 'number of reviews']
categ_col = ['room type', 'instant_bookable']
categ_default_dict = {"room type": 'Private room', 'instant_bookable':'TRUE'}
quant_agg_dict = {col:'mean' for col in quantitative_columns}
agg_dict = quant_agg_dict.copy()
agg_dict['id'] = 'count'

def get_categ_counts(categ_col:str, df =df_clean) -> pd.DataFrame:
    result_df =(df.groupby('neighbourhood')[categ_col]
            .value_counts()
            .unstack(level=-1)
            .fillna(0))
    df_totals = df.groupby('neighbourhood')['id'].count()
    result_df = result_df.rename(columns={col: f'{categ_col}_{col}' for col in result_df.columns})
    for col in result_df.columns:
        result_df['proportion'+'_'+col] = result_df[col]/df_totals
    
    return result_df

def get_hood_df(df = df_clean) -> pd.DataFrame:

    all_colls =['neighbourhood', 'id', 'room type']+quantitative_columns
    default_group = (df[all_colls]
        .groupby('neighbourhood', as_index=False)
        .agg(agg_dict))
    # print(default_group)
    for col in categ_col:
        categ_summary = get_categ_counts(col, df)
        default_group = default_group.join(categ_summary, on='neighbourhood')

    return default_group

def get_cloropleth(df: pd.DataFrame = pd.DataFrame(), color_col: str = 'price'):
    if df.empty:
        df_grouped = get_hood_df()
    else:
        df_grouped = get_hood_df(df)
    fig = px.choropleth_mapbox(df_grouped, geojson=hood_geometry, 
                        locations='neighbourhood', color=color_col,
                        featureidkey="properties.neighbourhood",
                           color_continuous_scale="Viridis",
                           mapbox_style="carto-positron",
                           labels={'price':'Price', 'id':'Count', 'proportion_room type_Private room':'Room Type',
                           'availability 365': 'Availability(days)'},
                           zoom=9, center = {"lat": 40.70271, "lon": -73.8993},
                          )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    return fig


# Make the layout 
app.layout = html.Div(style={'backgroundColor':"#1f2630", 'color': '#2cfec1'}, children=[
    html.Div(className='row', children=[
        html.Div(className='banner', children =[
            html.H2('Dash - Airbnb Listings', style={'marginTop':'0px','marginBottom':'0px','paddingTop':'25px'}),
            html.Hr()
        ]),
        html.Div(className='row', children = [
            html.Div(className='four columns div-user-controls', children=[
                html.Div(id='test'),
                html.P('''Filtering Options'''),
                html.Hr(),
                dcc.Dropdown(
                    # [{'label': 'Density', 'value': 'density'},
                    [{'label': 'Listing Density', 'value': 'density'},
                    {'label': 'Average Price', 'value': 'price'},
                    {'label': 'Average Availability', 'value': 'availability 365'},
                    {'label': 'Average Construction Year', 'value': 'Construction year'},
                    {'label': 'Average Minimum Nights', 'value': 'minimum nights'},
                    {'label': 'Average Review Number', 'value': 'number of reviews'},
                    {'label': 'Room Type', 'value': 'room type'},
                    {'label': 'Instant Bookable', 'value': 'instant_bookable'}],
                    id='dropdown-menu',
                    searchable=False,
                    clearable=False,
                    style={'backgroundColor':"#1f2630", 'color': '#2cfec1'},
                    value='density',
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
                    #html.Div(id='my-output'),
                    html.Div(
                        className="eight columns",
                        children=[
                        dcc.Graph(
                            id='cloropleth-map',
                            className='twelve columns',
                            figure=get_cloropleth(),
                            style={'backgroundColor':"#1f2630"},
                            )
                        ]),                  
                        
                    html.Div(className='four columns div-for-charts-bg-grey', 
                        children=[
                            dcc.Graph(
                                id='histogram',
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
    Input('preview_table', 'selected_row_ids'),
)
def select_listings(selected_rows):
    if not selected_rows:
        return PLgetRadarChart(pd.DataFrame(), names='NAME')
    display_df = df_normalized.loc[selected_rows]
    fig = PLgetRadarChart(display_df, names='NAME')
    fig.update_layout(paper_bgcolor="#1f2630",
                plot_bgcolor="#1f2630",
                font=dict(color="#2cfec1"))
    return fig

# Updates the hexbin map
@app.callback(
    Output('cloropleth-map', 'figure'),
    [Input('dropdown-menu', 'value'),
    Input('histogram', 'selectedData'),
    Input('preview_table', 'selected_row_ids')]
)
def update_graph(value, selectedData, selectedTableRows):
    if value == 'density':
        value = 'id'
    elif value not in quantitative_columns:
        if selectedData:
            categ_val = [point['x'] for point in selectedData['points']][0]
            value = f'proportion_{value}_{categ_val}'
        else: 
            value = f'proportion_{value}_{categ_default_dict[value]}'

    if selectedTableRows != None:
        df_traces = df_clean.loc[df_clean["id"].isin(selectedTableRows)]
        fig = go.Figure(get_cloropleth(df_traces, color_col=value))
    else:
        fig = go.Figure(get_cloropleth(pd.DataFrame(), color_col=value))
    fig.update_layout(paper_bgcolor="#1f2630",
                plot_bgcolor="#1f2630",
                font=dict(color="#2cfec1"))

    # if selectedTableRows:
    #     lats = list(df_clean.loc[selectedTableRows]['lat'])
    #     lons = list(df_clean.loc[selectedTableRows]['long'])
    #     texts = list(df_clean.loc[selectedTableRows]['NAME'])
    #     print(texts)

    #     fig.add_scattermapbox(
    #         lat = lats,
    #         lon = lons,
    #         mode = 'markers+text',
    #         text = texts,
    #         marker_size=20,
    #         marker_color='rgb(235, 0, 100)'
    #     )
    return fig

df_sorted = df_clean
# global df_sorted
@app.callback(
    Output('preview_table', 'data'),
    [Input('dropdown-menu', 'value'),
    Input('cloropleth-map', 'selectedData'),
    Input('histogram', 'selectedData'),
    State('histogram','figure')]
)
def sort_table_data(value, mapSelectedData, histSelectedData, histFigDict):
    if value == 'density':
        value = 'NAME'
    hist_filter_data = filter_hist_selected(histSelectedData, histFigDict)
    if (value == 'availability 365'):
        df_sorted = filter_map_selection(mapSelectedData, hist_filter_data).sort_values(by=[value], ascending=True)
    else:
        df_sorted = filter_map_selection(mapSelectedData, hist_filter_data).sort_values(by=[value], ascending=False)
    return df_sorted.iloc[:100].to_dict('records')

# @app.callback(
#     Output('test', 'children'),
#     Input('cloropleth-map', 'clickData'),
# )
# def get_map_click_data(clickData):
#     print(clickData)
#     return 'poop'
# Define interactions Parallel coordinates graph
@app.callback(
    Output(plot1.html_id, 'figure'),
    [Input('cloropleth-map', 'selectedData'),
    Input('dropdown-menu', 'value'),
    Input('histogram', 'selectedData'),
    State('histogram','figure')]
)
def update_parcoords(mapSelectedData, value, histSelectedData, histFigDict):#
    #MAKE SURE THE X AXIS TEXT NAME IS THE SAME AS THE COLUMN NAME OF PANDAS
    # OTHERWISE WE CANT FIND THE NEED VALUES
    # print(hist_column)  
    if value == 'density':
        value = 'neighbourhood group'
    color_col=value
    hist_filter_data = filter_hist_selected(histSelectedData,  histFigDict)
    fig = plot1.update(VALUE_PAIRS_PCP, filter_map_selection(mapSelectedData, hist_filter_data), color_col)
    fig.update_layout(paper_bgcolor="#1f2630",
                plot_bgcolor="#1f2630",
                font=dict(color="#2cfec1"))
    return fig

def filter_map_selection(selectedData:dict[list[dict]], df=df_clean) -> pd.DataFrame:
    if selectedData == None:
        return df
    hood_list = [point['location'] for point in selectedData['points']]
    df_map_filter = df.query('neighbourhood in @hood_list')
    return df_map_filter
#     Output(plot1.html_id, "figure"), [
#     Input('dropdown-menu', 'value')
# ])
# def update_comparison(value):
#     return plot1.update([("price","Price"),("review rate number","Review rate number")])

def filter_hist_selected(selectedData:dict, histFigDict:str, df=df_clean)->pd.DataFrame:
    if not selectedData:
        return df
    if not histFigDict:
        column = 'price'
    else:
        column = histFigDict['layout']['xaxis']['title']['text']
    
    if column in quantitative_columns:
        x_min = float(selectedData['range']['x'][0])
        x_max =  float(selectedData['range']['x'][1])
        # print(df.query(f'{column} >= @x_min and {column} <= @x_max'))
        return df.query(f'{column} >= @x_min and {column} <= @x_max')
    else:
        groups = [point['x'] for point in selectedData['points']]
        return df.query(f'`{column}` in @groups')


def filter_map_selection(selectedData:dict[list[dict]], df=df_clean) -> pd.DataFrame:
    if selectedData == None:
        return df
    hood_list = [point['location'] for point in selectedData['points']]
    df_map_filter = df.query('neighbourhood in @hood_list')
    return df_map_filter
#     Output(plot1.html_id, "figure"), [
#     Input('dropdown-menu', 'value')
# ])
# def update_comparison(value):
#     return plot1.update([("price","Price"),("review rate number","Review rate number")])

def filter_hist_selected(selectedData:dict, histFigDict:str, df=df_clean)->pd.DataFrame:
    if not selectedData:
        return df
    if not histFigDict:
        column = 'price'
    else:
        column = histFigDict['layout']['xaxis']['title']['text']
    
    if column in quantitative_columns:
        x_min = float(selectedData['range']['x'][0])
        x_max =  float(selectedData['range']['x'][1])
        # print(df.query(f'{column} >= @x_min and {column} <= @x_max'))
        return df.query(f'{column} >= @x_min and {column} <= @x_max')
    else:
        groups = [point['x'] for point in selectedData['points']]
        return df.query(f'`{column}` in @groups')

# Updates the histogram based on the selected option from the dropdown.
@app.callback(
    Output('histogram', 'figure'),
    [Input('dropdown-menu', 'value'),
    Input('cloropleth-map', 'selectedData')]
)
def update_grouped(value, selectedData):
    # When noting is selected, it shows an empty graph
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
    
    # Change the color of the bars and sets the margin and the gap between the bars.
    if value == 'density':
        value = 'neighbourhood group'
    if value == 'number of reviews' or value == 'minimum nights':
        fig_second = px.histogram(filter_map_selection(selectedData), x=value, 
                    nbins=11,  color_discrete_sequence=["#2cfec1"])
    else:
        fig_second = px.histogram(filter_map_selection(selectedData), x=value, 
                    nbins=10,  color_discrete_sequence=["#2cfec1"])
    fig_second.update_layout(margin = dict(l=0,r=20,b=20),bargap=0.2)
    fig_second.update_layout(paper_bgcolor="#1f2630",
                plot_bgcolor="#1f2630",
                font=dict(color="#2cfec1"))

    return fig_second

if __name__ == '__main__':
   app.run_server(debug=True)

