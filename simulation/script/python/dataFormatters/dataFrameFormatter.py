class DataFrameFormatter:

    def replaceDecimalSeparator(self, df, columnName):
        df[columnName] = df.apply(lambda row: str(row[columnName]).replace(',', '.'), axis=1)
        return df

    # int32
    def setColumnType(self, df, columnName, columnType):
        return df.astype({columnName: columnType})

    def dropColumn(self, df, columnName):
        return df.drop(columns=[columnName])

    def renameColumn(self, df, oldName, newName):
        df[newName] = df[oldName]
        return df

    def keepColumnOnly(self, df, columnArray):
        return df[columnArray]

    def makeCopy(self, df):
        return df.copy()
