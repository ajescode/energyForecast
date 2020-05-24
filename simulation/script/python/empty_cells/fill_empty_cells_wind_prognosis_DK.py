import pandas as pd

# Script fixing missing values from files wind_prognosis DK1 and DK2 for day ,
wpdk1 = "../../../data/data_sanitized/wind_prognosis_DK1.csv"
wpdk2 = "../../../data/data_sanitized/wind_prognosis_DK2.csv"

files = [wpdk1, wpdk2]

for file in files:
    data = pd.read_csv(file)

    start = data.at[990, '23']
    end = data.at[991, '14']
    for i in range(0, 14):
        data.at[991, str(i)] = start + (end - start) / 15 * (i + 1)

    data.to_csv(file, index=False)
    print("Done for file: " + file)
