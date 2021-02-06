import requests
import json
from comcrawl import IndexClient
import pandas as pd


index_list = ["2014-52", "2015-06", "2015-11", "2015-14"]

def search_domain(domain):
    record_list = []

    for index in index_list:
        print(f"Trying index {index}")

        cc_url = f"http://index.commoncrawl.org/CC-MAIN-{index}-index?"
        cc_url += f"url={domain}&matchType=domain&output=json"

        response = requests.get(cc_url)
        print(response)
        if response.status_code == 200:
            records = response.content.splitlines()

            for record in records:
                record_list.append(json.loads(record))

            print(f"Added {len(records)} results")
    
    print(f"found a total of {len(record_list)} hits.")

    return record_list

#search_domain("cnn.com")

client = IndexClient()
print("searching")
client.search("cnn.com", threads=4)

print("sorting")
client.results = (pd.DataFrame(client.results)
                  .sort_values(by="timestamp")
                  .drop_duplicates("urlkey", keep="last")
                  .to_dict("records"))

print(len(client.results))
print("downloading")
client.download(threads=4)

pd.DataFrame(client.results).to_csv("results.csv")

#client.download(threads=2)