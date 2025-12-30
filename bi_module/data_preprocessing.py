import pandas as pd
import numpy as np


def scd1():
    return new_names[np.random.randint(len(new_names))]


def scd2():
    return new_locations[np.random.randint(len(new_locations))]

df = pd.read_csv("file_storage/original_data.csv")

new_names = ["A", "B", "C", "D", "E", "F", "G", "H"]
new_locations = ["North-West", "North-East", "South-West", "South-East", "North"]

df_sample_copies = df.sample(200).drop_duplicates(subset=["Row ID"])

df_sample_dcp1 = df.sample(200).drop_duplicates(subset=["Row ID"])
df_sample_dcp1["Customer Name"] = df_sample_dcp1["Customer Name"].apply(lambda x: scd1())
df_sample_dcp1 = df_sample_dcp1.drop_duplicates()                                                                                                             

df_sample_dcp2 = df.sample(200).drop_duplicates(subset=["Row ID"])
df_sample_dcp2["Region"] = df_sample_dcp2["Region"].apply(lambda x: scd2())
df_sample_dcp2 = df_sample_dcp2.drop_duplicates()

df_sample_combinative = df.sample(200).drop_duplicates(subset=["Row ID"])
df_sample_combinative["Customer Name"] = df_sample_combinative["Customer Name"].apply(lambda x: scd1())
df_sample_combinative["Region"] = df_sample_combinative["Region"].apply(lambda x: scd2())
df_sample_combinative = df_sample_combinative.drop_duplicates()

df_concatenated = pd.concat([df_sample_copies,df_sample_dcp1, df_sample_dcp2, df_sample_combinative]).drop_duplicates(subset=["Row ID"])
df_concatenated.to_csv("csv_files/secondary_data.csv", index=False)
