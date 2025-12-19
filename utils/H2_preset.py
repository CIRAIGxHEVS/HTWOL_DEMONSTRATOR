#!/usr/bin/env python
# coding: utf-8

# In[146]:

import streamlit as st
import pandas as pd
import ast
import model.calculator as mh
import numpy as np
import utils.H2_version as vrs
import utils.H2_export as ext
import utils.session_variables as sv
from collections import defaultdict

FU_selected=vrs.FU_selected()
LCIA_selected=vrs.LCIA_selected()
TRL_selected=['-- Select --','Current Performance 2025','Target 2030','Target 2050']
TRL_storage_selected=['Current Performance 2025','Target 2030','Target 2050']
exergy_selected=[False,True]
h2_prod_selected=['Electrolysis','Steam Methane Reforming']
model_selected=['Baseline','Personalized']
purity_selected=['Grade A (98%)','Grade D (99.97%)','UltraPure (99.999%)']


def file_opening_dict(name):
    with open(name) as file_name:
        df = pd.read_csv(file_name,index_col=0, sep=';')
        scenarios = df.to_dict(orient='list')
    return scenarios

def file_opening_dict_index2(name):
    df = pd.read_csv(name, header=[0, 1], index_col=0, sep=';')
    return {
        level1: {
            level2: df[(level1, level2)].tolist()
            for level2 in df[level1].columns
        }
        for level1 in df.columns.levels[0]
    }

    
def techno_available(name_file_techno):
    techno_dict=sv.file_opening_dict(name_file_techno)
    techno_list = list(techno_dict.keys())
    return techno_dict,techno_list
    
# In[150]:

def ref_to_sublist(name_ref,baseline,electrolyser=True):
    if electrolyser:
        if baseline=='Personalized':
            ref_parameter=st.session_state.dictionary[2][name_ref]
        else:
            ref_parameter=st.session_state.dictionary[0][name_ref][baseline]
    else:
        if baseline=='Personalized':
            ref_parameter=st.session_state.dictionary[3][name_ref]
        else:
            ref_parameter=st.session_state.dictionary[1][name_ref][baseline]

    param_cell=[float(x) for x in ref_parameter[0:1]]
    param_stack=[float(x) for x in ref_parameter[1:5]]
    param_he = [float(ref_parameter[5]), float(ref_parameter[6]), ref_parameter[7], ast.literal_eval(ref_parameter[8])]
    param_oe = [float(ref_parameter[9]), float(ref_parameter[10]), ref_parameter[11], ast.literal_eval(ref_parameter[12])]
    param_bl = [float(ref_parameter[13]), float(ref_parameter[14]), ref_parameter[15], ast.literal_eval(ref_parameter[16])]
    param_cl = [float(ref_parameter[17]), float(ref_parameter[18]), ref_parameter[19], ast.literal_eval(ref_parameter[20])]
    param_el = [float(ref_parameter[21]), float(ref_parameter[22]), ref_parameter[23], ast.literal_eval(ref_parameter[24])]
    param_bp = [float(ref_parameter[25]), float(ref_parameter[26]), ref_parameter[27], ast.literal_eval(ref_parameter[28])]
    param_frame = [float(ref_parameter[29]), ref_parameter[30], float(ref_parameter[31]), ref_parameter[32], float(ref_parameter[33]), ref_parameter[34]]
    param_ep = [float(ref_parameter[35]), float(ref_parameter[36]), ref_parameter[37], ast.literal_eval(ref_parameter[38])]
    lifetime_bop = float(ref_parameter[39])
    list_bop = ['Compressor [kW]', 'HEX [m2]', 'Chiller [kW]', 'Rectifier [kW]', 'Separator [m3]', 'Pump [kW]', 'Piping [kg]', 'Instrumentation [kW]', 'Tank [kg]', 'Container [m3]']
    size_bop = [float(x) for x in ref_parameter[40:50]]
    param_bop = [lifetime_bop, list_bop, size_bop]
    param_cons = [float(x) for x in ref_parameter[50:58]]
    param_h2 = [float(x) for x in ref_parameter[58:61]]

    
    return param_cell,param_stack,param_he,param_oe,param_bl,param_cl,param_el,param_bp,param_frame,param_ep,param_bop,param_cons,param_h2


    
    
# In[151]:


def mix_name_to_list (name,elec=True):
    if elec:
        mix=st.session_state.dictionary[6][name]
    else:
        mix=st.session_state.dictionary[7][name]
    return mix
    
def ask_scope():
    
    st.markdown("<p style='font-size:18px'><u><b>Scope Definition</b> </u></p>", unsafe_allow_html=True)
        
    ## Selection of FU, the LCIA and preparation of the pre-set configurations collection according to the FU selected. ##

    col1, col2,col3= st.columns(3)
    
    with col1: 
        st.session_state.FU=st.selectbox("Functional Unit", FU_selected, index=FU_selected.index(st.session_state.FU), key='functional unit input',help="The reference basis of comparison of an LCA")
    with col2:
        st.session_state.LCIA = st.selectbox("LCIA Method", LCIA_selected, index=LCIA_selected.index(st.session_state.LCIA), key='LCIA input',help="Impact assessment method")    
	
    
    alternative_technologies_path = r"data/alternative_technologies"
    if st.session_state.FU == '-- Select --' or st.session_state.LCIA == '-- Select --' :
        return None
    elif st.session_state.FU=='1 kg H2':
        st.session_state.kgH2_per_FU = 1
        st.session_state.FC=False
        st.session_state.enduse_process=None
        st.session_state.name_file_techno=None
        st.session_state.boundaries=[True,None]
    elif st.session_state.FU=='1 MJ Heat':
        st.session_state.enduse_process='Burner' 
        kwh_per_FU=st.session_state.dictionary[8][st.session_state.enduse_process][0]
        st.session_state.purity_enduse='Grade A (98%)'
        st.session_state.kgH2_per_FU=kwh_per_FU/st.session_state.LHV_hydrogen #theoretical quantity of H2 to be converted by the FC for supplying the kWh_per_FU
        st.session_state.FC=False
        st.session_state.name_file_techno=alternative_technologies_path +r'/alt_heat_prod.csv'
        st.session_state.boundaries=[True,None]
    elif st.session_state.FU =='1 MJ co-generation':
        kwh_per_FU=1/3.6
        st.session_state.kgH2_per_FU = kwh_per_FU/st.session_state.LHV_hydrogen
        st.session_state.FC=True
        prodelec=True
        heat_allocation='energy'
        st.session_state.boundaries=[prodelec,heat_allocation]       
        st.session_state.enduse_process=None
        st.session_state.name_file_techno=alternative_technologies_path +r'/alt_cogeneration.csv'
    elif st.session_state.FU=='1 kWh stored':
        kwh_per_FU=1
        st.session_state.kgH2_per_FU=kwh_per_FU/st.session_state.LHV_hydrogen #theoretical quantity of H2 to be converted by the FC for supplying the kWh_per_FU
        st.session_state.FC=True
        prodelec=False
        heat_allocation='exergy'
        st.session_state.boundaries=[prodelec,heat_allocation] 
        st.session_state.enduse_process=None   
        st.session_state.name_file_techno=alternative_technologies_path +r'/alt_elec_storage.csv'
    elif st.session_state.FU=='1 kWh controllable electricity':
        kwh_per_FU=1
        st.session_state.kgH2_per_FU =kwh_per_FU/st.session_state.LHV_hydrogen #theoretical quantity of H2 to be converted by the FC for supplying the kWh_per_FU
        st.session_state.FC=True
        prodelec=True
        heat_allocation='exergy'
        st.session_state.boundaries=[prodelec,heat_allocation] 
        st.session_state.enduse_process=None
        st.session_state.name_file_techno=alternative_technologies_path +r'/alt_controllable_elec_prod.csv' 
    elif st.session_state.FU=='1 v.km fuel cell vehicle':
        st.session_state.enduse_process='FCEV' 
        kwh_per_FU=st.session_state.dictionary[8][st.session_state.enduse_process][0]
        st.session_state.purity_enduse='UltraPure (99.999%)'
        st.session_state.kgH2_per_FU=kwh_per_FU/st.session_state.LHV_hydrogen #theoretical quantity of H2 to be converted by the FC for supplying the kWh_per_FU
        st.session_state.FC=True
        prodelec=True
        heat_allocation='None'
        st.session_state.boundaries=[prodelec,heat_allocation] 
        st.session_state.name_file_techno=alternative_technologies_path +r'/alt_auto.csv'
    elif st.session_state.FU=='1 t.km shipping (e-fuel)':
        st.session_state.enduse_process='Ship' 
        kwh_per_FU=st.session_state.dictionary[8][st.session_state.enduse_process][0]
        st.session_state.purity_enduse='Grade D (99.97%)'
        st.session_state.kgH2_per_FU=kwh_per_FU/st.session_state.LHV_hydrogen #theoretical quantity of H2 to be converted by the FC for supplying the kWh_per_FU
        st.session_state.FC=False
        st.session_state.boundaries=[True,None] 
        st.session_state.name_file_techno=alternative_technologies_path +r'/alt_shipping.csv'
    return True

def ask(scenario_k):
    if st.session_state.scenario[scenario_k]==None:    
        col1,col2=st.columns(2)
        with col1:
            if st.button("Create New Scenario", key=f"button_scena_{scenario_k}"):
                pass
        with col2:
            with st.expander("Import: Upload Scenario "):
                uploaded_file = st.file_uploader("Upload your Scenario (CSV from HTWOL only)", type="csv", key=f"uploader_csv_{scenario_k}")
                if uploaded_file:
                    if st.button(f"Confirm Uploading"):
                        st.session_state.scenario[scenario_k] = ext.import_scenario(uploaded_file)
    
    if st.session_state.scenario[scenario_k]==None:
        return None
    
    ## Visualization + Name of the scenario ##
    col1,col2,col3=st.columns(3)  
    with col1:    
        st.markdown("""
        <style>
        /* make text inside ALL st.text_input bold */
        div[data-testid="stTextInput"] input {
            font-weight: 700;
            }
        </style>
        """, unsafe_allow_html=True)
        st.session_state.scenario[scenario_k][0]=st.text_input("Scenario Name", value=st.session_state.scenario[scenario_k][0], key=f"name_{scenario_k}")
	
    with st.expander("Click to define the scenario"):

        ## Hydrogen Requirements for the Application ##
        if st.session_state.FU=='1 kg H2':
            st.markdown("<p style='font-size:18px'><u><b>Hydrogen Requirements</b> </u></p>", unsafe_allow_html=True)	
            col1, col2= st.columns(2)
            with col1:
                st.session_state.scenario[scenario_k][2]=st.number_input("Pressure Required [bar]", value=st.session_state.scenario[scenario_k][2], key=f"pressure_{scenario_k}",help="Hydrogen pressure required by the final application")
            with col2:
                st.session_state.scenario[scenario_k][3]=st.selectbox("Purity Required [%]", purity_selected,index=purity_selected.index(st.session_state.scenario[scenario_k][3]), key=f"purity_{scenario_k}",help="Hydrogen purity required by the final application")
        
        elif st.session_state.enduse_process != None:
            st.session_state.scenario[scenario_k][2]=1
            st.session_state.scenario[scenario_k][3]=st.session_state.purity_enduse
        else:
            st.session_state.scenario[scenario_k][2]=1
            st.session_state.scenario[scenario_k][3]='Grade A (98%)'
        

        pressure_app=st.session_state.scenario[scenario_k][2]
        if st.session_state.scenario[scenario_k][3]=='Grade A (98%)':
            purity_app=98
        elif st.session_state.scenario[scenario_k][3]=='Grade D (99.97%)':
            purity_app=99.97
        elif st.session_state.scenario[scenario_k][3]=='UltraPure (99.999%)':
            purity_app=99.999

        requirement_app=[pressure_app,purity_app]
        heat_demand=False


        ## Type of hydrogen production and short cut if SMR ##
        if st.session_state.FU =='1 kWh stored':
            st.session_state.scenario[scenario_k][1] = 'Electrolysis'
        else:
            st.markdown("<p style='font-size:18px'><u><b>Hydrogen Production Method</b> </u></p>", unsafe_allow_html=True)
            st.session_state.scenario[scenario_k][1] = st.selectbox('Type of H2 production', h2_prod_selected, index=h2_prod_selected.index(st.session_state.scenario[scenario_k][1]), key=f"hydrogen_type_{scenario_k}",help="Type of hydrogen production.")
            if st.session_state.scenario[scenario_k][1] == '-- Select --':
                return None
            
        if st.session_state.scenario[scenario_k][1] != 'Electrolysis':
            st.session_state.SMR[scenario_k]=True
            st.session_state.scenario[scenario_k][7]=st.number_input("Flowrate of the Hydrogen Production [kgH2/h])", value=st.session_state.scenario[scenario_k][7], key=f"flowrate_{scenario_k}",help="Production scale of the system")
            input_EL=[st.session_state.scenario[scenario_k][1]]

        ## Pre-set configurations of the electrolyser ##
        else:
            st.session_state.SMR[scenario_k]=False

        
            st.markdown("<p style='font-size:18px'><u><b>Electrolyser Characteristics</b> </u></p>", unsafe_allow_html=True)
            
            col1, col2,col3,col4 = st.columns(4) 	
            with col1:
                st.session_state.scenario[scenario_k][4] = st.selectbox('Baseline or Custom Model', model_selected, index=model_selected.index(st.session_state.scenario[scenario_k][4]), key=f"model_{scenario_k}",help="Baseline: pre-set standard configuration; Custom: your own personalized model/project model.")
                
            if st.session_state.scenario[scenario_k][4] == 'Baseline':
                
                with col2:
                    st.session_state.scenario[scenario_k][5] = st.selectbox('Electrolyser \n Type', st.session_state.list_dictionary[0], index=st.session_state.list_dictionary[0].index(st.session_state.scenario[scenario_k][5]), key=f"electrolyser_{scenario_k}",help="Select the electrolyser baseline technology")
                with col4:
                    st.session_state.scenario[scenario_k][6]=st.selectbox('Electrolyser \n Maturity', TRL_selected, index=TRL_selected.index(st.session_state.scenario[scenario_k][6]), key=f"TRL_{scenario_k}",help="Select the technology level of maturity")
            
            else:
                with col2:
                    st.session_state.scenario[scenario_k][8] = st.selectbox('Electrolyser \nModel', st.session_state.list_dictionary[2], index=st.session_state.list_dictionary[2].index(st.session_state.scenario[scenario_k][8]), key=f"electrolysername_{scenario_k}",help="Select your personalized electrolyser model")   
                    
            with col3:       
                st.session_state.scenario[scenario_k][7]=st.number_input("Size of the System [kgH2/h])", value=st.session_state.scenario[scenario_k][7], key=f"flowrate_{scenario_k}",help="Production scale of the system")

            
            if st.session_state.scenario[scenario_k][4] == 'Baseline':
                if st.session_state.scenario[scenario_k][5] == '-- Select --' or st.session_state.scenario[scenario_k][6]  == '-- Select --' or st.session_state.scenario[scenario_k][7]  == '-- Select --':
                    return None
                param_cell,param_stack,param_he,param_oe,param_bl,param_cl,param_el,param_bp,param_frame,param_ep,param_bop,param_cons,characteristic_h2_produced=ref_to_sublist(st.session_state.scenario[scenario_k][5],st.session_state.scenario[scenario_k][6],True)
            else:
                if st.session_state.scenario[scenario_k][8] == '-- Select --' or st.session_state.scenario[scenario_k][7]  == '-- Select --':
                    return None
                param_cell,param_stack,param_he,param_oe,param_bl,param_cl,param_el,param_bp,param_frame,param_ep,param_bop,param_cons,characteristic_h2_produced=ref_to_sublist(st.session_state.scenario[scenario_k][8],'Personalized',True)
        
            component = [param_he, param_oe, param_bl, param_cl, param_el, param_bp, param_frame, param_ep]
            e_cell = component[:6]
            e_stack = component[6:]
            size_EL=st.session_state.scenario[scenario_k][7]
            input_EL=[size_EL, param_cell, e_cell, param_stack, e_stack, param_bop, param_cons,characteristic_h2_produced]
            if param_cons[3]>0:
                heat_demand=True

        ## Pre-set configurations of the supply chain processes : storage and distribution ##
        st.markdown("<p style='font-size:18px'><u><b>Storage and Distribution Scenario</b> </u></p>", unsafe_allow_html=True)
        col1, col2,col3 = st.columns(3)
        with col1:
            st.session_state.scenario[scenario_k][9][0] = st.selectbox('Storage Type', st.session_state.list_dictionary[4], index=st.session_state.list_dictionary[4].index(st.session_state.scenario[scenario_k][9][0]), key=f"storage_{scenario_k}",help="Select the type of hydrogen storage, if any")
        with col2:
            st.session_state.scenario[scenario_k][10][0] = st.selectbox('Distribution Type', st.session_state.list_dictionary[5], index=st.session_state.list_dictionary[5].index(st.session_state.scenario[scenario_k][10][0]), key=f"distrib_{scenario_k}",help="Select distribution method from the central facility to the use site")
                    
        if (st.session_state.scenario[scenario_k][9][0]!='-- Select --' and st.session_state.scenario[scenario_k][9][0]!='None') or (st.session_state.scenario[scenario_k][10][0]!='-- Select --' and st.session_state.scenario[scenario_k][10][0]!='None'):
            with col3:
                st.session_state.scenario[scenario_k][9][1]=st.selectbox('Storage&Distrib. \n Maturity', TRL_storage_selected, index=TRL_storage_selected.index(st.session_state.scenario[scenario_k][9][1]), key=f"mat_SD_{scenario_k}",help="Select the technology level of maturity")
                st.session_state.scenario[scenario_k][10][1]=st.session_state.scenario[scenario_k][9][1]
                if st.session_state.scenario[scenario_k][9][1] == '-- Select --':
                    return None

        if st.session_state.scenario[scenario_k][9][0] == '-- Select --' or st.session_state.scenario[scenario_k][10][0] == '-- Select --':
            return None
        
        supply_chain=[st.session_state.scenario[scenario_k][7],st.session_state.scenario[scenario_k][9],st.session_state.scenario[scenario_k][10]]

        
        ## Pre-set configurations of the Fuel Cell if required ##
        if st.session_state.FC:
            st.markdown("<p style='font-size:18px'><u><b>Fuel Cell Characteristics</b> </u></p>", unsafe_allow_html=True)
            col1, col2,col3,col4 = st.columns(4)
            with col1:
                st.session_state.scenario[scenario_k][11] = st.selectbox('Baseline or Custom Model', model_selected, index=model_selected.index(st.session_state.scenario[scenario_k][11]), key=f"model_fc_{scenario_k}",help="Baseline: pre-set standard configuration; Custom: your own personalized model/project model.")
            
            if st.session_state.scenario[scenario_k][11] == 'Baseline':
            
                with col2:
                    st.session_state.scenario[scenario_k][12] = st.selectbox('Fuel Cell Type', st.session_state.list_dictionary[1], index=st.session_state.list_dictionary[1].index(st.session_state.scenario[scenario_k][12]), key=f"fuelcell_{scenario_k}",help="Select the fuel cell baseline technology")
                with col4:
                    st.session_state.scenario[scenario_k][13] = st.selectbox('Fuel Cell Maturity', TRL_selected, index=TRL_selected.index(st.session_state.scenario[scenario_k][13]), key=f"fuelcellTRL_{scenario_k}",help="Select the technology level of maturity")
                    
                    
            else:
                with col2:
                    st.session_state.scenario[scenario_k][15] = st.selectbox('Fuel Cell \nModel', st.session_state.list_dictionary[3], index=st.session_state.list_dictionary[3].index(st.session_state.scenario[scenario_k][15]), key=f"fuelcellname_{scenario_k}")  
 
            with col3:
                st.session_state.scenario[scenario_k][14]=st.number_input("Size of the System [kW]", value=st.session_state.scenario[scenario_k][14], key=f"power_{scenario_k}",help="Electrical Power required by the final application")

            if st.session_state.scenario[scenario_k][11] == 'Baseline':
                if st.session_state.scenario[scenario_k][12] == '-- Select --' or st.session_state.scenario[scenario_k][13]  == '-- Select --' or st.session_state.scenario[scenario_k][14]  == '-- Select --':
                    return None
                param_cell_FC,param_stack_FC,param_he_FC,param_oe_FC,param_bl_FC,param_cl_FC,param_el_FC,param_bp_FC,param_frame_FC,param_ep_FC,param_bop_FC,param_cons_FC,param_h2_FC=ref_to_sublist(st.session_state.scenario[scenario_k][12],st.session_state.scenario[scenario_k][13],False)
            else:
                if st.session_state.scenario[scenario_k][15] == '-- Select --' or st.session_state.scenario[scenario_k][14]  == '-- Select --':
                    return None
                param_cell_FC,param_stack_FC,param_he_FC,param_oe_FC,param_bl_FC,param_cl_FC,param_el_FC,param_bp_FC,param_frame_FC,param_ep_FC,param_bop_FC,param_cons_FC,param_h2_FC=ref_to_sublist(st.session_state.scenario[scenario_k][15],'Personalized',False)
                
            component_FC = [param_he_FC, param_oe_FC, param_bl_FC, param_cl_FC, param_el_FC, param_bp_FC, param_frame_FC, param_ep_FC]
            e_cell_FC = component_FC[:6]
            e_stack_FC = component_FC[6:]
            P_stack=st.session_state.scenario[scenario_k][14]
            input_FC=[P_stack, param_cell_FC, e_cell_FC, param_stack_FC, e_stack_FC, param_bop_FC, param_cons_FC]

            ## Update of post-processing and requirements
            pressure_FC=param_h2_FC[0]
            purity_FC=param_h2_FC[2]
            requirement_FC=[pressure_FC,purity_FC]

        else:
            input_FC=None
            requirement_FC=None


        ## Pre-set configurations of the energy mixes and scenarios (heat recovered?) ##
        st.markdown("<p style='font-size:18px'><u><b>Energy Scenario</b> </u></p>", unsafe_allow_html=True)        
        col1, col2,col3 = st.columns(3) 
        with col1:
            st.session_state.scenario[scenario_k][16]=st.selectbox('Electricity Mix Scenario', st.session_state.list_dictionary[6], index=st.session_state.list_dictionary[6].index(st.session_state.scenario[scenario_k][16]), key=f"elecmix_{scenario_k}",help="Select the source of electricity used")
    
        if st.session_state.FC:
            T_stack=param_h2_FC[1]
            if st.session_state.boundaries[1]=='energy':
                heat_recovery=['energy',T_stack]

            elif st.session_state.boundaries[1]=='exergy':
                with col3:
                    st.session_state.scenario[scenario_k][17]=st.selectbox('Heat Recovered? (exergy allocation)', exergy_selected, index=exergy_selected.index(st.session_state.scenario[scenario_k][17]), key=f"exergy_{scenario_k}",help="Is the heat co-produced by the system recovered? (an exergy allocation is used)")
                    if st.session_state.scenario[scenario_k][17]:
                        heat_recovery=['exergy',T_stack]
                    else:
                        heat_recovery=['None',T_stack]
            else:
                heat_recovery=['None',T_stack]
            input_FC.append(heat_recovery)

        
        if heat_demand:
            with col2:
                st.session_state.scenario[scenario_k][18]=st.selectbox('Heat Mix Scenario', st.session_state.list_dictionary[7], index=st.session_state.list_dictionary[7].index(st.session_state.scenario[scenario_k][18]), key=f"heatmix_{scenario_k}",help="Select the source of heat used")
            if st.session_state.scenario[scenario_k][18] == '-- Select --':
                return None
            heat_mix=mix_name_to_list(st.session_state.scenario[scenario_k][18],False)
        else:
            heat_mix=mix_name_to_list('Available',False)
     
        if st.session_state.scenario[scenario_k][16] == '-- Select --' :
            return None       
        
        
        elec_mix=mix_name_to_list(st.session_state.scenario[scenario_k][16])
        

    requirement=[requirement_app,requirement_FC]
    boundaries_prodelec=st.session_state.boundaries[0]
    results=mh.generation_results(input_EL,input_FC,requirement,supply_chain,st.session_state.enduse_process,st.session_state.kgH2_per_FU,boundaries_prodelec,elec_mix,heat_mix)
    return results



def ask_tier(n,SMR):
    if SMR:
        st.session_state.tier[n][4]=True
    if not SMR :
        st.session_state.tier[n][4]=False
        st.markdown("<p style='font-size:16px'><u><b>Aggregation of Results</b> </u></p>", unsafe_allow_html=True)

        col1, col2,col3= st.columns(3)
        with col3:
            with st.expander("Zoom on a Specific Process"):
                if st.session_state.FC:
                    options_zoom=['None','Stack (EL)','BoP (EL)','Stack (FC)','BoP (FC)','Hydrogen Production','Hydrogen Reconversion']
                else:
                    options_zoom=['None','Stack (EL)','BoP (EL)','Hydrogen Production']
                st.session_state.tier[n][3][0] = st.selectbox("Which Process do you want to zoom on?", options=options_zoom, index=options_zoom.index(st.session_state.tier[n][3][0]),key='zoom_tier',help="Select if you want to zoom on a specific process")
                if st.session_state.tier[n][3][0] != "None":
                    st.session_state.tier[n][3][1]="FU"
                    if st.session_state.tier[n][3][0] == "Hydrogen Production":
                        zoom_FU_options=["FU","1 kgH2 produced"]
                    elif st.session_state.tier[n][3][0] == "Hydrogen Reconversion":
                        zoom_FU_options=["FU","1 kWh electricity produced"]
                    elif st.session_state.tier[n][3][0] == "Stack (EL)" or st.session_state.tier[n][3][0] == "BoP (EL)":
                        zoom_FU_options=["FU",f"1 electrolyser system"]
                    else:
                        zoom_FU_options=["FU",f"1 fuel cell system"]
                    st.session_state.tier[n][3][1] = st.selectbox("Define alternative scale/FU for the Zoom", options=zoom_FU_options, index=zoom_FU_options.index(st.session_state.tier[n][3][1]),key='zoom_FU',help="Select the FU to which the zoom should be scaled")

        if st.session_state.tier[n][3][0] == "None":
            with col1:
                with st.expander("Impacts Distribution"):
                    st.session_state.tier[n][0] = st.toggle("Classifying Impacts by Unit Processes", value=st.session_state.tier[n][0], key='elementary_tier',help="Check for more detailed on consumable processes impacts")
                    st.session_state.tier[n][1] = st.toggle("Distributing Impacts of H2 Surplus to Producer", value=st.session_state.tier[n][1], key='h2_surplus_tier',help="Check for more detailed on consumable processes impacts")

        with col2:
            if not st.session_state.tier[n][1] and st.session_state.tier[n][3][0] == "None":
                with st.expander("Level of Details"):
                    if not st.session_state.tier[n][0]:
                        st.write("Detailing Supply Chain Modules")
                        st.session_state.tier[n][2][0][0] = st.toggle("H2 Production", value=st.session_state.tier[n][2][0][0], key='detailed_H2') 
                        st.session_state.tier[n][2][0][1] = st.toggle("Post-Processing", value=st.session_state.tier[n][2][0][1], key='detailed_PP') 
                        st.write("Detailing Unit Processes from Supply Chain Modules")
                        st.session_state.tier[n][2][1][0] = st.toggle("H2 Production", value=st.session_state.tier[n][2][1][0], key='tier_prod')
                        st.session_state.tier[n][2][1][1] = st.session_state.tier[n][2][1][0]
                        st.session_state.tier[n][2][1][2] = st.toggle("Post-Processing", value=st.session_state.tier[n][2][1][2], key='tier_PP')
                        st.session_state.tier[n][2][1][3] = st.session_state.tier[n][2][1][2]
                        st.session_state.tier[n][2][1][4] = st.toggle("Distribution", value=st.session_state.tier[n][2][1][4], key='tier_distrib') 
                        st.session_state.tier[n][2][1][5] = st.toggle("Storage", value=st.session_state.tier[n][2][1][5], key='tier_storage') 
                        if st.session_state.FC: 
                            st.session_state.tier[n][2][1][6] = st.toggle("H2 Reconversion", value=st.session_state.tier[n][2][1][6], key='tier_fuelcell')
                        if st.session_state.enduse_process != None: 
                            st.session_state.tier[n][2][1][7] = st.toggle("End-Use Process", value=st.session_state.tier[n][2][1][7], key='tier_eup') 
                    else:
                        st.write("Detailing Supply Chain Module Contribution to Unit Processes")
                        st.session_state.tier[n][2][1][8] = st.toggle("Electricity", value=st.session_state.tier[n][2][1][8], key='tier_elec')
                        st.session_state.tier[n][2][1][9] = st.toggle("Heat", value=st.session_state.tier[n][2][1][9], key='tier_heat')
                        st.session_state.tier[n][2][1][10] = st.toggle("Water", value=st.session_state.tier[n][2][1][10], key='tier_water')
                        st.session_state.tier[n][2][1][11] = st.toggle("KOH", value=st.session_state.tier[n][2][1][11], key='tier_koh')
                        st.session_state.tier[n][2][1][12] = st.toggle("Stack Manuf.", value=st.session_state.tier[n][2][1][12], key='tier_stack') 
                        st.session_state.tier[n][2][1][13] = st.toggle("Equip. Manuf", value=st.session_state.tier[n][2][1][13], key='tier_equip') 
                        st.session_state.tier[n][2][1][14] = st.toggle("EoL", value=st.session_state.tier[n][2][1][14], key='tier_eol') 
                        st.session_state.tier[n][2][1][15] = st.toggle("H2 Leakage", value=st.session_state.tier[n][2][1][15], key='tier_h2leak')
                        st.session_state.tier[n][2][1][16] = st.toggle("Surplus H2", value=st.session_state.tier[n][2][1][16], key='tier_surplus')  








mat_dict=st.session_state.dictionary[9]
mat_selected=st.session_state.list_dictionary[9]



def ask_detailed_stack(stack,FC):
    
    label_element=['Hydrogen Electrode','Oxygen Electrode', 'Barrier Layer', 'Contact Layer', 'Membrane', 'Bipolar Plate','End Plate', 'Structure']
    label_frame=['Frame','Current Collector','Sealant']
    add_selected=['coating','load','--select--']

    param_cell, param_stack, param_he, param_oe, param_bl, param_cl, param_el, param_bp, param_frame, param_ep, param_bop, param_cons,param_h2 = stack[:]      
    component = [param_he, param_oe, param_bl, param_cl, param_el, param_bp, param_frame, param_ep]
    e_cell = component[:6]
    e_stack = component[6:]
    
    # Ajouter trois boutons pour les zones bleu, verte et orange
    zone = st.radio("Please select a life cycle stage :", ["Stack Manuf.", "BoP Equipment", "Operation"])
    
    if zone == "Stack Manuf.":
        st.markdown("<p style='font-size:18px'><u><b>Stack and Cell Design</b> </u></p>", unsafe_allow_html=True)	
        
        col1, col2= st.columns(2)
        with col1:
            param_cell[0] = st.number_input("Active Surface [m2]", value=param_cell[0])
        with col2:
            param_stack[0] = st.number_input("Cell per Stack", value=param_stack[0])
        
        st.markdown("<p style='font-size:18px'><u><b>Degradation</b> </u></p>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)     
        with col1:
            param_stack[1] = st.number_input("Degradation Rate [%/1000h]", value=param_stack[1])
        with col2:
            param_stack[2] = st.number_input("Degradation Max [%]", value=param_stack[2])
            
        st.markdown("<p style='font-size:18px'><u><b>End-Of-Life</b> </u></p>", unsafe_allow_html=True)
        param_stack[3] = st.number_input("Recycling Rate Metal [-]", value=param_stack[3])

        st.markdown("<p style='font-size:18px'><u><b>Design of Stack Layers</b> </u></p>", unsafe_allow_html=True)    
        with st.expander("Components parameters (material, thickness, coating)"):
            for i, component in enumerate([param_he, param_oe, param_bl, param_cl, param_el, param_bp, param_ep]):
            
                if component[2] == "-- Not concerned --":
                    continue  # Passe au prochain composant si le matériau est "not concerned"

                st.write(label_element[i])
                col1, col2,col3 = st.columns(3)
                # Dans la première colonne, l'épaisseur
                with col1:
                    component[0] = float(st.text_input(f"Thickness [um]", value=str(component[0]), key=f"epaisseur_{i}"))
                    
                # Dans la deuxième colonne, le ratio surface
                with col2:
                    component[1] = float(st.text_input(f"Ratio Surface", value=str(component[1]), key=f"ratioS_{i}"))

            
                # Dans la 3e colonne, le matériau
                with col3:
                    component[2] = st.selectbox(f"Material", mat_selected, index=mat_selected.index(component[2]), key=f"materiau_{i}")
                    
                if component[3]:
                    col1, col2,col3,col4 = st.columns(4)
                    
                    with col1:
                        component[3][0] = st.selectbox(f"Additive Type ", add_selected, index=add_selected.index(component[3][0]), key=f"additivetype_{i}")    
                     
                     
                    with col2:
                        component[3][2] = st.selectbox(f"Add. Material", mat_selected, index=mat_selected.index(component[3][2]), key=f"additivemat_{i}")                    
                       
                    with col3:
                        if component[3][0]=='coating':
                            component[3][1] = float(st.text_input(f"Add. thickness [um] ", value=str(component[3][1]), key=f"additiveQ_{i}"))
                        else:
                            component[3][1] = float(st.text_input(f"Add. Quantity [mg/cm2] ", value=str(component[3][1]), key=f"additiveQ_{i}"))

                                            
                    with col4:
                        if st.button(f"❌", key=f"remove_add_{i}"):
                            component[3]=[]
                            st.rerun()  # Forcer le rechargement de la page après la suppression
                            
                else:
                    if st.button("add an additive", key=f"add_add_{i}"):
                       component[3]=['--select--',0,'-- Not concerned --']
                       st.rerun()
                        
                st.markdown("---")
                
            st.write('Stack Structure')
            for k in range (3):       
                    
                st.write(label_frame[k])
                col1, col2 = st.columns(2)
                
                with col1:
                    param_frame[2*k] = float(st.text_input(f"Quantity [kg/m2 of active area]", value=str(param_frame[2*k]), key=f"epaisseur_{8+k}"))
                with col2:
                    param_frame[2*k+1] = st.selectbox(f"Material", mat_selected, index=mat_selected.index(param_frame[2*k+1]), key=f"materiau_{8+k}")                 


    elif zone == "BoP Equipment":
    
        st.subheader("Equipment BoP Element and Parameters")
        # Modifier les paramètres BoP
        param_bop[0] = st.number_input("Lifetime [h]", value=param_bop[0])                
        
        with st.expander("Size of equipment of the BoP"):
            for i in range (len(param_bop[1])):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(param_bop[1][i])
                with col2:
                    param_bop[2][i] = st.number_input("Size of " + param_bop[1][i], value=param_bop[2][i], key=f"bop_value_{i}")

               

    elif zone == "Operation":
        st.subheader("Consumables Parameters")
        # Modifier les autres paramètres ici si besoin
        if FC:
            col1, col2,col3,col4,col5,col6,col7 = st.columns(7)
        else:
            col1, col2,col3,col4,col5,col6 = st.columns(6)
        with col1:
            param_cons[0] = st.number_input("BoL Voltage [V]", value=param_cons[0])
        with col2:
            param_cons[1] = st.number_input("Current Density [A/m2]", value=param_cons[1])         
        with col3:
            param_cons[4] = st.number_input("Water demand [L/kgH2]", value=param_cons[4])             
        with col4:
            param_cons[5] = st.number_input("KOH demand [L/kgH2]", value=param_cons[5])     
        with col5:
            param_cons[7] = st.number_input("H2 Leakage [-]", value=param_cons[7])    
        if FC:
            with col6:
                 param_cons[6] = st.number_input("Recoverable Heat [kWh/kgH2]", value=param_cons[6])    
            with col7:
                param_cons[2] = st.number_input("Fuel Utilization [rate]", value=param_cons[2])    
   
        else:
            with col6:
                param_cons[3] = st.number_input("Heat demand [kWh/kgH2]", value=param_cons[3])                                   
            
            
    return  [param_cell, param_stack, param_he, param_oe, param_bl, param_cl, param_el, param_bp, param_frame, param_ep, param_bop, param_cons,param_h2]
               
def ask_detailed_energy(mix,electricity):
    if electricity:
        mix[0] = st.number_input("Europe_Average", value=mix[0])
        mix[1] = st.number_input("Wind", value=mix[1])
        mix[2]= st.number_input("PV", value=mix[2])
        mix[3] = st.number_input("Hydro", value=mix[3])
        mix[4] = st.number_input("Nuclear", value=mix[4])
        if np.sum(np.array(mix))!=1:
            st.warning("The sum should be equal to 1.")
        return mix                
    
    else:           
        mix[0] = st.number_input("Natural Gas", value=mix[0])
        mix[1] = st.number_input("Electricity (heaters)", value=mix[1])
        mix[2]= st.number_input("Available on site", value=mix[2])
        if np.sum(np.array(mix))!=1:
            st.warning("The sum should be equal to 1.")
        return mix             


def sublist_to_ref(param_cell, param_stack, param_he, param_oe, param_bl, param_cl,
                   param_el, param_bp, param_frame, param_ep, param_bop, param_cons, param_h2):
    
    ref_parameter = []
    
    ref_parameter += [str(x) for x in param_cell]                     # [0]
    ref_parameter += [str(x) for x in param_stack]                    # [1:5]
    
    ref_parameter += [str(param_he[0]), str(param_he[1]), param_he[2], str(param_he[3])]  # [4:8]
    ref_parameter += [str(param_oe[0]), str(param_oe[1]), param_oe[2], str(param_oe[3])]  # [8:12]
    ref_parameter += [str(param_bl[0]), str(param_bl[1]), param_bl[2], str(param_bl[3])]  # [12:16]
    ref_parameter += [str(param_cl[0]), str(param_cl[1]), param_cl[2], str(param_cl[3])]  # [16:20]
    ref_parameter += [str(param_el[0]), str(param_el[1]), param_el[2], str(param_el[3])]  # [20:24]
    ref_parameter += [str(param_bp[0]), str(param_bp[1]), param_bp[2], str(param_bp[3])]  # [24:28]
    
    ref_parameter += [str(param_frame[0]), param_frame[1], str(param_frame[2]), param_frame[3], str(param_frame[4]), param_frame[5]]  # [28:34]
    
    ref_parameter += [str(param_ep[0]), str(param_ep[1]), param_ep[2], str(param_ep[3])]  # [34:38]
    
    ref_parameter += [str(param_bop[0])]  # lifetime_bop = [38]
    ref_parameter += [str(x) for x in param_bop[2]]  # size_bop = [39:49]
    
    ref_parameter += [str(x) for x in param_cons]  # [49:56]
    ref_parameter += [str(x) for x in param_h2]    # [56:59]

    return ref_parameter        
