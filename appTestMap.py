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


VALUE_PAIRS_PCP = [("price","Price"),("review rate number","Review rate number"),("Construction year","Construction year"),("service fee","Service fee"),("number of reviews","Number of reviews"), ('availability 365','Availability in a year')]

def clean(x):
    x = x.replace("$", "").replace(" ", "")
    if "," in x:
        x = x.replace(",", "")
    return int(x)

def cleanServiceFee(x):
    x = x.replace("$", "").replace(" ", "")
    return int(x)

df = pd.read_csv('airbnb_open_data.csv', usecols=['NAME','host id', 'host_identity_verified','host name',
'neighbourhood group','neighbourhood','lat','long',	'country','country code','instant_bookable','cancellation_policy',
'room type','Construction year','price','service fee','minimum nights','number of reviews',	'last review',	
'reviews per month','review rate number','calculated host listings count','availability 365'])
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
df_clean['service fee'] = df_clean['service fee'].apply(cleanServiceFee)
df_clean['neighbourhood group'] = df_clean['neighbourhood group'].replace('brookln', 'Brooklyn')


plot1 = Parcoords("Comparison", df_clean)

# Separate these values into different bins
df_clean['bin'] = pd.cut(x=df_clean['service fee'], bins=[0, 10, 60, 120, 180, 240])
df_clean['bin'] = df_clean['bin'].astype(str)
df_clean['bin_price'] = pd.cut(x=df_clean['price'], bins=5, precision=0)
df_clean['bin_price'] = df_clean['bin_price'].astype(str)

# print(pd.cut(x=df_clean['price'], bins=5, precision=0).unique)

# reducing dataset size for faster user experience
# 
df_small = df_clean[:100]
radar_cols = ['price','service fee','minimum nights','number of reviews']
df_normalized = normalizeColumns(df_small[radar_cols])
df_normalized['NAME'] = df_small['NAME']
radar_fig = PLgetRadarChart(pd.DataFrame(), names='NAME')

# Make the layout 
app.layout = html.Div(children=[
    html.Div(
        className='row', children=[
            html.Div(className='four columns div-user-controls', children=[
                html.H2('Dash - Airbnb Listings'),
                html.P('''Filtering Options'''),
                html.Hr(),
                dcc.Dropdown(
                    [{'label': 'Location', 'value': 'Location'},
                    {'label': 'Average Price', 'value': 'price'},
                    {'label': 'Neighbourhood', 'value': 'neighbourhood group'},
                    {'label': 'Room Type', 'value': 'room type'},
                    {'label': 'Availability', 'value': 'availability 365'}],
                    id='dropdown-menu',
                    searchable=False,
                    clearable=False,
                    value="Location",
                ),
                html.Br(),
                dcc.RadioItems(
                    id='radio-menu-neighbourhood',
                    options=df_clean['neighbourhood group'].unique(),
                    style= {'display': 'none'},
                    value='Brooklyn',
                ),
                dcc.RadioItems(
                    id='radio-menu-room',
                    options=df_clean['room type'].unique(),
                    style= {'display': 'none'},
                    value='Private room',
                ),
                dcc.Dropdown(
                    options=['$50 - $280', '$281 - $509', '$510 - $739', '$740 - $969', '$970 - $1200'],
                    id='dropdown-price',
                    value='$50 - $280',
                    disabled=True,
                    style= {'display': 'none'},
                ),
                html.Br(),
                dash_table.DataTable(
                    df_small.to_dict('records'),
                    [{"name": i, "id": i} for i in df_small.columns],
                    row_selectable='multi',
                    id='preview_table',
                    style_table={'height': '300px', 'overflowY': 'auto'} ,
                    page_size=10,
                    ),

                dcc.Graph(figure=radar_fig, id = 'radar_fig')
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
                            style={'display': 'inline-block'}
                            )
                        ]),                  
                        
                    html.Div(className='four columns div-for-charts-bg-grey', children=[

                        ], id='grouped-bar-chart', style={'display': 'inline-block'}),
                    ]
                ),
                
                html.Div(
                    className="row",
                    children=[
                    plot1
                ]),
                
            ])
            
        ], 
    )
])

@app.callback(
    Output('radar_fig', "figure"),
    Input('preview_table', 'selected_rows')
)
def select_listings(selected_rows):
    # print(selected_rows)
    if not selected_rows:
        return PLgetRadarChart(pd.DataFrame(), names='NAME')
    display_df = df_normalized.iloc[selected_rows]
    fig = PLgetRadarChart(display_df, names='NAME')
    return fig



@app.callback(
    [Output('hexbin-mapbox', 'figure'),
    Output('radio-menu-neighbourhood', 'style'),
    Output('radio-menu-room', 'style')],
    [Input('dropdown-menu', 'value'),
    Input('radio-menu-neighbourhood', 'value'),
    Input('radio-menu-room', 'value')]
)
def update_graph(value, value_neighbour, value_room):
    disabled_neighbour = {'display': 'none'}
    disabled_room = {'display': 'none'}
    if (value == 'neighbourhood group'):
        disabled_neighbour = {'display': 'block'}
        fig = make_hexbin(df_clean.loc[df_clean[value] == value_neighbour], False)
    elif (value == 'room type'):
        disabled_room = {'display': 'block'}
        fig = make_hexbin(df_clean.loc[df_clean[value] == value_room], False)
    elif (value == 'Location'):
        fig = make_hexbin(df_clean, True)
    else:
        label = "Average " + value.capitalize()
        fig = ff.create_hexbin_mapbox(
            data_frame=df_clean, lat="lat", lon="long",
            opacity=1.0, labels={"color": label},
            min_count=1, color=value, agg_func=np.mean,
            show_original_data=True,
            original_data_marker=dict(size=4, opacity=0.2, color="deeppink"),
            zoom=8,
        )

    fig.update_layout(margin=dict(b=0, t=0, l=0, r=0))
    return fig, disabled_neighbour, disabled_room


# Define interactions Parallel coordinates graph
@app.callback(
    Output(plot1.html_id, 'figure'),
    [Input('dropdown-menu', 'value'),
    Input('dropdown-price', 'value')]
)
def update_comparison(value, priceRange):
    filtered_df = df_clean[df_clean["bin_price"]==priceParser(priceRange)]

    return plot1.update(VALUE_PAIRS_PCP, filtered_df)
#     Output(plot1.html_id, "figure"), [
#     Input('dropdown-menu', 'value')
# ])
# def update_comparison(value):
#     return plot1.update([("price","Price"),("review rate number","Review rate number")])


def make_hexbin(df, setOriginalData):
    return ff.create_hexbin_mapbox(
            data_frame=df, lat="lat", lon="long",
            opacity=1.0, labels={"color": "Listings Count"},
            min_count=1, show_original_data=setOriginalData, 
            original_data_marker=dict(size=4, opacity=0.2, color="deeppink"),
            zoom=8,
    )

@app.callback(
    [Output('grouped-bar-chart', 'children'),
    Output('dropdown-price', 'style'),
    Output('dropdown-price', 'disabled')],
    [Input('dropdown-menu', 'value'),
    Input('dropdown-price', 'value')],
    [State('grouped-bar-chart', 'children')]
)
def update_grouped(value, priceRange, children):
    disabled_bar = {'display':'None'}
    disable_drop = True
    if (value == 'price'):
        disabled_bar = {'display':'block'}
        disable_drop = False
        filtered_df = reviewPriceRange(df_clean[df_clean["bin_price"]==priceParser(priceRange)])
        if children:
            children[0]["props"]["figure"] = px.bar(filtered_df, x='range', y='bin', color='review', 
                        barmode="group", text='bin')
            children[0]["props"]["figure"].update_layout(xaxis_title="Service fee range", yaxis_title="Total Review")
        else:
            fig_second = px.bar(filtered_df, x='range', y='bin', color='review', 
                        barmode="group", text='bin')
            fig_second.update_layout(xaxis_title="Service fee range", yaxis_title="Total Review")
            children.append(
                    dcc.Graph(
                        figure=fig_second)
            )
    print("disabled: ")
    print(disabled_bar)
    return children, disabled_bar, disable_drop

def reviewPriceRange(df_clean):
    df1 = pd.DataFrame(df_clean.groupby(by=['bin','review rate number'])['bin'].count())
    df1.index.names = ['range', 'review']
    df1.reset_index(inplace=True)
    df1['review'] = df1['review'].astype(str)
    ranges = df1['range'].unique()
    priceRanges = ['$0 - $10', '$10 - $60', '$60 - $120', '$120 - $180', '$180 - $240']

    for element in ranges:
        inputToken = element
        if element == '(0, 10]':
            df1['range'] = df1['range'].str.replace(re.escape(inputToken), priceRanges[0])
        if element == '(10, 60]':
            df1['range'] = df1['range'].str.replace(re.escape(inputToken), priceRanges[1])
        if element == '(60, 120]':
            df1['range'] = df1['range'].str.replace(re.escape(inputToken), priceRanges[2])
        if element == '(120, 180]':
            df1['range'] = df1['range'].str.replace(re.escape(inputToken), priceRanges[3])
        if element == '(180, 240]':
            df1['range'] = df1['range'].str.replace(re.escape(inputToken), priceRanges[4])

    return df1

def priceParser(priceRange):
    if priceRange == '$50 - $280':
        return "(49.0, 280.0]"
    elif priceRange == '$281 - $509':
        return "(281.0, 510.0]"
    elif priceRange == '$510 - $739':
        return "(510.0, 740.0]"
    elif priceRange == '$740 - $969':
        return "(740.0, 970.0]"
    else:
        return "(970.0, 1200.0]"
    

if __name__ == '__main__':
    app.run_server(debug=True)
