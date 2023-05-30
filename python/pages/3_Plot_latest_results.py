import os
import pickle
import numpy as np
from PIL import Image
import streamlit as st
import matplotlib.pyplot as plt


##############################
# Page Config
path_to_python_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path_to_images = os.path.join(path_to_python_dir, 'resources', 'images')
st.set_page_config(
    page_title="BattMo",
    page_icon=Image.open(os.path.join(path_to_images, "battmo_logo.png"))
)
##############################

with open(os.path.join(path_to_python_dir, "battmo_result"), "rb") as pickle_result:
    result = pickle.load(pickle_result)

transp = np.ndarray.transpose(result)

e = transp[0]
i = transp[1]
t = transp[2]

# print("\n e", e, "\n i", i, "\n t", t, "\n\n")


def run_page():
    fig, ax = plt.subplots()
    ax.plot(t, e)

    fig2, ax2 = plt.subplots()
    ax2.plot(t, i)

    st.pyplot(fig)
    st.pyplot(fig2)


if __name__ == "__main__":
    run_page()



