#!/usr/bin/env python
# coding: utf-8

import utils.session_variables as sv
sv.init_session()
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import model.calculator as mh
import utils.H2_plotting as hplt
import utils.H2_preset as pst
import utils.H2_export as ext
import pandas as pd
from PIL import Image
import utils.inventory_producer as inv



# Option de modification des paramètres dans l'interface
st.subheader("Contribution Analysis")
scope=pst.ask_scope()
if scope is None:
    st.warning("You must define FU and LCIA to continue.")
else:
    result=pst.ask(0)
    if result is None:
        st.warning("You must define all scenarios to continue.")
    else: 
        inventory=list(result[3:])
        inv.ask_inventory(inventory)
        pst.ask_tier(0,st.session_state.SMR[0])         
        st.subheader("Impact Score Results :")
        fig = plt.figure()
        hplt.plotting(result, st.session_state.tier[0], st.session_state.LCIA)  # Cette fonction crée un graphique avec matplotlib
        st.pyplot(fig)
        
        """
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
        """
                

