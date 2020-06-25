import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from scipy import stats
from IPython.display import display
import ipywidgets as widgets
import statsmodels.api as sm
from simulation.script.python.forecasting.variables import VariablesGetter
from simulation.script.python.forecasting.helpers import *

# setup
area = 'DK2'
file = 'price'
window = 182
start_date = '2020-01-01'
end_date = '2020-05-12'
variables_list = ['dayofweek', 'prev_day1', 'prev_day2', 'prev_day7', 'min_day', 'max_day', 'last_val_day',
                  'consumption_prognosis_for_price', 'wind_prognosis_for_price']
# get_variables_neg_day1,get_variables_neg_day2,get_variables_neg_day7,consumption_prognosis


save_files = True
nordpool_prognosis = False
standarizing_method = 'asinh'

data_dir = "../../../data/data_sanitized/"
forecast_dir = '../../../data/forecasts/'
file_forecasts = forecast_dir + 'files.txt'
file_name = file + '_' + area + '.csv'

data = pd.read_csv(data_dir + file_name)
data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
data = data.drop(columns=['holiday'])
data_shape = count_frame_indeces(data, window, start_date, end_date)


def reload_data():
    global file_name, data, data_shape
    file_name = file + '_' + area + '.csv'

    data = pd.read_csv(data_dir + file_name)
    data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
    data = data.drop(columns=['holiday'])
    data_shape = count_frame_indeces(data, window, start_date, end_date)


# data: full dataframe with all varibales,
# window: window for forecasting, integer, ex. 730
# start_date: first data of window (if False takes last date - windowd), ex. '2016-05-05'
# variables: arrays of all variables []

def forecast(data_f, window_f, data_shape_f, variables_f):
    start_index, last_index = data_shape_f

    pred_data = data_f.copy()
    pred_data = pred_data.drop(columns=['date'])

    test_data = pred_data.copy()
    pred_data.loc[start_index:last_index, '0':'23'] = 0.0
    if nordpool_prognosis:
        pred_data.loc[start_index:last_index, '0':'23'] = load_nordpool_prognosis(data_dir, file, area).loc[
                                                          start_index:last_index, '0':'23']
    else:
        for i in pred_data.loc[start_index:last_index].index:
            pred_data.loc[i, '0':'23'] = forecast_row(i, window_f, test_data, variables_f)

    pred_data = pred_data.loc[start_index:last_index, :]

    real_data = data_f.loc[start_index:last_index, :]

    if save_files:
        with open(file_forecasts, 'r+') as f:
            lines = f.read().splitlines()
            if not lines:
                no = str(0)
            else:
                last_line = lines[-1]
                no = last_line.split('.', 1)[0]
            no = str(int(no) + 1)
            settings_desc = print_settings(file, area, window_f, start_date, end_date, standarizing_method,
                                           get_variables_list(variables_list, nordpool_prognosis))
            f.write(no + "." + settings_desc + "\n")
            print("Saved: " + settings_desc)
        pred_data.to_csv(forecast_dir + no + ".csv", index=True)

    return real_data, pred_data


# index for which forecast should be calculated
# window - number of rows taken for window
# data - filtered data - only with index and hour columns
# array of variables - definition above
def forecast_row(index_f, window_f, data_f, variables_f):
    row = np.zeros((1, 24))
    sizeB = 1  # size of variables in model

    # counting MAD and median
    median, mad = count_median_mad(data_f.loc[index_f - window_f:index_f - 1])

    # normalize values
    if standarizing_method:
        data_f = standarize(standarizing_method, data_f, median, mad)

    # counting variables vector size in model
    for v in variables_f:
        if v[0] == 'each_hour':
            sizeB += 1
        elif v[0] == 'each_day':
            if len(v[1].shape) == 1:
                sizeB += 1
            else:
                sizeB += v[1].shape[1]

    # forecasting for each row -> forecasting for each hour
    variablesMatrix = pd.DataFrame().from_records(np.ones((data_f.shape[0], sizeB)))

    for h in range(row.shape[1]):
        i = 0
        # copy values from variables matrix
        for v in variables_f:
            if v[0] == 'each_hour':
                variablesMatrix[i] = v[1][str(h)]
                if v[2]:
                    median_v, mad_v = count_median_mad(variablesMatrix[i].loc[index_f - window_f:index_f])
                    print(variablesMatrix[i].loc[index_f - window_f:index_f])
                    print('aaa')
                    print(variablesMatrix[i])
                    variablesMatrix[i] = standarize(v[2], variablesMatrix[i], median_v, mad_v)
                    print(variablesMatrix[i])
                    print('bbb')
                i += 1
            elif v[0] == 'each_day':
                if len(v[1].shape) == 1:
                    variablesMatrix[i] = v[1]
                    if v[2]:
                        median_v, mad_v = count_median_mad(variablesMatrix[i].loc[index_f - window_f:index_f])
                        variablesMatrix[i] = standarize(v[2], variablesMatrix[i], median_v, mad_v)
                    i += 1
                else:
                    for k in range(v[1].shape[1]):
                        variablesMatrix[i] = v[1][:, k]
                        if v[2]:
                            median_v, mad_v = count_median_mad(variablesMatrix[i].loc[index_f - window_f:index_f])
                            variablesMatrix[i] = standarize(v[2], variablesMatrix[i], median_v, mad_v)
                        i += 1

        # normalize variables_matrix

        row[0, h] = getParametersVector(index_f, h, window_f, data_f, variablesMatrix) @ getVariablesVector(index_f,
                                                                                                            variablesMatrix)

    # inverse normalization
    if standarizing_method:
        row = unstandarize(standarizing_method, row, median, mad)

    return row


def getParametersVector(index_f, h, window_f, data_f, variablesMatrix):
    Y = data_f.loc[index_f - window_f:index_f - 1, str(h)]
    X = variablesMatrix.loc[index_f - window_f:index_f - 1, :]

    model = sm.OLS(Y, X)
    results = model.fit()

    return results.params


def getVariablesVector(index, variables_f):
    return variables_f.loc[index, :]


def f():
    reload_data()
    variables_getter = VariablesGetter(file, data, area, variables_list, start_date, end_date, standarizing_method,
                                       window)
    variables = variables_getter.get_variables()
    return forecast(data, window, data_shape, variables)


# perform all forecasts
file = 'consumption'
areas = ['DK1']
windows = [4]
std_methods = ['asinh']
start_dates = [('2019-01-01', '2019-12-31'), ('2019-05-13', '2020-05-12'), ('2020-01-01', '2020-05-12'),
               ('2019-01-01', '2020-05-12')]
variables_lists = {
    'consumption': [
        ['dayofweek', 'consumption_prognosis'],
        # ['dayofweek', 'consumption_prognosis', 'prev_day1', 'prev_day2', 'prev_day7'],
        # ['dayofweek', 'consumption_prognosis', 'prev_day1', 'prev_day2', 'prev_day7', 'wind_prognosis']
    ],
    'wind': [
        ['dayofweek', 'wind_prognosis'],
        ['dayofweek', 'wind_prognosis', 'prev_day1', 'prev_day2', 'prev_day7'],
        ['dayofweek', 'wind_prognosis', 'prev_day1', 'prev_day2', 'prev_day7', 'consumption_prognosis']
    ],
    'price': [
        # ['dayofweek'],
        # ['dayofweek', 'prev_day1', 'prev_day2', 'prev_day7'],
        # ['dayofweek', 'prev_day1', 'prev_day2', 'prev_day7', 'min_day', 'max_day', 'last_val_day'],
        # ['dayofweek', 'prev_day1', 'prev_day2', 'prev_day7', 'min_day', 'max_day', 'last_val_day',
        #  'consumption_prognosis', 'wind_prognosis'],
        ['dayofweek', 'prev_day1', 'prev_day2', 'prev_day7', 'min_day', 'max_day', 'last_val_day',
         'consumption_prognosis_for_price', 'wind_prognosis_for_price']
    ]}

# f()

for a in areas:
    area = a
    for w in windows:
        window = w
        for s in start_dates:
            start_date = s[0]
            end_date = s[1]
            if not file == 'price':
                nordpool_prognosis = True
                f()
                nordpool_prognosis = False
            for m in std_methods:
                standarizing_method = m
                for v in variables_lists[file]:
                    variables_list = v
                    f()
                    exit()
