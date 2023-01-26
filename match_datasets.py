import pandas as pd

df_wide = pd.read_csv('datasets/listings.csv')
df_tall = pd.read_csv('airbnb_open_data.csv')

c = 0
print(df_tall['NAME'].head())
for name in df_wide['name']:
    if name in df_tall['NAME'].values:
        c+=1
    else:
        print(name)

print(df_wide.shape[0], df_tall.shape[0])
print(c , c/df_wide.shape[0], c/df_tall.shape[0])