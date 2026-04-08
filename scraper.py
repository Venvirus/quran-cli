import requests
from bs4 import BeautifulSoup
import json

url = "https://truemuslims.net/Chichewa.html"
res = requests.get(url)
soup = BeautifulSoup(res.text, "html.parser")

tracks = []
i = 1

for link in soup.find_all("a"):
    href = link.get("href")

    if href and ".mp3" in href:

        if not href.startswith("http"):
            href = "https://www.truemuslims.net/" + href

        # Extract number from filename
        num = href.split("/")[-1].replace(".mp3", "")

        tracks.append({
            "id": i,
            "title": f"Surah {int(num)}",
            "url": href
        })
        i += 1

with open("quran.json", "w") as f:
    json.dump(tracks, f, indent=2)

print(f"Done. Found {len(tracks)} audio files.")
