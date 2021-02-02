#!/usr/bin/env python3
import pandas as pd
import numpy as np
LOOK_BACK = 5
class Dataset:
    def __init__(self, path="./split_aa.csv"): # ./Wakashio_20200725_1200_1800.csv"):
        self.load_from_csv(path)
        self.clean()
        self.augment()
    def load_from_csv(self, path_to_csv):
        self.df = pd.read_csv(path_to_csv)

    def clean(self):
        self.df["SOG"].dropna()
        self.df.sort_values(by=['# Timestamp'], inplace=True, kind = "mergesort")
        self.df.sort_values(by=['MMSI'], inplace=True, kind = "mergesort")
        self.df = self.df.replace(np.NaN,0)
        # self.df = self.df.join(pd.get_dummies(self.df["Type of mobile"]))
        self.Xs = []
        for x in self.df.MMSI.unique():
            self.Xs.append(np.array(self.df[self.df["MMSI"]==x][["Latitude","Longitude", "ROT", "SOG", "COG","Heading"]]))
        self.Xs=np.array(self.Xs)
        # self.df.replace(np.nan,0)
        # self.df.replace(np.NAN,0)
    def augment(self):
        # TODO list all relevant columns
        pass

    def plot():
        pass
