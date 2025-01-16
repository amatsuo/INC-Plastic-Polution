# Load necessary library
library(stringi)
library(tidyverse)

df <- read_csv("data/df_youtube_links.csv")

# Extract fields using regular expressions
df <- df %>%
  select(-c(1)) |> 
  mutate(
    inc = title |> 
      stri_replace_first_fixed("INC D", "INC-1 D") |> 
      stri_match_first_regex("INC(\\s*-|\\s+)(\\d+)") %>% .[,3] |> as.integer(), # Extract INC value
    day = as.integer(stri_match_first_regex(title, "Day (\\d+)")[,2]), # Extract Day
    part = as.integer(stri_match_first_regex(title, "Plenary (\\d+)")[,2]), # Extract Plenary
    language = stri_match_first_regex(title, "(-|–)\\s*(\\w+)\\s*$")[,3] # Extract Language
  ) |> 
  replace_na(list(part = 1)) |> 
  mutate(newtitle = sprintf("INC-%s-Day-%s-Part-%s-%s", inc, day, part, language))

df |> write_csv("data/df_youtube_links_updated.csv")
