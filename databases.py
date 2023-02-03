import json
import pandas as pd
# The first thing we have to do is clean the dataframe

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

def cleanDatabase(df) -> pd.DataFrame:
    df_clean = df.copy()
    df_clean = df_clean.dropna().reset_index(drop=True)
    df_clean['price'] = df_clean['price'].apply(clean)
    df_clean['availability 365'] = df_clean['availability 365'].apply(cleanAvailability365)
    df_clean['service fee'] = df_clean['service fee'].apply(clean)
    df_clean['neighbourhood group'] = df_clean['neighbourhood group'].replace('brookln', 'Brooklyn')
    df_clean = df_clean.set_index('id', drop=False)
    df_clean['Revenue($)'] = df_clean['price']*(365 - df_clean['availability 365'].astype(int))

    return df_clean

def normalizeColumns(df: pd.DataFrame) -> pd.DataFrame:
    result_df = pd.DataFrame()
    for col in df.columns: 
        result_df[col] = df[col].rank()
        result_df[col] = (result_df[col]*100) / len(df)
    return result_df

def normalizeDatabase(df):
    radar_cols = ['price','service fee','minimum nights','number of reviews']
    df_normalized = normalizeColumns(df[radar_cols])
    df_normalized['NAME'] = df['NAME']
    df_normalized['id'] = df['id']
    df_normalized = df_normalized.set_index('id', drop=False)

    return df_normalized


# Load data from the database
df = pd.read_csv('datasets/airbnb_open_data.csv', usecols=['id', 'NAME', 'host id', 'host_identity_verified', 'host name',
    'neighbourhood group', 'neighbourhood', 'lat', 'long',	'country', 'country code', 'instant_bookable', 'cancellation_policy',
    'room type', 'Construction year', 'price', 'service fee', 'minimum nights', 'number of reviews',	'last review',
    'reviews per month', 'review rate number', 'calculated host listings count', 'availability 365'])

# Clean data from illegal values
df_clean = cleanDatabase(df)

# Generate helper databases used by different plots
# Reduced dataset for faster user experience with the table
df_small = df_clean[:100]
# Normalize data to be used by radar plot
df_normalized = normalizeDatabase(df_clean)


