#!/bin/bash
set -e
ffmpeg -y -f concat -safe 0 -i /Users/pattuvan/Youtube-agy/videos/20261011_144800_concat.txt -i /Users/pattuvan/Youtube-agy/audio/20261011_144800/full_voiceover.wav -stream_loop -1 -i /Users/pattuvan/Youtube-agy/music/ambient_sample.wav -filter_complex "[2:a]volume=0.08[bg];[1:a][bg]amix=inputs=2:duration=first[aout]" -map 0:v:0 -map "[aout]" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest /Users/pattuvan/Youtube-agy/videos/20261011_144800_final.mp4
