# Load necessary library
library(stringi)
library(tidyverse)

root_dir <- "~/Downloads/temp/inc-webtv-audio"
new_dir <- "~/Downloads/temp/inc-webtv-audio-use"

fn <- list.files(root_dir, pattern = '.mp4')
fn <- fn |> 
  stri_subset_regex("^INC.+part")

df <- tibble(fn) %>%
  mutate(newfn = fn |> str_replace("INC-(\\d+).*?part_(\\d+).+\\.mp4",
                                                "INC-\\1-Part-\\2-English.mp4"))df |> 
  rowwise() |> 
  mutate(tmp = file.copy(paste0(root_dir, "/", fn), paste0(new_dir, "/", newfn)))
