from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff
from dash.exceptions import PreventUpdate
import numpy as np

def clean(x):
    x = x.replace("$", "").replace(" ", "")
    if "," in x:
        x = x.replace(",", "")
    return int(x)

df = pd.read_csv('airbnb_open_data.csv', usecols=['NAME','host id', 'host_identity_verified','host name',
'neighbourhood group','neighbourhood','lat','long',	'country','country code','instant_bookable','cancellation_policy',
'room type','Construction year','price','service fee','minimum nights','number of reviews',	'last review',	
'reviews per month','review rate number','calculated host listings count','availability 365'])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

px.set_mapbox_access_token("pk.eyJ1IjoibXJhZmlwaCIsImEiOiJjbGMzdWZ0MTIwNmt5M3B0ODNnbzF1a3d2In0.7VgLitY9OXxhPSxlxJglfQ")

app = Dash(__name__,external_stylesheets=external_stylesheets)

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
df_clean['neighbourhood group'] = df_clean['neighbourhood group'].replace('brookln', 'Brooklyn')

# Make the layout 
app.layout = html.Div(children=[
    html.Div(
        className='row', children=[
            html.Div(className='four columns div-user-controls', children=[
                html.H2('Dash - Airbnb Listings'),
                html.P('''Filter Options'''),
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
                )
            ]),

            html.Div(className='eight columns div-for-charts-bg-grey', children=[
                dcc.Graph(
                    id='hexbin-mapbox',
                ),
            ])
        ], 
    )
])

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

def make_hexbin(df, setOriginalData):
    return ff.create_hexbin_mapbox(
            data_frame=df, lat="lat", lon="long",
            opacity=1.0, labels={"color": "Listings Count"},
            min_count=1, show_original_data=setOriginalData, 
            original_data_marker=dict(size=4, opacity=0.2, color="deeppink"),
            zoom=8,
        )
    

if __name__ == '__main__':
    app.run_server(debug=True)
