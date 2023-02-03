import json
import pandas as pd
import plotly.express as px

from databases import df_clean
from config import COLOR_SCALE


# Map data for the cloropleth map
with open('datasets/neighbourhoods.geojson') as f:
    hood_geometry = json.load(f)
# should be global
quantitative_columns = ['price', 'availability 365', 'Construction year',
                        'minimum nights', 'number of reviews', 'Revenue($)', 'review rate number']
default_categ_col = ['room type', 'instant_bookable']
categ_default_dict = {"room type": 'Private room', 'instant_bookable': 'True'}
agg_dict = {col: 'mean' for col in quantitative_columns}
agg_dict['id'] = 'count'


def get_categ_counts(categ_col: str, df=df_clean) -> pd.DataFrame:
    """
    Aggregates the given database by neighbourhood and creates a column with the count of the selected categorical attribute for each neighbourhood
    
    Paramters:
    categ_col (str): categorical attribute to count
    df (pd.DataFrame): database to aggregate

    Returns:
    pd.DataFrame: Database after aggregation
    """
    result_df = (df.groupby('neighbourhood')[categ_col]
                 .value_counts()
                 .unstack(level=-1)
                 .fillna(0))
    df_totals = df.groupby('neighbourhood')['id'].count()
    result_df = result_df.rename(
        columns={col: f'{categ_col}_{col}' for col in result_df.columns})
    for col in result_df.columns:
        result_df['proportion'+'_'+col] = result_df[col]/df_totals

    return result_df


def get_hood_df(df=df_clean) -> pd.DataFrame:
    """
    Aggregates the given database by neighbourhood and creates columns with the count of the selected attributes for each neighbourhood
    
    Paramters:
    df (pd.DataFrame): database to aggregate

    Returns:
    pd.DataFrame: Database after aggregation
    """

    # Aggregate quantative columns
    all_colls = ['neighbourhood', 'id', 'room type'] + quantitative_columns
    default_group = (df[all_colls]
                     .groupby('neighbourhood', as_index=False)
                     .agg(agg_dict))
    
    # Aggregate categorical columns
    for col in default_categ_col:
        categ_summary = get_categ_counts(col, df)
        default_group = default_group.join(categ_summary, on='neighbourhood')

    return default_group


def get_cloropleth(df: pd.DataFrame = pd.DataFrame(), color_col: str = 'price'):
    """
    Create cloropleth
    """

    if df.empty:
        df_grouped = get_hood_df()
    else:
        df_grouped = get_hood_df(df)
    fig = px.choropleth_mapbox(df_grouped, geojson=hood_geometry,
                               locations='neighbourhood', color=color_col,
                               featureidkey="properties.neighbourhood",
                               color_continuous_scale=COLOR_SCALE,
                               mapbox_style="carto-positron",
                               labels={'price': 'Price', 'id': 'Count', 'proportion_room type_Private room': 'Room Type',
                                       'availability 365': 'Availability(days)'},
                               zoom=9, center={"lat": 40.70271, "lon": -73.8993},
                               )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig