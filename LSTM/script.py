#!/usr/bin/env python3
import json
import Dataset
ds = Dataset("./Maritius_AOI_20200701_0731_full.csv")
df = ds.df


for mmsi in df.MMSI.unique():
     ship_dict = df[df["MMSI"]==mmsi].to_dict(orient="records")
     ship_file = open("./Jsons/{}.json".format(mmsi), "w")
     json.dump(ship_dict, ship_file, indent=4)
