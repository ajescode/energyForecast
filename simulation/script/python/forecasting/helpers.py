from scipy import stats
import numpy as np
import statsmodels.tsa.filters.hp_filter as hp
import pandas as pd


def count_frame_indeces(data_f, window_f, start_date_f, last_date_f):
    shape = data_f.shape
    start_index = shape[0] - 2 * window_f + 1
    last_index = shape[0] - window_f + 1
    if start_date_f:
        start_index = int(data_f[data_f['date'] == start_date_f].index[0])
        last_index = start_index + window_f
    if last_date_f:
        last_index = int(data_f[data_f['date'] == last_date_f].index[0])

    return start_index, last_index


def data_shape(data):
    print("Length (days): " + str(data.shape[0]))
    print("Width: " + str(data.shape[1]))
    print("First date: " + str(data.iloc[0, 0]))
    print("Last date: " + str(data.iloc[data.shape[0] - 1, 0]))


# data_shape(data)

def filter_hours(data):
    return data.loc[:, '0':'23']


def print_settings(file, area, window, start_date, end_date, method, variables_list):
    return '|'.join([file, area, str(window), str(start_date), str(end_date), str(method), str(variables_list)])


# counting median and MAD for each hour
def count_median_mad(data):
    if len(data.shape) > 1:
        data = filter_hours(data)
    median = np.median(data, axis=0)
    mad = stats.median_absolute_deviation(data)
    return median, mad


def standarize(method, data, median, mad, hp_filter=True, index_f=None, window_f=None):
    if method == 'asinh-hp' and hp_filter:
        data = hp.hpfilter(data, 110930628906)[0]
        median, mad = count_median_mad(data.loc[index_f - window_f:index_f])
    if method == 'asinh' or method == 'asinh-hp':
        data = (data - median) / mad
        data = np.arcsinh(data)
    else:
        data = (data - median) / mad
    return data


def unstandarize(method, data, median, mad):
    if method == 'asinh' or method == 'asinh-hp':
        data = np.sinh(data)
    data = data * mad + median
    return data


def get_standarize_method(file=None, method=None):
    if file == 'consumption' or file == 'wind':
        if not method:
            method = 'normal'
            method = 'asinh-hp'
    elif file == 'price':
        if not method:
            method = 'asinh'
    return method


def load_nordpool_prognosis(data_dir, name, area):
    file_name = name + '_prognosis_' + area + '.csv'

    return pd.read_csv(data_dir + file_name)


def get_variables_list(variables_list, nordpool_prognosis):
    if nordpool_prognosis:
        return 'nordpool_prognosis'
    else:
        return variables_list
