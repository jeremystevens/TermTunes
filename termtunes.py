#!/bin/python

######################################################################
# Copyright (C) 2023  Jeremy Stevens
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################

import os
import curses
import subprocess
import sys

# Define the error log file path
error_log_file = "error.log"

# Redirect stderr to the error log file
sys.stderr = open(error_log_file, "w")

# Configuration
user = os.getlogin()
# Change this to your music directory
MUSIC_DIR = f"/home/{user}/Music"
MUSIC_EXTENSIONS = [".mp3", ".ogg", ".wav"]

# Initialize curses
stdscr = curses.initscr()

# Initialize color support (before any color-related functions)
curses.start_color()

# Enable non-blocking input
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
curses.curs_set(0)

# Function to list music files and extract song titles
def list_music():
    songs = []
    for root, _, files in os.walk(MUSIC_DIR):
        for file in files:
            if file.lower().endswith(tuple(MUSIC_EXTENSIONS)):
                # Extract just the song title without the file extension
                song_title = os.path.splitext(os.path.basename(file))[0]
                songs.append(song_title)
    return songs

# Function to play a song
mpg123_process = None

def play_song(song_path):
    global mpg123_process
    try:
        # Use the -q option to suppress output
        mpg123_process = subprocess.Popen(["mpg123", "-q", song_path])
    except Exception as e:
        show_notification(f"Error playing song: {str(e)}")

# Function to display a popup notification
def show_notification(message):
    notification_height = 3
    notification_width = len(message) + 4
    max_y, max_x = stdscr.getmaxyx()
    y = (max_y - notification_height) // 2
    x = (max_x - notification_width) // 2

    notification_win = curses.newwin(notification_height, notification_width, y, x)
    notification_win.attron(curses.color_pair(3))
    notification_win.border()
    notification_win.addstr(1, 2, message, curses.color_pair(4))
    notification_win.refresh()
    notification_win.getch()
    del notification_win

# Main menu
selected_song = 0

# Define color pairs (white background with black text)
curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)

while True:
    stdscr.clear()

    # Get the terminal window dimensions
    max_y, max_x = stdscr.getmaxyx()

    # Calculate the available space for displaying the menu and options
    max_menu_height = max_y - 7  # Leave space for header and status

    # Check if there is enough space for the menu
    songs = list_music()

    if max_menu_height < 1:
        show_notification("Terminal window too small to display menu. Resize and restart.")
        break

    # Calculate the visible range of tracks based on scrolling offset
    start_idx = max(0, selected_song - max_menu_height + 2)
    end_idx = min(start_idx + max_menu_height, len(songs))

    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(0, 0, "Music Player Menu", curses.color_pair(2))
    stdscr.attroff(curses.color_pair(1))

    for i in range(start_idx, end_idx):
        if i == selected_song:
            stdscr.addstr(i - start_idx + 2, 0, f"> {i}. {songs[i]}", curses.color_pair(1))
        else:
            stdscr.addstr(i - start_idx + 2, 0, f"  {i}. {songs[i]}", curses.color_pair(2))

    # Display options and status
    stdscr.addstr(max_menu_height + 2, 0, "Options:", curses.color_pair(2))
    stdscr.addstr(max_menu_height + 3, 2, "p. Play", curses.color_pair(2))
    stdscr.addstr(max_menu_height + 4, 2, "s. Stop", curses.color_pair(2))
    stdscr.addstr(max_menu_height + 5, 2, "x. Exit", curses.color_pair(2))

    stdscr.refresh()

    key = stdscr.getch()

    if key == ord('x'):
        if mpg123_process is not None:
            # Terminate the mpg123 process if it's running
            mpg123_process.terminate()
        break
    elif key == ord('p') or key == 10:  # 'Enter' key
        if 0 <= selected_song < len(songs):
            play_song(os.path.join(MUSIC_DIR, songs[selected_song] + ".mp3"))
            show_notification(f"Now playing: {songs[selected_song]}")
    elif key == ord('s'):
        if mpg123_process is not None:
            # Terminate the mpg123 process if it's running
            mpg123_process.terminate()
    elif key in [curses.KEY_DOWN, ord('j')]:
        if selected_song < len(songs) - 1:
            selected_song += 1
    elif key in [curses.KEY_UP, ord('k')]:
        if selected_song > 0:
            selected_song -= 1

# Clean up
curses.nocbreak()
stdscr.keypad(False)
curses.echo()
curses.endwin()

# Close the error log file
sys.stderr.close()
