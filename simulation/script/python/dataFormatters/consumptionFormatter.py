import os.path
import pandas as pd
from .formatterInterface import FormatterInterface


class ConsumptionFormatter(FormatterInterface):

    def format(self):
        self.setConstants('consumption', '../../data/data_raw/consumption', '../../data/data_processed/{area}/consumption',
                          'consumption-{country}-areas_{year}_hourly.xls',
                          'consumption-{country}-areas_{year}_hourly.csv')

        FormatterInterface.format(self)

    def formatHourly(self, year):
        filePath = self.getFilePath(year)

        if os.path.exists(filePath):
            df = pd.read_excel(filePath, skiprows=[0, 1])
            df.rename(columns={df.columns[0]: "date"}, inplace=True)
            df.rename(columns={df.columns[1]: "hour"}, inplace=True)

            df = self.dff.keepColumnOnly(df, ['date', 'hour'] + self.areas)

            df['hour'] = df.apply(lambda row: row['hour'][:2], axis=1)

            df = self.dff.setColumnType(df, 'hour', 'int32')

            df['date'] = pd.to_datetime(df['date'], dayfirst=True)
            allHolidays = self.getSundays(year) + self.getBankHolidays(year)
            df['holiday'] = df.apply(lambda row: self.setHolidays(row, allHolidays), axis=1)

            for area in self.areas:
                filePathOutput = self.getFilePathOutput(year, area)

                df_area = self.dff.makeCopy(df)
                df_area = df_area.drop(columns=list(set(self.areas) - {area}))

                df_area = self.dff.replaceDecimalSeparator(df_area, area)
                df_area = self.dff.setColumnType(df_area, area, 'float64')
                df_area = self.dff.renameColumn(df_area, area, 'price')
                df_area = df_area.pivot_table(index=['date', 'holiday'], columns='hour', values='price').reset_index()

                df_area.to_csv(filePathOutput, index=False)

                print("Done for file: " + filePathOutput)
