import os
import time


class FileDriver:
    def __init__(self, name):
        self.path = f'./entities/{name}-{round(time.time(), 2)}.txt'
        self.exists = os.path.exists(self.path)

        if not os.path.exists('./entities/'):
            os.mkdir('./entities/')

        if not self.exists:
            open(self.path, 'w').close()

    def open(self):
        return open(self.path, 'r')

    def empty(self):
        return os.stat(self.path).st_size == 0

    def write_file(self, text=None):
        file = open(self.path, 'w')
        file.write(text)

        return self
    
    def delete(self):
        os.remove(self.path)
        