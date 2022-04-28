#!/usr/bin python
# -*- coding: utf-8 -*-
"""A module to preprocess Russian text.
This module is used to preprocess the text of posts from the VK corpus.
To produce preprocessed text to reproduce results comparable to the results presented in the paper, run the module as is.

This module is inspired by the following scripts:
https://www.kaggle.com/alxmamaev/how-to-easy-preprocess-russian-text (last accessed: 2022-04-23)

A custom Russian spacy tokenizer was used to produce the original results was obtained here,
https://github.com/aatimofeev/spacy_russian_tokenizer (last accessed: 2022-04-26, modified for our case, not used as is).
We do not provide the custom Russian spacy tokenizer, but provide an implementation with the default Russian spacy tokenizer.
"""
import argparse
import re
import time
from functools import reduce

import numpy as np
import pandas as pd
import spacy
from textacy.preprocessing import normalize, remove, replace

# Monitor time
start_time = time.time()

# Initialize variables
global df
tokens = []
processed = []
tokenized = []
fn = ""

# Load data
parser = argparse.ArgumentParser(description="Preprocessing agenda-setting.")
parser.add_argument("-d", "--debug", help="Debugging output", action="store_true")
parser.add_argument("--input", type=argparse.FileType("r"), help="Input CSV file")
parser.add_argument("--output", type=argparse.FileType("wb"), help="Output CSV file")
args = parser.parse_args()

print("Processing input file: " + args.input.name)

try:
    df = pd.read_csv(args.input, encoding="utf-8", sep="\t", parse_dates=[4], infer_datetime_format=True, )

    df["date"] = pd.to_datetime(df["date"], unit="s")
except IOError as io_error:
    print(io_error)

# Unicode normalize
df["text"] = df["text"].str.normalize("NFKC")
# Remove empty posts
df["text"] = df["text"].fillna("")
# Remove URLS # COMMENT OUT FOR EXTENSION
# df["text"] = df["text"].str.replace("http\S+|www.\S+", "", case=False)

# Retrieve texts as list and prepare for NER, if applied
texts = list(df["text"])
for text in texts:
    transforms = (
        normalize.whitespace, remove.punctuation, replace.user_handles, replace.numbers, replace.currency_symbols,
        replace.hashtags, replace.emojis,)
    processed.append(reduce(lambda r, f: f(r), transforms, text))

# Remove zero-width spaces and joiners
# Remove a special emoji not captured by the above pipeline
processed = [x.replace("\u200b", "") for x in processed]
processed = [x.replace("\u200d", "") for x in processed]
processed = [x.replace("\u200c", "") for x in processed]
processed = [x.replace("\u2642", "_EMOJI_") for x in processed]

processed = [x.replace("_EMOJI_", " ") for x in processed]
processed = [x.replace("_NUMBER_", " NUMBER ") for x in processed]
processed = [x.replace("_TAG_", " TAG ") for x in processed]
processed = [x.replace("_EMAIL_", " ") for x in processed]
processed = [x.replace("_USER_", " USER ") for x in processed]
processed = [x.replace("_CUR_", " CUR ") for x in processed]

# Uncomment if NER comparison is done
# Assign text prepared for NER back to complete DataFrame and save to CSV
# df["text"] = processed
# fn = args.input + "_processed_NER_comparison.csv"
# df.to_csv(fn, index=False)

# Uncomment if a custom Russian tokenizer is used (as for our submission)
# Note that we do not ship the modified custom Russian tokenizer

# Tokenize text with custom Russian tokenizer
# def create_russian_tokenizer(nlp,name):
#     return RussianTokenizer(nlp, MERGE_PATTERNS + SYNTAGRUS_RARE_CASES, name)
#
# nlp = Russian()
# name = "RussianTokenizer"
# Language.factory("russian_tokenizer", func=create_russian_tokenizer(nlp,name))
#
# nlp.add_pipe('russian_tokenizer', last=True)

nlp = spacy.load("ru_core_news_sm")
for text in processed:
    if type(text) == "":
        text = np.NaN
    else:
        tokens = [token.text.lower() for token in nlp(text)]
        post = " ".join(tokens)
        tokenized.append(post)

# Remove emojis, tags, user handles, and URLs
tokenized = [x.replace("emoji", " ") for x in tokenized]
tokenized = [x.replace("number", "NUMBER") for x in tokenized]
tokenized = [x.replace("tag", " TAG ") for x in tokenized]
tokenized = [x.replace("email", " ") for x in tokenized]
tokenized = [x.replace("user", " USER ") for x in tokenized]
tokenized = [x.replace("cur", "CUR") for x in tokenized]

# Assign preprocessed text back to complete DataFrame
df["text"] = tokenized

# Remove whatever is left of special emojis
df["text"] = df["text"].str.replace(r"[^\w\s]", "", flags=re.UNICODE, regex=True)

# Wrap up cleaning
df["text"] = df["text"].str.replace("ツ", "", regex=True)
df["text"] = df["text"].replace("", np.NaN, regex=True)
df["text"] = df["text"].str.replace(r"\s{2,}", " ", regex=True)
df["text"] = df["text"].str.strip()
df.dropna(subset=["text"], inplace=True)

# Save to CSV file
df.to_csv(args.output.name, index=False)
print("Processed posts saved to output file: " + args.output.name)

print("Time consumption of text prep: --- %s seconds ---" % (time.time() - start_time))
