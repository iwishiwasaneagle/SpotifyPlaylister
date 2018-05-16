#!/usr/bin/env bash


# Only exists because if you hook a keybinding to a python script, it will run it as root and fuck shit up.
# This way we can ensure that the correct working directory is used
cd /home/jan-hendrik/Documents/Code/Spotipi
python SpotiPi_main.py
