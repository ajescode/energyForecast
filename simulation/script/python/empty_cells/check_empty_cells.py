import os
import glob
import pandas as pd

# Script calculating all zero and incorrect values and transforming them to the average value of closest numbers

directory_merged = '../../../data/data_merged'
directory_sanitized = '../../../data/data_sanitized'

os.chdir(directory_merged)

# get all files from directory
all_files = [i for i in glob.glob('*.csv')]

print("Zero or incorrect values in datasets")

for file in all_files:
    # read file
    data = pd.read_csv(file)

    # drop last incomplete row of data
    data.drop(data.tail(1).index, inplace=True)

    # format only hour columns [0:23]
    df = data.loc[:, '0':]

    d = df.apply(lambda s: pd.to_numeric(s, errors="coerce"))
    m = d.eq(0) | d.isna()
    s = m.stack()
    val_list = s[s].index.tolist()
    count = len(val_list)

    print(file + ' | Found missing values: ' + str(count) + " | " + str(val_list))
