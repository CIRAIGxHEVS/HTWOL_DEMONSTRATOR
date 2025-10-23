#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import to_hex
import streamlit as st
import plotly.graph_objects as go

# ========= LEGENDS =========


legend_simplified=['Electricity Stored in H2', 'Elec-To-H2 Conversion','Post-Processing', 'Distribution', 'Storage', 'H2-To-Elec Conversion','End-Use Process']
legend_detailed=['Electricity', 'Heat','Other Cons.','Stack Manuf.', 'Equipment Manuf.', 'EoL','H2 Leakage','Surplus H2 Prod.']
legend_detailed_2=[['Electricity (Stack Losses)','Electricity (BoP Cons.)'], ['Water','KOH'],['Cathode','Anode','Contact Layer','Barrier Layer','Membrane','Bipolar','Frame','Endplate'], ['Compressor [kW]', 'HEX [m2]', 'Chiller [kW]', 'Rectifier [kW]', 'Separator [m3]', 'Pump [kW]', 'Piping [kg]', 'Instrumentation [kW]', 'Tank [kWstack]', 'Container [m3]','Heater [kW]'], ['End-Of-Life'],['H2 Leakage'], ['Surplus H2 Prod. (Stack Losses)','Surplus H2 Prod. (BoP Cons.)','Surplus H2 Prod. (H2 Leakage Losses)']]

legend_stack=['Cathode','Anode','Contact Layer','Barrier Layer','Membrane','Bipolar','Frame','Endplate']
legend_BoP=['Compressor [kW]', 'HEX [m2]', 'Chiller [kW]', 'Rectifier [kW]', 'Separator [m3]', 'Pump [kW]', 'Piping [kg]', 'Instrumentation [kW]', 'Tank [kWstack]', 'Container [m3]','Heater [kW]']
legend_cons_EL=['Electricity Losses','Electricity BoP','Heat','Water','KOH','H2 Leakage']

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


def list_color(L, FC):
    if FC:
        all_colors = [plt.cm.Oranges(np.linspace(0.4, 0.6, 1)),
                      plt.cm.RdPu(np.linspace(0.4, 1, L[3])),
                      plt.cm.Purples(np.linspace(0.5, 0.7, 1))]
        all_colors = np.vstack(all_colors)[:L[0]]
        red2_colors = plt.cm.Reds(np.linspace(0.6, 1, L[1]))
        blue_colors = plt.cm.Blues(np.linspace(0.2, 1, L[2]))
        lightgray_colors = plt.cm.Greys(np.linspace(0.2, 0.6, L[3]))
        green_colors = plt.cm.Greens(np.linspace(0.5, 1, L[4]))
        black_colors = plt.cm.Greys(np.linspace(0.7, 1, L[5]))
        color_list = np.concatenate([all_colors, red2_colors, blue_colors,
                                     lightgray_colors, green_colors, black_colors])
    else:
        red_colors = plt.cm.Reds(np.linspace(0.4, 0.6, L[0]))
        red2_colors = plt.cm.Reds(np.linspace(0.6, 1, L[1]))
        blue_colors = plt.cm.Blues(np.linspace(0.2, 1, L[2]))
        lightgray_colors = plt.cm.Greys(np.linspace(0.2, 0.6, L[3]))
        green_colors = plt.cm.Greens(np.linspace(0.5, 1, L[4]))
        gray_colors = plt.cm.Greys(np.linspace(0.2, 0.6, L[5]))
        purple_colors = plt.cm.Purples(np.linspace(0.5, 1, L[6]))
        yellow_colors = plt.cm.YlOrBr(np.linspace(0.2, 1, L[7]))
        black_colors = plt.cm.Greys(np.linspace(0.7, 1, L[8]))
        color_list = np.concatenate([red_colors, red2_colors, blue_colors,
                                     lightgray_colors, green_colors, gray_colors,
                                     purple_colors, yellow_colors, black_colors])

    return _ensure_hex(color_list)


def result_by_tier(results, tier):
    supply,detailed,producer=results
    if not tier[0]:    
        if not tier[1]:

            if not tier[2]:
                result=[]
                for s in supply:
                    result.append(np.sum(s, axis=0))
                legend = legend_simplified
                color=['red','orange','gold','green','lightblue','darkblue','purple']
                hash=None
            
            else:
                result=np.concatenate(supply)
                legend=[]
                for i in range (len(legend_simplified)):
                    for k in range (len(legend_detailed)):
                        legend.append(legend_detailed[k]+' ('+legend_simplified[i]+' )')

                reds    = [to_hex(c, keep_alpha=False) for c in plt.cm.Reds(np.linspace(0.7, 1, 8))]
                oranges = [to_hex(c, keep_alpha=False) for c in plt.cm.Oranges(np.linspace(0.20, 1, 8))]
                yellows = [to_hex(c, keep_alpha=False) for c in plt.cm.Wistia(np.linspace(0.10, 0.60, 8))]
                greens  = [to_hex(c, keep_alpha=False) for c in plt.cm.Greens(np.linspace(0.1, 0.85, 8))]
                blues   = [to_hex(c, keep_alpha=False) for c in plt.cm.Blues(np.linspace(0.1, 0.7, 8))]
                indigos = [to_hex(c, keep_alpha=False) for c in plt.cm.PuBu(np.linspace(0.50, 0.95, 8))]
                violets = [to_hex(c, keep_alpha=False) for c in plt.cm.Purples(np.linspace(0.35, 0.95, 8))]

                color = reds + oranges + yellows + greens + blues + indigos + violets
                hash=None

        else:

            result=[]
            legend=[]
            for n in range (len(producer)):
                result.append(np.sum(producer[n], axis=0))
                if (n & 1) == 0:
                    legend.append(legend_simplified[n//2])
                else:
                    legend.append(legend_simplified[n//2]+' (Surplus H2 Losses)')

            color=['red','red','orange','orange','gold','gold','green','green','lightblue','lightblue','darkblue','darkblue','purple','purple']
            hash=[False,True]*7
    

    else:
        supply = [[row[i] for row in supply] for i in range(len(supply[0]))]
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

        if not tier[1]:
            
            if not tier[2]:
                result=[]
                for s in supply:
                    result.append(np.sum(s, axis=0))
                legend = legend_detailed
                color=['pink','deeppink','violet','grey','brown','khaki','purple','salmon']
                hash=[False,False,False,False,False,False,False,True]
            
            else:
                result=np.concatenate(supply)
                legend=[]
                for i in range (len(legend_detailed)):
                    for k in range (len(legend_simplified)):
                        legend.append(legend_simplified[k]+' ('+legend_detailed[i]+' )')
        

                pinks    = [to_hex(c, keep_alpha=False) for c in plt.cm.Reds(np.linspace(0.7, 1, 7))]
                reds = [to_hex(c, keep_alpha=False) for c in plt.cm.Oranges(np.linspace(0.10, 0.6, 7))]
                violet = [to_hex(c, keep_alpha=False) for c in plt.cm.Purples(np.linspace(0.1, 0.6, 7))]
                greys = [to_hex(c, keep_alpha=False) for c in plt.cm.Greys(np.linspace(0.10, 0.60, 7))]
                browns   = [to_hex(c, keep_alpha=False) for c in plt.cm.Blues(np.linspace(0.30, 0.6, 7))]
                greens  = [to_hex(c, keep_alpha=False) for c in plt.cm.Greens(np.linspace(0.25, 0.85, 7))]
                purple = [to_hex(c, keep_alpha=False) for c in plt.cm.Purples(np.linspace(0.6, 1, 7))]
                oranges = [to_hex(c, keep_alpha=False) for c in plt.cm.Oranges(np.linspace(0.1, 0.4, 7))]

                color = pinks + reds+ violet + greys  + browns + greens + purple + oranges
                hash=[False]*49+[True]*7

        else:

            result=[]
            legend=[]
            for n in range (len(producer)):
                result.append(producer[n])
                if (n & 1) == 0:
                    legend.append(legend_detailed[n//2])
                else:
                    legend.append(legend_detailed[n//2]+' (Surplus H2 Losses)')

            color=['pink','pink','deeppink','deeppink','violet','violet','grey','grey','brown','brown','khaki','khaki','purple','purple','salmon','salmon']
            hash=[False,True]*8
    return result, legend, color, hash


# ========= PLOTTING =========
def plotting(result, tier, LCIA):
    array, labels, color_list,hash = result_by_tier(result, tier)
    array = np.vstack([np.atleast_2d(x) for x in array])

    if LCIA == 'Climate Change':
        legend_LCIA = ['CC <br>[kgCO2eq]']; array = array[:, 0:1]
    elif LCIA == 'IW+ Footprint':
        legend_LCIA = ['CC <br>[kgCO2eq]','Rem. EQ <br>[PDF.m2.yr]',
                       'Fossil and Nuc. Energy <br>n[MJ deprived]','Rem. HH <br>[DALY]','Water <br>[m3 worldEq]']
        array = array[:, 0:5]
    else:
        legend_LCIA = ['EQ <br>[PDF.m2.yr]','HH <br>[DALY]']; array = array[:, 5:7]

    col_sums = np.sum(array, axis=0)
    data_norm = (array / col_sums) * 100

    fig = go.Figure()
 
    for i, lbl in enumerate(labels):
        y_f = np.asarray(data_norm[i], dtype=float)   # plot all columns

        # skip the whole series if everything is (near) zero
        tol = 1e-12
        if np.all(np.isclose(y_f, 0.0, atol=tol)):
            continue

        x_f = legend_LCIA

        c = color_list[i]
        c_f = c if not isinstance(c, (list, tuple, np.ndarray)) else c

        marker_kwargs = dict(color=c_f)
        if hash is not None and i < len(hash) and bool(hash[i]):
            marker_kwargs["pattern"] = dict(shape="/", fgcolor="black", fillmode="overlay", solidity=0.2)

        fig.add_trace(go.Bar(
            x=x_f,
            y=y_f,
            name=lbl,                  # <- label (trace name)
            marker=marker_kwargs,
            customdata=array[i],       # pass absolute values for tooltip
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"     # the label
                "Impact score : %{y:.1f}% <br>"  # percent, rounded, no thousands sep
                "%{x}: %{customdata:.3g}"         # legend_LCIA + absolute value
                "<extra></extra>"
            ),
            hoverlabel=dict(font=dict(color=c_f))
        ))
            
    # === absolute values above stacks ===
    for j, total in enumerate(col_sums):
        fig.add_annotation(
            x=legend_LCIA[j],
            y=105,  # a bit above max (since axis range is 110)
            text=f"{total:.3g}",
            showarrow=False,
            font=dict(size=12, color="black")
        )

    fig.update_layout(
        barmode="stack",
        title=f"Contribution Analysis of the reference scenario providing {st.session_state.scenario[0][0]}",
        xaxis_title="Impact Categories", yaxis_title="Contribution [%]", yaxis_range=[0, 110]
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Table
    
    fmt = lambda x: f"{x:.3g}" if isinstance(x,(int,float,np.floating)) else x
    df = pd.DataFrame(array, index=labels, columns=legend_LCIA)
    df = df[(df.abs() > 1e-10).any(axis=1)]
    df.loc['Total'] = df.sum()
    df = df.applymap(fmt)
    st.table(df)

    
def plotting_comp(result1, result2, tier, LCIA):
    # === Préparation des données ===
    array1, labels, color_list, hash_flags = result_by_tier(result1, tier)
    array1 = np.vstack([np.atleast_2d(x) for x in array1]).astype(float)
    array2 = result_by_tier(result2, tier)[0]
    array2 = np.vstack([np.atleast_2d(x) for x in array2]).astype(float)

    # === LCIA ===
    if LCIA == 'Climate Change':
        legend_LCIA = ['CC <br>[kgCO2eq]']
        array1 = array1[:, 0:1]; array2 = array2[:, 0:1]
    elif LCIA == 'IW+ Footprint':
        legend_LCIA = [
            'CC <br>[kgCO2eq]', 'Rem. EQ <br>[PDF.m2.yr]',
            'Fossil and Nuc. Energy <br>[MJ deprived]', 'Rem. HH <br>[DALY]', 'Water <br>[m3 worldEq]'
        ]
        array1 = array1[:, 0:5]; array2 = array2[:, 0:5]
    else:
        legend_LCIA = ['EQ <br>[PDF.m2.yr]', 'HH <br>[DALY]']
        array1 = array1[:, 5:7]; array2 = array2[:, 5:7]

    # === Normalisation (par rapport au scénario 1) ===
    col_sums = np.sum(array1, axis=0)
    col_sums_safe = col_sums.copy()
    col_sums_safe[col_sums_safe == 0] = 1.0

    data1 = np.round((array1 / col_sums_safe) * 100, 1)
    data2 = np.round((array2 / col_sums_safe) * 100, 1)

    # === Hauteurs finales de piles (ajout h1, h2) ===
    h1 = data1.sum(axis=0)          # hauteur des piles S1 (≈100 si non vides)
    h2 = data2.sum(axis=0)          # hauteur des piles S2
    col_sums2 = array2.sum(axis=0)  # totaux absolus S2

    # --- Positionnement ---
    n_cols = data1.shape[1]
    group_spacing = 3
    bar_spacing = 1
    x1 = np.arange(0, n_cols * group_spacing, group_spacing)
    x2 = x1 + bar_spacing

    bottom1 = np.zeros(n_cols)
    bottom2 = np.zeros(n_cols)

    fig = go.Figure()

    # --- Tracer uniquement les séries non nulles (pas de label si tout zéro) ---
    tol = 1e-12
    for i, lbl in enumerate(labels):
        y1 = np.asarray(data1[i], dtype=float)
        y2 = np.asarray(data2[i], dtype=float)

        if np.all(np.isclose(y1, 0.0, atol=tol)) and np.all(np.isclose(y2, 0.0, atol=tol)):
            continue  # skip série

        c = color_list[i]
        c_f = c if not isinstance(c, (list, tuple, np.ndarray)) else c

        marker_kwargs = dict(color=c_f)
        if hash_flags is not None and i < len(hash_flags) and bool(hash_flags[i]):
            marker_kwargs["pattern"] = dict(shape="/", fgcolor="black", fillmode="overlay", solidity=0.2)

        y = data1[i]  # le % de ton segment
        abs_vals = array1[i]  # valeurs absolues
        cd = np.stack([abs_vals, y], axis=-1)  # [abs, segment%]

        fig.add_trace(go.Bar(
            x=x1, y=y1, name=lbl, legendgroup=lbl,
            marker_color=color_list[i], base=bottom1, width=0.8,
            marker=marker_kwargs,
            customdata=cd,
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Impact score : %{customdata[1]:.1f} %<br>"
                "%{x}: %{customdata[0]:.3g}"
                "<extra></extra>"
            ),
            hoverlabel=dict(font=dict(color=color_list[i]))
        ))

        y = data2[i]  # le % de ton segment
        abs_vals = array2[i]  # valeurs absolues
        cd = np.stack([abs_vals, y], axis=-1)  # [abs, segment%]

        fig.add_trace(go.Bar(
            x=x2, y=y2, name=lbl, legendgroup=lbl, showlegend=False,
            marker_color=color_list[i], base=bottom2, width=0.8,
            marker=marker_kwargs,
            customdata=cd,
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Impact score: %{customdata[1]:.1f} %<br>"
                "%{x}: %{customdata[0]:.3g}"
                "<extra></extra>"
            ),
            hoverlabel=dict(font=dict(color=color_list[i]))
        ))

        bottom1 += y1
        bottom2 += y2


    for j in range(n_cols):
        fig.add_annotation(
            x=x1[j], y=bottom1[j] + 6,
            text=f"{col_sums[j]:.3g}",
            showarrow=False, font=dict(size=11, color="black")
        )

        fig.add_annotation(
            x=x2[j], y=bottom2[j] + 6,
            text=f"{col_sums2[j]:.3g}",
            showarrow=False, font=dict(size=11, color="black")
        )
        
        fig.add_annotation(
            x=x1[j], y=-6,
            text="SO",
            showarrow=False, font=dict(size=11, color="black")
        )

        fig.add_annotation(
            x=x2[j], y=-6,
            text="PEM",
            showarrow=False, font=dict(size=11, color="black")
        )

    """fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode="markers",
        marker=dict(color='rgba(255,255,255,0)', size=1),
        showlegend=True,
        name=f"S1 = {str(st.session_state.scenario[0][20])}",
        hoverinfo="skip"
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode="markers",
        marker=dict(color='rgba(255,255,255,0)', size=1),
        showlegend=True,
        name=f"S2 = {str(st.session_state.scenario[1][20])}",
        hoverinfo="skip"
    ))"""
    
    # === Layout ===
    ymax = max(h1.max() if h1.size else 0, h2.max() if h2.size else 0)
    fig.update_layout(
        barmode="stack",
        title=f"Comparison Analysis of the two water electrolysis scenarios providing {st.session_state.scenario[0][0]}",
        xaxis=dict(
            tickmode='array',
            tickvals=[(x1[j] + x2[j]) / 2 for j in range(n_cols)],
            ticktext=legend_LCIA,
            title="Impact Categories"
        ),
        yaxis=dict(
            title="Impact Score [%]",
            range=[-10, max(110, float(ymax) * 1.25)]
        ),
        bargap=0.25,
        bargroupgap=0.05,
        legend=dict(title="Contributors", traceorder="normal", orientation="v"),
        margin=dict(t=90, b=60, l=70, r=70),
        hovermode="closest",
        hoverlabel=dict(bgcolor="white", font_size=14),
        hoverdistance=20, spikedistance=20
    )

    st.plotly_chart(fig, use_container_width=True)

    # === Tables comparatives ===
    legend_LCIA = [s.replace("<br>","\n") for s in legend_LCIA]
    fmt = lambda x: f"{x:.3g}" if isinstance(x, (int, float, np.floating)) else x
    df1 = pd.DataFrame(array1, index=labels, columns=legend_LCIA)
    df2 = pd.DataFrame(array2, index=labels, columns=legend_LCIA)
    df1.loc['Total'] = df1.sum(); df2.loc['Total'] = df2.sum()
    df1, df2 = df1.applymap(fmt), df2.applymap(fmt)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{st.session_state.scenario[0][20]}**")
        st.table(df1)
    with c2:
        st.markdown(f"**{st.session_state.scenario[1][20]}**")
        st.table(df2)




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

    fig.update_layout( barmode="group", title=f"Comparison of potential impact of technologies providing {st.session_state.scenario[0][0]}", xaxis_title="Impact Categories", yaxis_title="Impact Score [%]" )
    
    st.plotly_chart(fig, use_container_width=True)

    legend_LCIA = [s.replace("<br>","\n") for s in legend_LCIA]
    fmt = lambda x: f"{x:.3g}" if isinstance(x,(int,float,np.floating)) else x
    df = pd.DataFrame(arr, index=labels, columns=legend_LCIA)
    df = df[(df.abs()>1e-10).any(axis=1)]
    df = df.applymap(fmt)
    st.table(df)


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

    fig.update_layout( barmode="group", title=f"Comparison of potential impact of technologies providing {st.session_state.scenario[0][0]}", xaxis_title="Impact Categories", yaxis_title="Impact Score [%]" )
    
    st.plotly_chart(fig, use_container_width=True)
    fmt = lambda x: f"{x:.3g}" if isinstance(x,(int,float,np.floating)) else x
    df = pd.DataFrame(arr, index=labels, columns=legend_LCIA)
    df = df[(df.abs()>1e-10).any(axis=1)]
    df = df.applymap(fmt)
    st.table(df)




