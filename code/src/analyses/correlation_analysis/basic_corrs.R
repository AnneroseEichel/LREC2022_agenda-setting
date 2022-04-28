#!/usr/bin/env Rscript

# R script to calculate correlations for VK posts on post and word level.

# More specifically, the following correlations are calculated:
# Pearson's (not used in final version);
# - log-transformed Pearson's (not used in final version);
# Spearman's;
# - Time-lagged Spearman's with various lags (cf. §4.1).

# Prerequisites: VK post preprocessing and metrics calculation
# - run_preprocessing.sh
# - run_calculations.sh

# Load packages
load_pkg <- rlang::quos(corrplot, tidyverse, rstatix, zoo, stringr)
suppressMessages(invisible(lapply(lapply(load_pkg, rlang::quo_name),
                library,
                character.only = TRUE
)))

# sometimes the nice version version above does not work, in such cases
# resort to:
# library(tidyverse)
# library(corrplot)
# library(rstatix)
# library(zoo)
# library(stringr)

args = commandArgs(trailingOnly = TRUE)
if (length(args) == 0) {
  stop("At least one argument must be supplied (input file).n", call. = FALSE)
} else if (length(args) == 1) {
  # default output file
  args[2] = "out.txt"
}

# Set data directory and read in data
df <-
  read.csv(
    args[1],
    na = "NA",
    header = TRUE,
    sep = ",",
    stringsAsFactors = FALSE,
    dec = ".",
    row.names = "date", 
    quote="",
    comment.char="",
    encoding = "utf-8"
  )
# Exclude stuff not needed right now
df$rtsi_pct <- NULL
df$status <- NULL

# Compute Pearson's correlation
cor.mat.p <- df %>% cor_mat(method = "pearson")
#cor.mat.p %>% cor_get_pval()
cor.mat.p = cor.mat.p[1, ]
cor.mat.p = cor.mat.p %>% cor_gather()
cor.mat.p = cor.mat.p[order(cor.mat.p$var2), ]
cor.mat.p = cor.mat.p %>%
  rename("pearsons" = cor,
         "pvals_pear" = p)

# Compute Pearson's correlation LOG TRANSFORMED
logged <- log(df + 1)
cor.mat.log <- logged %>% cor_mat(method = "pearson")
#cor.mat.log %>% cor_get_pval()
cor.mat.log = cor.mat.log[1, ]
cor.mat.log  = cor.mat.log  %>% cor_gather()
cor.mat.log  = cor.mat.log[order(cor.mat.log$var2), ]
cor.mat.log  = cor.mat.log  %>%
  rename("logged_pearsons" = cor,
         "pvals_pear" = p)

# Compute Spearman's correlation
cor.mat.s <- df %>% cor_mat(method = "spearman")
#cor.mat.s  %>% cor_get_pval()
cor.mat.s = cor.mat.s[1, ]
cor.mat.s = cor.mat.s %>% cor_gather()
cor.mat.s = cor.mat.s[order(cor.mat.s$var2), ]
cor.mat.s = cor.mat.s %>%
  rename("spearmans" = cor,
         "pvals_spear_log" = p)

# Compute time-lagged SPEARMAN'S correlation (!= autocorrelation)

# Create time-lagged series
df.zoo <- zoo(df)
lag1 <- data.frame(stats:::lag((df.zoo$close), -1, na.pad = T))
lag2 <- data.frame(stats:::lag((df.zoo$close), -2, na.pad = T))
lag3 <- data.frame(stats:::lag((df.zoo$close), -3, na.pad = T))

# Fill NaN with 0 (not supported by lag function of zoo)
lag1[is.na(lag1)] <- 0
lag2[is.na(lag2)] <- 0
lag3[is.na(lag3)] <- 0

# Generate data frames where RTSI close price only is lagged by t-1, t-2, t-3
lag1.prep <- cbind(lag1, df[,-1])
lag2.prep <- cbind(lag2, df[,-1])
lag3.prep <- cbind(lag3, df[,-1])


# Calculate lagged correlations: r_t-1
cor.mat.lag1 <- lag1.prep %>% cor_mat(method = "spearman")
#cor.mat.lag1 %>% cor_get_pval()
cor.mat.lag1 = cor.mat.lag1[1,]
cor.mat.lag1 = cor.mat.lag1 %>% cor_gather()
cor.mat.lag1 = cor.mat.lag1[order(cor.mat.lag1$var2),]
cor.mat.lag1[1] <- NULL
cor.mat.lag1 = cor.mat.lag1 %>%
  rename(
    "spearmans1" = cor,
    "pvals_spear_lag1" = p)

# Calculate lagged correlations: r_t-2
cor.mat.lag2 <- lag2.prep %>% cor_mat(method = "spearman")
#cor.mat.lag2 %>% cor_get_pval()
cor.mat.lag2 = cor.mat.lag2[1,]
cor.mat.lag2 = cor.mat.lag2 %>% cor_gather()
cor.mat.lag2 = cor.mat.lag2[order(cor.mat.lag2$var2),]
cor.mat.lag2[1] <- NULL
cor.mat.lag2 = cor.mat.lag2 %>%
  rename(
    "spearmans2" = cor,
    "pvals_spear_lag2" = p
  )

# Calculate lagged correlations: r_t-3
cor.mat.lag3 <- lag3.prep %>% cor_mat(method = "spearman")
#cor.mat.lag3 %>% cor_get_pval()
cor.mat.lag3 = cor.mat.lag3[1,]
cor.mat.lag3 = cor.mat.lag3 %>% cor_gather()
cor.mat.lag3 = cor.mat.lag3[order(cor.mat.lag3$var2),]
cor.mat.lag3[1] <- NULL
cor.mat.lag3 = cor.mat.lag3 %>%
  rename(
    "spearmans3" = cor,
    "pvals_spear_lag3" = p
  )

# Store results in CSV file
temp1 <- merge(cor.mat.p, cor.mat.log, by = c("var1", "var2"))
both <- merge(temp1, cor.mat.s, by = c("var1", "var2"))
temp2 <- merge(cor.mat.lag1, cor.mat.lag2, by = c("var2"))
lagged <- merge(temp2, cor.mat.lag3, by = c("var2"))

# Get file names
fn <- args[1]
if (grepl("free", fn, fixed=TRUE)){
 fn <- str_sub(args[1], start= -17)
} else {
 fn <- str_sub(args[1], start= -20)
}

# Set correct file name and save results as .csv files
main_dir <- "code/data"
sub_dir <- "/correlation_results/"
output_dir <- file.path(main_dir,sub_dir)

if (!dir.exists(output_dir)){
  dir.create(output_dir)
} else {
  print("Results directory for calculating correlations exists.
         Results are stored in the directory.")
}

fn_both <- paste(output_dir,paste("correlations_",fn,sep = ""),sep = "")
fn_lagged <- paste(output_dir,paste("correlations_",fn,sep = ""),sep = "")
write.csv(both, fn_both,
          row.names = FALSE)
write.csv(lagged, fn_lagged,
          row.names = FALSE)
