#!/bin/sh
python api.py & 
P1=$!
streamlit run python/Introduction.py --global.disableWidgetStateDuplicationWarning true &
P2=$!
wait $P1 $P2