#!/usr/bin/env python3

### from: https://github.com/NiceLabs/un-web-tv-downloader/blob/main/un-web-tv-downloader.py
import json
import re
import sys
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
import pandas as pd
from time import sleep 

RE_ENTRY_ID = re.compile(re.escape("/").join([
    re.escape("https://webtv.un.org"),
    r"[a-z]{2}",
    "asset",
    r"k[a-z\d]+",
    r"k([a-z\d]+)"
]))


def get_metadata(entry_id: str):
    partner_id = 2503451
    data = {
        "apiVersion": "3.3.0",
        "format": 1,
        "partnerId": partner_id,
        "1": {"service": "session", "action": "startWidgetSession", "widgetId": "_" + str(partner_id)},
        "2": {"service": "baseEntry", "action": "list", "ks": "{1:result:ks}",
              "filter": {"redirectFromEntryId": entry_id}},
        "3": {"service": "baseEntry", "action": "getPlaybackContext", "ks": "{1:result:ks}",
              "entryId": "{2:result:objects:0:id}",
              "contextDataParams": {"objectType": "KalturaContextDataParams", "flavorTags": "all"}}
    }
    request = Request(
        method="POST",
        url="https://cdnapisec.kaltura.com/api_v3/service/multirequest",
        headers={"content-type": "application/json"},
        data=json.dumps(data).encode()
    )
    with urlopen(request) as response:
        payload = json.load(response)
    meta = payload[1]["objects"][0]
    playback = payload[2]
    urls = {"Original": meta["downloadUrl"]}
    for assets in playback["flavorAssets"]:
        tags = assets["tags"].split(",")
        name = assets["language"] if "audio_only" in tags else "%dp" % assets["height"]
        download_url = meta["downloadUrl"][:-1] + str(assets["flavorParamsId"])
        urls.update({name: download_url})
    return {
        "name": meta["name"],
        "description": meta["description"],
        "created_at": datetime.fromtimestamp(meta["createdAt"]),
        "updated_at": datetime.fromtimestamp(meta["updatedAt"]),
        "duration": timedelta(milliseconds=meta["msDuration"]),
        "urls": urls
    }


def extract_entry_id(url: str):
    matched = RE_ENTRY_ID.search(url)
    if not matched:
        return
    (entry_id,) = matched.groups()
    return entry_id[0] + "_" + entry_id[1:]

def get_df(media_url: str):
    try:
        metadata = get_metadata(extract_entry_id(media_url))
        metadata = pd.json_normalize(metadata)
        df = pd.DataFrame(metadata)
    except Exception as e:
        print(f"Error occurred: {e}")  
        df = pd.DataFrame()  
    sleep(3)
    return df


multiline_string = """https://webtv.un.org/en/asset/k1r/k1rivdh4wm
https://webtv.un.org/en/asset/k1i/k1i80bjq6x
https://webtv.un.org/en/asset/k17/k17w4yp2r3
https://webtv.un.org/en/asset/k1n/k1ngcaixml
https://webtv.un.org/en/asset/k1j/k1jodu41u9
https://webtv.un.org/en/asset/k1b/k1b84linf2
https://webtv.un.org/en/asset/k1a/k1aa63hiif
https://webtv.un.org/en/asset/k1v/k1vu04zopw
https://webtv.un.org/en/asset/k1b/k1bxfx78ot
http://webtv.un.org/en/asset/k16/k16zvyn60n
http://webtv.un.org/en/asset/k1r/k1rtt3wkca
https://webtv.un.org/en/asset/k17/k17gbo7gxf
https://webtv.un.org/en/asset/k1l/k1l9a19eyj
https://webtv.un.org/en/asset/k1r/k1rfj82o5r
https://webtv.un.org/en/asset/k14/k14zkrolrg
https://webtv.un.org/en/asset/k1n/k1nnjvorct
https://webtv.un.org/en/asset/k1h/k1hjm0x4z0
https://webtv.un.org/en/asset/k14/k14rko09xz
https://webtv.un.org/en/asset/k1s/k1ssf1706d
https://webtv.un.org/en/asset/k12/k12ifikvd7
https://webtv.un.org/en/asset/k1f/k1fml8thi1
https://webtv.un.org/en/asset/k1y/k1y5almvfi"""

# Convert the multiline string into a list
url_list = multiline_string.splitlines()

out = [get_df(url) for url in url_list]
df_all = pd.concat(out, axis = 0)
df_all.to_csv("../../data/df_download_links.csv")


# def main(media_url: str):
#     metadata = get_metadata(extract_entry_id(media_url))
#     print("Name:", metadata["name"])
#     print("Created at:", metadata["created_at"])
#     print("Updated at:", metadata["updated_at"])
#     print("Duration:", metadata["duration"])
#     for name, url in metadata["urls"].items():
#         print("Download URL (%s):" % name, url)
# 
# 
# if __name__ == '__main__':
#     if len(sys.argv) == 1:
#         print("please set parameters")
#     else:
#         main(sys.argv[1])
