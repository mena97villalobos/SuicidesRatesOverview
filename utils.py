import plotly.express as px
from constants import *


def create_graph_bar(dataFrame, xAxisColumnName, yAxisColumnName):
    return px.bar(
        dataFrame,
        x=xAxisColumnName,
        y=yAxisColumnName,
        barmode='stack',
        color=xAxisColumnName
    )


def get_unique_column_values(dataFrame, columnName):
    return dataFrame[columnName].unique()


class DataHolder:

    def __init__(self, originalData, original_year_range: list):
        self.originalData = originalData
        self.currentYearsSelected = original_year_range
        self.originalYearRange = original_year_range
        self.yearFilteredData = originalData

    def get_filtered_data(self, year_range: list):
        if self.originalYearRange == year_range:
            self.currentYearsSelected = year_range
            return self.originalData
        elif self.year_changed(year_range):
            self.yearFilteredData = \
                self.originalData[self.originalData[YEAR].isin(range(year_range[0], year_range[1] + 1))]
            self.currentYearsSelected = year_range
        return self.yearFilteredData

    def year_changed(self, year_range):
        current_year = self.currentYearsSelected
        return not (current_year[0] == year_range[0] and current_year[1] == year_range[1])
