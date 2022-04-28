#!/usr/bin python
# -*- coding: utf-8 -*-
"""A module to collapse NER results into 15 country labels.

In more detail, this module is used to process the NER results obtained
from the module <ner.py>. Specifically, the identified country mentions
are collapsed into 15 country and country group labels.

For a translation of the country groups, see Table 1 and Appendix A.1.
"""
import argparse
import re
import time

import pandas as pd

from country_groups import COUNTRY_GROUPS


def get_unique_names(df):
    """
    A method to retrieve a set of unique country names.
    :param df: A pandas DataFrame df containing at least
    -  a column 'GPE_COUNTRY'
    :return: A set flattened which contains unique
    """
    df.dropna(subset=["GPE_COUNTRY"], inplace=True)
    gpe_country = df["GPE_COUNTRY"]
    unique = set(gpe_country.explode().unique())
    unique = [x.split() for x in unique]
    flattened = [val.lower() for sublist in unique for val in sublist]
    return set(flattened)


def get_country_mention_counts(df):
    """
    A method to retrieve the number of times a country is mentioned
    :param df: A pandas DataFrame df containing at least
    -  a column 'GPE_COUNTRY'
    :return: A pandas DataFrame counts of country mentions with
    corresponding counts.
    """
    df.dropna(subset=["GPE_COUNTRY"], inplace=True)
    gpe_country = df["GPE_COUNTRY"]
    counts = pd.DataFrame(gpe_country.explode().value_counts(dropna=False))
    return counts


if __name__ == "__main__":

    # Monitor time
    start_time = time.time()

    # Load data
    parser = argparse.ArgumentParser(description="Merge NER results into country labels.")
    parser.add_argument("-d", "--debug", help="Debugging output", action="store_true")
    parser.add_argument("--input", type=argparse.FileType("r"), help="Input JSON file")
    parser.add_argument("--output", type=argparse.FileType("wb"), help="Output CSV file")
    args = parser.parse_args()

    print("Processing input file: " + args.input.name)

    ner = pd.read_json(args.input.name, orient="index", dtype=False)
    ner.GPE_COUNTRY = ner.GPE_COUNTRY.fillna("")
    ner["GPE_COUNTRY"] = ner["GPE_COUNTRY"].map(lambda x: list(map(str.lower, x)))

    # Prepare NER results
    ner_exploded = ner.explode("GPE_COUNTRY")
    # Group labels in NER results
    for country in COUNTRY_GROUPS:  # Go through labels to collapse to
        for name in COUNTRY_GROUPS.get(country):  # Iterate through corresponding named entities
            ner_exploded.loc[ner_exploded["GPE_COUNTRY"].str.contains(name.lower(), regex=True, flags=re.IGNORECASE,
                na=False), "COL_GPE_COUNTRY",] = country

    # Drop all posts with country mentions numbers < 2
    ner_exploded.dropna(subset=["COL_GPE_COUNTRY"], inplace=True)
    ner_exploded.reset_index(inplace=True)
    ner_exploded.rename(columns={"index": "ID"}, inplace=True)

    # Save to CSV file
    ner_exploded.to_csv(args.output.name, index=False)
    print("Results saved to output file: " + args.output.name)

    print("Time consumption collapsing labels: --- %s seconds ---" % (time.time() - start_time))
