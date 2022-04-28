#!/usr/bin/env bash

# Prerequisite: VK prep and metrics calculation
# - run_preprocessing.sh or individual modules
# - run_calculations.sh

# Run from base dir using $ bash ./code/src/analyses/correlation_analysis/run_correlation_analysis.sh

Rscript --vanilla ./code/src/analyses/correlation_analysis/basic_corrs.R ./data/metrics_percent_results/7days/control_pst_all7.csv
Rscript --vanilla ./code/src/analyses/correlation_analysis/basic_corrs.R ./data/metrics_percent_results/7days/free_pst_all7.csv

Rscript --vanilla ./code/src/analyses/correlation_analysis/basic_corrs.R ./data/metrics_percent_results/7days/control_wrd_all7.csv
Rscript --vanilla ./code/src/analyses/correlation_analysis/basic_corrs.R ./data/metrics_percent_results/7days/free_wrd_all7.csv

Rscript --vanilla ./code/src/analyses/correlation_analysis/basic_corrs.R ./data/metrics_percent_results/5days/control_pst_all5.csv
Rscript --vanilla ./code/src/analyses/correlation_analysis/basic_corrs.R ./data/metrics_percent_results/5days/free_pst_all5.csv

Rscript --vanilla ./code/src/analyses/correlation_analysis/basic_corrs.R ./data/metrics_percent_results/5days/control_wrd_all5.csv
Rscript --vanilla ./code/src/analyses/correlation_analysis/basic_corrs.R ./data/metrics_percent_results/5days/free_wrd_all5.csv

Rscript --vanilla ./code/src/analyses/correlation_analysis/basic_corrs.R ./data/metrics_percent_results/3days/control_pst_all3.csv
Rscript --vanilla ./code/src/analyses/correlation_analysis/basic_corrs.R ./data/metrics_percent_results/3days/free_pst_all3.csv

Rscript --vanilla ./code/src/analyses/correlation_analysis/basic_corrs.R ./data/metrics_percent_results/3days/control_wrd_all3.csv
Rscript --vanilla ./code/src/analyses/correlation_analysis/basic_corrs.R ./data/metrics_percent_results/3days/free_wrd_all3.csv

Rscript --vanilla ./code/src/analyses/correlation_analysis/basic_corrs.R ./data/metrics_percent_results/1days/control_pst_all1.csv
Rscript --vanilla ./code/src/analyses/correlation_analysis/basic_corrs.R ./data/metrics_percent_results/1days/free_pst_all1.csv

Rscript --vanilla ./code/src/analyses/correlation_analysis/basic_corrs.R ./data/metrics_percent_results/1days/control_wrd_all1.csv
Rscript --vanilla ./code/src/analyses/correlation_analysis/basic_corrs.R ./data/metrics_percent_results/1days/free_wrd_all1.csv
