#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A module to apply NER on Russian text.

In more detail, this module is used to perform NER on the text of
posts from the non-annotated VK corpus.

Note that APIs such as the Texterra API allow for 60 requests/hour and
restrict the size of the batches to process. Hence, plan at least 4-5h
to run this script for the ~15,000 posts of the VK corpus.

For more information on the Texterra REST API see:
https://www.ispras.ru/technologies/texterra/ (Russian only)
(last accessed: 2022-27-04)
"""
import argparse
import json
import time
import pandas as pd

import texterra

from texterra_token import TOKEN


def ner(data):
    """
    A method to access the Texterra API to perform NER.
    As a requirement, a valid token TOKEN is needed
    (cf. https://texterra.ispras.ru/).

    Note: If no results could be retrieved for a given post ID,
    the ID and its corresponding empty results dictionary
    will nevertheless be included in the ner_results.json.

    :param data: A pandas DataFrame at least containing a column "ID"
     with unique post IDs and "text" with strings of (preprocessed) text.
    :return: A nested dictionary containing the NER results for each
    unique post ID.
    """
    # Initialize variables
    texts = list(data["text"])
    ids = list(data["ID"])
    n = 100  # Batch size to satisfy requirements of the API
    text_batches = [texts[i * n: (i + 1) * n] for i in range((len(texts) + n - 1) // n)]
    id_batches = [ids[i * n: (i + 1) * n] for i in range((len(ids) + n - 1) // n)]
    ner_all = {}
    counter = 0

    # Access Texterra API
    ispras_texterra = texterra.API(TOKEN)

    # Batch-wise call of API
    for batch in text_batches:
        if ispras_texterra is not None:
            ner_helper = ner_api_call_helper(ispras_texterra, batch, id_batches[counter])
            ner_all.update(ner_helper)
            print("Batch " + str(counter) + " done.")
            # Timer implemented to satisfy the requirements of API:
            # Number of calls per hour <= 60
            time.sleep(61)
            counter = counter + 1
        else:
            print("An error occurred which is most likely due"
                  "to the absence of a valid Texterra token.\n"
                  "Please get a valid token, place it into file texterra.py, and try again.")
    print("All batches done.")
    return ner_all


def ner_api_call_helper(texterra_api, data, ids):
    """
    A helper method to store the results sent back from the Texterra API.

    :param texterra_api: Texterra API access.
    :param data: A portion of a pandas DataFrame containing at least
    - a column "ID" with unique post IDs
    - a column "text" with strings of (preprocessed) text (in Russian)
     with a batch size of n.
    :param ids: A "controller" batch of unique post IDs to be processed
    in this batch.
    :return: A dictionary ner_dict containing the unique post IDs and
    corresponding NER results for the posts in a given batch.
    """
    ner_dict = {}
    ner_from_text = texterra_api.named_entities(data, rtype="full",
        language="ru")  # Access the Texterra REST API and request NER results
    k = 0
    # Process and store results batch-wise
    for elem in ner_from_text:
        ner_dict_helper = {}
        for entry in elem:
            column_name = entry[3]
            if column_name in ner_dict_helper:
                ner_dict_helper[column_name].append("{}".format(entry[2]))
            else:
                ner_dict_helper.update({column_name: ["{}".format(entry[2])]})
        if ids[k] not in ner_dict:
            ner_dict.update({ids[k]: ner_dict_helper})
        k = k + 1

    return ner_dict


if __name__ == "__main__":
    # Monitor time
    start_time = time.time()

    # Load data
    parser = argparse.ArgumentParser(description="Apply NER to post texts.")
    parser.add_argument("-d", "--debug", help="Debugging output", action="store_true")
    parser.add_argument("--input", type=argparse.FileType("r"), help="Input CSV file")
    parser.add_argument("--output", type=argparse.FileType("wb"), help="Output JSON file")
    args = parser.parse_args()
    col_list = ["ID", "text"]
    df = pd.read_csv(args.input, encoding="utf-8", sep="\t", usecols=col_list)
    # df = df.truncate(before=2, after=19) # Uncomment to test API quickly
    print("Processing input file: " + str(args.input.name) + "\nSend API requests and wait...")

    # Check once again for empty strings and no NaNs as these are not allowed to be sent to the API
    df = df.dropna(subset=["text"])
    # Apply NER
    ner_results = ner(df)
    # Save to .json
    with open(args.output.name, "w", encoding="utf-8") as f:
        json.dump(ner_results, f, ensure_ascii=False, indent=4)
    print("NER results written to " + str(args.output.name) + ".")
    print("NER successfully completed.")
    print("Time consumption NER: --- %s seconds ---" % (time.time() - start_time))
