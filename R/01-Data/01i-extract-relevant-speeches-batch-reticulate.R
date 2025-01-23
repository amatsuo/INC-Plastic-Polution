library(tidyverse)
library(stringi)
library(ellmer)
library(jsonlite)
library(reticulate)

# Load the openai library from Python
openai <- import("openai")

# Set your OpenAI API key (replace with your actual key)
api_key <- read_lines("cred/open_inc")[1]
chat <- openai$OpenAI(api_key = api_key)

## Functions
convert_to_hms <- function(seconds) {
  seconds <- round(seconds)
  # Calculate hours, minutes, and remaining seconds
  hours <- seconds %/% 3600
  minutes <- (seconds %% 3600) %/% 60
  remaining_seconds <- seconds %% 60
  
  # Format as hh:mm:ss
  sprintf("%02d:%02d:%02d", hours, minutes, remaining_seconds)
}

## Define a function to query GPT
query_gpt <- function(current_speech, previous_speech) {
  prompt <- paste0(
    "You are analyzing a conference meeting transcript. Here is a speaker's speech and the chairperson's speech before it. ",
    "For the speaker's speech:\n\n",
    "1. Determine whether the speech was made by a representative of a country. (Yes/No, If Yes: Specify the group(s))\n",
    "2. If yes to 1, does the speaker represent any country groups (e.g., African Group)? (Yes/No, If Yes: Specify the group(s)) ",
    "3. If yes to question 1, clean the text by removing procedural or non-meaningful parts (e.g., 'Thank you chairman'). This include the expression of gratitude to the host country. ",
    "If no to question one, you delete the speech text and nothing will be returned. ",    
    "The text should be separated into paragraphs (the paragraphs should be created).\n\n",
    "Chairperson's speech:\n", previous_speech, "\n\n",
    "Speaker's speech:\n", current_speech, "\n\n",
    "Return your analysis in the following format:\n",
    "{\n",
    "  \"is_country_representative\": true/false,\n",
    "  \"country_name\": <country name here>,\n",
    "  \"is_country_group\": true/false,\n",
    "  \"country_group_name\": <country group name here>,\n",
    "  \"cleaned_text\": \"<cleaned text here>\"\n",
    "}"
  )
  
  response <- chat$chat$completions$create(
    model = "gpt-4o-mini",
    messages = r_to_py(list(
      list("role"="system", "content"="You are a political scientist analyzing conference minutes of international negotiations."),
      list("role"= "user", "content" = prompt))),
    stop = NULL
  )
  
  return(response$choices[[1]]$message$content)
}


## Main function
process_file <- function(current_file) {
  cat(paste("Processing:", current_file))
  ## Open the data
  df <- paste0(transcript_folder, current_file) |> read_csv() |> 
    mutate(id = row_number()) |> 
    select(6, 1:5) |> 
    mutate(speaker = speaker |>  stri_extract_first_regex("\\d+") |> as.integer())
  
  df_combined <- df |> 
    filter(duration >= 3) |> 
    mutate(
      gap = c(Inf, start[-1] - end[-n()]),  # Calculate gaps between consecutive speeches
      group = cumsum(gap > 15 | speaker != lag(speaker, default = first(speaker)))  # Create groups
    ) %>%
    group_by(group, speaker) %>%
    summarize(
      start = first(start),
      end = last(end),
      start_id = first(id),
      end_id = last(id),
      text = paste(text, collapse = " "),
      .groups = "drop"
    ) %>%
    select(-group) |> 
    mutate(start_hms =convert_to_hms(start)) |> 
    mutate(end_hms =convert_to_hms(end)) |> 
    mutate(duration = end - start)
  
  
  ## Find who is the chair
  df |> count(speaker) |> arrange(-n)
  chair_id_cand <- df |> 
    filter(duration > 10) |> 
    count(speaker) |> arrange(-n) |> slice(1) |> pull(speaker)
  #browser()
  chair_cand_speech <- df |> 
    filter(speaker == chair_id_cand) |> 
    filter(duration <= 100 & duration >= 30) |> 
    sample_n(3) |> 
    arrange(id) |> 
    pull(text) 
  
  prompt <- sprintf("
You are reading the meeting transcript generated from the speech recognition software.

The First thing you want to know is who is the chair of the meeting. Do you think the following spkear is the chair of the meeting (Your answer should be Yes or No)? You read sample of three speeches by the speaker below

Speech 1:
%s

Speech 2:
%s

Speech 3:
%s
", 
                    chair_cand_speech[1], 
                    chair_cand_speech[2], 
                    chair_cand_speech[3])
  cat("Checking who is chair...\n")
  res <- chat$chat$completions$create(
    model = "gpt-4o-mini",
    messages = r_to_py(list(
      list("role"="system", "content"="You are a political scientist analyzing conference minutes of international negotiations."),
      list("role"= "user", "content" = prompt))),
    stop = NULL
  )
  out <- res$choices[[1]]$message$content
  if(out == "Yes"){
    chair_id <- chair_id_cand
  } else {
    warning(paste0("Chair was not found\nPrompt:", prompt))
    return(NLLL)
  }
  
  ## remove unnecessary speech
  df_combined_sub <- df_combined |> 
    filter(speaker == chair_id | duration  >= 20)
  
  # Find the most recent chairperson's speech for each row
  df_combined_sub <- df_combined_sub %>%
    mutate(
      previous_chair_speech = purrr::map_chr(
        1:n(),
        function(i) {
          # Find rows before the current one
          prior_rows <- df_combined_sub[max(1, i - 2):(i - 1), ]
          
          # Get the most recent chair speech
          chair_speech <- prior_rows %>%
            filter(speaker == chair_id) %>%
            tail(1) %>%
            pull(text)
          
          if (length(chair_speech) == 0) "" else chair_speech
        }
      )
    ) 
  
  # Apply GPT to each row of the transcript
  cat("Processing individual speeches...\n")
  df_combined_sub_out <- df_combined_sub %>%
    filter(speaker != chair_id) |> 
    rowwise() |> 
    mutate(
      gpt_response = query_gpt(text, previous_chair_speech)
    )
  
  df_combined_sub_out <- df_combined_sub_out |> 
    mutate(
      gpt_response_json = map(gpt_response, fromJSON)
    ) |> 
    unnest_wider(gpt_response_json)
  
  df_combined_sub_out |> write_excel_csv(paste0(out_folder, current_file))
  cat("File succesfully parsed\n")
}

transcript_folder <- "~/Dropbox/plastics_text analysis/transcripts/"
out_folder <- "~/Dropbox/plastics_text analysis/transcripts_parsed/"

dir.create(out_folder)
fn <- list.files(transcript_folder, pattern = ".csv")

#process_file(fn[16])
#process_file(fn[21])
# process_file(fn[22])
# process_file(fn[6])
#process_file(fn[7])
#process_file(fn[1])
#process_file(fn[2])
process_file(fn[15])
#current_file <- fn[21]
