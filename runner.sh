#!/bin/sh
python api.py & 
P1=$!
streamlit run python/Introduction.py --config config.toml &
P2=$!
wait $P1 $P2