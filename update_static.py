import bz2
import shutil
import requests
import sys

if __name__ == '__main__':
    print("Updating static data.")

    response = requests.get("https://www.fuzzwork.co.uk/dump/latest/eve.db.bz2", stream=True)

    print("Downloading EVE static data.")

    with open("data/eve.db.bz2", 'wb') as f:
        i = 0
        for data in response.iter_content(chunk_size=4096):
            i += len(data)
            f.write(data)
            sys.stdout.write(f"Data downloaded: {round(i / (1024 * 1024), 2)} MiB   \r")
            sys.stdout.flush()

    print("Decompressing data.")

    with bz2.open("data/eve.db.bz2", 'rb') as f_in:
        with open("data/eve.sqlite", 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    print("Done!")
