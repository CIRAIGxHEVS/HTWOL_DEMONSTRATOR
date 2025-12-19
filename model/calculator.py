#mat!/usr/bin/env python
# coding: utf-8

# In[146]:


import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt
import copy
import streamlit as st
import utils.session_variables as sv



mat_dict=st.session_state.dictionary[9]
cons_dict=st.session_state.dictionary[10]
bop_dict=st.session_state.dictionary[11]

enduse_dict=st.session_state.dictionary[8]
storage_dict=st.session_state.dictionary[4]
distrib_dict=st.session_state.dictionary[5]



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
    intensity=flow*st.session_state.Faraday*st.session_state.electron_exchanged/(st.session_state.M_H2*3600)  #intensity in Ampere
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
    i_elec=[i_elec_loss,i_elec_bop]
    return np.sum(i_elec, axis=0),i_heat,i_water,i_KOH,i_elec


def consumption_BoP (list_bop,size_bop_per_kg,flow): #to adapt to equipment power and BoP_per_stack
    P_bop=0
    for k in range (len(list_bop)):
        real_size=size_bop_per_kg[k]*flow
        P_bop+=bop_dict[list_bop[k]][0]*real_size

    return P_bop

# In[160]:


def impact_BoP (list_bop,size_bop_per_flow,flow,BoP_per_FU): #to adapt to equipment power and BoP_per_stack
    i_bop=[]
    inventory_bop=[]
    for k in range (len(list_bop)):
        real_size=size_bop_per_flow[k]*flow
        unit_impact=bop_dict[list_bop[k]][2:]
        sizing_factor=bop_dict[list_bop[k]][1]
        i=np.array(unit_impact)*pow(real_size,sizing_factor)
        i_bop.append(i)
        inventory_bop.append(real_size)
    i_bop=np.vstack(i_bop)
    i_bop=i_bop*BoP_per_FU
    
    return np.sum(i_bop, axis=0),i_bop,inventory_bop

    
def power_compression (Pout,Pin,flow,Tin):
    hr=1.41
    R_gas=8.314
    Z_gas=1.024
    eff_comp=0.9*0.95
    rate_per_stage=2.1
    flow_mol=flow/st.session_state.M_H2/3600 #mol/s
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
    inventory_element=[[name_mat],[mass_component/active_S]] 
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
        inventory_element[0].append(name_add)
        inventory_element[1].append(mass_add/active_S)

    
    inert=mat_dict['EoL_inert']
    i_eol_inert=np.array(inert[1:])
    mass_tot=mass_component+mass_add 
    i_eol_comp=i_eol_inert*mass_tot*(1-recycling_rate)  
    inventory_element[0].append('EoL_inert')
    inventory_element[1].append(mass_tot/active_S*(1-recycling_rate))

    inventory_element[1]=np.array(inventory_element[1])
    
    return (i_component+i_add),i_eol_comp,inventory_element

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

    inventory_frame=[[name_mat,'EoL_inert'],np.array([mass_frame/total_area,mass_frame/total_area*(1-recycling_rate)])]    #inventory for cells are per m2 active area
    return i_frame,i_eol_frame,inventory_frame

# In[178]:


def impact_cell (active_S,element_cell):
    impact=[]
    impact_eol=[]
    inventory_cell=[]
    for e in element_cell:
        i,i_eol_comp,inventory_element=stack_component(active_S,e)
        impact.append(i)
        impact_eol.append(i_eol_comp)
        inventory_cell.append(inventory_element)
    impact=np.vstack(impact)
    return np.sum(impact, axis=0),impact,np.sum(impact_eol, axis=0),inventory_cell
    


# In[179]:


def impact_stack (stack_per_FU,cell,active_S,N_cell,e_stack,N_stack,recycling_rate=0):
    #N_cell total number of cell in the system
    #N_stack number of stack
    i_cell=cell[0]*N_cell 
    detailed_cell=cell[1]*N_cell
    i_eol_cell=cell[2]*N_cell
    inventory_cell=cell[3]
    #for k in range (len(inventory_cell)):
        #inventory_cell[k][1]=inventory_cell[k][1]*N_cell #scaled to the 
        

    
    i_frame=(frame_component(active_S*N_cell,e_stack[0][:2],recycling_rate)[0]+frame_component(active_S*N_cell,e_stack[0][2:4],recycling_rate)[0]+frame_component(active_S*N_cell,e_stack[0][4:])[0])
    i_eol_frame=(frame_component(active_S*N_cell,e_stack[0][:2],recycling_rate)[1]+frame_component(active_S*N_cell,e_stack[0][2:4],recycling_rate)[1]+frame_component(active_S*N_cell,e_stack[0][4:])[1])
    
    inv_frame_1=frame_component(active_S*N_cell,e_stack[0][:2],recycling_rate)[2]
    inv_frame_2=frame_component(active_S*N_cell,e_stack[0][2:4],recycling_rate)[2]
    inv_frame_3=frame_component(active_S*N_cell,e_stack[0][4:])[2]

    i_ep=stack_component(active_S,e_stack[1],recycling_rate)[0]*2*N_stack #2 ends of the stack
    i_eol_ep=stack_component(active_S,e_stack[1],recycling_rate)[1]*2*N_stack
    inventory_ep=stack_component(active_S,e_stack[1],recycling_rate)[2]
    inventory_ep[1]=inventory_ep[1]*2*N_stack/N_cell #for scaling to 1 m2 active area

    i_element=np.vstack([detailed_cell, i_frame, i_ep])
    i_eol=np.vstack([i_eol_cell, i_eol_frame, i_eol_ep])
    inventory_stack=inventory_cell+[inv_frame_1]+[inv_frame_2]+[inv_frame_3]+[inventory_ep]

    i_element=i_element*stack_per_FU
    i_eol=i_eol*stack_per_FU
    
    return np.sum(i_element, axis=0),i_element,np.sum(i_eol, axis=0),inventory_stack


def impact_supply_infrastructure (i_eq,elec_cons,leakage_rate,elec_imp=np.zeros((7))):
    ## impact of equipment is given per kgH2 (stored/distributed/prepared) 
    i_elec=elec_cons*elec_imp
    i_leakage=leakage_rate*leakage_impact
    
    i_infra=[i_elec,np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),i_eq,np.zeros((N_cat)),i_leakage,[0,0,leakage_rate]]
    inventory_infra=[elec_cons,0,0,0,0,1,0,leakage_rate]
    
    return i_infra, inventory_infra

    
def total_impact_EL_per_kgH2 (flow,param_cell,element_cell,param_stack,element_stack,param_bop,param_consumables,elec_mix,heat_mix):
    
    active_S_max=param_cell[0]
    cell_per_stack,d_rate,d_max,recycling_rate=param_stack
    lifetime_bop=param_bop[0]
    list_bop = copy.deepcopy(param_bop[1])  
    size_bop_per_flow = copy.deepcopy(param_bop[2])  ## size is given per unit of flow (i.e. per kgH2/h)
    U,J_dens,fuel_utilization,heat_demand,water_demand,KOH_demand,heat_out,leakage_rate_EL=param_consumables
    

    ## Computation of impacts of the electricity stored in H2 and Elec-to-H2 Conversion (Electrolyser) ##

    #degradation modeling
    U=U*(1+d_max/100/2)
   
    ## impact consumables ##
    
    ## KP for electricity calculation ##

    ## Stack Consumption ##
    elec_stored=st.session_state.LHV_hydrogen
    electrical_efficiency=st.session_state.V_electrolysis/U
    elec_loss=(st.session_state.LHV_hydrogen/electrical_efficiency-st.session_state.LHV_hydrogen)
    
    ## BoP Consumption ##
    P_bop=consumption_BoP(list_bop,size_bop_per_flow,flow)
    elec_bop=P_bop/flow
    
    ## Energy Mixes ##
    elec_imp=electricity_impact(elec_mix)
    heat_imp=heat_impact(heat_mix,elec_mix)
    
    
    i_elec_stored=elec_stored*elec_imp
    i_elec_EL,i_heat_EL,i_water_EL,i_KOH_EL,i_detailed_elec_EL=impact_consumables([elec_loss,elec_bop,heat_demand,water_demand,KOH_demand],elec_imp,heat_imp,water_impact,KOH_impact)
    i_leakage_EL=leakage_rate_EL*leakage_impact
    ## KP stack & BoP calculation ##
    ## Quantity of stack and BoP per FU ##
    lifetime_stack=d_max/d_rate*1000
    stack_per_kgH2=1/(lifetime_stack*flow)
    BoP_per_kgH2=1/(lifetime_bop*flow)

    ## Stack Design ##
    active_S,N_cell,N_stack=sizing_parameters(flow,U,J_dens,active_S_max,cell_per_stack)
    inventory_stack_EL=[N_cell*active_S,N_cell*active_S,N_cell*active_S,N_cell*active_S,N_cell*active_S,N_cell*active_S,N_cell*active_S,N_cell*active_S]
       
    ## impact cell ##
    
    cell=impact_cell(active_S,element_cell)
    
    ## impact stack ##
    
    i_stack_EL,i_detailed_stack_EL,i_eol_EL,inventory_stack_detailed_EL=impact_stack(stack_per_kgH2,cell,active_S,N_cell,element_stack,N_stack,recycling_rate)
    
    ### impact BoP ###
    
    i_bop_EL,i_detailed_bop_EL,inventory_bop_EL=impact_BoP(list_bop,size_bop_per_flow,flow,BoP_per_kgH2)
    
    ### impact electrolysis ###
    i_elec_stored_in_H2=[i_elec_stored,np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),[0,0,0]]
    i_EL=[i_elec_EL,i_heat_EL,i_water_EL,i_KOH_EL,i_stack_EL,i_bop_EL,i_eol_EL,i_leakage_EL,[0,0,0]]

    i_detailed_cons=[np.vstack([i_elec_stored,np.vstack(i_detailed_elec_EL),i_heat_EL,i_water_EL,i_KOH_EL,i_stack_EL,i_bop_EL,i_eol_EL,i_leakage_EL])]
    i_detailed_EL=[i_detailed_cons,[i_detailed_stack_EL],[i_detailed_bop_EL]]
    

    inventory_EL=[[elec_stored,0,0,0,0,0,0,0],[elec_loss+elec_bop,heat_demand,water_demand,KOH_demand,stack_per_kgH2,BoP_per_kgH2,stack_per_kgH2,leakage_rate_EL]]
    inventory_cons_EL=[elec_stored,elec_loss,elec_bop,heat_demand,water_demand,KOH_demand,stack_per_kgH2,BoP_per_kgH2,stack_per_kgH2,leakage_rate_EL]

    inventory_detailed_EL=[inventory_cons_EL,inventory_stack_EL,inventory_stack_detailed_EL,inventory_bop_EL]
    
    return [i_elec_stored_in_H2,i_EL], [i_detailed_EL], inventory_EL, [inventory_detailed_EL]

def total_impact_supply_chain_per_kgH2 (requirement,supply_chain,lifetime_bop,characteristic_h2_produced,elec_mix):
    requirement_app,requirement_FC=requirement
    flow,storage,distribution=supply_chain
    P_EL,T_EL,purity_EL=characteristic_h2_produced
    
    ## Additional Impacts (Post Processing, Distribution, Storage, and End-Use Processes) ##
    BoP_per_kgH2=1/(lifetime_bop*flow)
    elec_imp=electricity_impact(elec_mix)
    ## Post Processing ##


    if requirement_FC!=None:
        pressure_required=max(requirement_app[0],requirement_FC[0])
        purity_required=max(requirement_app[1],requirement_FC[1])
    else:
        pressure_required=requirement_app[0]
        purity_required=requirement_app[1]

    ## for printing in inventory ##


    ## H2 requirement calculation (max of all requirements) ##
    if storage[0]!="None":
        storage_list=storage_dict[storage[0]][storage[1]]
        pressure_required=max(pressure_required,storage_list[0])
    else:
        storage_list=None
        
    if distribution[0]!="None":
        distrib_list=distrib_dict[distribution[0]][distribution[1]]
        pressure_required=max(pressure_required,distrib_list[0])
    else:
        distrib_list=None

    st.session_state.characteristic_h2_produced=characteristic_h2_produced
    st.session_state.requirements=[pressure_required,purity_required]

    
    ## Calculating the size of equipment required for Post-Processing ##
    i_comp=[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),[0,0,0]]
    inventory_comp=[0]*8
    leakage_rate_comp=0
    if pressure_required>P_EL:
        P_compressor=power_compression (pressure_required,P_EL,flow,T_EL)
        eq_comp=['Compressor [kW]']
        i_eq_comp=impact_BoP (eq_comp,[P_compressor/flow],flow,BoP_per_kgH2)[0]
        elec_cons_comp=consumption_BoP(eq_comp,[P_compressor/flow],flow)/flow
        i_comp,inventory_comp=impact_supply_infrastructure (i_eq_comp,elec_cons_comp,leakage_rate_comp,elec_imp)
        inventory_comp[5]=BoP_per_kgH2

    i_purif=[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),[0,0,0]]   
    inventory_purif=[0]*8
    leakage_rate_purif=0
    if purity_required > purity_EL:
        power_PSA=0
    # First level purification (Grade A to Grade D)
        if purity_required >= 99.96 and purity_EL < 99.96:
            leakage_rate_purif+=0.03  # Adjust for 97% recovery
            power_PSA+=0.5
            purity_EL=99.97

    # Second level purification (Grade D to UltraPure)
        if purity_required >= 99.997 and purity_EL < 99.997:
            leakage_rate_purif+=0.04  # Adjust for 97% recovery
            power_PSA+=3.5
        
        eq_purif=['PSA [kW]']
        i_eq_purif=impact_BoP(eq_purif,[power_PSA],flow,BoP_per_kgH2)[0]
        elec_cons_purif=consumption_BoP(eq_purif,[power_PSA],flow)/flow
        i_purif,inventory_purif=impact_supply_infrastructure (i_eq_purif,elec_cons_purif,leakage_rate_purif,elec_imp)  
        inventory_purif[5]=BoP_per_kgH2      

    if distrib_list!=None:
        leakage_rate_distrib=distrib_list[1]
        elec_cons_distrib=distrib_list[2]
        i_eq_distrib=np.array(distrib_list[3:])
        i_distrib,inventory_distrib=impact_supply_infrastructure(i_eq_distrib,elec_cons_distrib,leakage_rate_distrib,elec_imp)

    else:
        i_distrib=[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),[0,0,0]]
        inventory_distrib=[0]*8
    
    if storage_list!=None:
        leakage_rate_storage=storage_list[1]
        elec_cons_storage=storage_list[2]
        i_eq_storage=np.array(storage_list[3:])
        i_storage,inventory_storage=impact_supply_infrastructure(i_eq_storage,elec_cons_storage,leakage_rate_storage,elec_imp)
    else:
        i_storage=[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),[0,0,0]]
        inventory_storage=[0]*8

    return [i_comp,i_purif,i_distrib,i_storage], [inventory_comp,inventory_purif,inventory_distrib,inventory_storage]

    

def sizing_parameters_FC (P_stack,voltage,J_dens,active_S_max,cell_per_stack,fuel_utilization):

    intensity=P_stack*1000/voltage
    flow=intensity*(st.session_state.M_H2*3600)/st.session_state.Faraday/st.session_state.electron_exchanged/fuel_utilization
    surface_tot=intensity/J_dens
    N_cell_min=(surface_tot/active_S_max)
    N_stack=np.ceil(N_cell_min/cell_per_stack)
    N_cell=N_stack*cell_per_stack
    active_S=surface_tot/N_cell    

    return flow,active_S,N_cell,N_stack


def total_impact_alternative_h2_prod(name_techno):
    techno_dict=sv.file_opening_dict("data/alternative_technologies/alt_h2_prod.csv")
    techno=techno_dict[name_techno]
    characteristic_h2_prod=techno[0:3]
    lifetime_bop=techno[3]
    impact=np.array(techno[4:])
    return impact,characteristic_h2_prod,lifetime_bop

def impact_techno(techno_dict,name_techno):
    techno=techno_dict[name_techno]
    impact=np.array(techno)
    return impact

def heat_recovery_modeling(allocation,heat_out,T_out):
    ## Potential multifunctionality with heat co-produced ##

    ## Case 1: Heat Not Recovered OR Heat Recovered treated as a Waste (Cut-Off)    
    heat_recovered=0
    T0=298 #ambiant temperature

    ## Case 2: Heat Recovered - Exergy Allocation
    if allocation=='exergy':
        Ex_heat=heat_out*(1-T0*np.log(T_out/T0)/(T_out-T0))
        heat_recovered=Ex_heat
        
    ## Case 3: Heat Recovered - Energy Allocation (Co-generation)
    elif allocation=='energy':
        heat_recovered=heat_out

    elif allocation=='None':
        heat_recovered=0

    return heat_recovered
    
    
    
def total_impact_FC_per_kgH2 (P_stack,param_cell,element_cell,param_stack,element_stack,param_bop,param_consumables,heat_recovery):

    active_S_max=param_cell[0]
    cell_per_stack,d_rate,d_max,recycling_rate=param_stack
    lifetime_bop=param_bop[0]
    list_bop = copy.deepcopy(param_bop[1])  
    size_bop_per_flow = copy.deepcopy(param_bop[2])  
    U,J_dens,fuel_utilization,heat_demand,water_demand,KOH_demand,heat_out,leakage_rate_FC=param_consumables
    allocation,T_out=heat_recovery
   
    #degradation modeling
    U=U*(1-d_max/100/2)
    
    flow,active_S,N_cell,N_stack=sizing_parameters_FC(P_stack,U,J_dens,active_S_max,cell_per_stack,fuel_utilization) #changer avec Power
    inventory_stack_FC=[N_cell*N_stack,N_cell*N_stack,N_cell*N_stack,N_cell*N_stack,N_cell*N_stack,N_cell*N_stack,N_stack,2*N_stack]



    #print(P_stack,N_stack,N_cell,flow)
    
    ## KP calculation ##

    ## Calculation of efficiency, accounting for stack losses, BoP losses H2 leakage ##

    ## stack ##
    electricity_recovered_per_kgH2=U/st.session_state.V_electrolysis*fuel_utilization*st.session_state.LHV_hydrogen
    heat_recovered_per_kgH2=heat_recovery_modeling(allocation,heat_out,T_out)
    h2_stack_efficiency=(electricity_recovered_per_kgH2+heat_recovered_per_kgH2)/st.session_state.LHV_hydrogen

    ## BoP ##
    P_bop=consumption_BoP(list_bop,size_bop_per_flow,flow)
    surplus_h2_bop_cons=(P_bop/flow)/st.session_state.LHV_hydrogen


    #kgH2_per_kWh=1/(h2_stack_efficiency*h2_BoP_efficiency*(1-leakage_rate_FC))
    
    ## Consumables and leakage impacts ##
    i_KOH=KOH_demand*KOH_impact
    i_leakage_FC=leakage_rate_FC*leakage_impact
    
    #i_detailed_other_cons_FC=[np.zeros((N_cat)),i_KOH]


    lifetime_stack=d_max/d_rate*1000
    stack_per_kgH2=st.session_state.LHV_hydrogen/(lifetime_stack*P_stack)
    BoP_per_kgH2=st.session_state.LHV_hydrogen/(lifetime_bop*P_stack)
    
    
        
    ## impact cell ##
    
    cell=impact_cell(active_S,element_cell)
    
    ## impact stack ##
    
    i_stack_FC,i_detailed_stack_FC,i_eol_FC,inventory_detailed_stack_FC=impact_stack(stack_per_kgH2,cell,active_S,N_cell,element_stack,N_stack,recycling_rate)
    
    ### impact BoP ###
    i_bop_FC,i_detailed_bop_FC,inventory_bop_FC=impact_BoP(list_bop,size_bop_per_flow,flow,BoP_per_kgH2)
    
    i_FC=[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),i_KOH,i_stack_FC,i_bop_FC,i_eol_FC,i_leakage_FC,[(1-h2_stack_efficiency),surplus_h2_bop_cons,leakage_rate_FC]]
    i_detailed_cons_FC=[np.vstack([i_KOH,i_stack_FC,i_bop_FC,i_eol_FC,i_leakage_FC])]
    i_detailed_FC=[i_detailed_cons_FC,i_detailed_stack_FC,i_detailed_bop_FC]

    inventory_FC=[0,0,0,KOH_demand,stack_per_kgH2,BoP_per_kgH2,stack_per_kgH2,leakage_rate_FC]
    inventory_cons_FC=[1,1/h2_stack_efficiency-1,1/(1-surplus_h2_bop_cons)-1,1/(1-leakage_rate_FC)-1,KOH_demand,stack_per_kgH2,BoP_per_kgH2,stack_per_kgH2,leakage_rate_FC]
    inventory_detailed_FC=[inventory_cons_FC,inventory_stack_FC,inventory_detailed_stack_FC,inventory_bop_FC]


    return [i_FC],[i_detailed_FC], [inventory_FC], [inventory_detailed_FC]
    


def total_impact_EUP_per_FU (enduse_process,kgH2_per_FU,elec_mix):
    if enduse_process!=None:
        leakage_rate_EUP=enduse_dict[enduse_process][1]
        i_leakage=leakage_rate_EUP*leakage_impact

        elec_imp=electricity_impact(elec_mix)
        elec_demand=enduse_dict[enduse_process][2]
        i_elec_EUP=elec_demand*elec_imp
        
        i_eq=np.array(enduse_dict[enduse_process][3:])/kgH2_per_FU ## impact of equipment is given per end-use FU : scaled to 1kgH2eq!
        i_EUP=[i_elec_EUP,np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),i_eq,np.zeros((N_cat)),i_leakage,[0,0,0]]
        inventory_EUP=[elec_demand,0,0,0,0,1,0,leakage_rate_EUP]
    else:
        i_EUP=[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),[0,0,0]]
        inventory_EUP=[0,0,0,0,0,0,0,0]
    return [i_EUP], [inventory_EUP]



def generation_results(input_EL,input_FC,requirement,supply_chain,enduse_process,kgH2_per_FU,boundaries_prodelec,elec_mix,heat_mix):
    
    if len(input_EL)>1:
        flow, param_cell, e_cell, param_stack, e_stack, param_bop, param_cons,characteristic_h2_produced=input_EL
        results_EL, detailed_results_EL,inventory_EL,detailed_inventory_EL = total_impact_EL_per_kgH2(flow, param_cell, e_cell, param_stack, e_stack, param_bop, param_cons, elec_mix,heat_mix)
        lifetime_bop=param_bop[0]
    else:   
        name_techno=input_EL[0]
        i_EL,characteristic_h2_produced,lifetime_bop=total_impact_alternative_h2_prod(name_techno)
        results_EL=[[i_EL,np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),[0,0,0]],[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),[0,0,0]]]
        detailed_results_EL=[None]
        inventory_EL=[[0]*8,[0]*8]
        detailed_inventory_EL=[None]
    
    results_supply,inventory_supply = total_impact_supply_chain_per_kgH2 (requirement,supply_chain,lifetime_bop,characteristic_h2_produced,elec_mix)
    results_FC=[[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),[0,0,0]]]
    detailed_results_FC=[None]
    inventory_FC=[[0]*8]
    detailed_inventory_FC=[None]
    if input_FC!=None:
        operating_FC, param_cell_FC, e_cell_FC, param_stack_FC, e_stack_FC, param_bop_FC, param_cons_FC,heat_recovery_FC=input_FC
        results_FC,detailed_results_FC,inventory_FC,detailed_inventory_FC = total_impact_FC_per_kgH2(operating_FC, param_cell_FC, e_cell_FC, param_stack_FC, e_stack_FC, param_bop_FC, param_cons_FC,heat_recovery_FC)
        #results_per_kgH2[5]=i_FC
        #detailed_results_per_kgH2[1]=i_detailed_FC

    results_EUP=[[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),[0,0,0]]]
    inventory_EUP=[[0]*8]
    if enduse_process!=None:
        results_EUP,inventory_EUP=total_impact_EUP_per_FU (enduse_process,kgH2_per_FU,elec_mix)
        #results_per_kgH2[6]=i_EUP

    results_per_kgH2=results_EL+results_supply+results_FC+results_EUP
    detailed_results_per_kgH2=detailed_results_EL+detailed_results_FC
    inventory_per_kgH2=inventory_EL+inventory_supply+inventory_FC+inventory_EUP
    detailed_inventory=detailed_inventory_EL+detailed_inventory_FC

    list_efficiency=[]
    results_supply_per_FU=[]
    inventory_supply_per_FU=[]
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
        current_inventory=inventory_per_kgH2[n]
        current_result = [np.asarray(x, dtype=float) * kgH2_per_FU
                  for x in current_result]
        current_inventory=[np.asarray(x, dtype=float) * kgH2_per_FU
                  for x in current_inventory]
        
        #i_surplus_h2=(current_impact_supply_chain+np.sum(current_result, axis=0))*(1/current_efficiency-1) #inlcuding current result
        i_surplus_h2=(current_impact_supply_chain)*(1/current_efficiency-1) #excluding current result
        
        i_surplus_h2_stack=current_impact_supply_chain*(1/(1-L[0])-1)
        i_surplus_h2_leakage=(current_impact_supply_chain+i_surplus_h2_stack)*(1/(1-L[2])-1)
        i_surplus_h2_eq=(current_impact_supply_chain+i_surplus_h2_stack+i_surplus_h2_leakage)*(1/(1-L[1])-1)
        i_detailed_surplus_h2=np.vstack([i_surplus_h2_stack,i_surplus_h2_eq,i_surplus_h2_leakage])

        current_result.append(i_surplus_h2) 
        current_inventory.append((1/current_efficiency-1)* kgH2_per_FU)
        
        results_supply_per_FU.append(current_result)
        inventory_supply_per_FU.append(current_inventory)

        if n==6 and detailed_results_per_kgH2[1]!=None:
            for k in range (3):
                current_detailed_results = detailed_results_per_kgH2[1][k]
                current_detailed_results = [np.asarray(x, dtype=float) * kgH2_per_FU
                    for x in current_detailed_results]
                detailed_results_supply[1][k]=current_detailed_results
            detailed_results_supply[1][0]= [np.vstack(([current_impact_supply_chain,i_detailed_surplus_h2,detailed_results_supply[1][0][0]]))]

        if n==1 and detailed_results_per_kgH2[0]!=None:
            for k in range (3):
                current_detailed_results = detailed_results_per_kgH2[0][k]
                current_detailed_results = [np.asarray(x, dtype=float) * kgH2_per_FU
                    for x in current_detailed_results]
                detailed_results_supply[0][k]=current_detailed_results         
        

    ## Producer Oriented Results Generation (i.e. impact of surplus of hydrogen is allocated to the upstream processes, where the elementary processes are.)

    results_producer_per_FU=[]
    inventory_producer_per_FU=[]
    list_retro=[1]
    ## décalage car l'inefficiacité du process n va impacter à partir de n-1
    p = 1
    for x in reversed(list_efficiency): 
        p *= x
        list_retro.append(p)
    list_retro = list_retro[::-1]
    list_retro = list_retro[1:]



    for n in range (len(results_supply_per_FU)):
        surplus=1/list_retro[n]-1
        current=results_supply_per_FU[n].copy()
        current[-1]=np.zeros((N_cat))
        results_producer_per_FU.append(current)
        current_surplus = [np.asarray(x, dtype=float) * surplus
                  for x in current]
        results_producer_per_FU.append(current_surplus)

        current_inventory=inventory_supply_per_FU[n].copy()
        current_inventory[-1]=0
        inventory_producer_per_FU.append(current_inventory)
        current_surplus = [np.asarray(x, dtype=float) * surplus
                  for x in current_inventory]
        inventory_producer_per_FU.append(current_surplus)
    
    ## Exclusion of energy stored from boundaries  
    if not boundaries_prodelec:
        results_supply_per_FU[0]=[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat))]
        results_producer_per_FU[0]=[np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat)),np.zeros((N_cat))]

    return results_supply_per_FU,detailed_results_supply,results_producer_per_FU,kgH2_per_FU,inventory_supply_per_FU,inventory_producer_per_FU,detailed_inventory





        



