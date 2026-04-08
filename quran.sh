#!/data/data/com.termux/files/usr/bin/bash

PLAYLIST="https://youtube.com/playlist?list=PLH2SOmg2YPWmA-u_g0O1KauoXCb5xCb6i"
CACHE="$HOME/quran-cli/cache"
BOOK="$HOME/quran-cli/bookmarks/bookmarks.txt"

mkdir -p "$CACHE"

logo(){
clear
echo "================================="
echo "         QURAN CLI"
echo "================================="
}

get_urls(){
yt-dlp --flat-playlist --print "%(url)s" "$PLAYLIST"
}

get_titles(){
yt-dlp --flat-playlist --print "%(playlist_index)s %(title)s" "$PLAYLIST"
}

read_menu(){

title=$(get_titles | fzf)

echo "$title"

read -p "Press Enter..."
}

play_surah(){

line=$(get_titles | fzf)

num=$(echo "$line" | awk '{print $1}')

url=$(get_urls | sed -n "${num}p")

echo
echo "Playing Surah $num"
echo

mpv "https://youtube.com/watch?v=$url"
}

play_full(){

echo "Playing full Qur'an..."
mpv "$PLAYLIST"
}

random_surah(){

total=$(get_titles | wc -l)

num=$((RANDOM % total + 1))

url=$(get_urls | sed -n "${num}p"

)

echo "Random Surah $num"

mpv "https://youtube.com/watch?v=$url"
}

bookmarks(){

cat "$BOOK" 2>/dev/null || echo "No bookmarks yet."
read
}

menu(){

logo

echo
echo "1 Read Surah List"
echo "2 Play Surah Audio"
echo "3 Play Full Qur'an"
echo "4 Random Surah"
echo "5 Bookmarks"
echo "6 Exit"
echo

read -p "Choose > " choice

case $choice in

1) read_menu ;;
2) play_surah ;;
3) play_full ;;
4) random_surah ;;
5) bookmarks ;;
6) exit ;;

*) echo "Invalid"; sleep 1 ;;

esac

menu
}

menu

