from databases import df_clean

PCP_ITEMS = [("price","Price"),("service fee","Service fee"),("review rate number","Review rate number"),("Construction year","Construction year"),
("number of reviews","Number of reviews"), ('availability 365','Availability in a year'),  ('Revenue($)','Revenue($)')]

COLOR_SCALE="Bluyl"

DROPDOWN_MENU_ITEMS = [{'label': 'Listing Density', 'value': 'density'},
                    {'label': 'Average Price', 'value': 'price'},
                    {'label': 'Average Availability', 'value': 'availability 365'},
                    {'label': 'Average Construction Year', 'value': 'Construction year'},
                    {'label': 'Average Minimum Nights', 'value': 'minimum nights'},
                    {'label': 'Average Review Number', 'value': 'number of reviews'},
                    {'label': 'Average Revenue', 'value': 'Revenue($)'},
                    {'label': 'Average Rating', 'value': 'review rate number'},
                    {'label': 'Room Type', 'value': 'room type'},
                    {'label': 'Instant Bookable', 'value': 'instant_bookable'}]

HIDDEN_TABLE_ROWS = {'host_identity_verified',
               'neighbourhood group',
               'lat',
               'long',
               'country',
               'country code',
               'cancellation_policy',
               'last review',
               'reviews per month',
               'calculated host listings count'}

TABLE_ROWS = [col for col in df_clean.columns if col not in HIDDEN_TABLE_ROWS]
