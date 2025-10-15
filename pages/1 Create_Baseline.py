#!/usr/bin/env python
# coding: utf-8

# In[1]:
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import model_H2_with_heat as mh
import H2_plotting as hplt
import H2_preset as pst
import H2_export as ext
import pandas as pd
from PIL import Image

# In[2]:


# Option de modification des paramètres dans l'interface
st.subheader("Contribution Analysis")

result=pst.ask(0)
if result is None:
    st.warning("You must define all scenarios to continue.")
else: 
    pst.ask_tier()         
    st.subheader("Impact Score Results :")
    fig = plt.figure()
    hplt.plotting(result, st.session_state.scenario[0][1], st.session_state.scenario[0][19])  # Cette fonction crée un graphique avec matplotlib
    st.pyplot(fig)
    
    with st.expander("Export Scenario Created"):
        csv_data=ext.export_scenario()
        name_file='Personalized Scenario'
        name_file = st.text_input("Enter a name for the download file:", value=name_file, key=f'download_name')

        st.download_button(
        label="📥 Download personalized models",
        data=csv_data,
        file_name=name_file+'.csv',
        mime="text/csv"
        )
                

