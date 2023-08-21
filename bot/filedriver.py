import os
import time

import pandas as pd


class FileDriver:
    def __init__(self, name):
        self.path = f'./entities/{name}-{round(time.time(), 2)}.xlsx'
        self.exists = os.path.exists(self.path)

        if not os.path.exists('./entities/'):
            os.mkdir('./entities/')

        if not self.exists:
            open(self.path, 'w').close()

    def empty(self):
        return os.stat(self.path).st_size == 0
    
    '''
    def open(self):
        return open(self.path, 'r')

    def write_file(self, text=None):
        file = open(self.path, 'w')
        file.write(text)

        return self
    '''

    def make_excel(self, df: pd.DataFrame):
        df.to_excel(self.path)

        return self

    def delete(self):
        os.remove(self.path)
        