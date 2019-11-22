#Script for scrap the radicals

import pandas as pd 

radicals_file = "radicals.csv"

radicals_df = pd.read_csv(radicals_file)

print(radicals_df.shape)
print(radicals_df.columns)
print(radicals_df.dtypes)

for index,row in radicals_df.iterrows():
	print(index,row['name'])