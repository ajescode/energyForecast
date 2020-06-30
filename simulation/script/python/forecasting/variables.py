from simulation.script.python.forecasting.helpers import *
import pandas as pd
import numpy as np
import re


class VariablesGetter:

    def __init__(self, file, data, area, variables_list, start_date, end_date, method, window):
        self.data = data
        self.area = area
        self.file = file
        self.method = method
        self.window = window
        self.variables_list = variables_list
        self.dir_file = "../../../data/data_sanitized/"
        self.dir_data = '../../../data/'
        self.dir_forecasts = '../../../data/forecasts/'
        self.start_date = start_date
        self.end_date = end_date

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
        return "each_hour", d, get_standarize_method(self.file)

    def get_variables_holidays(self):
        days_file = self.dir_data + 'days.csv'
        holidays = pd.read_csv(days_file)
        holidays = holidays['holiday']
        return "each_day", holidays, get_standarize_method()

    def get_variables_dayofweek(self):
        days_file = self.dir_data + 'days.csv'
        dayofweek = pd.read_csv(days_file)
        dayofweek['date'] = pd.to_datetime(dayofweek['date'], format='%Y-%m-%d')
        dayofweek = np.where(dayofweek['holiday'] == 1, 6, dayofweek['date'].dt.dayofweek)

        var_dayofweek = np.zeros((dayofweek.shape[0], 7))
        for i in range(0, 7):
            var_dayofweek[:, i] = dayofweek == i
        return "each_day", var_dayofweek, get_standarize_method()

    def get_variables_max_day(self):
        dc = filter_hours(self.data)
        dc['max'] = dc.max(axis=1)
        d = np.zeros((1, 1))
        d = np.append(d, dc[['max']])
        return "each_day", d[:-1], get_standarize_method(self.file)

    def get_variables_min_day(self):
        dc = filter_hours(self.data)
        dc['min'] = dc.min(axis=1)
        d = np.zeros((1, 1))
        d = np.append(d, dc[['min']])
        return "each_day", d[:-1], get_standarize_method(self.file)

    def get_variables_last_val_day(self):
        df = filter_hours(self.data)
        d = np.zeros((1, 1))
        d = np.append(d, df[['23']])
        return "each_day", d[:-1], get_standarize_method(self.file)

    def get_variables_prognosis(self, prognosis_name):
        file_name = prognosis_name + '_prognosis_' + self.area + '.csv'

        data = pd.read_csv(self.dir_file + file_name)
        data = filter_hours(data)

        return "each_hour", data, get_standarize_method(prognosis_name)

    def get_variables_consumption_prognosis(self):
        return self.get_variables_prognosis('consumption')

    def get_variables_wind_prognosis(self):
        return self.get_variables_prognosis('wind')

    # variables for price model 5
    def get_variables_prognosis_for_price(self, prognosis_name):
        file_name = prognosis_name + '_prognosis_' + self.area + '.csv'
        data = pd.read_csv(self.dir_file + file_name)
        data = filter_hours(data)

        forecasts_file = self.dir_forecasts + prognosis_name + '/files.txt'

        if prognosis_name == 'wind':
            vars_a = ['dayofweek', 'wind_prognosis', 'prev_day1', 'prev_day2', 'prev_day7', 'consumption_prognosis']
        else:
            vars_a = ['dayofweek', 'consumption_prognosis', 'prev_day1', 'prev_day2', 'prev_day7', 'wind_prognosis']

        forecast_file = None
        with open(forecasts_file, 'r+') as f:
            lines = f.read().splitlines()
            for line in lines:
                if line.find(print_settings(prognosis_name, self.area, self.window, self.start_date, self.end_date,
                                            self.method, vars_a)) != -1:
                    forecast_file = line.split('.', 1)[0] + '.csv'
                    break

        if forecast_file:
            data_forecast = pd.read_csv(self.dir_forecasts + prognosis_name + '/' + forecast_file)
            start_index = data_forecast.iloc[0, 0]
            last_index = data_forecast.iloc[-1, 0]
            data.loc[start_index:last_index, '0':'23'] = data_forecast.loc[:, '0':'23'].values
        else:
            print('No prognosis for price')

        return "each_hour", data, get_standarize_method(prognosis_name)

    def get_variables_consumption_prognosis_for_price(self):
        return self.get_variables_prognosis_for_price('consumption')

    def get_variables_wind_prognosis_for_price(self):
        return self.get_variables_prognosis_for_price('wind')

    def get_variables(self):
        variables = []
        for key in self.variables_list:
            if key == 'prev_day1':
                v = self.get_variables_prev_day(1)
            elif key == 'prev_day2':
                v = self.get_variables_prev_day(2)
            elif key == 'prev_day7':
                v = self.get_variables_prev_day(7)
            elif key == 'max_day':
                v = self.get_variables_max_day()
            elif key == 'min_day':
                v = self.get_variables_min_day()
            elif key == 'last_val_day':
                v = self.get_variables_last_val_day()
            elif key == 'dayofweek':
                v = self.get_variables_dayofweek()
            elif key == 'holidays':
                v = self.get_variables_holidays()
            elif key == 'consumption_prognosis':
                v = self.get_variables_consumption_prognosis()
            elif key == 'consumption_prognosis_for_price':
                v = self.get_variables_consumption_prognosis_for_price()
            elif key == 'wind_prognosis':
                v = self.get_variables_wind_prognosis()
            elif key == 'wind_prognosis_for_price':
                v = self.get_variables_wind_prognosis_for_price()
            variables.append(v)
        return variables
