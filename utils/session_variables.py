#!/usr/bin/env python
# coding: utf-8

# In[146]:

import streamlit as st
import pandas as pd
import utils.H2_version as vrs
import utils.credential_ecoinvent as cred
import parameters.physical_constant as phys

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

def dictionary():
    electrolyser_baseline_dict=file_opening_dict_index2('data/baseline/electrolyser_baseline.csv')
    fuelcell_baseline_dict=file_opening_dict_index2('data/baseline/fuelcell_baseline.csv')
    electrolyser_project_dict=file_opening_dict('data/baseline/electrolyser_project.csv')
    fuelcell_project_dict=file_opening_dict('data/baseline/fuelcell_project.csv')
    storage_dict=file_opening_dict_index2('data/impact_assessment/storage_database.csv')
    distrib_dict=file_opening_dict_index2('data/impact_assessment/distrib_database.csv')
    elec_dict=file_opening_dict('data/baseline/elec_mix.csv')
    heat_dict=file_opening_dict('data/baseline/heat_mix.csv')
    enduse_dict=file_opening_dict('data/impact_assessment/enduse_database.csv')
    mat_dict=file_opening_dict('data/impact_assessment/material_database.csv')
    cons_dict=file_opening_dict('data/impact_assessment/consumables_database.csv')
    bop_dict=file_opening_dict('data/impact_assessment/BoP_database.csv')
    st.session_state.dictionary= [electrolyser_baseline_dict,fuelcell_baseline_dict,electrolyser_project_dict,fuelcell_project_dict,storage_dict,distrib_dict,elec_dict, heat_dict,enduse_dict,mat_dict,cons_dict,bop_dict]

def key_dictionary():
    electrolyser_baseline_list=list(st.session_state.dictionary[0].keys())  
    fuelcell_baseline_list=list(st.session_state.dictionary[1].keys())  
    electrolyser_project_list=list(st.session_state.dictionary[2].keys())  
    fuelcell_project_list=list(st.session_state.dictionary[3].keys())  
    storage_list=list(st.session_state.dictionary[4].keys())  
    distrib_list=list(st.session_state.dictionary[5].keys())  
    elec_list=list(st.session_state.dictionary[6].keys())  
    heat_list=list(st.session_state.dictionary[7].keys())
    enduse_list=list(st.session_state.dictionary[8].keys())
    mat_list=list(st.session_state.dictionary[9].keys())
    st.session_state.list_dictionary=[electrolyser_baseline_list,fuelcell_baseline_list,electrolyser_project_list,fuelcell_project_list,storage_list,distrib_list,elec_list,heat_list,enduse_list,mat_list]

def scope():
    st.session_state.FU='-- Select --'
    st.session_state.LCIA='-- Select --'
    st.session_state.kgH2_per_FU=None
    st.session_state.name_file_techno=None #name of .csv containing alternative techno for the given functional unit
    st.session_state.FC=None #True if fuel cell is required for the given FU; False if not.
    st.session_state.boundaries='-- Select --'
    st.session_state.enduse_process=None 
    st.session_state.purity_enduse='Grade A (98%)'

def scenario():
    st.session_state.scenario = [] #list containing the baseline
    st.session_state.scenario.append([f"Scenario {1}",'Electrolysis',1.0,'Grade A (98%)','Baseline','-- Select --','-- Select --',1.0,'-- Select --',['-- Select --','Current Performance 2025'],['-- Select --','Current Performance 2025'],'Baseline','-- Select --','-- Select --',30,'-- Select --','-- Select --',False,'-- Select --'])
    st.session_state.tier=[[False,False,[[True,False],[False]*17],['None','FU'],False],[False,False,[[True,False],[False]*17],['None','FU'],False]]
    st.session_state.SMR=[False] #if one of the scenario contains hydrogen production through SMR and not electrolysis.
    st.session_state.characteristic_h2_produced=None
    st.session_state.requirements=None

def add_scenario():
        n=len(st.session_state.scenario)
        st.session_state.scenario.append([f"Scenario {n+1}",'Electrolysis',1.0,'Grade A (98%)','Baseline','-- Select --','-- Select --',1.0,'-- Select --',['-- Select --','Current Performance 2025'],['-- Select --','Current Performance 2025'],'Baseline','-- Select --','-- Select --',30,'-- Select --','-- Select --',False,'-- Select --'])
        st.session_state.SMR.append(False)

LOGIN_URL = "https://htwol-co2.streamlit.app/"

def require_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in =vrs.log()

    if st.session_state.logged_in:
        return

    st.title("Ecoinvent Login")


    st.write(f"Please enter your ecoinvent login to continue on the HTWOL complete version. If you do not have an ecoinvent license, please visit our open-access HTWOL Demonstrator (with only CO2 impact category): {LOGIN_URL}")

    st.write("Ecoinvent login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Connect"):
        if username and password:
            ok = cred.test_ecoinvent_connection(username, password)
            st.session_state.logged_in = bool(ok)
            if st.session_state.logged_in:
                st.rerun()
        else:
            st.warning("Please fill in the username and password.")

    st.stop()  # page blanche en dehors de la boîte de login

def init_session():
    if "dictionary" not in st.session_state:
        dictionary()
        key_dictionary()
    
    if "scenario" not in st.session_state:
        scenario()
    if "FU" not in st.session_state:
        scope()

    phys.physical_constant()
    require_login()



