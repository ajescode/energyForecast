import os
import glob
import pandas as pd

# Script calculating all zero and incorrect values and transforming them to the average value of closest numbers

directory = '../../../data/data_merged'
directory_output = '../data_sanitized'

os.chdir(directory)

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

    data_len = len(df)
    first_col = int(df.columns[0])
    last_col = int(df.columns[len(df.columns) - 1])
    d = df.apply(lambda s: pd.to_numeric(s, errors="coerce"))
    m = d.eq(0) | d.isna()
    s = m.stack()
    val_list = s[s].index.tolist()
    count = len(val_list)

    # print(val_list)

    for el in val_list:
        row = int(el[0])
        col = int(el[1])
        if (row == 0 and col == first_col) or (row == data_len - 1 and col == last_col):
            continue
        next = df.iat[row + 1, first_col] if col == last_col else df.iat[row, col + 1]
        prev = df.iat[row - 1, last_col] if col == first_col else df.iat[row, col - 1]
        if prev == 0 or next == 0:
            next2 = df.iat[row + 1, first_col + 1 if col == last_col else 0] if col in [last_col, last_col - 1] else \
                df.iat[row, col + 2]
            if next2 == 0:
                continue
            df.iat[row, col] = prev + (next2 - prev) / 3
        else:
            df.iat[row, col] = (prev + next) / 2



    data.loc[:, '0':] = df

    d = df.apply(lambda s: pd.to_numeric(s, errors="coerce"))
    m = d.eq(0) | d.isna()
    s = m.stack()
    left_list = s[s].index.tolist()
    left_count = len(left_list)

    filePathOutput = directory_output + "/" + file
    data.to_csv(filePathOutput, index=False)
    print(file + ' | Found missing values: ' + str(count) + " | Left (" + str(left_count) + "): " + str(left_list))
