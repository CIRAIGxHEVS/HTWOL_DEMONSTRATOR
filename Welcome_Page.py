#!/usr/bin/env python
# coding: utf-8

# In[1]:
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


# In[2]:

st.set_page_config(
    page_title="HTWOL",
    page_icon="images/logo.ico", 
    layout="wide",
)

# Interface utilisateur Streamlit
st.title("Welcome on the HTWOL - the parametrized tool for LCA of Water Electrolysis supply chain. ")

st.write("This app is the Demonstration Version of the tool. It aims to be used for accompanying the partners in understanding the carbon footprint of their technology and evaluate by themselves potential innovation for improving the durability of their technology.")

st.write("Please visit the git repository (https://github.com/CIRAIGxHEVS/HTWOL_DEMONSTRATOR) and the supplementary information (https://doi.org/10.5281/zenodo.17428317) to obtain more details on methodology and datasets used.")
st.write("**When using the tool, please cite: Magnaval, G., Mouhoub, M., Boulay, A.-M., & Margni, M. (2025). HTWOL / Harmonizing the assessment of (Green) Hydrogen Supply Chain: a modular and parametrized Life Cycle Assessment Framework. (v0.1) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.18019828**")

st.write("Warning: If you want to have access to the complete version of the HTWOL (you would need an ecoinvent license), or in case of problem, please contact gabriel.magnaval@hevs.ch. Any feedback is valuable to help us in further developing the app.")


st.subheader("Thanks to our partners and financial supports.")
col1,col2,col3=st.columns(3)
with col1:
    image = Image.open("images/ciraig.png") 
    st.image(image) 

with col2:
    image = Image.open("images/hesso.png") 
    st.image(image)
   
with col3:
    image = Image.open("images/europe.png") 
    st.image(image)

col1,col2,col3=st.columns(3)
with col1:
    image = Image.open("images/presshyous.png") 
    st.image(image)
with col2:
    image = Image.open("images/sustaincell.png") 
    st.image(image)
with col3:
    image = Image.open("images/anemel.png") 
    st.image(image)


