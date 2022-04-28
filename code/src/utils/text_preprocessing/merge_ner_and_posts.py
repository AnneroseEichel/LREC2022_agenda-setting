#!/usr/bin python
# -*- coding: utf-8 -*-
"""A module to merge the collapsed country labels and preprocessed posts.

In more detail, this module is used to merge
- the collapsed country labels from the module <merge_labels.py> and
- the preprocessed posts from <preprocess_labels.py>
to have all data together to study agenda-setting.
"""
import argparse
import sys
import time

import pandas as pd
import numpy as np

from country_groups import COUNTRY_GROUPS

start_time = time.time()
print("Executing merge NER and posts")

# Global variables
global vk, ner

# Load data
parser = argparse.ArgumentParser(description="Merge country labels and posts.")
parser.add_argument("-d", "--debug", help="Debugging output", action="store_true")
parser.add_argument("--input", nargs= "+", type=argparse.FileType("r"), help="Input CSV files")
parser.add_argument("--output", type=argparse.FileType("wb"), help="Output CSV file")
args = parser.parse_args()

fn_vk = args.input[0].name
fn_ner = args.input[1].name
print("Processing input files: " + fn_vk + ", " + fn_ner)

try:
    vk = pd.read_csv(
        fn_vk,
        encoding="utf-8",
        sep=",",
        parse_dates=[4],
        infer_datetime_format=True
    )
    vk["date"] = pd.to_datetime(vk["date"], unit="s")
    vk["ID"] = vk["ID"].str.replace("_", "", regex=True).astype("int64")
except IOError as io_error:
    print(io_error)

try:
    ner = pd.read_csv(fn_ner, encoding="utf-8", sep=",")
    ner.set_index("ID", inplace=True)
except IOError as io_error:
    print(io_error)

# Prepare collapsed labels by imploding them back to frames with row of unique IDs
collapsed_large = ner[["GPE_COUNTRY", "COL_GPE_COUNTRY"]]
collapsed = pd.DataFrame(
    collapsed_large.groupby(collapsed_large.index).GPE_COUNTRY.agg(list)
)
collapsed["COL_GPE_COUNTRY"] = collapsed_large.groupby(
    collapsed_large.index
).COL_GPE_COUNTRY.agg(list)

# Merge the two DataFrames back into one
collapsed = collapsed.reset_index()
m1 = list(vk["ID"])
m2 = list(collapsed["ID"])
m3, m4 = [], []
for ID in m1:
    if ID in m2:
        row_number = collapsed[collapsed["ID"] == ID].index[0]
        m3.append(collapsed.at[row_number, "GPE_COUNTRY"])
        m4.append(collapsed.at[row_number, "COL_GPE_COUNTRY"])
    else:
        m3.append(np.NaN)
        m4.append(np.NaN)

vk["GPE_COUNTRY"] = m3
vk["COL_GPE_COUNTRY"] = m4

# Monitor country mentions per post
merged = pd.DataFrame(vk["COL_GPE_COUNTRY"])
merged = merged.explode("COL_GPE_COUNTRY")
for country in COUNTRY_GROUPS:
    merged.loc[
        merged["COL_GPE_COUNTRY"].str.contains(country, na=False), country,
    ] = 1

for country in COUNTRY_GROUPS:
    vk[country] = merged.groupby(merged.index).agg({country: "sum"})

# Set date as date time index and sort merged DataFrame in ascending order
vk = vk.sort_values(by="date")
vk = vk.set_index(pd.DatetimeIndex(vk["date"]))

# Add a column "status" with value 0 if post comes from TASS or RT.
# Add a column "status" with value 1 if post comes from RBC or Meduza
# Note: -26284064: TASS, -403167058: RussiaToday, -76982440: Meduza, -25232578: RBC.
vk.loc[vk.ID.astype(str).str.startswith("-26284064"), "status"] = 0
vk.loc[vk.ID.astype(str).str.startswith("-40316705"), "status"] = 0
vk.loc[vk.ID.astype(str).str.startswith("-76982440"), "status"] = 1
vk.loc[vk.ID.astype(str).str.startswith("-25232578"), "status"] = 1

# Save as CSV file
vk.to_csv(args.output.name, index=False)

print(
    "Time consumption of final merging: --- %s seconds ---" % (time.time() - start_time)
)

