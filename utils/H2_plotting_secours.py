#!/usr/bin/env python
# coding: utf-8

# In[146]:

import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt
import streamlit as st

legend_detailed_EL=[['Electricity Stored'],['Electricity Losses','Electricity BoP','Heat','Water','KOH','H2 Leakage'],['Cathode','Anode','Contact Layer','Barrier Layer','Membrane','Bipolar','Frame','Endplate'],['EoL'],['Compressor [kW]', 'HEX [m2]', 'Chiller [kW]', 'Rectifier [kW]', 'Separator [m3]', 'Pump [kW]', 'Piping [kg]', 'Instrumentation [kW]', 'Tank [kWstack]', 'Container [m3]','Heater [kW]'],['Prep. Equipment','Prep. Elec. Cons.','Prep. Leakage','Prep. Surplus H2 Prod.'],['Storage Equipment','Storage Elec. Cons.','Storage Leakage','Storage Surplus H2 Prod.'],['Distribution Equipment','Distrib. Elec. Cons.','Distrib. Leakage','Distrib. Surplus H2 Prod.'],['End-Use Equipment','End-Use Elec. Cons.','End-Use Leakage','End-Use Surplus H2 Prod.']]

legend_detailed_FC=[['Elec. Stored','Elec-to-H2 Conversion','H2 Supply (Storage/Distrib.)'],['H2 Lost (FC Stack)','H2 Consumed (FC BoP Cons.)','KOH','H2 Leakage'],['Cathode','Anode','Contact Layer','Barrier Layer','Membrane','Bipolar','Frame','Endplate'],['EoL'],['Compressor [kW]', 'HEX [m2]', 'Chiller [kW]', 'Rectifier [kW]', 'Separator [m3]', 'Pump [kW]', 'Piping [kg]', 'Instrumentation [kW]', 'Tank [kWstack]', 'Container [m3]'],['End-Use Equipment','End-Use Elec. Cons.','End-Use Leakage','End-Use Surplus H2 Prod.']]


legend_simplified_EL=[['Electricity Stored'], ['Consumables'],['Electrolyser Stack'], ['Electrolyser EoL'], ['Electrolyser BoP'], ['H2 Preparation'],['Storage'], ['Distrib'], ['Add.']]
legend_simplified_FC=[ ['H2 Supply Chain'],['FC Consumable Lost'], ['Fuel Cell Stack'], ['Fuel Cell EoL'], ['Fuel Cell BoP'],['Add.']]

legend_LCIA=[['CC \n[kgCO2eq]'],['CC \n[kgCO2eq]','Rem. EQ \n[PDF.m2.yr]','Energy \n[MJ deprived]','Rem. HH \n[DALY]','Water \n[m3 worldEq]'],['EQ \n[PDF.m2.yr]','HH \n[DALY]']]



# In[154]:


def list_color (L,FC):
    if FC:
        all_colors = [plt.cm.Oranges(np.linspace(0.4, 0.6, 1)), plt.cm.RdPu(np.linspace(0.4, 1, L[3])), plt.cm.Purples(np.linspace(0.5, 0.7, 1))]
        all_colors=np.vstack(all_colors)[:L[0]]
        red2_colors = plt.cm.Reds(np.linspace(0.6, 1, L[1]))
        blue_colors = plt.cm.Blues(np.linspace(0.2, 1, L[2]))
        lightgray_colors   = plt.cm.Greys(np.linspace(0.2, 0.6, L[3]))
        green_colors = plt.cm.Greens(np.linspace(0.5, 1, L[4])) 
        black_colors=plt.cm.Greys(np.linspace(0.7, 1, L[5]))
        color_list = np.concatenate([all_colors,red2_colors,blue_colors,lightgray_colors, green_colors,black_colors])
    
    else:
        red_colors = plt.cm.Reds(np.linspace(0.4, 0.6, L[0]))
        red2_colors = plt.cm.Reds(np.linspace(0.6, 1, L[1]))
        blue_colors = plt.cm.Blues(np.linspace(0.2, 1, L[2]))
        lightgray_colors   = plt.cm.Greys(np.linspace(0.2, 0.6, L[3]))
        green_colors = plt.cm.Greens(np.linspace(0.5, 1, L[4])) 
        gray_colors=plt.cm.Greys(np.linspace(0.2, 0.6, L[5]))
        purple_colors=plt.cm.Purples(np.linspace(0.5, 1, L[6]))
        yellow_colors = plt.cm.YlOrBr(np.linspace(0.2, 1, L[7]))
        black_colors=plt.cm.Greys(np.linspace(0.7, 1, L[8]))          
        color_list = np.concatenate([red_colors,red2_colors,blue_colors,lightgray_colors, green_colors,gray_colors,purple_colors,yellow_colors,black_colors])
    
    return color_list
    
def result_by_tier (result,tier,FC):

    if FC:
        legend=legend_detailed_FC.copy()
        if not tier[4]:
            result[0]=np.sum(result[0],axis=0)   
            legend[0]=legend_simplified_FC[0]
        if not tier[0]:
            result[1]=np.sum(result[1],axis=0)   
            legend[1]=legend_simplified_FC[1]
        if not tier[1]:
            result[2]=np.sum(result[2],axis=0)   
            legend[2]=legend_simplified_FC[2]
        if not tier[2]:
            result[4]=np.sum(result[4],axis=0)
            legend[4]=legend_simplified_FC[4]
   
    else:
        legend=legend_detailed_EL.copy()
        if not tier[0]:
            result[1]=np.sum(result[1],axis=0)   
            legend[1]=legend_simplified_EL[1]
        if not tier[1]:
            result[2]=np.sum(result[2],axis=0)   
            legend[2]=legend_simplified_EL[2]
        if not tier[2]:
            result[4]=np.sum(result[4],axis=0)   
            legend[4]=legend_simplified_EL[4]
        if not tier[3]:
            result[5]=np.sum(result[5],axis=0)   
            legend[5]=legend_simplified_EL[5]
        if not tier[4]:
            result[6]=np.sum(result[6],axis=0)  
            result[7]=np.sum(result[7],axis=0) 
            result[8]=np.sum(result[8],axis=0) 
            legend[6]=legend_simplified_EL[6]
            legend[7]=legend_simplified_EL[7]
            legend[8]=legend_simplified_EL[8]
    return result,legend
    

# In[155]:


def plotting (array,tier,name_techno,name_mix,LCIA,stack_only=False,FC=False):

    array,labels=result_by_tier (array,tier,FC)
    lc = [len(sublist) for sublist in labels]
    color_list=list_color(lc,FC)
    if stack_only:
        array=array[2]
        array = np.atleast_2d(array)
        labels=labels[2]
        color_list=color_list[lc[0]+lc[1]:lc[0]+lc[1]+lc[2]]
    
    else:   
        array = [np.atleast_2d(x) for x in array]
        array= np.vstack(array)
        labels = [elem for sublegend in labels for elem in sublegend]

    
    if LCIA=='Climate Change':
        legend_LCIA=['CC \n[kgCO2eq]']
        array=array[:,0:1]
    elif LCIA=='IW+ Footprint':
        legend_LCIA=['CC \n[kgCO2eq]','Rem. EQ \n[PDF.m2.yr]','Energy \n[MJ deprived]','Rem. HH \n[DALY]','Water \n[m3 worldEq]']
        array=array[:,0:5]
    else:
        legend_LCIA=['EQ \n[PDF.m2.yr]','HH \n[DALY]']
        array=array[:,5:7]

    
    
    # Définir les colonnes
    n_cols = array.shape[1]
    n_rows = array.shape[0]
    col_sums = np.sum(array, axis=0)
    data_normalized = (array / col_sums) * 100
    # Index des colonnes
    x = np.arange(1, n_cols + 1)

    # Création de l'histogramme empilé avec des couleurs différentes pour chaque ligne
    bottom = np.zeros(n_cols)

    for i in range(n_rows):
        if data_normalized[i][0]!=0:
            plt.bar(x, data_normalized[i], bottom=bottom, label=labels[i], color=color_list[i])
            bottom += data_normalized[i]  # Mise à jour de la position de base pour l'empilement

    for j in range (n_cols):
        plt.text(j+1, 105, f"{col_sums[j]:.3g}", ha='center', va='center', fontsize=13)
        
        
    # Ajouter les détails du graphique
    plt.xlabel('Impact Categories')
    plt.ylabel('Contribution [%]')
    plt.xticks(range(1,len(legend_LCIA)+1),legend_LCIA)
    plt.ylim(0, 110)
    plt.title(f"Contribution Analysis of the reference scenario providing {st.session_state.scenario[0][0]}")
    
    handles, labels = plt.gca().get_legend_handles_labels()
    legend=plt.legend(handles[::-1], labels[::-1],bbox_to_anchor=(1.4, 1))
    """legend=plt.legend()"""
    plt.show()
            


    row_labels = [text.get_text() for text in legend.get_texts()][::-1]
    df_result = pd.DataFrame(array) 
    df_result = df_result[(df_result.abs() > 1e-10).any(axis=1)]
    df_result=df_result[:len(row_labels)]
    df_result.columns = legend_LCIA
    df_result.index = row_labels
    total = df_result.sum()
    df_result.loc['Total'] = total       
    df_result = df_result.apply(lambda col: col.map(lambda x: f"{x:.3g}" if isinstance(x, (int, float)) else x))
    st.table(df_result)


# In[156]:


def plotting_comp (tier,array1,array2,LCIA,stack_only=False,FC=False):
    
    fig, ax = plt.subplots(figsize=(9, 6))
    array1,labels=result_by_tier (array1,tier,FC)
    array2,labels2=result_by_tier (array2,tier,FC)
    lc = [len(sublist) for sublist in labels]    
    color_list=list_color(lc,FC)
        
    if stack_only:
        array1=array1[2]
        array1 = np.atleast_2d(array1)
        array2=array2[2]
        array2 = np.atleast_2d(array2)        
        labels=labels[2]
        color_list=color_list[lc[0]+lc[1]:lc[0]+lc[1]+lc[2]]
        
    else:
        array1 = [np.atleast_2d(x) for x in array1]
        array1= np.vstack(array1)
        array2 = [np.atleast_2d(x) for x in array2]
        array2= np.vstack(array2)
        labels = [elem for sublegend in labels for elem in sublegend]


    if LCIA=='Climate Change':
        legend_LCIA=['CC \n[kgCO2eq]']
        array1=array1[:,0:1]
        array2=array2[:,0:1]
    elif LCIA=='IW+ Footprint':
        legend_LCIA=['CC \n[kgCO2eq]','Rem. EQ \n[PDF.m2.yr]','Energy \n[MJ deprived]','Rem. HH \n[DALY]','Water \n[m3 worldEq]']
        array1=array1[:,0:5]
        array2=array2[:,0:5]
    else:
        legend_LCIA=['EQ \n[PDF.m2.yr]','HH \n[DALY]']
        array1=array1[:,5:7]
        array2=array2[:,5:7]   
    
    
    # Définir les colonnes
    n_cols = array1.shape[1]
    n_rows = array1.shape[0]
    col_sums = np.sum(array1, axis=0)
    data_normalized_1 = (array1 / col_sums) * 100
    data_normalized_2 = (array2 / col_sums) * 100

    # Index des colonnes
    x1 = np.arange(0, n_cols*3 ,3)
    x2 = np.arange(1, n_cols*3 ,3)

    # Création de l'histogramme empilé avec des couleurs différentes pour chaque ligne
    bottom1 = np.zeros(n_cols)
    bottom2 = np.zeros(n_cols)

    for i in range (n_rows):
        if data_normalized_1[i][0]!=0 or data_normalized_2[i][0]!=0:
            ax.bar(x1, data_normalized_1[i], bottom=bottom1, label=labels[i], color=color_list[i])
            ax.bar(x2, data_normalized_2[i], bottom=bottom2, color=color_list[i])
            bottom1 += data_normalized_1[i]  # Mise à jour de la position de base pour l'empilement
            bottom2 += data_normalized_2[i]  # Mise à jour de la position de base pour l'empilement
        
    for j in np.arange(n_cols-1):
        ax.axvline(x=j*3 + 2, color='grey', linestyle='--', linewidth=0.5)
    
    for j in range (n_cols):
        ax.text(j*3, 102, f"{col_sums[j]:.3g}", ha='center', va='center', fontsize=8)
        ax.text(j*3+1, bottom2[j]+2, f"{bottom2[j]/100*col_sums[j]:.3g}", ha='center', va='center', fontsize=8)

    # Ajouter les détails du graphique
    ax.set_xlabel('Impact Categories')
    ax.set_ylabel('Impact Score [%]')
    ax.set_xticks(np.arange(0.5, len(legend_LCIA)*3+0.4, 3))
    ax.set_xticklabels(legend_LCIA)
    
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    
    handles, legend_lbls = ax.get_legend_handles_labels()
    legend_obj = ax.legend(handles[::-1], legend_lbls[::-1], bbox_to_anchor=(1.4, 1))
    
    bottom_labels = [st.session_state.scenario[0][20], st.session_state.scenario[1][20]]*len(legend_LCIA) # alternance tous les 1 unité
    secax = ax.secondary_xaxis('bottom')
    arr = (3*np.arange(len(legend_LCIA))[:,None] + np.array([0,1])).ravel()
    secax.set_xticks(arr)
    
    if len(legend_LCIA)>2:
        secax.set_xticklabels(bottom_labels, rotation=45, ha='right')
    else:
        secax.set_xticklabels(bottom_labels)
    
    
    ax.set_title(f"Contribution Analysis of the two water electrolysis scenarios providing {st.session_state.scenario[0][0]}")
    ymax = max(np.max(bottom1), np.max(bottom2))*1.1
    ax.set_ylim(0, ymax)
    
    # ===== Tables (S1 / S2) =====
    
    row_labels = [t.get_text() for t in legend_obj.get_texts()][::-1]
    fmt = lambda x: f"{x:.3g}" if isinstance(x, (int, float, np.floating)) else x

    df1 = pd.DataFrame(array1, index=row_labels, columns=legend_LCIA)
    df2 = pd.DataFrame(array2, index=row_labels, columns=legend_LCIA)

    mask = (df1.abs().sum(axis=1) > 1e-10) | (df2.abs().sum(axis=1) > 1e-10)
    df1 = df1[mask]; df2 = df2[mask]

    df1.loc['Total'] = df1.sum(); df2.loc['Total'] = df2.sum()
    df1 = df1.applymap(fmt); df2 = df2.applymap(fmt)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{st.session_state.scenario[0][20]}**")
        st.table(df1)
    with c2:
        st.markdown(f"**{st.session_state.scenario[1][20]}**")
        st.table(df2)
    
    return fig
    



def plotting_technosphere (baseline,technosphere,LCIA,labels,FU):
    
    purple_colors=plt.cm.Purples(np.linspace(0.5, 1, len(baseline)))
    yellow_colors = plt.cm.YlOrBr(np.linspace(0.5, 1, len(technosphere)))
    color_list=np.concatenate([purple_colors,yellow_colors])

    if LCIA=='Climate Change':
        legend_LCIA=['CC \n[kgCO2eq]']
        baseline = [array[0:1] for array in baseline]
        technosphere = [array[0:1] for array in technosphere]
    elif LCIA=='IW+ Footprint':
        legend_LCIA=['CC \n[kgCO2eq]','Rem. EQ \n[PDF.m2.yr]','Energy \n[MJ deprived]','Rem. HH \n[DALY]','Water \n[m3 worldEq]']
        baseline = [array[0:5] for array in baseline]
        technosphere = [array[0:5] for array in technosphere]
    else:
        legend_LCIA=['EQ \n[PDF.m2.yr]','HH \n[DALY]']
        baseline = [array[5:7] for array in baseline]
        technosphere = [array[5:7] for array in technosphere]
   
    # Définir les colonnes

    reference = baseline[0]
    number_case=len(baseline)+len(technosphere)
    print('ref is',reference)
    n_indicator = len(legend_LCIA)
    
    """
    array_normalized=[]
    for k in range (len(baseline)):
        array_normalized+= [(baseline[k]/ reference) * 100]
    for k in range (len(technosphere)):
        array_normalized+= [(technosphere[k]/ reference) * 100]
    """
    
    array_normalized=np.vstack(baseline + technosphere)
    ref_max=np.max(array_normalized, axis=0)
    for k in range (len(array_normalized)):
        array_normalized[k]= (array_normalized[k]/ ref_max) * 100


    # Index des colonnes
    for i in range (number_case):
        x = np.arange(i, (number_case+1)*n_indicator ,number_case+1)
        plt.bar(x, array_normalized[i], label=labels[i], color=color_list[i])

    for j in np.arange(n_indicator-1):
        plt.axvline(x=j*(number_case+1) + 2, color='grey', linestyle='--', linewidth=0.5)
        
    for j in range (n_indicator):
        plt.text(j*3, array_normalized[0][j]+2, f"{array_normalized[0][j]/100*ref_max[j]:.3g}", ha='center', va='center', fontsize=8)
        plt.text(j*3+1, array_normalized[1][j]+2, f"{array_normalized[1][j]/100*ref_max[j]:.3g}", ha='center', va='center', fontsize=8)

    # Ajouter les détails du graphique
    plt.xlabel('Impact Categories')
    plt.ylabel('Impact Score [%]')
    plt.xticks(np.arange(0.5*(number_case-1), n_indicator*(number_case+1) ,number_case+1),legend_LCIA)


    plt.title(f"Comparison of potential impact of technologies providing {st.session_state.scenario[0][0]}")
    
    plt.legend(bbox_to_anchor=(1.4, 1))
    plt.show()
    
    # ===== Table (raw values per case) =====
    raw_values = np.vstack(baseline + technosphere)  # unnormalized values
    df = pd.DataFrame(raw_values)
    df = df[(df.abs() > 1e-10).any(axis=1)]
    df = df[:len(labels)]
    df.columns = legend_LCIA
    df.index = labels[:len(df)]
    df = df.applymap(lambda x: f"{x:.3g}" if isinstance(x, (int, float, np.floating)) else x)
    st.table(df)


