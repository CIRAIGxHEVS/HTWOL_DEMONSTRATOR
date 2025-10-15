#!/usr/bin/env python
# coding: utf-8

# In[1]:
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import model_H2_with_heat as mh
import H2_plotting as hplt
import H2_preset as pst
import pandas as pd
from PIL import Image

# In[2]:


# Option de modification des paramètres dans l'interface
st.subheader("Comparison Analyses Page")



col1, col2= st.columns(2)
if "comparison_choice" not in st.session_state:
    st.session_state['comparison_choice'] = "Comparison between two FC&EL systems"

# Ajouter un bouton dans chaque colonne

st.session_state.comparison_choice = st.select_slider(
        "Please Select the type of comparison you want to assess :",
        options=["Comparison between two FC&EL systems", "Comparison with an alternative technology"],
        value=st.session_state.comparison_choice,
    )        

        

        
if st.session_state['comparison_choice'] == "Comparison between two FC&EL systems":
   
    result=pst.ask(0)
    if result is None :
        st.warning("You must define the first scenario to continue.")
    else:
        result_2=pst.ask(1,tier=st.session_state.scenario[0][1])
        if result_2 is None:
            st.warning("You must define the second scenario to continue.")
        else:
            pst.ask_tier()            
            fig=hplt.plotting_comp(result,result_2,st.session_state.scenario[0][1],st.session_state.scenario[0][19])
        

elif st.session_state['comparison_choice'] == "Comparison with an alternative technology":
    result=pst.ask(0,tier=False)
    if result is None:
        st.warning("You must define all scenarios to continue.")
    else:                             
        result=np.concatenate(result[0])
        result=[np.sum(result,axis=0)]
        labels=[st.session_state.scenario[0][20]]
                    
        st.markdown("<p style='font-size:18px'><u><b>Alternative Technology</b> </u></p>", unsafe_allow_html=True)
        techno_dict,techno_selected=pst.techno_available(st.session_state.name_file_techno)
        techno='-- Select --'
                
        techno = st.selectbox('Technology Compared', techno_selected, index=techno_selected.index(techno), key='techno_scenario',help="Select a functionnally equivalent technology to compare with the reference FC&EL system")
         
        
        if techno == '-- Select --' :
            st.warning("You must select an option to continue.")  
        else:
            t=mh.impact_techno(techno_dict,techno)
            result_techno=np.array([t])
            labels+=[techno]
                
            fig = plt.figure()
            hplt.plotting_technosphere(result,result_techno,st.session_state.scenario[0][19],labels)
                

