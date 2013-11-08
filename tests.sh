#!/bin/bash

# Klassikaraadio
python fetch/radio_shows.py --pretend 'http://klassikaraadio.err.ee/kuularhiiv?saade=255&kid=113'

# Raadio 2
python fetch/radio_shows.py --pretend 'http://r2.err.ee/saated?saade=285&sub=292'
