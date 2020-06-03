from simulation.script.python.forecasting.helpers import *
import pandas as pd
import numpy as np


class VariablesGetter:

    def __init__(self, data, area, variables_list):
        self.data = data
        self.area = area
        self.variables_list = variables_list
        self.dir_file = "../../../data/data_sanitized/"
        self.dir_data = '../../../data/'

    # get variables -n days

    # types of variables
    # each_hour - for each our and for day (1,24)
    # each_day - for each day (1,1)
    def get_variables_prev_day(self, n=1):
        data_copy = filter_hours(self.data)
        d = pd.DataFrame(np.zeros((n, len(data_copy.columns))))
        d.columns = data_copy.columns
        d = d.append(data_copy)
        d = d.reset_index(drop=True)
        d = d.drop(d.tail(n).index)
        return "each_hour", d

    def get_variables_holidays(self):
        days_file = self.dir_data + 'days.csv'
        holidays = pd.read_csv(days_file)
        holidays = holidays['holiday']
        return "each_day", holidays

    def get_variables_dayofweek(self):
        days_file = self.dir_data + 'days.csv'
        dayofweek = pd.read_csv(days_file)
        dayofweek['date'] = pd.to_datetime(dayofweek['date'], format='%Y-%m-%d')
        dayofweek = dayofweek['date'].dt.dayofweek
        var_dayofweek = np.zeros((dayofweek.shape[0], 7))
        for i in range(0, 7):
            var_dayofweek[:, i] = dayofweek == i
        return "each_day", var_dayofweek

    def get_variables_prognosis(self, prognosis_name):
        file_name = prognosis_name + '_' + self.area + '.csv'

        data = pd.read_csv(self.dir_file + file_name)
        data = filter_hours(data)

        return data

    def get_variables_consumption_prognosis(self):
        return "each_hour", self.get_variables_prognosis('consumption')

    def get_variables_wind_power_prognosis(self):
        return "each_hour", self.get_variables_prognosis('wind_power')

    def get_variables(self):
        variables = []
        for key in self.variables_list:
            if key == 'prev_day1':
                v = self.get_variables_prev_day(1)
            elif key == 'prev_day2':
                v = self.get_variables_prev_day(2)
            elif key == 'prev_day7':
                v = self.get_variables_prev_day(7)
            elif key == 'dayofweek':
                v = self.get_variables_dayofweek()
            elif key == 'holidays':
                v = self.get_variables_holidays()
            elif key == 'consumption_prognosis':
                v = self.get_variables_consumption_prognosis()
            variables.append(v)
        return variables
