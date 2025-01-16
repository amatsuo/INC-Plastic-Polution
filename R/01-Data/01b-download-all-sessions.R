library(tidyverse)
library(rvest)
library(stringi)

# Function to extract data from a session page
extract_data <- function(nod, session) {
  # Extract the headers (h5) and their associated content
  headers <- nod %>% html_nodes("h5") %>% html_text()
  
  # Extract all <p> tags containing dates, titles, and links
  if(session < 5){
    p_nodes <- nod %>% html_nodes("p")
  } else {
    p_nodes <- nod %>% html_nodes("div")
  }
  
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
    if(length(p_nodes[i] %>% html_nodes("a")) > 1) {
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

# List of session URLs
session_urls <- c(
  "https://www.unep.org/inc-plastic-pollution/session-1/statements",
  "https://www.unep.org/inc-plastic-pollution/session-2/statements",
  "https://www.unep.org/inc-plastic-pollution/session-3/statements",
  "https://www.unep.org/inc-plastic-pollution/session-4/statements",
  "https://www.unep.org/inc-plastic-pollution/session-5/statements"
)

# Folder to save downloads
save_folder <- "~/Dropbox/plastics_text_analysis/downloads"
text_folder <- "~/Dropbox/research_seed/INC-Plastic-Polution/tmp_data/text"
# Loop over each session and process data
all_files <- list()

for (url in session_urls) {
  print(url)
  session_name <- str_extract(url, "session-[0-9]")  # Extract session name
  ht <- read_html(url)
  # Extract group and member files
  group_states <- ht |> html_element("#GroupsStates div, #GroupofStates div")
  df_group <- extract_data(group_states, stri_sub(session_name, -1) |> as.numeric()) |> 
    mutate(type = "Group States", session = session_name)
  
  members <- ht |> html_element("#Members div, #MembersStatements div")
  df_member <- extract_data(members, stri_sub(session_name, -1) |> as.numeric()) |> 
    mutate(type = "Members", session = session_name)
  
  # Combine group and member data
  session_files <- bind_rows(df_group, df_member)
  all_files <- append(all_files, list(session_files)) 
}

# Combine all session data 
df_files <- bind_rows(all_files) |> 
  mutate(
    file_name = paste0(save_folder, "/", session, "/", stri_replace_first_regex(Link, "^.+\\/", ""))  
  ) |> 
  mutate(
    text_file_name = paste0(text_folder, "/", session, "/", stri_replace_first_regex(Link, "^.+\\/", "")) |> 
      stri_replace_last_regex("\\.pdf", ".txt")
  )
df_files <- df_files |> distinct(Link, .keep_all = T)


# Save the list of files to a CSV
write_csv(df_files, "data/df_all_sessions_file_list.csv")

# Download the files
df_files %>%
  rowwise() %>%
  mutate(
    file_name = paste0(save_folder, "/", session, "/", stri_replace_first_regex(Link, "^.+\\/", ""))  # Create file path
  ) %>%
  do({
    dir.create(dirname(.$file_name), recursive = TRUE, showWarnings = FALSE)  # Ensure directory exists
    # Add error handling for file download
    tryCatch(
      {
        if(!file.exists(.$file_name)) {
          download.file(.$Link, destfile = .$file_name, mode = "wb")  # Attempt to download
          Sys.sleep(2)  # Pause to avoid overwhelming the server
          cat("Downloaded:", .$file_name, "\n")  # Log successful download
        } else{
          cat("File already exists", .$file_name, "\n")
        }
      },
      error = function(e) {
        cat("Error downloading:", .$Link, "\nReason:", e$message, "\n")  # Log error
      }
    )
    data.frame()  # Required to prevent warnings in dplyr
  })
