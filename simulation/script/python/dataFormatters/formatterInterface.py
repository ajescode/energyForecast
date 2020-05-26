from abc import abstractmethod
from datetime import date, timedelta
from .dataFrameFormatter import DataFrameFormatter


class FormatterInterface:
    def __init__(self, years, areas, fileNameDict=None):
        self.years = years  # array
        self.areas = areas
        self.holidaysPathFile = "../../data/holidays/bank_holidays_{holidays_country}_{year}.txt"
        if fileNameDict is None:
            fileNameDict = {}
        self.fileNameDict = fileNameDict
        self.dff = DataFrameFormatter()

    def setConstants(self, name, directorySource, directoryDestination, fileFormatSource, fileFormatDestination):
        self.name = name
        self.directorySource = directorySource
        self.directoryDestination = directoryDestination
        self.fileFormatSource = fileFormatSource
        self.fileFormatDestination = fileFormatDestination

    def format(self):
        for year in self.years:
            self.formatHourly(year)

    @abstractmethod
    def formatHourly(self, year):
        pass

    def getBankHolidays(self, year):
        fileNameDict = dict(self.fileNameDict)
        fileNameDict['year'] = str(year)
        file = open(self.holidaysPathFile.format(**fileNameDict), "r")
        return file.read().split(',')

    def getSundays(self, year):
        d = date(year, 1, 1)
        d += timedelta(days=6 - d.weekday())
        list = []
        while d.year == year:
            list.append(str(d))
            d += timedelta(days=7)
        return list

    def setHolidays(self, row, allSundays):
        if row['date'].strftime("%Y-%m-%d") in allSundays:
            return 1
        else:
            return 0

    def getFilePath(self, year):
        filePath = self.formatFilePath()

        fileNameDict = dict(self.fileNameDict)
        fileNameDict['year'] = str(year)
        filePath = filePath.format(**fileNameDict)

        return filePath

    def getFilePathOutput(self, year, area=None):
        filePath = self.formatFilePath(True)

        fileNameDict = dict(self.fileNameDict)
        fileNameDict['year'] = str(year)
        fileNameDict['area'] = area

        filePath = filePath.format(**fileNameDict)

        return filePath

    def formatFilePath(self, output=False):
        if output:
            directory = self.directoryDestination
            file = self.fileFormatDestination
        else:
            directory = self.directorySource
            file = self.fileFormatSource

        return directory + '/' + file