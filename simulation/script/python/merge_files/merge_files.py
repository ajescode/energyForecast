import os
import glob
import pandas as pd

directoryInput = '../../../data/data_processed/{area}/{name}'
directoryOutput = '../../../../data/data_merged'
fileNameOutput = '{name}_{area}.csv'
extension = 'csv'

names = {'price', 'wind', 'wind_prognosis', 'consumption', 'consumption_prognosis'}
areas = {'DK1', 'DK2'}

baseDirectory = os.getcwd()

for name in names:
    for area in areas:
        formatDict = {'name': name, 'area': area}
        directory = directoryInput.format(**formatDict)
        filePathOutput = directoryOutput + '/' + fileNameOutput.format(**formatDict)
        if os.path.exists(directory):
            os.chdir(directory)

            all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
            all_filenames.sort()

            if all_filenames:
                # combine all files in the list
                combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames])

                combined_csv = combined_csv.groupby(['date']).sum().reset_index()

                # export to csv
                combined_csv.to_csv(filePathOutput, index=False,
                                    encoding='utf-8-sig')

                print("Done for file: " + filePathOutput)

            os.chdir(baseDirectory)
        else:
            print("Not found: " + directory)
