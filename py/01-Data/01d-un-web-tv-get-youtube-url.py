## INC 2 and 1, youtube

import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep

multiline_string= """https://youtu.be/aD3cke8KrMc
https://youtu.be/3G0N-Y8DeYA?si=7jG9bYKaMoy3S5rn
https://www.youtube.com/watch?v=-OZ1DR8Sn70
https://youtu.be/oLHn1xT3SjQ
https://youtube.com/live/NadBwglkcZI
https://youtu.be/gcFnKP-ziDs
https://youtu.be/Jyuc_zIVUg4
https://youtu.be/oBTMXxTOkm0
https://youtu.be/-H2ei3hX5r8
https://youtu.be/C8mojvYXsbw
https://youtu.be/GUDqh5hHR9c
https://youtu.be/6W7VBp1GFic
https://youtu.be/cEOGQxMczug
https://youtu.be/N1P8EZ3ZXlc
https://youtu.be/6L3dQanotr8
https://www.youtube.com/watch?v=iv2YqonIm9I
https://youtu.be/7-y8dw3G7P0
https://youtu.be/ia6DbXJfpoA
https://youtu.be/I0dSo4yQ5dE
https://youtu.be/Iylc8CGljbs
https://youtu.be/deEeUrnga38
https://youtu.be/F0cN0AZXM28
https://youtu.be/DDBqkekDAMo
https://youtu.be/DZCSgMbjZmQ
https://youtu.be/LHJsNJD-abA
https://youtu.be/f4ZrDlF81hI
https://youtu.be/eDF8BJb6j5o
https://youtu.be/_77miA4bUJE
https://www.youtube.com/watch?v=Hjp5NlE4C8o
https://youtu.be/YACT9VvAaFM
https://youtu.be/1ivg3xURCvM
https://youtu.be/NFGehya6ekQ
https://youtu.be/t8-NUPlj5VM
https://youtu.be/456pzVIaHBw
https://youtu.be/wyZq-f94DoU
https://youtu.be/Dnt-ImxHIWs
https://youtu.be/5wsLiAJKtDU
https://youtu.be/57gA_ikFauI
https://youtu.be/0_AuDGy3rtk
https://youtu.be/xCvM3erT2wU
https://youtu.be/bspq0LsgQW0
https://youtu.be/-aaju9OwTxs
https://www.youtube.com/watch?v=S9qYSpWdZO8
https://youtu.be/eqeHjD_nN18
https://youtu.be/MdaMk7ajEXA
https://youtu.be/YF6U5h1_5eU
https://youtu.be/QvAo4chpjjY
https://youtu.be/AsnysdkCtgs
https://youtu.be/k3BUn3tDHg0
https://youtu.be/rnU-VhRzySQ
https://youtu.be/ie7zD7lFq1s
https://youtu.be/X_j5gX6nK-k
https://youtu.be/Rktx8RCh5D4
https://youtu.be/kg7-e88kQEk
https://youtu.be/5IOJeduLCLQ
https://youtu.be/gPho5jC_TV4
https://youtu.be/pJQkvOlIYac
https://www.youtube.com/watch?v=Iiq92C8bv7k
https://youtu.be/6Ej-M0Pmsak
https://youtu.be/V5OhR6sA8ys
https://youtu.be/N_GSIL0lLDs
https://youtu.be/N0tndIkgmhE
https://youtu.be/rI9yR9Unecs
https://youtu.be/faWpcV3_ft8
https://youtu.be/kKJQ2JLEjCw
https://www.youtube.com/live/nHWOm3jnM4k?si=Quv6OyR4JmAOHy6k
https://youtu.be/ok2W6StHNN4
https://youtu.be/v8yQgZOdliQ
https://youtu.be/lvZazc9HwzU
https://youtu.be/rULFUwbNL1M
https://youtu.be/7RT5xpE9i9A
https://youtu.be/aLkn6JthYpU
https://youtu.be/yg4uKHqyIdo
https://youtu.be/o0SnFfqM-vY
https://youtu.be/3kd_aowmGbU
https://youtu.be/ZhRN68iWz1k
https://youtu.be/s_89v97a7xM
https://youtu.be/UKpl8ow0BOY
https://youtu.be/02NpoZmPh5U
https://youtu.be/rxLrJlIPeHQ%20
https://youtu.be/flQcIIXolDU
https://youtu.be/r6d7Cil915I
https://youtu.be/h0LsDf0-rz8
https://youtu.be/J8dZVczMnvg
https://youtu.be/w8dh0Jd12n4
https://youtu.be/yQWUgUmTS8w
https://youtu.be/TeNi2dggDbg
https://youtu.be/KJyStOb3RhA
https://youtu.be/c8wjbRH0LB0
https://youtu.be/rwNWK-ceGuI
https://youtu.be/Qyszy1BKbPE
https://www.youtube.com/watch?v=1fiohAv4jOo
"""
url_list = multiline_string.splitlines()

def get_youtube_title(youtube_link):
  print(f"Visiting YouTube link: {youtube_link}")
  youtube_response = requests.get(youtube_link)
  if youtube_response.status_code != 200:
    print(f"Failed to fetch YouTube page: {youtube_response.status_code}")
    return(pd.DataFrame())
  # Parse the YouTube page
  youtube_soup = BeautifulSoup(youtube_response.text, 'html.parser')
  # Extract the title of the YouTube video
  title_tag = youtube_soup.find("meta", property="og:title")
  if title_tag:
    video_title = title_tag.get("content", "No Title Found")
    print(f"Video Title: {video_title}")
  else:
    video_title = ""
    print("Could not extract the video title.")
  sleep(3)
  return(pd.DataFrame({"url": youtube_link, "title": video_title}, index = [0]))

titles = [get_youtube_title(item) for item in url_list]


df_youtube_title = pd.concat(titles, axis = 0, ignore_index = True)
df_youtube_title.to_csv("../../data/df_youtube_links.csv")

