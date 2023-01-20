from jbi100_app.main import app
from jbi100_app.views.menu import make_menu_layout
from jbi100_app.views.scatterplot import Scatterplot

from dash import html
import plotly.express as px
from dash.dependencies import Input, Output


if __name__ == '__main__':
    # Create data
    df = px.data.iris()

    # Instantiate custom views
    scatterplot1 = Scatterplot("Scatterplot 1", 'sepal_length', 'sepal_width', df)
    scatterplot2 = Scatterplot("Scatterplot 2", 'petal_length', 'petal_width', df)

    app.layout = html.Div(
        id="app-container",
        children=[
            # Left column
            html.Div(
                id="left-column",
                className="three columns",
                children=make_menu_layout()
            ),

            # Right column
            html.Div(
                id="right-column",
                className="nine columns",
                children=[
                    scatterplot1,
                    scatterplot2
                ],
            ),
        ],
    )

    # Define interactions
    @app.callback(
        Output(component_id = scatterplot1.html_id, component_property = "figure"), [
        Input(component_id = "select-color-scatter-1", component_property = "value"),
        Input(component_id = scatterplot2.html_id, component_property = 'selectedData')
    ])
    # The number of parameters needs to be the same as the number of inputs and states
    # This function needs to be defined right underneath the callback decorator
    def update_scatter_1(selected_color, selected_data):
        return scatterplot1.update(selected_color, selected_data)

    @app.callback(
        Output(component_id =scatterplot2.html_id, component_property = "figure"), [
        Input(component_id ="select-color-scatter-2", component_property = "value"),
        Input(component_id =scatterplot1.html_id, component_property = 'selectedData')
    ])
    def update_scatter_2(selected_color, selected_data):
        return scatterplot2.update(selected_color, selected_data)


    app.run_server(debug=False, dev_tools_ui=False)