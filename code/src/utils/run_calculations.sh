#!/usr/bin/env bash

# A bash script to calculate metrics post and word level as well as the corresponding percent change values.
# Values are calculated for each country in each subcorpus of the VK corpus for time slices of 7, 5, 3, and 1 day(s).

python3 code/src/utils/calculations/calculate_metrics_prct_change.py code/data/media_posts_processed_final.csv code/data/rtsi_topics.xlsx 7
python3 code/src/utils/calculations/calculate_metrics_prct_change.py code/data/media_posts_processed_final.csv code/data/rtsi_topics.xlsx 5
python3 code/src/utils/calculations/calculate_metrics_prct_change.py code/data/media_posts_processed_final.csv code/data/rtsi_topics.xlsx 3
python3 code/src/utils/calculations/calculate_metrics_prct_change.py code/data/media_posts_processed_final.csv code/data/rtsi_topics.xlsx 1
