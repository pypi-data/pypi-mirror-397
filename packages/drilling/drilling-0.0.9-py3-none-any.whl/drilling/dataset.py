import pandas as pd

class Dataset:
    def __init__(self, dataframe: pd.DataFrame = pd.DataFrame()):
        self.dataframe = dataframe

    def get_data(self):
        return self.dataframe