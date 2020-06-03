import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from scipy import stats
from IPython.display import display
import ipywidgets as widgets
from simulation.script.python.forecasting.variables import VariablesGetter
from simulation.script.python.forecasting.helpers import *

# setup
area = 'DK1'
file = 'consumption'
window = 728
variables_list = ['dayofweek', 'consumption_prognosis','prev_day1','prev_day2','prev_day7']
# get_variables_neg_day1,get_variables_neg_day2,get_variables_neg_day7,consumption_prognosis

start_date = False
save_files = True

file_name = file + '_' + area + '.csv'
data_dir = "../../../data/data_sanitized/"
forecast_dir = '../../../data/forecasts/'
file_forecasts = forecast_dir + 'files.txt'

data = pd.read_csv(data_dir + file_name)
data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
data = data.drop(columns=['holiday'])
data_shape = count_frame_indeces(data, window, start_date)

variables_getter = VariablesGetter(data, area, variables_list)
variables = variables_getter.get_variables()


# data: full dataframe with all varibales,
# window: window for forecasting, integer, ex. 730
# start_date: first data of window (if False takes last date - windowd), ex. '2016-05-05'
# variables: arrays of all variables []

def forecast(data_f, window_f, data_shape_f, variables_f):
    start_index, last_index = data_shape_f
    # out = widgets.HTML()
    # display(out)

    pred_data = data_f.copy()
    pred_data = pred_data.drop(columns=['date'])

    test_data = pred_data.copy()
    pred_data.loc[last_index:, '0':'23'] = 0.0
    for i in pred_data.loc[last_index:].index:
        # out.value = "Forecasting row " + str(i) + ", left: " + str(shape[0] - i - 1)
        # exit()
        pred_data.loc[i, '0':'23'] = forecast_row(i, window_f, test_data, variables_f)

    pred_data = pred_data.loc[last_index:, :]

    real_data = data_f.loc[last_index:, :]

    if save_files:
        with open(file_forecasts, 'r+') as f:
            lines = f.read().splitlines()
            if not lines:
                no = str(0)
            else:
                last_line = lines[-1]
                no = last_line.split('.', 1)[0]
            no = str(int(no) + 1)
            f.write(no + "." + print_settings(file, area, window, start_date, variables_list) + "\n")

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

    # print(median, mad)
    # normalize values
    data_f = standarize(data_f, median, mad)

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
        for v in variables_f:
            if v[0] == 'each_hour':
                variablesMatrix[i] = v[1][str(h)]
                i += 1
            elif v[0] == 'each_day':
                if len(v[1].shape) == 1:
                    variablesMatrix[i] = v[1]
                    i += 1
                else:
                    for k in range(v[1].shape[1]):
                        variablesMatrix[i] = v[1][:, k]
                        i += 1

        # if (index_f == 1590):
        row[0, h] = getParametersVector(index_f, h, window_f, data_f, variablesMatrix) @ getVariablesVector(index_f,
                                                                                                            variablesMatrix)

        if h == 8:
            # print(getParametersVector(index_f, h, window_f, data_f, variablesMatrix))
            print(row[0, h])

    # inverse normalization
    row = unstandarize(row, median, mad)

    return row


def getParametersVector(index_f, h, window_f, data_f, variablesMatrix):
    Y = data_f.loc[index_f - window_f:index_f - 1, str(h)]
    X = variablesMatrix.loc[index_f - window_f:index_f - 1, :]

    print(np.dot(X.T, X).shape)
    print(np.dot(X.T, X))
    print(Y)

    return np.dot(np.dot(np.linalg.inv(np.dot(X.T, X)), X.T), Y)


def getVariablesVector(index, variables_f):
    return variables_f.loc[index, :]


# forecast_row(874,730,data,variables)

def f():
    return forecast(data, window, data_shape, variables)


f()
