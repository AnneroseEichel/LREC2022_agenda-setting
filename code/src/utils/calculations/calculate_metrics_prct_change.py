#!/usr/bin python
# -*- coding: utf-8 -*-
"""A module to merge to calculate post and word level metrics.
In addition, the percent change of these metrics and RTSI values is calculated for a specified time slice.

This module can be run from the terminal or in combination with the utils modules using the bash script <run_calculations.sh>

NOTE: When calculating percent change, NaNs are replaced with 0 as they indicate a percent change of 0%. 
inf is replaced with 100 as it always indicates that a percent change from 0 in the previous row to some value in the current row occurred.
(percent change: (in-/decrease = (float - 0))// 0 * 100 => inf).
"""
import argparse
import os
import sys
import time
from datetime import timedelta
from pathlib import Path
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
import pandas as pd
from country_groups import COUNTRY_GROUPS

# Monitor time
start_time = time.time()

# Load data
fn_vk = ""
fn_rtsi = ""
time_slice = 0

if len(sys.argv) < 2:
    print(
        "python3 calculate_metrics_prct_change.py \
        <media_posts_processed_final.csv \
        rtsi_topics.xlsx time_slice>"
    )
else:
    fn_vk = sys.argv[1]
    fn_rtsi = sys.argv[2]
    time_slice = int(sys.argv[3])
if time_slice >= 1:
    print(
        "Calculate values for a time slice of " + str(time_slice) + " day(s)."
    )
else:
    print(
        "Invalid time slice: "
        + str(time_slice)
        + ".\nPlease enter a valid time slice > 0."
    )
    sys.exit()
print("Prep time slice " + str(time_slice))

# Prep output
path = Path("code/data/metrics_percent_results/" + str(time_slice) + "days/")
path.mkdir(parents=True, exist_ok=True)

# Load data
data_all = pd.read_csv(
    fn_vk,
    encoding="utf_8",
    sep=",",
    index_col=["date"],
    parse_dates=["date"],
    infer_datetime_format=True,
)
data_all.index = pd.to_datetime(data_all.index, unit="s")

rtsi = pd.read_excel(
    fn_rtsi,
    usecols="A,C",
    index_col=[0],
    parse_dates=[0]
)

# Partition data into free and control
tass = data_all[data_all.ID.astype(str).str.contains("-26284064")]
rt = data_all[data_all.ID.astype(str).str.startswith("-40316705")]
control = pd.concat([tass, rt])

meduza = data_all[data_all.ID.astype(str).str.startswith("-76982440")]
rbc = data_all[data_all.ID.astype(str).str.startswith("-25232578")]
free = pd.concat([meduza, rbc])
subcorpora = [control, free]

# Calculate percent change of RTSI for a given time slice
# For each subcorpus:
# - Calculate post and word level metrics for each country
# - Calculate the percent change of these metrics for each country
countries = list(COUNTRY_GROUPS.keys())
results = []
for corpus in subcorpora:
    # RTSI prep
    rtsi.reset_index(inplace=True)
    d = {"date": "last", "close": "sum"}
    res = rtsi.groupby(rtsi.index // time_slice).agg(d)
    res.set_index("date", inplace=True)
    rtsi.set_index("date", inplace=True)

    # Calculate percent change of RTSI
    res["rtsi"] = res["close"]
    res["rtsi_pct"] = res["close"].pct_change() * 100

    # Prep for correlation calculation
    cov_psts = res.copy(deep=True)
    cov_wrds = res.copy(deep=True)

    # Get number of total posts and words per time slice
    num_posts = []
    num_words = []
    start_date = rtsi.index.min()
    end_date = rtsi.index.min()
    final_date = rtsi.index.max() + timedelta(days=1)

    # Account for time slices > 1 day
    if time_slice > 1:
        end_date = end_date + timedelta(days=time_slice - 1)

    while start_date < final_date:
        # Convert to searchable type
        start_date_searchable = str(start_date.date())
        end_date_searchable = str(end_date.date())

        # Count all posts per day
        num_posts.append(
            corpus.loc[start_date_searchable:end_date_searchable]
            .ID.value_counts()
            .sum()
        )
        # Count all words per post
        corpus["num_words"] = corpus["text"].str.split().str.len()
        num_words.append(
            corpus.loc[start_date_searchable:end_date_searchable]
            .num_words.sum()
            .astype("float")
        )
        start_date = start_date + timedelta(days=time_slice)
        end_date = end_date + timedelta(days=time_slice)

    for country in countries:
        # Add country variable
        res[country + "_name"] = country

        # Reset vars
        country_posts = []
        country_words = []
        country_mentions = []
        temp = corpus.loc[corpus[country] >= 1]
        start_date = rtsi.index.min()
        end_date = rtsi.index.min()
        final_date = rtsi.index.max() + timedelta(days=1)

        # Account for time slices > 1 day
        if time_slice > 1:
            end_date = end_date + timedelta(days=time_slice - 1)

        while start_date < final_date:
            start_date_searchable = str(start_date.date())
            end_date_searchable = str(end_date.date())
            # Count posts per country on a day
            country_posts.append(
                temp.loc[start_date_searchable:end_date_searchable]
                .ID.value_counts()
                .sum()
                .astype("float")
            )
            # Count words per country on a day
            country_words.append(
                temp.loc[start_date_searchable:end_date_searchable]
                .text.str.split()
                .str.len()
                .sum()
                .astype("float")
            )
            # Count occurrences of country as a string per day, e.g. U.S.
            country_mentions.append(
                temp.loc[start_date_searchable:end_date_searchable][
                    country
                ].sum()
            )
            start_date = start_date + timedelta(days=time_slice)
            end_date = end_date + timedelta(days=time_slice)

        # Get normalized # of country coverage on post level per day per country
        country_pst_norm = np.divide(country_posts, num_posts)
        res[country + " pst_pct_norm"] = country_pst_norm
        # Interim results for calculating DAILY correlations:
        # Normalized absolute values needed
        cov_psts[country + "_psts"] = country_pst_norm
        # Calculate percent changes
        res[country + "_psts"] = country_pst_norm
        res[country + " pst_pct_norm"] = (
            res[country + " pst_pct_norm"].pct_change() * 100
        )

        # Get normalized # of country coverage on word level per day per country
        country_words_norm = np.divide(country_mentions, num_words)
        res[country + " wrd_pct_norm"] = country_words_norm
        # Interim results for calculating DAILY correlations: normalized absolute values needed
        cov_wrds[country + "_wrds"] = country_words_norm
        # Calculate percent change
        res[country + " wrd_pct_norm"] = (
            res[country + " wrd_pct_norm"].pct_change() * 100
        )

    # Convert NaN to 0 and inf to 100
    res.replace([np.inf, -np.inf], 100.0, inplace=True)
    res.fillna(0, inplace=True)
    cov_psts.fillna(0, inplace=True)
    cov_wrds.fillna(0, inplace=True)

    # Store result of given subcorpus
    results.append(res)
    results.append(cov_psts)
    results.append(cov_wrds)
    del res

# Add status as a column to each subcorpus
# Codes: control == 0, free == 1
results[0]["status"] = 0
results[1]["status"] = 0
results[2]["status"] = 0

results[3]["status"] = 1
results[4]["status"] = 1
results[5]["status"] = 1

# Save results as CSV files.
for i in range(0, 6):
    fn = ""
    if i == 0:
        fn = "control_pct_change_all_"
    elif i == 1:
        fn = "control_pst_all"
    elif i == 2:
        fn = "control_wrd_all"
    elif i == 3:
        fn = "free_pct_change_all_"
    elif i == 4:
        fn = "free_pst_all"
    elif i == 5:
        fn = "free_wrd_all"
    else:
        print("Something went wrong. Please try again.")
    results[i].to_csv(
        str(path)
        + "/"
        + str(fn)
        + str(time_slice)
        + ".csv",
        encoding="utf-8",
    )

# Create individual country CSV files with all country coverage values and status.
# Save each country table in control and free version as .csv file
path_countries = Path("code/data/metrics_percent_results/" + str(time_slice) + "days/countries/")
path_countries.mkdir(parents=True, exist_ok=True)

results_country = {}
pct_changed = [results[0], results[3]]

for country in countries:
    results_country[country] = []
    for subcorpus in pct_changed:
        # Select columns of a given country
        res_country = pd.DataFrame(subcorpus["rtsi_pct"])
        res_country["rtsi"] = pd.DataFrame(subcorpus["rtsi"])
        country_cols = [col for col in subcorpus.columns if country in col]
        res_country[country_cols] = subcorpus[country_cols]
        # Remove country prefix
        res_country.rename(
            columns={country + "_name": "country"}, inplace=True
        )
        res_country.rename(
            columns={country + " pst_pct_norm": "post"}, inplace=True
        )
        res_country.rename(
            columns={country + " wrd_pct_norm": "word"}, inplace=True
        )
        res_country.rename(
            columns={country + "_psts": "abs_posts"}, inplace=True
        )
        # Assign status of given subcorpus to given country
        res_country["status"] = subcorpus["status"]
        # Add country to corpus frame with all countries and stati
        results_country[country].append(res_country)
        # Save each country as individual .csv file
        # Save results as CSV files.
        if subcorpus["status"].astype(str).str.contains("0").any():
            res_country.to_csv(
                str(path_countries)
                + "/"
                + country
                + "_control"
                + str(time_slice)
                + ".csv",
                encoding="utf-8",
            )
        else:
            res_country.to_csv(
                str(path_countries)
                + "/"
                + country
                + "_free"
                + str(time_slice)
                + ".csv",
                encoding="utf-8",
            )

print("Time consumption prep: --- %s seconds ---" % (time.time() - start_time))
