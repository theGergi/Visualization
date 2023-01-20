from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import re

def clean(x):
    x = x.replace("$", "").replace(" ", "")
    return int(x)

df = pd.read_csv('airbnb_open_data.csv', usecols=['NAME','host id', 'host_identity_verified','host name',
'neighbourhood group','neighbourhood','lat','long',	'country','country code','instant_bookable','cancellation_policy',
'room type','Construction year','price','service fee','minimum nights','number of reviews',	'last review',	
'reviews per month','review rate number','calculated host listings count','availability 365'])

app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = "Dash Grouped Bar Chart"

server = app.server

# We want to know about the relationship between service fee and ratings (service fee - independent var and ratings - dependent)

# First remove all the NaN values in the column and convert the values of the column service fee into integer

df_clean = df.copy()

df_clean = df_clean.dropna().reset_index(drop=True)

df_clean['service fee'] = df_clean['service fee'].apply(clean)

# Separate these values into different bins
df_clean['bin'] = pd.cut(x=df_clean['service fee'], bins=[0, 10, 60, 120, 180, 240])

df_clean['bin'] = df_clean['bin'].astype(str)

df1 = pd.DataFrame(df_clean.groupby(by=['bin','review rate number'])['bin'].count())

df1.index.names = ['range', 'review']

df1.reset_index(inplace=True)

df1['review'] = df1['review'].astype(str)

ranges = df1['range'].unique()

priceRanges = ['$0 - $10', '$10 - $60', '$60 - $120', '$120 - $180', '$180 - $240']

index = 0

for element in ranges:
    inputToken = element
    df1['range'] = df1['range'].str.replace(re.escape(inputToken), priceRanges[index])
    index+=1

app.layout = html.Div(
    id="app-container", 
    children=[
        html.Div( id = 'left column',
        children=[html.H3('Service fee vs. Review rate comparison'),
        dcc.Dropdown(['$0 - $10', '$10 - $60', '$60 - $120', '$120 - $180', '$180 - $240'],
                    ['$10 - $60', '$60 - $120', '$120 - $180', '$180 - $240'],
                     multi=True, id="msd")], style={"textAlign": "float-left"}),

        html.Div( id = 'right column',
        children =[
        dcc.Graph(
            id='graph',
        )])
])

@app.callback(
    Output("graph", "figure"),
    Input("msd", "value")
)
def update_graph(priceRange):
    pr = priceRange
    filtered_df = df1.query("range == @pr")

    fig = px.bar(filtered_df, x='range', y='bin', color='review', 
             barmode="group", text='bin')

    fig.update_layout(xaxis_title="Service fee range", yaxis_title="Total Review")

    fig.update_layout(transition_duration=500)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)