# Install necessary packages
#install.packages(c("cld2", "cld3", "textTinyR", "dplyr"))

# Load libraries
library(cld2)
library(cld3)
library(fastText)
library(tidyverse)

# Load CSV file
csv_file <- "data/df_all_sessions_file_list.csv"  # Replace with your CSV file path
data <- read_csv(csv_file)

# Check if files exist and read text content
data <- data %>%
  rowwise() %>%
  mutate(
    file_exists = file.exists(text_file_name),  # Check if file exists
    file_content = if (file_exists) {
      tryCatch(readLines(text_file_name, warn = FALSE) %>% paste(collapse = " "),
               error = function(e) NA)
    } else {
      NA
    }
  )

# Detect language using cld2, cld3, and fastText
data <- data %>%
  mutate(
    cld2_lang = if (!is.na(file_content)) detect_language(file_content) else NA,
    cld3_lang = if (!is.na(file_content)) cld3::detect_language(file_content) else NA
    #fastText_lang = if (!is.na(file_content)) detect_language(file_content) else NA
  )

file_pretrained = system.file("language_identification/lid.176.ftz", package = "fastText")

fast_text_out <- language_identification(input_obj = data$file_content,
                                         pre_trained_language_model_path = file_pretrained,
                                   k = 3,
                                   th = 0.0,
                                   verbose = TRUE)
data$fastText_lang <- fast_text_out$iso_lang_1

data <- data %>%
  mutate(lang_agreement = case_when(
    !is.na(cld2_lang) & !is.na(fastText_lang) & fastText_lang == cld2_lang ~ 1,
    TRUE ~ 0
  )) |> 
  mutate(language = case_when(
    lang_agreement == 1 ~ cld2_lang, 
    T ~ ""
  ))

# Save results to a new CSV file
write_excel_csv(data, "data/df_all_sessions_file_list-with-lang.csv")
           
