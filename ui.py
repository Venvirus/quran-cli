import curses
import json
import subprocess
import os
import socket
import time
import random

BASE_DIR = os.path.expanduser("~/quran-cli")
DATA_FILE = os.path.join(BASE_DIR, "quran.json")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
SOCKET_PATH = "/data/data/com.termux/files/usr/tmp/mpv-socket"

SURAH_NAMES = [
"Al-Fatiha","Al-Baqarah","Aal-E-Imran","An-Nisa","Al-Ma'idah","Al-An'am","Al-A'raf",
"Al-Anfal","At-Tawbah","Yunus","Hud","Yusuf","Ar-Ra'd","Ibrahim","Al-Hijr","An-Nahl",
"Al-Isra","Al-Kahf","Maryam","Ta-Ha","Al-Anbiya","Al-Hajj","Al-Mu'minun","An-Nur",
"Al-Furqan","Ash-Shu'ara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum","Luqman",
"As-Sajdah","Al-Ahzab","Saba","Fatir","Ya-Sin","As-Saffat","Sad","Az-Zumar",
"Ghafir","Fussilat","Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiyah","Al-Ahqaf",
"Muhammad","Al-Fath","Al-Hujurat","Qaf","Adh-Dhariyat","At-Tur","An-Najm","Al-Qamar",
"Ar-Rahman","Al-Waqi'ah","Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahanah",
"As-Saff","Al-Jumu'ah","Al-Munafiqun","At-Taghabun","At-Talaq","At-Tahrim","Al-Mulk",
"Al-Qalam","Al-Haqqah","Al-Ma'arij","Nuh","Al-Jinn","Al-Muzzammil","Al-Muddathir",
"Al-Qiyamah","Al-Insan","Al-Mursalat","An-Naba","An-Nazi'at","Abasa","At-Takwir",
"Al-Infitar","Al-Mutaffifin","Al-Inshiqaq","Al-Buruj","At-Tariq","Al-A'la","Al-Ghashiyah",
"Al-Fajr","Al-Balad","Ash-Shams","Al-Lail","Ad-Duha","Ash-Sharh","At-Tin","Al-Alaq",
"Al-Qadr","Al-Bayyinah","Az-Zalzalah","Al-Adiyat","Al-Qari'ah","At-Takathur","Al-Asr",
"Al-Humazah","Al-Fil","Quraysh","Al-Ma'un","Al-Kawthar","Al-Kafirun","An-Nasr",
"Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"
]

# Load tracks
try:
    with open(DATA_FILE) as f:
        tracks = json.load(f)
except:
    tracks = []

current_index = 0
player_process = None
current_playing = None
paused = False

def send_command(cmd):
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)
        client.send((cmd + "\n").encode())
        client.close()
    except:
        pass

def play(track):
    global player_process, current_playing, paused

    if player_process:
        player_process.terminate()

    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    local_file = os.path.join(AUDIO_DIR, f"{track['id']}.mp3")
    source = local_file if os.path.exists(local_file) else track["url"]

    player_process = subprocess.Popen([
        "mpv",
        "--no-video",
        "--quiet",
        "--no-terminal",
        f"--input-ipc-server={SOCKET_PATH}",
        source
    ])

    current_playing = track["id"]
    paused = False
    time.sleep(0.2)

def toggle_pause():
    global paused
    send_command('{ "command": ["cycle", "pause"] }')
    paused = not paused

def generate_wave():
    return "".join(["▁▂▃▄▅▆▇"[random.randint(0,6)] for _ in range(25)])

def draw(stdscr):
    global current_index

    curses.curs_set(0)
    stdscr.timeout(150)

    # Colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)   # header
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # playing
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # paused
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # selected

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        if not tracks:
            stdscr.addstr(0, 0, "No data. Run scraper.")
            stdscr.refresh()
            continue

        # Header
        stdscr.addstr(0, 0, "╔══════════ Qur'an CLI Player ══════════╗", curses.color_pair(1))
        stdscr.addstr(1, 0, "↑↓ Move | ENTER Play | SPACE Pause | n Next | q Quit", curses.color_pair(1))
        stdscr.addstr(2, 0, "╚══════════════════════════════════════╝", curses.color_pair(1))

        selected_name = SURAH_NAMES[current_index]

        if current_playing:
            playing_name = SURAH_NAMES[current_playing - 1]

            if paused:
                status = "⏸ Paused"
                color = curses.color_pair(3)
                wave = ""
            else:
                status = "▶ Playing"
                color = curses.color_pair(2)
                wave = generate_wave()

            stdscr.addstr(4, 0, f"{status}: {playing_name}", color | curses.A_BOLD)
            stdscr.addstr(5, 0, wave, curses.color_pair(2))
        else:
            stdscr.addstr(4, 0, f"Selected: {selected_name}", curses.color_pair(4) | curses.A_BOLD)

        # Scroll area with border
        start = max(0, current_index - (h // 2) + 6)
        end = min(len(tracks), start + h - 12)
        stdscr.addstr(6, 0, "Surah List:", curses.A_UNDERLINE)
        for i in range(start, end):
            name = SURAH_NAMES[i]
            y = i - start + 7

            if i == current_index:
                stdscr.attron(curses.A_REVERSE)

            if current_playing == i+1:
                stdscr.attron(curses.A_BOLD)

            stdscr.addstr(y, 2, f"{i+1}. {name}")

            if i == current_index:
                stdscr.attroff(curses.A_REVERSE)

            if current_playing == i+1:
                stdscr.attroff(curses.A_BOLD)

        stdscr.refresh()
        key = stdscr.getch()

        # Navigation
        if key == curses.KEY_UP:
            current_index = (current_index - 1) % len(tracks)
        elif key == curses.KEY_DOWN:
            current_index = (current_index + 1) % len(tracks)
        elif key == 10:  # ENTER
            play(tracks[current_index])
        elif key == ord('n'):
            current_index = (current_index + 1) % len(tracks)
            play(tracks[current_index])
        elif key == ord(' '):
            toggle_pause()
        elif key == ord('q'):
            if player_process:
                player_process.terminate()
            break

        # AUTOPLAY NEXT SURAH
        if current_playing and player_process and player_process.poll() is not None:
            current_index = (current_index + 1) % len(tracks)
            play(tracks[current_index])

def main():
    curses.wrapper(draw)

if __name__ == "__main__":
    main()
