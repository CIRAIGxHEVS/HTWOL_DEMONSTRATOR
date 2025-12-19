#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap, to_hex
import streamlit as st
import plotly.graph_objects as go


# ========= LEGENDS =========

legend_SMR=['H2 Production','Post-Processing', 'Distribution', 'Storage', 'H2-To-Elec Conversion','End-Use Process']
legend_supply=['Electricity Stored in H2', 'Elec-To-H2 Conversion','Compression (PP)','Purification (PP)', 'Distribution', 'Storage', 'H2-To-Elec Conversion','End-Use Process']
legend_detailed=['Electricity', 'Heat','Water','KOH','Stack Manuf.', 'Equipment Manuf.', 'EoL','H2 Leakage','Surplus H2 Prod.']

legend_stack=['Hydrogen Electrode','Oxygen Electrode','Barrier Layer','Contact Layer','Electrolyte','Bipolar Plate','Frame','End plate']
legend_BoP=['Compressor [kW]', 'HEX [m2]', 'Chiller [kW]', 'Rectifier [kW]', 'Separator [m3]', 'Pump [kW]', 'Piping [kg]', 'Instrumentation [kW]', 'Tank [kWstack]', 'Container [m3]']
legend_EL=['Electricity Stored in H2','Elec. Losses Stack','Elec. Consumed BoP','Heat','Water','KOH','Stack Manuf.', 'Equipment Manuf.', 'EoL','H2 Leakage']
legend_FC=['Hydrogen Production','Surplus H2 (Stack Losses)','Surplus H2 (BoP Cons)','Surplus H2 (H2 Leakage)','KOH','Stack Manuf.', 'Equipment Manuf.', 'EoL','H2 Leakage']

inventory_unit   = ["kWh", "kWh", "kg", "kg", "unit", "unit", "unit", "kg H2 leakage", "kgH2"]
inventory_format   = [".3g", ".3g", ".0g", ".2e", ".2e", ".2e", ".2e", ".2g", ".2g"]

inventory_consEL_detailed_unit=["kWh","kWh","kWh", "kWh", "kg", "kg", "unit", "unit", "unit", "kg H2 leakage"]
inventory_consEL_detailed_format   = [".1f", ".1f",".1f", ".1f", ".0f", ".2e", ".2e", ".2e", ".2e", ".2f"]
inventory_consFC_detailed_unit=["kgH2","kgH2","kgH2","kgH2", "kg", "unit", "unit", "unit", "kg H2 leakage"]
inventory_consFC_detailed_format   = [".2g",".2g", ".2g",".2g", ".2e", ".2e", ".2e", ".2e", ".2f"]
inventory_bop_detailed_unit=["kW","m2","kW", "kW", "m3", "kW", "kg", "kW", "kWstack", "m3"]
# ========= HELPERS =========
def _ensure_hex(colors):
    """Convertit une liste de couleurs Matplotlib en hex utilisables par Plotly"""
    out = []
    for c in colors:
        try:
            out.append(mcolors.to_hex(c, keep_alpha=False))
        except Exception:
            out.append(c)
    return out

def preparation_inventories(inventory_values, inventory_unit, inventory_format):
    inventory = [
        ""  # if the value is missing, store an empty string
        if inventory_values[j] is None
        else (
            # format the number with the per-column format, then append the unit
            f"{inventory_values[j]:{inventory_format[j]}} {inventory_unit[j]}"
        )
        for j in range(len(inventory_values))
    ]
    return inventory

"""def preparation_inventories(kgH2_per_FU, inventory_supply_values, inventory_producer_values):
    # Same "general" inventory text repeated for the 7 scenarios/tiers
    inventory_general_detailed = [f"{kgH2_per_FU} kgH2"]
    inventory_general_nodetail=[f"{kgH2_per_FU} kgH2 produced", f"{kgH2_per_FU} kgH2 produced"]

    # Units are the same for all 7 elements (only depend on column j)
    inventories_supply_unit   = ["kWh", "kWh", "kg", "kg", "unit", "unit", "unit", "kg H2 leakage", "kgH2"]
    inventories_producer_unit = ["kWh", "kWh", "kg", "kg", "unit", "unit", "unit", "kg H2 leakage", "kgH2"]

    # Number formats are the same for all 7 elements (only depend on column j)
    # Here: supply has 9 columns, producer has 8 columns
    formats_supply   = [".1f", ".1f", ".0f", ".2e", ".2e", ".2e", ".2e", ".2f", ".2g"]
    formats_producer = [".1f", ".1f", ".0f", ".2e", ".2e", ".2e", ".2e", ".2f", ".2g"]

    # Build formatted strings "value unit" for supply
    st.write(inventory_supply_values,inventory_producer_values)
    inventories_supply = [
        [
            # Format the number with the per-column format (formats_supply[j])
            # Then attach the unit (inventories_supply_unit[j])
            f"{inventory_supply_values[i][j]:{formats_supply[j]}} {inventories_supply_unit[j]}"
            for j in range(len(inventory_supply_values[i]))
        ]
        for i in range(len(inventory_supply_values))
    ]

    # Build formatted strings "value unit" for producer
    inventories_producer = [
        [
            f"{inventory_producer_values[i][j]:{formats_producer[j]}} {inventories_producer_unit[j]}"
            for j in range(len(inventory_producer_values[i]))
        ]
        for i in range(len(inventory_producer_values))
    ]

    return inventory_general, inventories_supply, inventories_producer"""


def result_by_tier(results, tier):
    
    supply,detailed,producer,kgH2_per_FU,inventory_supply_values,inventory_producer_values,detailed_inventory=results

    if tier[4]: #SMR
        result=[]
        for s in supply:
            result.append(np.sum(s, axis=0))
        result=np.vstack([result[0] + result[1], result[2]+result[3],result[4:]])
        legend=legend_SMR
        color=['orangered','gold','green','lightblue','darkblue','purple']
        inventory=preparation_inventories([kgH2_per_FU]*6,[" kgH2"]*6,[".2g"]*6)
        hash=None


    elif tier[3][0]=='Stack (EL)':
        result=detailed[0][1]
        inv=detailed_inventory[0][1]
        legend = legend_stack
        color = [to_hex(c, keep_alpha=False) for c in plt.cm.Greys(np.linspace(0.20, 0.90, 8))]
        if tier[3][1]!='FU':
            stack_per_kgH2=detailed_inventory[0][0][6]*kgH2_per_FU
            result=[r/(stack_per_kgH2) for r in result]
        inventory=preparation_inventories(inv,[" m2 active area"]*len(inv),[".2g"]*len(inv))
        hash=None


    elif tier[3][0]=='BoP (EL)':
        result=detailed[0][2]
        inv=detailed_inventory[0][3]
        legend = legend_BoP
        cmap_bb = LinearSegmentedColormap.from_list(
            'bordeaux_to_brown',
            ["#f9c9ca","#ff888c",'#b74a4e',"#a53131", '#6e0f1a',  '#2b000d']
            )
        color = [to_hex(c, keep_alpha=False) for c in cmap_bb(np.linspace(0, 1, 11))]
        if tier[3][1]!='FU':
            bop_per_FU=detailed_inventory[0][0][7]*kgH2_per_FU
            result=[r/bop_per_FU for r in result]
            #inv=[i/bop_per_FU for i in inv]
        inventory=preparation_inventories(inv,inventory_bop_detailed_unit,[".2g"]*len(inv))
        hash=None

    elif tier[3][0]=='Stack (FC)':
        result=detailed[1][1]
        inv=detailed_inventory[1][1]
        legend = legend_stack
        color = [to_hex(c, keep_alpha=False) for c in plt.cm.Greys(np.linspace(0.20, 0.90, 8))]
        if tier[3][1]!='FU':
            stack_per_FU=detailed_inventory[1][0][6]*kgH2_per_FU
            result=[r/stack_per_FU for r in result]
            #inv=[i/stack_per_FU for i in inv]
        inventory=preparation_inventories(inv,[" m2 active area"]*len(inv),[".2g"]*len(inv))
        hash=None

    elif tier[3][0]=='BoP (FC)':
        result=detailed[1][2]
        inv=detailed_inventory[1][3]
        legend = legend_BoP
        cmap_bb = LinearSegmentedColormap.from_list(
            'bordeaux_to_brown',
            ["#f9c9ca","#ff888c",'#b74a4e',"#a53131", '#6e0f1a',  '#2b000d']
            )
        color = [to_hex(c, keep_alpha=False) for c in cmap_bb(np.linspace(0, 1, 11))]
        if tier[3][1]!='FU':
            bop_per_FU=detailed_inventory[1][0][7]*kgH2_per_FU
            result=[r/bop_per_FU for r in result]
            #inv=[i/bop_per_FU for i in inv]
        inventory=preparation_inventories(inv,inventory_bop_detailed_unit,[".2g"]*len(inv))
        hash=None

    elif tier[3][0]=='Hydrogen Production':

        result=detailed[0][0]
        inv=detailed_inventory[0][0]
        inv=[i*(kgH2_per_FU) for i in inv]
        legend = legend_EL
        color = ['red','pink','hotpink','deeppink','palevioletred','violet','grey','brown','khaki','purple']
        if tier[3][1]!='FU':
            result=[r/(kgH2_per_FU) for r in result]
            inv=[i/(kgH2_per_FU) for i in inv]
        inventory=preparation_inventories(inv,inventory_consEL_detailed_unit,inventory_consEL_detailed_format)
        hash=None

    elif tier[3][0]=='Hydrogen Reconversion':
        result=detailed[1][0]
        inv=detailed_inventory[1][0]
        inv=[i*(kgH2_per_FU/st.session_state.LHV_hydrogen) for i in inv]
        legend = legend_FC
        color = ['orangered','salmon','tomato','sandybrown','indigo','grey','brown','khaki','purple']
        if tier[3][1]!='FU':
            result=[r/(kgH2_per_FU/st.session_state.LHV_hydrogen) for r in result]
            inv=[i/(kgH2_per_FU/st.session_state.LHV_hydrogen) for i in inv]
        inventory=preparation_inventories(inv,inventory_consFC_detailed_unit,inventory_consFC_detailed_format)
        hash=None

    elif not tier[0]:

        if not tier[1]:
            ## preparation no detail ##
            color_supply=['red','orange','yellow','goldenrod','green','lightblue','darkblue','purple']
            result_supply=[]
            for s in supply:
                result_supply.append(np.sum(s, axis=0))
            inventory_supply=[33.3*kgH2_per_FU]*2+[kgH2_per_FU]*6
            inventory_unit_supply=[" kWh produced"]+[f" kWh converted in {kgH2_per_FU:.2g} kgH2"]+[" kgH2 supplied"]*6
            inventory_format_supply=[".3g"]*2+[".2g"]*6
            legend_sup = legend_supply.copy()
            hash=None

            ## preparation full details ##
            reds    = [to_hex(c, keep_alpha=False) for c in plt.cm.Reds(np.linspace(0.7, 1, 9))]
            oranges = [to_hex(c, keep_alpha=False) for c in plt.cm.Oranges(np.linspace(0.20, 1, 9))]
            yellows1 = [to_hex(c, keep_alpha=False) for c in plt.cm.Wistia(np.linspace(0.10, 0.40, 9))]
            yellows2 = [to_hex(c, keep_alpha=False) for c in plt.cm.Wistia(np.linspace(0.50, 0.70, 9))]
            greens  = [to_hex(c, keep_alpha=False) for c in plt.cm.Greens(np.linspace(0.1, 0.85, 9))]
            blues   = [to_hex(c, keep_alpha=False) for c in plt.cm.Blues(np.linspace(0.1, 0.7, 9))]
            indigos = [to_hex(c, keep_alpha=False) for c in plt.cm.PuBu(np.linspace(0.50, 0.95, 9))]
            violets = [to_hex(c, keep_alpha=False) for c in plt.cm.Purples(np.linspace(0.35, 0.95, 9))]
            color_detailed = [reds] + [oranges] +[yellows1]+[yellows2] + [greens] + [blues] + [indigos] + [violets]

            inv_detailed=inventory_supply_values
            result_detailed=supply.copy()

            legend=[]
            color=[]
            inventory_v=[]
            result=[]
            inventory_u=[]
            inventory_f=[]

            if not tier[2][0][0]:
                color_supply[1]='darkorange'
                legend_sup[1]='Hydrogen Production'
                inventory_supply[1]=kgH2_per_FU
                inventory_supply[0]=0
                inventory_unit_supply[1]='kgH2 produced'
                inventory_format_supply[1]=".2g"

            if not tier[2][0][1]:
                color_supply[3]='gold'
                legend_sup[3]='Post-Processing'
                inventory_supply[3]=0

            legend_det=[]
            for i in range (len(legend_sup)):
                legend_for_one_supply=[]
                for k in range (len(legend_detailed)):
                    legend_for_one_supply.append(legend_detailed[k]+' ('+legend_sup[i]+' )')
                legend_det.append(legend_for_one_supply)


            for k in range (len(result_supply)):
                if not tier[2][1][k]:
                    legend.append([legend_sup[k]])
                    color.append([color_supply[k]])
                    result.append([result_supply[k]])
                    inventory_v.append([inventory_supply[k]])
                    inventory_u.append([inventory_unit_supply[k]])
                    inventory_f.append([inventory_format_supply[k]])

                else:
                    legend.append(legend_det[k])
                    color.append(color_detailed[k])
                    result.append(result_detailed[k])
                    inventory_v.append(inv_detailed[k])
                    inventory_u.append(inventory_unit)
                    inventory_f.append(inventory_format)


            if not tier[2][0][0]:
                del color[0]
                inventory_v[1]=[inventory_v[1][k]+inventory_v[0][k] for k in range (len(inventory_v[1]))]
                del inventory_v[0]
                del inventory_u[0]
                del inventory_f[0]
                del legend[0]
                result[1]=[result[1][k]+result[0][k] for k in range (len(result[1]))]
                del result[0]

            if not tier[2][0][1]:
                del color[-6]
                inventory_v[-5]=[inventory_v[-5][k]+inventory_v[-6][k] for k in range (len(inventory_v[-5]))]
                del inventory_v[-6]
                del inventory_u[-6]
                del inventory_f[-6]
                del legend[-6]
                result[-5]=[result[-5][k]+result[-6][k] for k in range (len(result[-5]))]
                del result[-6]

            inventory=preparation_inventories(np.concatenate(inventory_v),np.concatenate(inventory_u),np.concatenate(inventory_f))
            color=np.concatenate(color)
            result=np.concatenate(result)
            legend=np.concatenate(legend)


        else:

            result=[]
            legend=[]
            inventory_v=[]
            inventory_supply=[33.3*kgH2_per_FU]*2+[kgH2_per_FU]*6
            inventory_unit_supply=[" kWh produced"]*2+[f" kWh converted in {kgH2_per_FU:.2g} kgH2"]*2+[" kgH2 supplied"]*12
            inventory_format_supply=[".2g"]*16
            for n in range (len(producer)):
                result.append(np.sum(producer[n], axis=0))
                if (n & 1) == 0:
                    legend.append(legend_supply[n//2])
                    inventory_v.append(inventory_supply[n//2])
                else:
                    legend.append(legend_supply[n//2]+' (Surplus H2 Losses)')
                    inventory_v.append(inventory_supply[n//2]*(inventory_producer_values[n][0]/inventory_producer_values[n-1][0])) #calculation of the H2 eff losses thanks to the more details inventory.
            inventory=preparation_inventories(inventory_v,inventory_unit_supply,inventory_format_supply*2)
            color=['red','red','orange','orange','yellow','yellow','gold','gold','green','green','lightblue','lightblue','darkblue','darkblue','purple','purple']
            hash=[False,True]*8
    

    else:
        supply = [[row[i] for row in supply] for i in range(len(supply[0]))]
        inventory_supply = [[row[i] for row in inventory_supply_values] for i in range(len(inventory_supply_values[0]))]
        P = np.asarray(producer)
        even = P[0::2, ...]
        odd  = P[1::2, ...]
        sum_even = even.sum(axis=0)
        sum_odd  = odd.sum(axis=0)
        
        A, B = sum_even, sum_odd                 
        m = min(A.shape[0], B.shape[0])
        out = np.empty((A.shape[0] + B.shape[0],) + A.shape[1:], dtype=A.dtype)
        out[0:2*m:2, ...] = A[:m, ...]               
        out[1:2*m:2, ...] = B[:m, ...]               
        if A.shape[0] > m: out[2*m:, ...] = A[m:, ...]
        if B.shape[0] > m: out[2*m:, ...] = B[m:, ...]

        producer=out
        
        inventory_no_detail=[]
        for i in inventory_supply:
            inventory_no_detail.append(np.sum(i, axis=0))
 
        if not tier[1]:

            """result=[]
            for s in supply:
                result.append(np.sum(s, axis=0))

            inventory=preparation_inventories(inventory_v,inventory_unit,inventory_format)
            inventory[4]=f"{inventory_supply[4][1]:.2g} unit of electrolyser"
            if st.session_state.FC:
                inventory[4]+=f"<br> {inventory_supply[4][6]:.2g} unit of fuel cell"
            inventory[5]=f"{inventory_supply[5][1]:.2g} unit of BoP (EL and PP)"
            if inventory_supply[5][4]>0:
                inventory[5]+=f"<br> Equipment for distributing {kgH2_per_FU:.2g} kgH2"
            if inventory_supply[5][5]>0:
                inventory[5]+=f"<br> Equipment for storing {kgH2_per_FU:.2g} kgH2"
            if st.session_state.FC:
                inventory[5]+=f"<br> {inventory_supply[5][6]:.2g} unit of BoP (FC)"
            inventory[6]=inventory[4]

            legend = legend_detailed
            color=['pink','deeppink','palevioletred','violet','grey','brown','khaki','purple','salmon']
            hash=[False,False,False,False,False,False,False,False,True]
            
            else:
                result=np.concatenate(supply)

                inventory=preparation_inventories(np.concatenate(inventory_supply),inventory_unit*len(inventory_supply),inventory_format*len(inventory_supply))
                legend=[]
                for i in range (len(legend_detailed)):
                    for k in range (len(legend_supply)):
                        legend.append(legend_supply[k]+' ('+legend_detailed[i]+' )')
        
                pinks    = [to_hex(c, keep_alpha=False) for c in plt.cm.Reds(np.linspace(0.7, 1, 8))]
                reds = [to_hex(c, keep_alpha=False) for c in plt.cm.Oranges(np.linspace(0.10, 0.6, 8))]
                violet = [to_hex(c, keep_alpha=False) for c in plt.cm.Purples(np.linspace(0.1, 0.5, 8))]
                orchids = [to_hex(c, keep_alpha=False) for c in plt.cm.Purples(np.linspace(0.6, 1, 8))]
                greys = [to_hex(c, keep_alpha=False) for c in plt.cm.Greys(np.linspace(0.10, 0.60, 8))]
                browns   = [to_hex(c, keep_alpha=False) for c in plt.cm.Blues(np.linspace(0.30, 0.6, 8))]
                greens  = [to_hex(c, keep_alpha=False) for c in plt.cm.Greens(np.linspace(0.25, 0.85, 8))]
                purple = [to_hex(c, keep_alpha=False) for c in plt.cm.Purples(np.linspace(0.6, 1, 8))]
                oranges = [to_hex(c, keep_alpha=False) for c in plt.cm.Oranges(np.linspace(0.1, 0.4, 8))]

                color = pinks + reds+ violet +orchids+ greys  + browns + greens + purple + oranges
                hash=[False]*64+[True]*8"""
            
            ## preparation no detail ##
            color_supply=['pink','deeppink','palevioletred','violet','grey','brown','khaki','purple','salmon']
            hash_supply=[False,False,False,False,False,False,False,False,True]
            result_supply=[]
            for s in supply:
                result_supply.append(np.sum(s, axis=0))
            inventory_sup=inventory_no_detail.copy()
            inventory_sup[4]=None
            inventory_sup[5]=None
            inventory_sup[6]=None
            inventory_unit_supply=inventory_unit.copy()
            inventory_format_supply=inventory_format.copy()
            legend_sup = legend_detailed.copy()

            ## preparation full details ##
            pinks = [to_hex(c, keep_alpha=False) for c in plt.cm.RdPu(np.linspace(0.35, 0.9, 8))]
            reds = [to_hex(c, keep_alpha=False) for c in plt.cm.Oranges(np.linspace(0.10, 0.6, 8))]
            violet = [to_hex(c, keep_alpha=False) for c in plt.cm.Purples(np.linspace(0.1, 0.5, 8))]
            orchids = [to_hex(c, keep_alpha=False) for c in plt.cm.Purples(np.linspace(0.6, 1, 8))]
            greys = [to_hex(c, keep_alpha=False) for c in plt.cm.Greys(np.linspace(0.10, 0.60, 8))]
            browns   = [to_hex(c, keep_alpha=False) for c in plt.cm.Blues(np.linspace(0.30, 0.6, 8))]
            greens  = [to_hex(c, keep_alpha=False) for c in plt.cm.Greens(np.linspace(0.25, 0.85, 8))]
            purple = [to_hex(c, keep_alpha=False) for c in plt.cm.Purples(np.linspace(0.6, 1, 8))]
            oranges = [to_hex(c, keep_alpha=False) for c in plt.cm.Oranges(np.linspace(0.1, 0.4, 8))]

            color_detailed = [pinks] + [reds]+ [violet] +[orchids]+ [greys]  + [browns] + [greens] + [purple] + [oranges]
            hash_detailed=[[False]*8]*8+[[True]*8]
            inventory_unit_detailed=[[inventory_unit[k]] * 8 for k in range(len(inventory_unit))]
            inventory_format_detailed=[[inventory_format[k]] * 8 for k in range(len(inventory_format))]

            inv_detailed=inventory_supply.copy()
            inventory=preparation_inventories(np.concatenate(inventory_supply_values),inventory_unit*len(inventory_supply_values),inventory_format*len(inventory_supply_values))
            result_detailed=supply.copy()

            legend=[]
            color=[]
            inventory_v=[]
            result=[]
            inventory_u=[]
            inventory_f=[]
            hash=[]

            legend_det=[]
            for i in range (len(legend_detailed)):
                legend_for_one_unit=[]
                for k in range (len(legend_supply)):
                    legend_for_one_unit.append(legend_detailed[i]+' ('+legend_supply[k]+' )')
                legend_det.append(legend_for_one_unit)


            for k in range (len(result_supply)):
                if not tier[2][1][k+8]:
                    legend.append([legend_sup[k]])
                    color.append([color_supply[k]])
                    result.append([result_supply[k]])
                    inventory_v.append([inventory_sup[k]])
                    inventory_u.append([inventory_unit_supply[k]])
                    inventory_f.append([inventory_format_supply[k]])
                    hash.append([hash_supply[k]])

                else:
                    legend.append(legend_det[k])
                    color.append(color_detailed[k])
                    result.append(result_detailed[k])
                    inventory_v.append(inv_detailed[k])
                    inventory_u.append(inventory_unit_detailed[k])
                    inventory_f.append(inventory_format_detailed[k])
                    hash.append(hash_detailed[k])

            inventory=preparation_inventories(np.concatenate(inventory_v),np.concatenate(inventory_u),np.concatenate(inventory_f))
            ## Non sense to sum amount of stack units and amount of equipment units between different modules ##

            color=np.concatenate(color)
            result=np.concatenate(result)
            legend=np.concatenate(legend)
            hash=np.concatenate(hash)



        else:

            result=[]
            legend=[]
            factor_inv=[]
            for n in range (len(producer)):
                result.append(producer[n])
                if (n & 1) == 0:
                    legend.append(legend_detailed[n//2])
                    factor_inv.append(1)
                else:
                    legend.append(legend_detailed[n//2]+' (Surplus H2 Losses)')
                    factor_inv.append(producer[n][0]/producer[n-1][0])
            inventory_v = [x
                        for k in range(len(inventory_no_detail))
                        for x in (inventory_no_detail[k] * factor_inv[2*k],
                                    inventory_no_detail[k] * factor_inv[2*k+1])]

            inventory_u = [u for u in inventory_unit for _ in range(2)]
            inventory_f = [f for f in inventory_format for _ in range(2)]
            inventory=preparation_inventories(inventory_v,inventory_u,inventory_f)
            inventory[4*2]=f"{inventory_supply[4][1]:.2g} unit of electrolyser"
            inventory[4*2+1]=f"{factor_inv[9]:.2g} stack manufacturing"
            if st.session_state.FC:
                inventory[4]+=f"<br> {inventory_supply[4][6]:.2g} unit of fuel cell"
            inventory[5]=f"{inventory_supply[5][1]:.2g} unit of BoP (EL and PP)"
            inventory[5*2+1]=f"{factor_inv[11]:.2g} equipment manufacturing"
            if inventory_supply[5][4]>0:
                inventory[5]+=f"<br> Equipment for distributing {kgH2_per_FU:.2g} kgH2"
            if inventory_supply[5][5]>0:
                inventory[5]+=f"<br> Equipment for storing {kgH2_per_FU:.2g} kgH2"
            if st.session_state.FC:
                inventory[5]+=f"<br> {inventory_supply[5][6]:.2g} unit of BoP (FC)"
            inventory[6*2]=inventory[8]
            inventory[6*2+1]=f"{factor_inv[9]:.2g} stack eol"


            color=['pink','pink','deeppink','deeppink','palevioletred','palevioletred','violet','violet','grey','grey','brown','brown','khaki','khaki','purple','purple','salmon','salmon']
            hash=[False,True]*9
    return result, inventory, legend, color, hash


# ========= PLOTTING =========
def plotting(result, tier, LCIA):
    array, inventory, labels, color_list, hash = result_by_tier(result, tier)
    array = np.vstack([np.atleast_2d(x) for x in array])

    if LCIA == 'Climate Change':
        legend_LCIA = ['CC <br>[kgCO2eq]']; array = array[:, 0:1]
    elif LCIA == 'IW+ Footprint':
        legend_LCIA = ['CC <br>[kgCO2eq]','Rem. EQ <br>[PDF.m2.yr]',
                       'Fossil and Nuc. Energy <br>[MJ deprived]','Rem. HH <br>[DALY]','Water <br>[m3 worldEq]']
        array = array[:, 0:5]
    else:
        legend_LCIA = ['EQ <br>[PDF.m2.yr]','HH <br>[DALY]']; array = array[:, 5:7]

    col_sums = np.sum(array, axis=0)
    data_norm = (array / col_sums) * 100

    # ensure inventory is aligned and stringified
    if inventory is None:
        inventory = [""] * len(labels)
    else:
        inventory = list(inventory)
        if len(inventory) < len(labels):
            inventory = inventory + [""] * (len(labels) - len(inventory))
        inventory = ["" if v is None else str(v) for v in inventory]

    fig = go.Figure()

    for i, lbl in enumerate(labels):
        y_f = np.asarray(data_norm[i], dtype=float)

        tol = 1e-12
        if np.all(np.isclose(y_f, 0.0, atol=tol)):
            continue

        x_f = legend_LCIA

        c = color_list[i]
        c_f = c if not isinstance(c, (list, tuple, np.ndarray)) else c

        # customdata per bar segment: [inventory_text, absolute_value]
        inv_i = inventory[i] if i < len(inventory) else ""
        customdata_i = np.column_stack([np.repeat(inv_i, len(x_f)), np.asarray(array[i], dtype=float)])

        marker_kwargs = dict(color=c_f)
        if hash is not None and i < len(hash) and bool(hash[i]):
            marker_kwargs["pattern"] = dict(shape="/", fgcolor="black", fillmode="overlay", solidity=0.2)

        fig.add_trace(go.Bar(
            x=x_f,
            y=y_f,
            name=lbl,
            marker=marker_kwargs,
            customdata=customdata_i,
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "%{customdata[0]}<br>"
                "Impact score : %{y:.1f}% <br>"
                "%{x}: %{customdata[1]:.3g}"
                "<extra></extra>"
            ),
            hoverlabel=dict(font=dict(color=c_f))
        ))

    # === absolute values above stacks ===
    for j, total in enumerate(col_sums):
        fig.add_annotation(
            x=legend_LCIA[j],
            y=105,
            text=f"{total:.3g}",
            showarrow=False,
            font=dict(size=12, color="black")
        )
    
    if st.session_state.tier[0][3][0]=="None":
        if st.session_state.FU=="1 kg H2":
            title_selected=f"Contribution Analysis of the reference scenario providing {st.session_state.FU} ({st.session_state.scenario[0][2]} bar and {st.session_state.scenario[0][3]}) "
        else:
            title_selected=f"Contribution Analysis of the reference scenario providing {st.session_state.FU} "
    else:
        title_selected=f"Zoom on {st.session_state.tier[0][3][0]} (scaled to : {st.session_state.tier[0][3][1]})"
    
    fig.update_layout(
        barmode="stack",
        title=title_selected,
        xaxis_title="Impact Categories", yaxis_title="Contribution [%]", yaxis_range=[0, 110]
    )
    st.plotly_chart(fig, use_container_width=True)

    # Table
    legend_LCIA_df = [s.replace("<br>", "\n") for s in legend_LCIA]
    fmt = lambda x: f"{x:.3g}" if isinstance(x, (int, float, np.floating)) else x

    df = pd.DataFrame(array, index=labels, columns=legend_LCIA_df)

    # (1) inventory as first column
    df.insert(0, "Inventory", inventory[:len(labels)])

    df = df[(df.drop(columns=["Inventory"]).abs() > 1e-10).any(axis=1)]
    df.loc['Total'] = df.drop(columns=["Inventory"]).sum()
    df.loc['Total', 'Inventory'] = ""

    df = df.applymap(fmt)

    st.dataframe(df, use_container_width=True)

    # --- Export results


    st.download_button(
        "Export Results (CSV)",
        data=df.to_csv(index=True).encode("utf-8"),
        file_name=f"result_{st.session_state.scenario[0][0]}.csv",
        mime="text/csv",
    )




def plotting_comp(results, tier, LCIA, scenario_name):
    """
    results: list like [result1, result2, ...] (>=2)
    Plots the same stacked comparison bars, but for N scenarios (+ tables for each).
    """
    # === Prepare data (labels/colors/hatches from the 1st scenario) ===
    array0, inventory0, labels, color_list, hash_flags = result_by_tier(results[0], tier)
    array0 = np.vstack([np.atleast_2d(x) for x in array0]).astype(float)

    arrays = [array0]
    inventories = [inventory0]

    for r in results[1:]:
        a, inv, _, _, _ = result_by_tier(r, tier)
        a = np.vstack([np.atleast_2d(x) for x in a]).astype(float)
        arrays.append(a)
        inventories.append(inv)

    # === LCIA slicing ===
    if LCIA == 'Climate Change':
        legend_LCIA = ['CC <br>[kgCO2eq]']
        arrays = [a[:, 0:1] for a in arrays]
    elif LCIA == 'IW+ Footprint':
        legend_LCIA = [
            'CC <br>[kgCO2eq]', 'Rem. EQ <br>[PDF.m2.yr]',
            'Fossil and Nuc. Energy <br>[MJ deprived]', 'Rem. HH <br>[DALY]',
            'Water <br>[m3 worldEq]'
        ]
        arrays = [a[:, 0:5] for a in arrays]
    else:
        legend_LCIA = ['EQ <br>[PDF.m2.yr]', 'HH <br>[DALY]']
        arrays = [a[:, 5:7] for a in arrays]

    # === Normalisation (relative to scenario 1) ===
    col_sums = np.sum(arrays[0], axis=0)
    col_sums_safe = col_sums.copy()
    col_sums_safe[col_sums_safe == 0] = 1.0
    datas = [np.round((a / col_sums_safe) * 100, 1) for a in arrays]

    # === Positioning (proportional spacing to bar width) ===
    n_scen = len(results)
    n_cols = datas[0].shape[1]

    bar_width = 0.8
    intra_gap = 0.15 * bar_width
    cat_gap = 1.20 * bar_width

    step = bar_width + intra_gap
    group_spacing = n_scen * step + cat_gap

    x_base = np.arange(0, n_cols * group_spacing, group_spacing)
    xs = [x_base + s * step for s in range(n_scen)]
    bottoms = [np.zeros(n_cols) for _ in range(n_scen)]

    # === Ensure inventories aligned and stringified (one list per scenario) ===
    invs = []
    for s in range(n_scen):
        inv = inventories[s]
        if inv is None:
            inv = [""] * len(labels)
        else:
            inv = list(inv)
            if len(inv) < len(labels):
                inv = inv + [""] * (len(labels) - len(inv))
            inv = ["" if v is None else str(v) for v in inv]
        invs.append(inv)

    fig = go.Figure()

    tol = 1e-12
    for i, lbl in enumerate(labels):
        if all(np.all(np.isclose(np.asarray(d[i], float), 0.0, atol=tol)) for d in datas):
            continue

        c = color_list[i]
        c_f = c if not isinstance(c, (list, tuple, np.ndarray)) else c

        marker_kwargs = dict(color=c_f)
        if hash_flags is not None and i < len(hash_flags) and bool(hash_flags[i]):
            marker_kwargs["pattern"] = dict(shape="/", fgcolor="black", fillmode="overlay", solidity=0.2)

        for s in range(n_scen):
            y_pct = np.asarray(datas[s][i], dtype=float)
            abs_vals = np.asarray(arrays[s][i], dtype=float)

            inv_i = invs[s][i] if i < len(invs[s]) else ""
            customdata = np.column_stack([np.repeat(inv_i, n_cols), abs_vals, y_pct])  # [inv, abs, pct]

            fig.add_trace(go.Bar(
                x=xs[s], y=y_pct,
                name=lbl, legendgroup=lbl, showlegend=(s == 0),
                marker=marker_kwargs,
                base=bottoms[s],
                width=bar_width,
                customdata=customdata,
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "%{customdata[0]}<br>"
                    "Impact score: %{customdata[2]:.1f} %<br>"
                    "%{x}: %{customdata[1]:.3g}"
                    "<extra></extra>"
                ),
                hoverlabel=dict(font=dict(color=c_f))
            ))
            bottoms[s] += y_pct

    # === Annotations totals + scenario names (vertical) ===
    totals_abs = [a.sum(axis=0) for a in arrays]

    for j in range(n_cols):
        for s in range(n_scen):
            fig.add_annotation(
                x=xs[s][j], y=bottoms[s][j] + 15,
                text=f"{totals_abs[s][j]:.3g}",
                showarrow=False, font=dict(size=11, color="black")
            )
            fig.add_annotation(
                x=xs[s][j], y=-20,
                text=str(scenario_name[s]),
                textangle=45,
                showarrow=False, font=dict(size=11, color="black")
            )

    # === Layout ===
    ymax = max((b.max() if b.size else 0) for b in bottoms) if bottoms else 0
    
    if st.session_state.tier[0][3][0]=="None":
        if st.session_state.FU=="1 kg H2":
            title_selected=f"Contribution Analysis of the hydrogen product systems providing {st.session_state.FU} ({st.session_state.scenario[0][2]} bar and {st.session_state.scenario[0][3]}) "
        else:
            title_selected=f"Contribution Analysis of the hydrogen product systems providing {st.session_state.FU} "
    else:
        title_selected=f"Zoom on {st.session_state.tier[0][3][0]} (scaled to : {st.session_state.tier[0][3][1]})"
        
    fig.update_layout(
        barmode="stack",
        title=title_selected,
        xaxis=dict(
            tickmode='array',
            tickvals=[np.mean([xs[s][j] for s in range(n_scen)]) for j in range(n_cols)],
            ticktext=legend_LCIA,
            title="Impact Categories"
        ),
        yaxis=dict(
            title="Impact Score [%]",
            range=[-20, max(110, float(ymax) * 1.25)]
        ),
        bargap=0.25,
        bargroupgap=0.05,
        legend=dict(title="Contributors", traceorder="normal", orientation="v"),
        margin=dict(t=90, b=140, l=70, r=70),
        hovermode="closest",
        hoverlabel=dict(bgcolor="white", font_size=14),
        hoverdistance=20, spikedistance=20
    )

    st.plotly_chart(fig, use_container_width=True)

    # === Tables (one per scenario) ===
    legend_LCIA_tbl = [s.replace("<br>", "\n") for s in legend_LCIA]
    fmt = lambda x: f"{x:.3g}" if isinstance(x, (int, float, np.floating)) else x

    dfs = []
    for s, a in enumerate(arrays):
        df = pd.DataFrame(a, index=labels, columns=legend_LCIA_tbl)
        df.insert(0, "Inventory", invs[s][:len(labels)])
        df = df[(df.drop(columns=["Inventory"]).abs() > 1e-10).any(axis=1)]
        df.loc['Total'] = df.drop(columns=["Inventory"]).sum()
        df.loc['Total', 'Inventory'] = ""
        df = df.applymap(fmt)
        dfs.append(df)

    cols = st.columns(n_scen)
    for s, (col, df) in enumerate(zip(cols, dfs)):
        scen_title = (
            st.session_state.scenario[s][0]
            if "scenario" in st.session_state and s < len(st.session_state.scenario)
            else f"S{s+1}"
        )
        with col:
            st.markdown(f"**{scen_title}**")
            st.dataframe(df, use_container_width=True)

    # === Export Excel with all tables (one sheet per scenario) ===
    import io

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for s, df in enumerate(dfs):
            sheet = str(scenario_name[s]) if s < len(scenario_name) else f"S{s+1}"
            sheet = sheet[:31]  # Excel sheet name limit
            df.to_excel(writer, sheet_name=sheet, index=True)

    st.download_button(
        "Export Results (Excel)",
        data=output.getvalue(),
        file_name="results_comparison.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

   
def plotting_technosphere(baseline, technosphere, LCIA, labels):
    #purple_colors = plt.cm.Purples(np.linspace(0.5,1,len(baseline)))
    #yellow_colors = plt.cm.YlOrBr(np.linspace(0.5,1,len(technosphere)))
    color_list = ('mediumpurple','chocolate','yellowgreen','black','steelblue','crimson','silver')

    if LCIA == 'Climate Change':
        legend_LCIA=['CC <br>[kgCO2eq]']
        baseline=[a[0:1] for a in baseline]; technosphere=[a[0:1] for a in technosphere]
    elif LCIA == 'IW+ Footprint':
        legend_LCIA=['CC <br>[kgCO2eq]','Rem. EQ <br>[PDF.m2.yr]','Fossil and Nuc. Energy <br>[MJ deprived]','Rem. HH <br>[DALY]','Water <br>[m3 worldEq]']
        baseline=[a[0:5] for a in baseline]; technosphere=[a[0:5] for a in technosphere]
    else:
        legend_LCIA=['EQ <br>[PDF.m2.yr]','HH <br>[DALY]']
        baseline=[a[5:7] for a in baseline]; technosphere=[a[5:7] for a in technosphere]
    arr = np.vstack(baseline+technosphere)
    ref_max = np.max(baseline, axis=0)
    arr_norm = (arr / ref_max) * 100

    fig = go.Figure()
    for i, lbl in enumerate(labels):
        fig.add_trace(go.Bar(
            x=legend_LCIA,
            y=arr_norm[i],
            name=lbl,
            marker_color=color_list[i],
            text=[f"{arr[i, j]:.3g}" for j in range(arr.shape[1])],
            textposition="outside",
            texttemplate="%{text}",
            customdata=arr[i],
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"     # the label
                "Impact score : %{y:.1f} % <br>"  # percent, rounded, no thousands sep
                "%{x}: %{customdata:.3g}"         # legend_LCIA + absolute value
                "<extra></extra>"
            ),
            hoverlabel=dict(font=dict(color=color_list[i])))
        )


     # leave some headroom for the outside labels
    fig.update_yaxes(range=[0, max(110, np.nanmax(arr_norm) * 1.15)])

    fig.update_layout( barmode="group", title=f"Comparison of potential impact of technologies providing {st.session_state.FU}", xaxis_title="Impact Categories", yaxis_title="Impact Score [%]" )
    
    st.plotly_chart(fig, use_container_width=True)

    legend_LCIA = [s.replace("<br>","\n") for s in legend_LCIA]
    fmt = lambda x: f"{x:.3g}" if isinstance(x,(int,float,np.floating)) else x
    df = pd.DataFrame(arr, index=labels, columns=legend_LCIA)
    df = df[(df.abs()>1e-10).any(axis=1)]
    df = df.applymap(fmt)

    st.dataframe(df,use_container_width=True)

    # --- Export CSV
    st.download_button(
        "Export Results (CSV)",
        data=df.to_csv(index=True).encode("utf-8"),
        file_name=f"comp_technosphere_{st.session_state.scenario[0][0]}.csv",
        mime="text/csv",
    )


def plotting_stack(result, LCIA, labels):
    purple_colors = plt.cm.Purples(np.linspace(0.5,1,len(baseline)))
    yellow_colors = plt.cm.YlOrBr(np.linspace(0.5,1,len(technosphere)))
    color_list = _ensure_hex(np.concatenate([purple_colors,yellow_colors]))

    if LCIA == 'Climate Change':
        legend_LCIA=['CC \n[kgCO2eq]']
        baseline=[a[0:1] for a in baseline]; technosphere=[a[0:1] for a in technosphere]
    elif LCIA == 'IW+ Footprint':
        legend_LCIA=['CC \n[kgCO2eq]','Rem. EQ \n[PDF.m2.yr]','Fossil and Nuc. Energy \n[MJ deprived]','Rem. HH \n[DALY]','Water \n[m3 worldEq]']
        baseline=[a[0:5] for a in baseline]; technosphere=[a[0:5] for a in technosphere]
    else:
        legend_LCIA=['EQ \n[PDF.m2.yr]','HH \n[DALY]']
        baseline=[a[5:7] for a in baseline]; technosphere=[a[5:7] for a in technosphere]
    
    arr = np.vstack(baseline+technosphere)
    ref_max = np.max(arr, axis=0)
    arr_norm = (arr / ref_max) * 100

    fig = go.Figure()
    for i, lbl in enumerate(labels):
        fig.add_trace(go.Bar(
            x=legend_LCIA,
            y=arr_norm[i],
            name=lbl,
            marker_color=color_list[i],
            text=[f"{arr[i, j]:.3g}" for j in range(arr.shape[1])],
            textposition="outside",
            texttemplate="%{text}",
            customdata=arr[i],
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"     # the label
                "Impact score : %{y:.1f} % <br>"  # percent, rounded, no thousands sep
                "%{x}: %{customdata:.3g}"         # legend_LCIA + absolute value
                "<extra></extra>"
            ),
            hoverlabel=dict(font=dict(color=color_list[i])))
        )


     # leave some headroom for the outside labels
    fig.update_yaxes(range=[0, max(110, np.nanmax(arr_norm) * 1.15)])

    fig.update_layout( barmode="group", title=f"Comparison of potential impact of technologies providing {st.session_state.FU}", xaxis_title="Impact Categories", yaxis_title="Impact Score [%]" )
    
    st.plotly_chart(fig, use_container_width=True)
    fmt = lambda x: f"{x:.3g}" if isinstance(x,(int,float,np.floating)) else x
    df = pd.DataFrame(arr, index=labels, columns=legend_LCIA)
    df = df[(df.abs()>1e-10).any(axis=1)]
    df = df.applymap(fmt)
    st.table(df)


