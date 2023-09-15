# streamlit_toggle_component

A streamlit component that allows you to create multiple toggles and specify how many of this toggles can be enabled at the same time

## Installation instructions 

```sh
pip install streamlit_toggle_component
```

## Usage instructions

```python
import streamlit as st

from st_toggle_component import st_toggle_component

value = st_toggle_component()

st.write(value)
