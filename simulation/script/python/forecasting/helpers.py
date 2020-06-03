from scipy import stats
import numpy as np


def count_frame_indeces(data_f, window_f, start_date_f):
    shape = data_f.shape
    start_index = shape[0] - 2 * window_f + 1
    last_index = shape[0] - window_f + 1
    if start_date_f:
        start_date_index = int(data_f[data_f['date'] == start_date_f].index[0])
        if start_date_index > start_index:
            print(start_index)
            raise Exception('Start date is too big')
        start_index = start_date_index
        last_index = start_date_index + window_f
    last_index -= 1
    return start_index, last_index


def data_shape(data):
    print("Length (days): " + str(data.shape[0]))
    print("Width: " + str(data.shape[1]))
    print("First date: " + str(data.iloc[0, 0]))
    print("Last date: " + str(data.iloc[data.shape[0] - 1, 0]))


# data_shape(data)

def filter_hours(data):
    return data.loc[:, '0':'23']


def print_settings(file, area, window, start_date, variables_list):
    return '|'.join([file, area, str(window), str(start_date), str(variables_list)])


# counting median and MAD for each hour
def count_median_mad(data):
    data = filter_hours(data)
    median = np.median(data, axis=0)
    mad = stats.median_absolute_deviation(data)
    return median, mad


def standarize(data, median, mad):
    mad = np.tile(mad, (data.shape[0], 1))
    return np.arcsinh((data - np.tile(median, (data.shape[0], 1))) / mad)


def unstandarize(data, median, mad):
    data = np.sinh(data)
    data = data * mad + median
    return data
