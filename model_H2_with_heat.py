#!/usr/bin/env python
# coding: utf-8

# In[146]:


import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt
import copy
import streamlit as st


# In[147]:


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

    return result

# In[148]:


mat_dict=file_opening_dict('mat_database.csv')
cons_dict=file_opening_dict('consumables_database.csv')
bop_dict=file_opening_dict('BoP_database.csv')
elec_dict=file_opening_dict('elec_mix.csv')
heat_dict=file_opening_dict('heat_mix.csv')

enduse_dict=file_opening_dict('enduse_database.csv')
storage_dict=file_opening_dict_index2('storage_database.csv')
distrib_dict=file_opening_dict_index2('distrib_database.csv')


# In[149]:

    
def techno_available(name_file_techno):
    techno_dict=file_opening_dict(name_file_techno)
    techno_list = list(techno_dict.keys())
    return techno_dict,techno_list
    


# In[150]:




def mix_name_to_list (name,elec=True):
    if elec:
        mix=elec_dict[name]
    else:
        mix=heat_dict[name]
    return mix



# General Parameters #
Faraday=96485 #C/mol
electron=2 
M_H2=0.002016 #kg/mol
V_electrolysis=1.25 #[V] standard potential of the electrolysis of water 
LHV_hydrogen=33.3 #kWh/kg

RER_imp=np.array(cons_dict['RER'])
wind_imp=np.array(cons_dict['Wind'])
PV_imp=np.array(cons_dict['PV'])
hydro_imp=np.array(cons_dict['Hydro'])
nuclear_imp=np.array(cons_dict['Nuclear'])
NG_impact=np.array(cons_dict['NG'])
water_impact=np.array(cons_dict['Water'])
KOH_impact=np.array(cons_dict['KOH'])
leakage_impact=np.array(cons_dict['h2_leakage'])

N_cat=len(RER_imp)



# In[157]:


def electricity_impact(elec_mix):
    RER,wind,PV,hydro,nuclear=elec_mix
    return RER*RER_imp+wind*wind_imp+PV*PV_imp+hydro*hydro_imp+nuclear*nuclear_imp


# In[158]:


def heat_impact(heat_mix,elec_mix):
    NG,elec,recup=heat_mix
    elec_impact=electricity_impact(elec_mix)
    return NG*NG_impact+elec*elec_impact


def sizing_parameters (flow,voltage,J_dens,active_S_max,cell_per_stack):
    intensity=flow*Faraday*electron/(M_H2*3600)  #intensity in Ampere
    surface_tot=intensity/J_dens
    N_cell_min=(surface_tot/active_S_max)
    N_stack=np.ceil(N_cell_min/cell_per_stack)
    N_cell=N_stack*cell_per_stack
    active_S=surface_tot/N_cell    
    return active_S,N_cell,N_stack

# In[159]:


def impact_consumables (KP_consumables,elec_impact,heat_impact,water_impact,KOH_impact):
    elec_loss,elec_bop,heat_demand,water_demand,KOH_demand=KP_consumables
    i_elec_loss=elec_loss*elec_impact
    i_elec_bop=elec_bop*elec_impact
    i_heat=heat_demand*heat_impact
    i_water=water_demand*water_impact
    i_KOH=KOH_demand*KOH_impact
    i_elec=[i_elec_loss+i_elec_bop]
    i_other_cons=[i_water,i_KOH]
    return np.sum(i_elec, axis=0),i_heat,np.sum(i_other_cons, axis=0),i_elec,i_other_cons


def consumption_BoP (list_bop,size_bop_per_kg,flow): #to adapt to equipment power and BoP_per_stack
    P_bop=0
    for k in range (len(list_bop)):
        real_size=size_bop_per_kg[k]*flow
        P_bop+=bop_dict[list_bop[k]][0]*real_size

    return P_bop

# In[160]:


def impact_BoP (list_bop,size_bop_per_flow,flow,BoP_per_FU): #to adapt to equipment power and BoP_per_stack
    i_bop=[]
    for k in range (len(list_bop)):
        real_size=size_bop_per_flow[k]*flow
        unit_impact=bop_dict[list_bop[k]][2:]
        sizing_factor=bop_dict[list_bop[k]][1]
        i=np.array(unit_impact)*pow(real_size,sizing_factor)
        i_bop.append(i)
    i_bop=np.vstack(i_bop)
    i_bop=i_bop*BoP_per_FU
    
    return np.sum(i_bop, axis=0),i_bop

    
def power_compression (Pout,Pin,flow,Tin):
    hr=1.41
    R_gas=8.314
    Z_gas=1.024
    eff_comp=0.9*0.95
    rate_per_stage=2.1
    flow_mol=flow/M_H2/3600 #mol/s
    N_stage=np.ceil(np.log(Pout/Pin)/np.log(rate_per_stage))  #round to the next int
    

    
    P_comp=N_stage*hr/(hr-1)*flow_mol*Tin*R_gas*Z_gas/eff_comp*(pow((Pout/Pin),(hr-1)/(N_stage*hr))-1)/1000
    #print(P_comp)
    
    return P_comp


# In[171]:


def stack_component (active_S,element,recycling_rate=0):
    thickness,ratioS,name_mat,additive=element #thickness [um]
    
    material=mat_dict[name_mat]
    density=material[0]
    impact_mat=np.array(material[1:])
    mass_component=active_S*ratioS*thickness*1e-6*density
    i_component=impact_mat*mass_component
    
    i_add=np.zeros((7))
    mass_add=0
    if additive:
        type_add,quantity_add,name_add=additive #quantity for catalyst load in mg/cm2 and in um for coating thickness
        material_add=mat_dict[name_add]
        impact_add=np.array(material_add[1:])
        if type_add=='load':
            mass_add=active_S*ratioS*quantity_add*0.01
            i_add=impact_add*mass_add
        elif type_add=='coating':
            mass_add=active_S*ratioS*quantity_add*1e-6*density
            i_add=impact_add*mass_add
    
    inert=mat_dict['EoL_inert']
    i_eol_inert=np.array(inert[1:])
    mass_tot=mass_component+mass_add 
    i_eol_comp=i_eol_inert*mass_tot*(1-recycling_rate)   
    return (i_component+i_add),i_eol_comp  

# In[178]:
    
def frame_component (total_area,element,recycling_rate=0):
    quantity_per_m2,name_mat=element 
    
    material=mat_dict[name_mat]
    impact_mat=np.array(material[1:])
    mass_frame=quantity_per_m2*total_area
    i_frame=impact_mat*mass_frame
    
    inert=mat_dict['EoL_inert']
    i_eol_inert=np.array(inert[1:])
    i_eol_frame=i_eol_inert*mass_frame*(1-recycling_rate)       
    return i_frame,i_eol_frame    

# In[178]:


def impact_cell (active_S,element_cell):
    impact=[]
    impact_eol=[]
    for e in element_cell:
        i,i_eol_comp=stack_component(active_S,e)
        impact.append(i)
        impact_eol.append(i_eol_comp)
    impact=np.vstack(impact)
    return np.sum(impact, axis=0),impact,np.sum(impact_eol, axis=0)
    


# In[179]:


def impact_stack (stack_per_FU,cell,active_S,N_cell,e_stack,N_stack,recycling_rate=0):
    i_cell=cell[0]*N_cell
    detailed_cell=cell[1]*N_cell
    i_eol_cell=cell[2]*N_cell
    
    i_frame=(frame_component(active_S*N_cell,e_stack[0][:2],recycling_rate)[0]+frame_component(active_S*N_cell,e_stack[0][2:4],recycling_rate)[0]+frame_component(active_S*N_cell,e_stack[0][4:])[0])
    i_eol_frame=(frame_component(active_S*N_cell,e_stack[0][:2],recycling_rate)[1]+frame_component(active_S*N_cell,e_stack[0][2:4],recycling_rate)[1]+frame_component(active_S*N_cell,e_stack[0][4:])[1])
    
    i_ep=stack_component(active_S,e_stack[1],recycling_rate)[0]*2*N_stack #2 ends of the stack
    i_eol_ep=stack_component(active_S,e_stack[1],recycling_rate)[1]*2*N_stack

    i_element=np.vstack([detailed_cell, i_frame, i_ep])
    i_eol=np.vstack([i_eol_cell, i_eol_frame, i_eol_ep])

    i_element=i_element*stack_per_FU
    i_eol=i_eol*stack_per_FU
    
    return np.sum(i_element, axis=0),i_element,np.sum(i_eol, axis=0)


def impact_supply_infrastructure (i_eq,elec_cons,leakage_rate,elec_imp=np.zeros((7))):
    ## impact of equipment is given per kgH2 (stored/distributed/prepared) 
    i_elec=elec_cons*elec_imp
    i_leakage=leakage_rate*leakage_impact
    
    i_infra=[i_elec,np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),i_eq,np.zeros((N_cat)),i_leakage,[0,0,leakage_rate]]
    
    return i_infra
    


    
def total_impact_EC_per_kgH2 (operating,param_cell,element_cell,param_stack,element_stack,param_bop,param_consumables,param_hydro,elec_mix,heat_mix):
    
    flow,pressure_required,purity_required,storage,distribution=operating
    active_S_max=param_cell[0]
    cell_per_stack,d_rate,d_max,recycling_rate=param_stack
    lifetime_bop=param_bop[0]
    list_bop = copy.deepcopy(param_bop[1])  
    size_bop_per_flow = copy.deepcopy(param_bop[2])  ## size is given per unit of flow (i.e. per kgH2/h)
    U,J_dens,fuel_utilization,heat_demand,water_demand,KOH_demand,heat_out,leakage_rate_EL=param_consumables
    P_EL,T_EL,purity_EL=param_hydro


    ## Computation of impacts of the electricity stored in H2 and Elec-to-H2 Conversion (Electrolyser) ##

    #degradation modeling
    U=U*(1+d_max/100/2)
   
    ## impact consumables ##
    
    ## KP for electricity calculation ##

    ## Stack Consumption ##
    elec_stored=LHV_hydrogen
    electrical_efficiency=V_electrolysis/U
    elec_loss=(LHV_hydrogen/electrical_efficiency-LHV_hydrogen)
    
    ## BoP Consumption ##
    P_bop=consumption_BoP(list_bop,size_bop_per_flow,flow)
    elec_bop=P_bop/flow
    
    ## Energy Mixes ##
    elec_imp=electricity_impact(elec_mix)
    heat_imp=heat_impact(heat_mix,elec_mix)
    
    
    i_elec_stored=elec_stored*elec_imp
    i_elec_EL,i_heat_EL,i_other_cons_EL,i_detailed_elec_EL,i_detailed_other_cons_EL=impact_consumables([elec_loss,elec_bop,heat_demand,water_demand,KOH_demand],elec_imp,heat_imp,water_impact,KOH_impact)
    i_leakage_EL=leakage_rate_EL*leakage_impact
    
    ## KP stack & BoP calculation ##
    ## Quantity of stack and BoP per FU ##
    lifetime_stack=d_max/d_rate*1000
    stack_per_kgH2=1/(lifetime_stack*flow)
    BoP_per_kgH2=1/(lifetime_bop*flow)

    ## Stack Design ##
    active_S,N_cell,N_stack=sizing_parameters(flow,U,J_dens,active_S_max,cell_per_stack)
       
    ## impact cell ##
    
    i_cell=impact_cell(active_S,element_cell)
    
    ## impact stack ##
    
    i_stack_EL,i_detailed_stack_EL,i_eol_EL=impact_stack(stack_per_kgH2,i_cell,active_S,N_cell,element_stack,N_stack,recycling_rate)
    
    ### impact BoP ###

    ## adding Electrical Heater if needed (no in the default configuration) ##
    if heat_mix[1]>0:
        P_ELH=heat_mix[1]*heat_demand*flow
        list_bop.append('ELH [kW]')
        size_bop_per_flow.append(P_ELH/flow)
    
    i_bop_EL,i_detailed_bop_EL=impact_BoP(list_bop,size_bop_per_flow,flow,BoP_per_kgH2)
    
    ### impact electrolysis ###
    i_elec_stored_in_H2=[i_elec_stored,np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),[0,0,0]]
    i_EL=[i_elec_EL,i_heat_EL,i_other_cons_EL,i_stack_EL,i_bop_EL,i_eol_EL,i_leakage_EL,[0,0,0]]
    i_detailed_EL=[i_detailed_elec_EL,i_heat_EL,i_detailed_other_cons_EL,i_detailed_stack_EL,i_detailed_bop_EL,i_eol_EL,i_leakage_EL]
    
    ## Additional Impacts (Post Processing, Distribution, Storage, and End-Use Processes) ##
    
    ## Post Processing ##

    ## H2 requirement calculation (max of all requirements) ##
    if storage[0]!=None:
        storage_list=storage_dict[storage[0]][storage[1]]
        pressure_required=max(pressure_required,storage_list[0])
    else:
        storage_list=None
        
    if distribution[0]!=None:
        distrib_list=distrib_dict[distribution[0]][distribution[1]]
        pressure_required=max(pressure_required,distrib_list[0])
    else:
        distrib_list=None
    
    ## Calculating the size of equipment required for Post-Processing ##
    eq_PP=[]
    power_eq_PP=[]
    leakage_rate_PP=0
    if pressure_required>P_EL:
        P_compressor=power_compression (pressure_required,P_EL,flow,T_EL)
        eq_PP.append('Compressor [kW]')     
        power_eq_PP.append(P_compressor/flow)
    
    if purity_required > purity_EL:
        power_PSA=0
    # First level purification (Grade A to Grade D)
        if purity_required >= 99.96 and purity_EL < 99.96:
            leakage_rate_PP+=0.03  # Adjust for 97% recovery
            power_PSA+=0.5
            purity_EL=99.97

    # Second level purification (Grade D to UltraPure)
        if purity_required >= 99.997 and purity_EL < 99.997:
            leakage_rate_PP+=0.04  # Adjust for 97% recovery
            power_PSA+=3.5
        
        eq_PP.append('PSA [kW]')
        power_eq_PP.append(power_PSA)  # Energy in kWh/kg H2
        

    
    if eq_PP==[]:
        i_PP=[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),[0,0,0]]
    else:
        i_eq_PP=impact_BoP (eq_PP,power_eq_PP,flow,BoP_per_kgH2)[0]
        elec_cons_PP=consumption_BoP(eq_PP,power_eq_PP,flow)/flow
        i_PP=impact_supply_infrastructure (i_eq_PP,elec_cons_PP,leakage_rate_PP,elec_imp)

    
    if distrib_list!=None:
        leakage_rate_distrib=distrib_list[1]
        elec_cons_distrib=distrib_list[2]
        i_eq_distrib=np.array(distrib_list[3:])
        i_distrib=impact_supply_infrastructure(i_eq_distrib,elec_cons_distrib,leakage_rate_distrib,elec_imp)

    else:
        i_distrib=[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),[0,0,0]]
    
    if storage_list!=None:
        leakage_rate_storage=storage_list[1]
        elec_cons_storage=storage_list[2]
        i_eq_storage=np.array(storage_list[3:])
        i_storage=impact_supply_infrastructure(i_eq_storage,elec_cons_storage,leakage_rate_storage,elec_imp)
    else:
        i_storage=[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),[0,0,0]]
        
    i_FC=[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),[0,0,0]]
    i_EUP=[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),[0,0,0]]
    results=[i_elec_stored_in_H2,i_EL,i_PP,i_distrib,i_storage,i_FC,i_EUP]

    i_detailed_FC=[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat))]
    detailed_results=[i_detailed_EL,i_detailed_FC]
    return results,detailed_results
    

def sizing_parameters_FC (P_stack,voltage,J_dens,active_S_max,cell_per_stack,fuel_utilization):

    intensity=P_stack*1000/voltage
    flow=intensity*(M_H2*3600)/Faraday/electron/fuel_utilization
    surface_tot=intensity/J_dens
    N_cell_min=(surface_tot/active_S_max)
    N_stack=np.ceil(N_cell_min/cell_per_stack)
    N_cell=N_stack*cell_per_stack
    active_S=surface_tot/N_cell    

    return flow,active_S,N_cell,N_stack

def impact_techno(techno_dict,name_techno):
    techno=techno_dict[name_techno]
    impact=np.array(techno)
    return impact
    
    
    
def impact_consumables_FC (KP_consumables,h2_impact,elec_stored_h2,i_supply,KOH_impact,leakage_impact):
    h2_loss_per_FU,h2_converted_per_FU,KOH_demand,leakage_per_FU=KP_consumables
    h2_fc_loss=h2_loss_per_FU*h2_impact
    h2_el=h2_converted_per_FU*(h2_impact-elec_stored_h2-i_supply)
    h2_storage=h2_converted_per_FU*elec_stored_h2
    h2_supply=h2_converted_per_FU*i_supply
    h2=h2_storage+h2_el+h2_fc_loss+h2_supply
    KOH=KOH_demand*KOH_impact
    leakage=leakage_per_FU*leakage_impact
    return h2_fc_loss+KOH+leakage,[h2_fc_loss,np.zeros((7)),KOH,leakage],h2_storage+h2_el+h2_supply,[h2_storage,h2_el,h2_supply]  #0 is for the future impact of electricity of BoP.
    
    
    
    
def total_impact_FC_per_kgH2 (operating,param_cell,element_cell,param_stack,element_stack,param_bop,param_consumables):
    
    P_stack=operating[0]
    active_S_max=param_cell[0]
    cell_per_stack,d_rate,d_max,recycling_rate=param_stack
    lifetime_bop=param_bop[0]
    list_bop = copy.deepcopy(param_bop[1])  
    size_bop_per_flow = copy.deepcopy(param_bop[2])  
    U,J_dens,fuel_utilization,heat_demand,water_demand,KOH_demand,heat_out,leakage_rate_FC=param_consumables
   
    #degradation modeling
    U=U*(1-d_max/100/2)
    
    flow,active_S,N_cell,N_stack=sizing_parameters_FC(P_stack,U,J_dens,active_S_max,cell_per_stack,fuel_utilization) #changer avec Power


    #print(P_stack,N_stack,N_cell,flow)
    
    ## KP calculation ##

    ## Calculation of efficiency, accounting for stack losses, BoP losses H2 leakage ##

    ## stack ##
    h2_stack_efficiency=U/V_electrolysis*fuel_utilization

    ## BoP ##
    P_bop=consumption_BoP(list_bop,size_bop_per_flow,flow)
    surplus_h2_bop_cons=(P_bop/flow)/LHV_hydrogen

    #kgH2_per_kWh=1/(h2_stack_efficiency*h2_BoP_efficiency*(1-leakage_rate_FC))
    
    ## Consumables and leakage impacts ##
    i_KOH=KOH_demand*KOH_impact
    i_leakage_FC=leakage_rate_FC*leakage_impact
    
    i_other_cons_FC=i_KOH
    i_detailed_other_cons_FC=[np.zeros((N_cat)),i_KOH]


    lifetime_stack=d_max/d_rate*1000
    stack_per_kgH2=LHV_hydrogen/(lifetime_stack*P_stack)
    BoP_per_kgH2=LHV_hydrogen/(lifetime_bop*P_stack)
    
    
        
    ## impact cell ##
    
    i_cell=impact_cell(active_S,element_cell)
    
    ## impact stack ##
    
    i_stack_FC,i_detailed_stack_FC,i_eol_FC=impact_stack(stack_per_kgH2,i_cell,active_S,N_cell,element_stack,N_stack,recycling_rate)
    
    ### impact BoP ###
    i_bop_FC,i_detailed_bop_FC=impact_BoP(list_bop,size_bop_per_flow,flow,BoP_per_kgH2)
    
    
    i_FC=[np.zeros((N_cat)),np.zeros((N_cat)),i_other_cons_FC,i_stack_FC,i_bop_FC,i_eol_FC,i_leakage_FC,[(1-h2_stack_efficiency),surplus_h2_bop_cons,leakage_rate_FC]]
    i_detailed_FC=[np.zeros((N_cat)),np.zeros((N_cat)),i_detailed_other_cons_FC,i_detailed_stack_FC,i_detailed_bop_FC,i_eol_FC,i_leakage_FC]
    return i_FC,i_detailed_FC
    


def total_impact_EUP_per_FU (enduse_process,kgH2_per_FU):
    if enduse_process!=None:
        leakage_rate_EUP=enduse_dict[enduse_process][1]
        i_leakage=leakage_rate_EUP*leakage_impact
        
        i_eq=np.array(enduse_dict[enduse_process][2:])/kgH2_per_FU ## impact of equipment is given per end-use FU : scaled to 1kgH2eq!
        i_EUP=[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),i_eq,np.zeros((N_cat)),i_leakage,[0,0,0]]
    else:
        i_EUP=[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),[0,0,0]]
    
    return i_EUP



def generation_results(input_EL,input_FC,enduse_process,kgH2_per_FU,boundaries):
    operating, param_cell, e_cell, param_stack, e_stack, param_bop, param_cons,param_h2, elec_mix,heat_mix=input_EL
    results_per_kgH2, detailed_results_per_kgH2 = total_impact_EC_per_kgH2(operating, param_cell, e_cell, param_stack, e_stack, param_bop, param_cons,param_h2, elec_mix,heat_mix)
    
    if input_FC!=None:
        operating_FC, param_cell_FC, e_cell_FC, param_stack_FC, e_stack_FC, param_bop_FC, param_cons_FC=input_FC
        i_FC,i_detailed_FC = total_impact_FC_per_kgH2(operating_FC, param_cell_FC, e_cell_FC, param_stack_FC, e_stack_FC, param_bop_FC, param_cons_FC)
        results_per_kgH2[5]=i_FC
        detailed_results_per_kgH2[1]=i_detailed_FC

    
    if enduse_process!=None:
        i_EUP=total_impact_EUP_per_FU (enduse_process,kgH2_per_FU)
        results_per_kgH2[6]=i_EUP


    ## Potential multifunctionality with heat co-produced ##

    ## Quantity of Hydrogen consumed in Fuel Cell per FU
    kgH2_consumed_FC_per_FU=1
    if input_FC!=None:
        eff_FC=(1-i_FC[-1][0])*(1-i_FC[-1][1])*(1-i_FC[-1][2])
        kgH2_consumed_FC_per_FU=1/eff_FC
    heat_recovered_per_FU=boundaries[4]*kgH2_consumed_FC_per_FU

    ## Case 1: Heat Not Recovered OR Heat Recovered treated as a Waste (Cut-Off)    
    ratio=1

    ## Case 2: Heat Recovered - Exergy Allocation
    if boundaries[1]:
        Ex_heat=(1-298/boundaries[3])*(heat_recovered_per_FU)
        ratio=LHV_hydrogen/(LHV_hydrogen+Ex_heat)
        
    ## Case 3: Heat Recovered - Energy Allocation (Co-generation)
    if boundaries[2]:
        ratio=LHV_hydrogen/(LHV_hydrogen+heat_recovered_per_FU)
    
    kgH2_per_FU=kgH2_per_FU*ratio

    list_efficiency=[]
    results_supply_per_FU=[]
    detailed_results_supply=detailed_results_per_kgH2.copy()

    ## Supply Oriented Results Generation (i.e. impact of surplus of hydrogen is allocated to the main life cycle stage that lose the hydrogen)
    
    for n in range (len(results_per_kgH2)):
        current_impact=results_per_kgH2[n]
        L=current_impact[-1]
        current_efficiency=(1-L[0])*(1-L[1])*(1-L[2])
        list_efficiency.append(current_efficiency)

        current_impact_supply_chain = np.sum(np.concatenate(results_supply_per_FU), axis=0) if results_supply_per_FU else np.zeros(7)
        #computing surplus hydrogen impact
        current_result=current_impact[:-1]
        current_result = [np.asarray(x, dtype=float) * kgH2_per_FU
                  for x in current_result]
        
        i_surplus_h2=(current_impact_supply_chain+np.sum(current_result, axis=0))*(1/current_efficiency-1)
        
        i_surplus_h2_stack=current_impact_supply_chain*(1/(1-L[0])-1)
        i_surplus_h2_leakage=(current_impact_supply_chain+i_surplus_h2_stack)*(1/(1-L[2])-1)
        i_surplus_h2_eq=(current_impact_supply_chain+i_surplus_h2_stack+i_surplus_h2_leakage)*(1/(1-L[1])-1)
        i_detailed_surplus_h2=[i_surplus_h2_stack,i_surplus_h2_eq,i_surplus_h2_leakage]

        current_result.append(i_surplus_h2) 
        
        results_supply_per_FU.append(current_result)
        if n==5:
            current_detailed_results = detailed_results_per_kgH2[1]
            current_detailed_results = [np.asarray(x, dtype=float) * kgH2_per_FU
                  for x in current_detailed_results]
            current_detailed_results.append(i_detailed_surplus_h2)
            detailed_results_supply[1]=current_detailed_results
        if n==1:
            current_detailed_results = detailed_results_per_kgH2[0]
            current_detailed_results = [np.asarray(x, dtype=float) * kgH2_per_FU
                  for x in current_detailed_results]
            current_detailed_results.append(i_detailed_surplus_h2)
            detailed_results_supply[0]=current_detailed_results         
        

    ## Producer Oriented Results Generation (i.e. impact of surplus of hydrogen is allocated to the upstream processes, where the elementary processes are.)

    results_producer_per_FU=[]
    list_retro=[]
    
    p = 1
    for x in reversed(list_efficiency): 
        p *= x
        list_retro.append(p)
    list_retro = list_retro[::-1]


    for n in range (len(results_supply_per_FU)):
        surplus=1/list_retro[n]-1
        current=results_supply_per_FU[n].copy()
        current[-1]=np.zeros((7))
        results_producer_per_FU.append(current)
        current_surplus = [np.asarray(x, dtype=float) * surplus
                  for x in current]
        results_producer_per_FU.append(current_surplus)
    
    ## Exclusion of energy stored from boundaries  
    if not boundaries[0]:
        results_supply_per_FU[0]=[np.zeros((7)),np.zeros((7)),np.zeros((7)),np.zeros((7)),np.zeros((7)),np.zeros((7)),np.zeros((7)),np.zeros((7))]
        results_producer_per_FU[0]=[np.zeros((7)),np.zeros((7)),np.zeros((7)),np.zeros((7)),np.zeros((7)),np.zeros((7)),np.zeros((7)),np.zeros((7))]

    return results_supply_per_FU,detailed_results_supply,results_producer_per_FU





        



