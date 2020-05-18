# from dataFormatters.consumptionFormatter import ConsumptionFormatter
# from dataFormatters.consumptionPrognosisFormatter import ConsumptionPrognosisFormatter
from dataFormatters.priceFormatter import PriceFormatter

# from dataFormatters.windPowerFormatter import WindPowerFormatter
# from dataFormatters.windPowerPrognosisFormatter import WindPowerPrognosisFormatter

fileNameDict = {"country": "dkk",
                "holidays_country": "dk"}

areas = ['DK1', 'DK2']

formatters = []
# formatters.append(ConsumptionFormatter("dk", [2016, 2017, 2018, 2019], True, True, 'xls', 'csv'))
# formatters.append(ConsumptionPrognosisFormatter("dk", [2016, 2017, 2018, 2019], False, True, 'xls', 'csv'))
formatters.append(PriceFormatter([2016, 2017, 2018, 2019, 2020], areas, fileNameDict))
# formatters.append(WindPowerFormatter("dk", [2016, 2017, 2018, 2019], True, True, 'xls', 'csv'))
# formatters.append(WindPowerPrognosisFormatter("dk", [2016, 2017, 2018, 2019], False, True, 'xls', 'csv'))

for formatter in formatters:
    formatter.format()
