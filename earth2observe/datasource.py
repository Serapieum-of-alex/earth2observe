from abc import ABC, abstractmethod


class DataSource:

    @abstractmethod
    def download(self):
        pass