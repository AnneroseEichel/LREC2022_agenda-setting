#!/usr/bin bash

# A bash script to apply NER on raw media posts, preprocess posts texts, collapse labels, and create a final merged dataframe.

python3 code/src/utils/text_preprocessing/preprocess_text.py --input "code/data/media_posts.csv" --output "code/data/media_posts_processed.csv"
python3 code/src/utils/text_preprocessing/ner.py --input "code/data/media_posts.csv" --output "code/data/media_posts_ner.json"
python3 code/src/utils/text_preprocessing/merge_labels.py --input "code/data/media_posts_ner.json" --output "code/data/media_posts_ner_collapsed.csv"
python3 code/src/utils/text_preprocessing/merge_ner_and_posts.py --input "code/data/media_posts_processed.csv" "code/data/media_posts_ner_collapsed.csv" --output "code/data/media_posts_processed_final.csv"

exit
