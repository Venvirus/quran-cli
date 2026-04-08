import json
import subprocess
import sys

with open("quran.json") as f:
    tracks = json.load(f)

def list_tracks():
    for t in tracks:
        print(f"{t['id']}. {t['title']}")

def play(track_id):
    for t in tracks:
        if t["id"] == track_id:
            print(f"Playing: {t['title']}")
            subprocess.run(["mpv", "--no-video", t["url"]])
            return
    print("Track not found")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("python player.py list")
        print("python player.py play 1")
    elif sys.argv[1] == "list":
        list_tracks()
    elif sys.argv[1] == "play":
        play(int(sys.argv[2]))
