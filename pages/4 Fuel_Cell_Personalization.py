#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import streamlit as st
import H2_preset as pst
import H2_export as ext

model_selected=['-- Select --', 'Baseline','Personalized']
TRL_selected=['-- Select --','Present','State-of-the-Art','Target 2050']

def restart():
    st.session_state['FuelCell_Perso'] = None
    st.session_state['Baseline_FC_Perso'] = None
    st.session_state['Name_FC_Scenario'] = None
    st.rerun()
    
col1,col2,col3,col4=st.columns(4)  

with col3: 
    with st.expander("Import: Upload Scenario "):
        uploaded_file = st.file_uploader("Upload your personalized CSV", type="csv")
        if uploaded_file:
            if st.button(f"Confirm Uploading"):
                ext.import_dict(uploaded_file,True)
                pst.key_dictionary()
            

with col4:
    with st.expander("Export Scenario Created"):
        csv_data=ext.export_dict(True)
        name_file='Personalized Scenario'
        name_file = st.text_input("Enter a name for the download file:", value=name_file, key=f'download_name')

        st.download_button(
        label="📥 Download personalized models",
        data=csv_data,
        file_name=name_file+'.csv',
        mime="text/csv"
        )


if 'FuelCell_Perso' not in st.session_state or st.session_state['FuelCell_Perso'] is None:
    st.write("Initialisation: Start by selecting the reference scenario")
    st.session_state['FuelCell_Perso'] = None
    st.session_state['Baseline_FC_Perso'] = None
    if "dictionary" not in st.session_state:
        pst.dictionary()
        pst.key_dictionary()
    fuelcell = '-- Select --'
    fuelcell_name = '-- Select --'
    TRL = '-- Select --'
    baseline='-- Select --'
    
    col1, col2,col3,col4 = st.columns(4) 	
    with col1:
         baseline= st.selectbox('Choose Between Baseline and Custom Model', model_selected, index=model_selected.index(baseline), key=f"model_fc_perso")
            
    if baseline == '-- Select --':
        st.warning("You must select an option to continue.")  
        
    elif baseline == 'Baseline':
            
        with col2:
            fuelcell = st.selectbox('Fuel Cell \n Type', st.session_state.list_dictionary[1], index=st.session_state.list_dictionary[1].index(fuelcell), key=f"fuelcell")
        with col3:
            TRL=st.selectbox('Fuel Cell \n TRL', TRL_selected, index=TRL_selected.index(TRL), key=f"fuelcell_TRL")
            
        if fuelcell == '-- Select --' or TRL == '-- Select --' :
            st.warning("You must select an option to continue.")  
        
        elif st.button("Confirm Initialisation"):   
                param_cell,param_stack,param_he,param_oe,param_bl,param_cl,param_el,param_bp,param_frame,param_ep,param_bop,param_cons,param_h2=pst.ref_to_sublist(fuelcell,TRL,False)
                st.session_state['FuelCell_Perso'] =[param_cell,param_stack,param_he,param_oe,param_bl,param_cl,param_el,param_bp,param_frame,param_ep,param_bop,param_cons,param_h2]
                st.session_state['Baseline_FC_Perso'] = "Baseline"
                st.rerun()
        
    else:
        with col2:
            fuelcell_name = st.selectbox('Fuel Cell \nModel', st.session_state.list_dictionary[3], index=st.session_state.list_dictionary[3].index(fuelcell_name), key=f"fuelcellname")   
        if fuelcell_name == '-- Select --' :
            st.warning("You must select an option to continue.")  
        elif st.button("Confirm Initialisation"): 
            param_cell,param_stack,param_he,param_oe,param_bl,param_cl,param_el,param_bp,param_frame,param_ep,param_bop,param_cons,param_h2=pst.ref_to_sublist(fuelcell_name,'Personalized',False)
            st.session_state['FuelCell_Perso'] =[param_cell,param_stack,param_he,param_oe,param_bl,param_cl,param_el,param_bp,param_frame,param_ep,param_bop,param_cons,param_h2]
            st.session_state['Baseline_FC_Perso'] = "Personalized"
            st.session_state['Name_FC_Scenario'] = fuelcell_name
            st.rerun()
        
        
            


else:
    st.session_state['FuelCell_Perso'] = pst.ask_detailed_stack(st.session_state['FuelCell_Perso'],True)

    if 'Name_FC_Scenario' not in st.session_state :
        st.session_state['Name_FC_Scenario'] = None
    col1,col2,col3,col4=st.columns(4)
    with col1:
        with st.expander("Create New Scenario"):
            scenario_name = st.text_input("Enter a name for the new scenario:", key=f'scenario_name')
            if st.button("Confirm name and Create New Scenario"):
                if scenario_name:
                    st.session_state['Name_FC_Scenario'] = scenario_name
                    st.session_state.dictionary[3][st.session_state['Name_FC_Scenario']] = pst.sublist_to_ref(*st.session_state['FuelCell_Perso'])
                    pst.key_dictionary()
                    st.success(f"Scenario '{st.session_state['Name_FC_Scenario']}' has been created and saved")
                    restart()
                else:
                    st.warning("Please enter a name for the scenario before saving.")
                        
    if st.session_state['Baseline_FC_Perso'] =='Personalized':
        with col2:
            if st.button(f"Save your work in {st.session_state['Name_FC_Scenario']}"):
                st.session_state.dictionary[3][st.session_state['Name_FC_Scenario']] = pst.sublist_to_ref(*st.session_state['FuelCell_Perso'])               
                st.success(f"Changes saved in {st.session_state['Name_FC_Scenario']}.")
                restart()

    with col4:
        if st.button("Restart"):
            restart()