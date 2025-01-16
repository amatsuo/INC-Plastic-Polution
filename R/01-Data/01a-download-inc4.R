library(tidyverse)
library(rvest)
library(stringi)


extract_data <- function(nod){
  # Extract the headers (h5) and their associated content
  headers <- nod %>% html_nodes("h5") %>% html_text()
  
  # Extract all <p> tags containing dates, titles, and links
  p_nodes <- nod %>% html_nodes("p")
  
  # Initialize empty list to store rows
  results <- list()
  
  # Loop through each <p> tag and extract date, title, and links
  for (i in seq_along(p_nodes)) {
    p_text <- p_nodes[i] %>% html_text(trim = TRUE)  # Full paragraph text
    p_links <- p_nodes[i] %>% html_nodes("a") %>% html_attr("href")  # Links
    p_titles <- p_nodes[i] %>% html_nodes("a") %>% html_text(trim = TRUE)  # Link texts
    
    # Extract the date (matches the format DD/MM/YYYY)
    date <- str_extract(p_text, "\\d{2}/\\d{2}/\\d{4}")
    
    # Identify the nearest header (based on position)
    if(length(headers) > 0){
      header <- headers[cumsum(p_nodes[i] %>% html_nodes(xpath = "preceding-sibling::h5") %>% length())]
    } else{
      header <- NA
    }
    
    # Extract the paragraph text before links (outside <a> tags)
    if(length(p_nodes[i] %>% html_nodes("a")) > 1){
      main_title <- str_trim(str_replace_all(p_text, "^.+?\\|", ""))
      p_titles <- paste0(main_title, " ", p_titles)  # Combine outside text with link text
    }
    
    # If multiple links exist, combine with the main title and create separate rows
    if (length(p_links) > 0) {
      for (j in seq_along(p_links)) {
        
        results <- append(results, list(data.frame(
          Header = header,
          Date = date,
          Title = p_titles[j],
          Link = p_links[j],
          stringsAsFactors = FALSE
        )))
      }
    }
  }
  # Combine all results into a single data frame
  df_out <- bind_rows(results)
  return(df_out)
}


url <- "https://www.unep.org/inc-plastic-pollution/session-4/statements"
ht <-  read_html(url)

group_states <- ht |> html_element("#GroupsStates div")
df_group <- extract_data(group_states) |> 
  mutate(type = "Group States")
members <- ht |> html_element("#Members div")
df_member <- extract_data(members) |> 
  mutate(type = "Members")

df_files <- bind_rows(df_group, df_member)

df_files <- df_files |> select(5, 1:4)
df_files |> 
  write_csv("data/df_inc4_file_list.csv")


save_folder <- "~/Dropbox/plastics_text analysis/downloads/inc4"
df_files %>%
  rowwise() %>%
  mutate(
    file_name = paste0(save_folder, "/", stri_replace_first_regex(Link, "^.+\\/", ""), ".pdf")  # Clean and set file names
  ) %>%
  do({
    download.file(.$Link, destfile = .$file_name, mode = "wb")  # Download the file
    cat("Downloaded:", .$file_name, "\n")
    Sys.sleep(2)
    data.frame()  # Required to prevent warnings in dplyr
  })
