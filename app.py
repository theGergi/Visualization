from dash import Dash, dcc, html, Input, Output, State, dash_table, State
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from views.radar_chart import PLgetRadarChart
from views.parcoords import Parcoords
from config import PCP_ITEMS, DROPDOWN_MENU_ITEMS, TABLE_ROWS
from databases import df_clean, df_small, df_normalized, normalizeDatabase
from views.cloropleth import get_cloropleth, quantitative_columns, categ_default_dict

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

px.set_mapbox_access_token(
    "pk.eyJ1IjoibXJhZmlwaCIsImEiOiJjbGMzdWZ0MTIwNmt5M3B0ODNnbzF1a3d2In0.7VgLitY9OXxhPSxlxJglfQ")

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.config.suppress_callback_exceptions = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.title = "Dash Map"

server = app.server


# Instatiate radar plot and pa
parcoordsPlot = Parcoords(df_clean)
radar_fig = PLgetRadarChart(pd.DataFrame(), names='NAME')


# ================================================LAYOUT================================================


# Make the layout
app.layout = html.Div(style={'backgroundColor': "#1f2630", 'color': '#2cfec1'}, children=[
    html.Div(className='row', children=[
        html.Div(className='banner', children=[
            html.H2('Dash - Airbnb Listings',
                    style={'marginTop': '0px', 'marginBottom': '0px', 'paddingTop': '25px'}),
            html.Hr()
        ]),
        html.Div(className='row', children=[
            html.Div(className='four columns div-user-controls', children=[
                html.Div(id='test'),
                html.P('''Filtering Options'''),
                html.Hr(),
                dcc.Dropdown(
                    DROPDOWN_MENU_ITEMS,
                    id='dropdown-menu',
                    searchable=False,
                    clearable=False,
                    style={'backgroundColor': "#1f2630", 'color': '#2cfec1'},
                    value='density',
                ),
                html.Br(),
                dash_table.DataTable(
                    df_small.to_dict('records'),
                    [{"name": i, "id": i, 'selectable': (i in quantitative_columns)} for i in TABLE_ROWS],
                    row_selectable='multi',
                    column_selectable='multi',
                    id='preview_table',
                    style_table={'height': '300px',
                                 'overflowY': 'auto', 'color': '#2cfec1', },
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
                          id='radar_fig',
                          style={'backgroundColor': "#1f2630"},)
            ],

            ),


            html.Div(className='eight columns div-for-charts-bg-grey', children=[
                html.Div(
                    className="row",
                    children=[
                        # html.Div(id='my-output'),
                        html.Div(
                            className="eight columns",
                            children=[
                                dcc.Graph(
                                    id='cloropleth-map',
                                    className='twelve columns',
                                    figure=get_cloropleth(),
                                    style={'backgroundColor': "#1f2630"},
                                )
                            ]),

                        html.Div(className='four columns div-for-charts-bg-grey',
                                 children=[
                                     dcc.Graph(
                                         id='histogram',
                                         style={'backgroundColor': "#1f2630"}
                                     )
                                 ]),
                    ]
                ),
                html.Div(
                    className="row",
                    children=[
                        parcoordsPlot
                    ]),

            ])
        ])
    ])
])

# ================================================CALLBACKS================================================

# Updates the radar chart
@app.callback(
    Output('radar_fig', "figure"),
    Input('preview_table', 'selected_row_ids'),
    Input('preview_table', 'selected_columns'),
)
def select_listings(selected_rows, selected_cols):
    if not selected_rows:
        return PLgetRadarChart(pd.DataFrame(), names='NAME')
    display_df = df_normalized.loc[selected_rows]
    if selected_cols is not None and len(selected_cols) > 2:
        display_df = normalizeDatabase(df_clean, selected_cols).loc[selected_rows]
    fig = PLgetRadarChart(display_df, names='NAME')
    fig.update_layout(paper_bgcolor="#1f2630",
                      plot_bgcolor="#1f2630",
                      font=dict(color="#2cfec1"))
    return fig

# Updates the cloropleth map
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
    print('pop')
    if selectedTableRows != None:
        df_traces = df_clean.loc[df_clean["id"].isin(selectedTableRows)]
        print(df_traces)
        fig = go.Figure(get_cloropleth(df_traces, color_col=value))

    else:
        fig = go.Figure(get_cloropleth(pd.DataFrame(), color_col=value))
    fig.update_layout(paper_bgcolor="#1f2630",
                      plot_bgcolor="#1f2630",
                      font=dict(color="#2cfec1"))
    return fig


# Updates the table
@app.callback(
    Output('preview_table', 'data'),
    [Input('dropdown-menu', 'value'),
     Input('cloropleth-map', 'selectedData'),
     Input('histogram', 'selectedData'),
     State('histogram', 'figure')]
)
def sort_table_data(value, mapSelectedData, histSelectedData, histFigDict):
    if value == 'density':
        value = 'NAME'
    hist_filter_data = filter_hist_selected(histSelectedData, histFigDict)
    if (value == 'availability 365'):
        df_sorted = filter_map_selection(
            mapSelectedData, hist_filter_data).sort_values(by=[value], ascending=True)
    else:
        df_sorted = filter_map_selection(
            mapSelectedData, hist_filter_data).sort_values(by=[value], ascending=False)
    return df_sorted.iloc[:100].to_dict('records')

# Updates the Parallel Coordinate
@app.callback(
    Output(parcoordsPlot.html_id, 'figure'),
    [Input('cloropleth-map', 'selectedData'),
     Input('dropdown-menu', 'value'),
     Input('histogram', 'selectedData'),
     State('histogram', 'figure')]
)
def update_parcoords(mapSelectedData, value, histSelectedData, histFigDict):
    # MAKE SURE THE X AXIS TEXT NAME IS THE SAME AS THE COLUMN NAME OF PANDAS
    # OTHERWISE WE CANT FIND THE NEED VALUES
    # print(hist_column)
    if value == 'density':
        value = 'neighbourhood group'
    color_col = value
    hist_filter_data = filter_hist_selected(histSelectedData,  histFigDict)
    diplayed_columns = PCP_ITEMS
    fig = parcoordsPlot.update(diplayed_columns, filter_map_selection(
        mapSelectedData, hist_filter_data), color_col)
    fig.update_layout(paper_bgcolor="#1f2630",
                      plot_bgcolor="#1f2630",
                      font=dict(color="#2cfec1"))
    return fig


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
    fig_second.update_layout(margin=dict(l=0, r=20, b=20), bargap=0.2)
    fig_second.update_layout(paper_bgcolor="#1f2630",
                             plot_bgcolor="#1f2630",
                             font=dict(color="#2cfec1"))

    return fig_second


# ================================================HELPER METHODS================================================

# Helper methods for callbacks
def filter_map_selection(selectedData: dict[list[dict]], df=df_clean) -> pd.DataFrame:
    if selectedData == None:
        return df
    hood_list = [point['location'] for point in selectedData['points']]
    df_map_filter = df.query('neighbourhood in @hood_list')
    return df_map_filter


def filter_hist_selected(selectedData: dict, histFigDict: str, df=df_clean) -> pd.DataFrame:
    if not selectedData:
        return df
    if not histFigDict:
        column = 'price'
    else:
        column = histFigDict['layout']['xaxis']['title']['text']

    if column in quantitative_columns:
        x_min = float(selectedData['range']['x'][0])
        x_max = float(selectedData['range']['x'][1])
        # print(df.query(f'{column} >= @x_min and {column} <= @x_max'))
        return df.query(f'{column} >= @x_min and {column} <= @x_max')
    else:
        groups = [point['x'] for point in selectedData['points']]
        return df.query(f'`{column}` in @groups')


if __name__ == '__main__':
    app.run_server(debug=False)
