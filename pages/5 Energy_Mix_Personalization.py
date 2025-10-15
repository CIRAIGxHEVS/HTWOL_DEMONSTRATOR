#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import streamlit as st
import H2_preset as pst

model_selected=['-- Select --', 'Baseline','Personalized']
TRL_selected=['-- Select --','Present','State-of-the-Art','Target 2050']
choice_selected=['Electricity','Heat','-- Select --']
elec_ref='-- Select --'
heat_ref='-- Select --'
choice_mix='-- Select --'

if 'elec_mix' not in st.session_state:
    st.session_state.elec_mix=[0.,0.,0.,0.,0.]
if 'heat_mix' not in st.session_state:
    st.session_state.heat_mix=[0.,0.,0.]
    

def restart():
    elec_ref='-- Select --'
    st.session_state.elec_mix=[0.,0.,0.,0.,0.]
    heat_ref='-- Select --'
    st.session_state.heat_mix=[0.,0.,0.]
    choice_mix='-- Select --'
    scenario_name=''
    scenario_name_heat=''



choice_mix= st.selectbox('Do You Want to adjust Electricity or Heat Mix?', choice_selected, index=choice_selected.index(choice_mix), key=f"choice_perso")

if choice_mix == '-- Select --':
        st.warning("You must select an option to continue.")   

elif choice_mix == 'Electricity':
    
    st.session_state.elec_mix=pst.ask_detailed_energy(st.session_state.elec_mix,True)
    
    col1,col2=st.columns(2)
    with col1:
        with st.expander("Reset to a Reference Mix"):
            elec_ref = st.selectbox('Reference Electricity Mix', st.session_state.list_dictionary[6], index=st.session_state.list_dictionary[6].index(elec_ref), key=f"elec")
            if elec_ref == '-- Select --' :
                st.warning("You must select an option to continue.")  
        
            elif st.button("Confirm Initialisation"):   
                st.session_state.elec_mix=pst.mix_name_to_list (elec_ref,True)
                elec_ref='-- Select --'
                st.rerun()

    with col2:
        with st.expander("Save New Scenario"):
            scenario_name = st.text_input("Enter a name for the new scenario:", key=f'scenario_name')
            if st.button("Confirm name and Create New Scenario"):
                if scenario_name:
                    st.session_state.dictionary[6][scenario_name] = st.session_state.elec_mix
                    pst.key_dictionary()
                    st.success(f"Scenario '{scenario_name}' has been created and saved")
                    restart()
                else:
                    st.warning("Please enter a name for the scenario before saving.")

                
elif choice_mix == 'Heat':
    
    st.session_state.heat_mix=pst.ask_detailed_energy(st.session_state.heat_mix,False)
    col1,col2=st.columns(2)
    with col1:    
        with st.expander("Reset to a Reference Mix"):
            heat_ref = st.selectbox('Reference Heat Mix', st.session_state.list_dictionary[7], index=st.session_state.list_dictionary[7].index(heat_ref), key=f"heat")
            if heat_ref == '-- Select --' :
                st.warning("You must select an option to continue.")  
        
            elif st.button("Confirm Initialisation"):   
                st.session_state.heat_mix=pst.mix_name_to_list (heat_ref,False)
                heat_ref='-- Select --'
                st.rerun()
                
    with col2:
        with st.expander("Save New Scenario"):
            scenario_name_heat = st.text_input("Enter a name for the new scenario:", key=f'scenario_heat_name')
            if st.button("Confirm name and Create New Scenario"):
                if scenario_name_heat:
                    st.session_state.dictionary[7][scenario_name_heat] = st.session_state.heat_mix
                    pst.key_dictionary()
                    st.success(f"Scenario '{scenario_name_heat}' has been created and saved")
                    restart()
                else:
                    st.warning("Please enter a name for the scenario before saving.")
  

