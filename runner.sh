#!/bin/bash
python api.py &
P1=$!
streamlit run python/Introduction.py &
P2=$!
wait $P1 $P2