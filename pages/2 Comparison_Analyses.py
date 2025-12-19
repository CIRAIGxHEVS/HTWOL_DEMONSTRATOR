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
import pandas as pd

from PIL import Image




# Option de modification des paramètres dans l'interface
st.subheader("Comparison Analyses Page")



col1, col2= st.columns(2)
if "comparison_choice" not in st.session_state:
    st.session_state['comparison_choice'] = "Comparison between two hydrogen system products"

# Ajouter un bouton dans chaque colonne

st.session_state.comparison_choice = st.select_slider(
        "Please Select the type of comparison you want to assess :",
        options=["Comparison between two hydrogen system products", "Comparison with an alternative technology"],
        value=st.session_state.comparison_choice,
    )        

        
        
if st.session_state['comparison_choice'] == "Comparison between two hydrogen system products":
    results=[]
    scope=pst.ask_scope()
    if scope is None:
        st.warning("You must define FU and LCIA to continue.")
    else: 
        with st.expander("click here to define and/or update scenarios"):
            k = 0
            while k < len(st.session_state.scenario):
                results.append(pst.ask(k))

                if k == len(st.session_state.scenario) - 1:
                    if st.button("Create New Scenario", key=f"button_scena_{len(st.session_state.scenario)}"):
                        sv.add_scenario()

                k += 1

        hydrogen_selected=[st.session_state.scenario[scenario_k][0] for scenario_k in range (len(st.session_state.scenario)) if results[scenario_k]!=None]
        name_selected_to_scenario_k = {st.session_state.scenario[k][0]: k for k in range(len(results))}
        if hydrogen_selected==[]:
            st.warning("You must define at least one scenario to continue.")
        else:
            #PLACEHOLDER_FCEL = "-- Select --"
            # Ensure placeholder is present (and first)
            options = [h for h in hydrogen_selected]
            # Default = only placeholder selected
            selected_list = st.multiselect(
                'Hydrogen Systems Compared',
                options=options,
                default=[],
                key='h2_scenario',
                help="Select one or more hydrogen product systems to be compared with alternative technologies."
            )

            results_selected=[results[name_selected_to_scenario_k[name]] for name in selected_list]
            smr_selected = any(st.session_state.SMR[name_selected_to_scenario_k[name]]for name in selected_list)                
            #result=np.concatenate(result[0])
            #result=[np.sum(result,axis=0)]
            #labels=[st.session_state.scenario[0][20]]
            if results_selected==[]:
                st.warning("You must select at least one option to continue.")
            else:
                pst.ask_tier(1,smr_selected)          
                fig=hplt.plotting_comp(results_selected,st.session_state.tier[1],st.session_state.LCIA,scenario_name=selected_list)
    
        

elif st.session_state['comparison_choice'] == "Comparison with an alternative technology":
    results=[]
    scope=pst.ask_scope()
    if scope is None:
        st.warning("You must define FU and LCIA to continue.")
    else: 
        with st.expander("click here to update scenarios"):
            k = 0
            while k < len(st.session_state.scenario):
                results.append(pst.ask(k))

                if k == len(st.session_state.scenario) - 1:
                    if st.button("Create New Scenario", key=f"button_scena_{len(st.session_state.scenario)}"):
                        sv.add_scenario()

                k += 1

        hydrogen_selected=[st.session_state.scenario[scenario_k][0] for scenario_k in range (len(st.session_state.scenario)) if results[scenario_k]!=None]
        name_selected_to_scenario_k = {st.session_state.scenario[k][0]: k for k in range(len(results))}
        if hydrogen_selected==[]:
            st.warning("You must define at least one scenario to continue.")
        else:
            #PLACEHOLDER_FCEL = "-- Select --"
            # Ensure placeholder is present (and first)
            options = [h for h in hydrogen_selected]
            # Default = only placeholder selected
            selected_list = st.multiselect(
                'Hydrogen Systems Compared',
                options=options,
                default=[],
                key='h2_scenario',
                help="Select one or more hydrogen product systems to be compared with alternative technologies."
            )

            results_selected=[results[name_selected_to_scenario_k[name]] for name in selected_list]                   
            #result=np.concatenate(result[0])
            #result=[np.sum(result,axis=0)]
            #labels=[st.session_state.scenario[0][20]]
            if results_selected==[]:
                st.warning("You must select at least one option to continue.")
            else:
                for k in range (len(results_selected)):
                    res=np.concatenate(results_selected[k][0])
                    res=np.sum(res,axis=0)
                    results_selected[k]=res
                labels=selected_list
                            
                st.markdown("<p style='font-size:18px'><u><b>Alternative Technology</b> </u></p>", unsafe_allow_html=True)
                if st.session_state.name_file_techno == None:
                    st.error('No alternative available. Please compare directly with FC&EL system comparison.')
                else:
                    techno_dict, techno_selected = pst.techno_available(st.session_state.name_file_techno)

                    PLACEHOLDER = "-- Select --"
                    # Ensure placeholder is present (and first)
                    options = [PLACEHOLDER] + [t for t in techno_selected if t != PLACEHOLDER]

                    # Default = only placeholder selected
                    selected_list = st.multiselect(
                        'Technologies Compared',
                        options=options,
                        default=[PLACEHOLDER],
                        key='techno_scenario',
                        help="Select one or more functionally equivalent technologies to compare with the reference FC&EL system."
                    )

                    # Drop placeholder from the working list; deduplicate while preserving order
                    chosen = [t for t in selected_list if t != PLACEHOLDER]
                    chosen = list(dict.fromkeys(chosen))

                    if not chosen:
                        st.warning("You must select at least one option to continue.")
                    else:
                        # Compute impacts for each selected technology
                        tech_impacts = [mh.impact_techno(techno_dict, t) for t in chosen]
                        result_techno = np.array(tech_impacts)   # shape: (n_selected, ...)

                        # Extend labels with the chosen technology names
                        
                        labels_extended = labels + chosen

                        # Plot
                        fig = hplt.plotting_technosphere(
                            results_selected,                 # baseline
                            result_techno,          # compared technologies
                            st.session_state.LCIA,  # LCIA selection
                            labels_extended
                        )
                

