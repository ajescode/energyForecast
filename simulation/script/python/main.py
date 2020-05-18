from dataFormatters.priceFormatter import PriceFormatter
from dataFormatters.consumptionFormatter import ConsumptionFormatter
from dataFormatters.consumptionPrognosisFormatter import ConsumptionPrognosisFormatter
from dataFormatters.windFormatter import WindFormatter
from dataFormatters.windPrognosisFormatter import WindPrognosisFormatter

fileNameDict = {'price_country': 'dkk',
                'country': 'dk',
                'holidays_country': 'dk'}

areas = ['DK1', 'DK2']

formatters = []
formatters.append(ConsumptionFormatter([2016, 2017, 2018, 2019, 2020], areas, fileNameDict))
formatters.append(ConsumptionPrognosisFormatter([2016, 2017, 2018, 2019, 2020], areas, fileNameDict))
formatters.append(WindFormatter([2016, 2017, 2018, 2019, 2020], areas, fileNameDict))
formatters.append(WindPrognosisFormatter([2016, 2017, 2018, 2019, 2020], areas, fileNameDict))
formatters.append(PriceFormatter([2016, 2017, 2018, 2019, 2020], areas, fileNameDict))

for formatter in formatters:
    formatter.format()
