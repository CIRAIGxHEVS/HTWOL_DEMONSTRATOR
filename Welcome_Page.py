#!/usr/bin/env python
# coding: utf-8

# In[1]:
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


# In[2]:


# Interface utilisateur Streamlit
st.title("Welcome on the HTWOL - the parametrized tool for LCA of Water Electrolysis supply chain. ")

st.write("This app is the Demonstration Version of the tool. It aims to be used for accompanying the partners in understanding the carbon footprint of their technology and evaluate by themselves potential innovation for improving the durability of their technology.")

st.write('Link to Zenodo and Git repository will soon be available.')

st.write("Warning: If you want to have access to the complete version of the HTWOL (you would need an ecoinvent license), or in case of problem, please contact gabriel.magnaval@hevs.ch. Any feedback is valuable to help us in further developing the app.")

col1,col2,col3=st.columns(3)
with col1:
    if st.button("Go to Contribution Page"):
        st.switch_page("pages/1 Contribution_Analysis.py")

with col2:        
    if st.button("Go to Comparison Page"):
        st.switch_page("pages/2 Comparison_Analyses.py")
        
with col3:        
    if st.button("Go to FAQ"):
        st.switch_page("pages/6 F.A.Q.py")

st.subheader("Thanks to our partners and financial supports.")
col1,col2,col3=st.columns(3)
with col1:
    image = Image.open("ciraig.png") 
    st.image(image) 

with col2:
    image = Image.open("hesso.png") 
    st.image(image)
   
with col3:
    image = Image.open("europe.png") 
    st.image(image)

col1,col2,col3=st.columns(3)
with col1:
    image = Image.open("presshyous.png") 
    st.image(image)
with col2:
    image = Image.open("sustaincell.png") 
    st.image(image)
with col3:
    image = Image.open("anemel.png") 
    st.image(image)


