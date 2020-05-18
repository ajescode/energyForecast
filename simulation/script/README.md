Modelling and forecasting electricity price and demand
========================================

Steps to obtain data to calculations.

1. Download desired data from Nordpool webpage
https://www.nordpoolgroup.com/historical-market-data/

Script support data currently for:
 - Elspot price
 - Wind power
 - Wind power prognosis
 - Consumption
 - Consumption prognosis
 
2. Run python/main.py script with parameters suitable for selected country (default is Denmark).

3. Run merge_files/merge_files.py script in order to merge all year data into one file.