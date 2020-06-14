import pandas as pd
from sklearn import metrics

areas = ['DK1', 'DK2']
files = ['consumption', 'price', 'wind']

data_dir = "../../../data/data_sanitized/"
forecast_dir = '../../../data/forecasts/'
forecasts_file = forecast_dir + 'files.txt'

data = {}
for file in files:
    data[file] = {}
    for area in areas:
        data[file][area] = pd.read_csv(data_dir + file + "_" + area + ".csv")


def get_forecast_file(no):
    return pd.read_csv(forecast_dir + no + ".csv")


forecasts = {}

with open(forecasts_file, 'r+') as f:
    lines = f.read().splitlines()
    if not lines:
        print('Empty file')
    for line in lines:
        cur_line = line.split('.', 1)
        no = cur_line[0]
        cur_line[1] = cur_line[1].split('|')
        forecasts[no] = {"data": get_forecast_file(no), 'file': cur_line[1][0], 'area': cur_line[1][1],
                         'variables': cur_line[1][4]}

# print(forecasts)

forecasts_mae = {}
for f in forecasts:
    first_index = forecasts[f]['data'].iloc[0, 0]
    last_index = forecasts[f]['data'].iloc[-1, 0]
    y_pred = forecasts[f]['data'].loc[:, '0':'23']
    y_true = data[forecasts[f]['file']][forecasts[f]['area']].loc[first_index:last_index, '0':'23']
    forecasts_mae[f] = metrics.mean_absolute_error(y_true, y_pred)

for m in forecasts_mae:
    print(m + ": " + str(forecasts_mae[m]))
