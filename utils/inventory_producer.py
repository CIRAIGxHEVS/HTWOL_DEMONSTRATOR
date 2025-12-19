import pandas as pd
import streamlit as st
from io import BytesIO
import utils.H2_preset as pst

### Names of lines ###

supply_names=['Hydrogen Production','Post-Processing', 'Distribution', 'Storage', 'H2-To-Elec Conversion','End-Use Process']
stack_names=['Hydrogen Electrode','Oxygen Electrode','Barrier Layer','Contact Layer','Electrolyte','Bipolar Plate','Frame','End plate']
component_name_detailed=label_element=['Hydrogen Electrode','Oxygen Electrode','Barrier Layer','Contact Layer','Electrolyte','Bipolar Plate','Structure and Screw (Frame)','Current Collector (Frame)','Sealant (Frame)','Endplate']
bop_names=['Compressor [kW]', 'HEX [m2]', 'Chiller [kW]', 'Rectifier [kW]', 'Separator [m3]', 'Pump [kW]', 'Piping [kg]', 'Instrumentation [kW]', 'Tank [kWstack]', 'Container [m3]']
EL_names=['Electricity Stored in H2','Elec. Losses Stack','Elec. Consumed BoP','Heat','Water','KOH','Stack Manuf.', 'Equipment Manuf.', 'EoL','H2 Leakage']
FC_names=['Hydrogen Production','Surplus H2 (Stack Losses)','Surplus H2 (BoP Cons)','Surplus H2 (H2 Leakage)','KOH','Stack Manuf.', 'Equipment Manuf.', 'EoL','H2 Leakage']
other_names=['Electricity', 'Heat','Water','KOH','Stack Manuf.', 'Equipment Manuf.', 'EoL','H2 Leakage','Surplus H2 Prod.']
elec_names=['EU Grid','Wind','PV','Hydro','Nuclear']
heat_names=['Natural Gas','Electricity','Fatal Heat']
other_sources=['see elec','see heat','background (ecoinvent or personal modeling)','background (ecoinvent or personal modeling)','see stack manufacturing','background (ecoinvent or personal modeling)','background (ecoinvent or personal modeling)','background (ecoinvent or personal modeling)','see supply chain']
EL_sources=['see elec','see elec','see elec','see heat','background (ecoinvent or personal modeling)','background (ecoinvent or personal modeling)','see stack manufacturing','background (ecoinvent or personal modeling)','background (ecoinvent or personal modeling)','background (ecoinvent or personal modeling)','see supply chain']
FC_sources=['see supply chain','see supply chain','see supply chain','see supply chain','background (ecoinvent or personal modeling)','see stack manufacturing','background (ecoinvent or personal modeling)','background (ecoinvent or personal modeling)','background (ecoinvent or personal modeling)','supply chain']

inventory_unit   = ["kWh", "kWh", "kg", "kg", "unit", "unit", "unit", "kg H2 leakage", "kgH2"]
inventory_format   = [".1f", ".1f", ".0f", ".2e", ".2e", ".2e", ".2e", ".2g", ".2g"]

inventory_consEL_detailed_unit=["kWh","kWh","kWh", "kWh", "kg", "kg", "unit", "unit", "unit", "kg H2 leakage"]
inventory_consEL_detailed_format   = [".1f", ".1f",".1f", ".1f", ".0f", ".2e", ".2e", ".2e", ".2e", ".2g"]
inventory_consFC_detailed_unit=["kgH2","kgH2","kgH2","kgH2", "kg", "unit", "unit", "unit", "kg H2 leakage"]
inventory_consFC_detailed_format   = [".2g",".2g", ".2g",".2g", ".2e", ".2e", ".2e", ".2e", ".2g"]
inventory_bop_detailed_unit=["kW","m2","kW", "kW", "m3", "kW", "kg", "kW", "kWstack", "m3"]

### Sources for each lines ###
def make_sheet_table(process_names, inventory_values, inventory_unit, inventory_format, process_sources, tol=1e-12):
    """
    Returns one "table" in your sheet format: (names_out, qty_out, sources_out),
    with rows removed when the numeric value is ~0 (and names/sources removed too).
    """
    names_out, qty_out, sources_out = [], [], []
    n = min(len(process_names), len(inventory_values), len(inventory_unit), len(inventory_format), len(process_sources))

    for j in range(n):
        v = inventory_values[j]

        # drop row if value is numeric and ~0
        try:
            if abs(float(v)) <= tol:
                continue
        except (TypeError, ValueError):
            pass  # keep non-numeric values

        names_out.append(process_names[j])
        qty_out.append(f"{v:{inventory_format[j]}} {inventory_unit[j]}".strip())
        sources_out.append(process_sources[j])

    return (names_out, qty_out, sources_out)

def _df_from_inventory(names, quantities, sources):
    # basic safety: align lengths (truncate to shortest)
    n = min(len(names), len(quantities), len(sources))
    return pd.DataFrame({
        "Name": names[:n],
        "Quantity": quantities[:n],
        "Source": sources[:n],
    })

def build_inventory_excel_bytes(sheets_dict):
    """
    sheets_dict format (NEW):
        {
          "Sheet 1": [ (names, qty, sources), (names, qty, sources), ... ],
          "Sheet 2": [ (names, qty, sources), ... ],
          ...
        }

    Each (names, qty, sources) is a "table" with 3 columns.
    All tables of a given sheet are written one under another, separated by a blank row.

    Returns:
        bytes of the Excel file (.xlsx) to feed to st.download_button
    """
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for sheet_name, tables in sheets_dict.items():
            # Excel sheet names are limited to 31 characters
            safe_name = str(sheet_name)[:31]

            dfs = []

            # tables is expected to be a list: [ (names, qty, sources), (names, qty, sources), ... ]

            for k, (names, quantities, sources) in enumerate(tables):
                # Build the current table dataframe
                dfk = _df_from_inventory(names, quantities, sources)

                dfs.append(dfk)

            # If no table exists, create an empty dataframe with the right columns
            df = pd.concat(dfs, ignore_index=True) if dfs else _df_from_inventory([], [], [])

            # Write the sheet
            df.to_excel(writer, index=False, sheet_name=safe_name)

            # Optional: set column widths for readability
            ws = writer.sheets[safe_name]
            ws.set_column(0, 0, 45)  # Name
            ws.set_column(1, 1, 20)  # Quantity
            ws.set_column(2, 2, 60)  # Source

    output.seek(0)
    return output.getvalue()

# ---- Example usage in Streamlit ----
# Provide your inventories here (names, quantities, sources) for each "array"

def layout(product_name,product_qty):
    layout_table=(['','Product',product_name,'','Flows in'],['','',product_qty,'',''],['','','','',''])
    return layout_table

def build_inventories(inventory):
    kgH2=inventory[0]
    supply=[kgH2]*4+[kgH2*st.session_state.LHV_hydrogen]+[1]

    sup,EL,comp,purif,distrib,storage,FC,enduse=inventory[1]

    if comp[0]==0 and purif[0]==0:
        PP_sheet=[([], [], [])]
        supply[1]=0
    else:
        PP_sheet=[]
        if comp[0]!=0:
            comp_scaled=[c/kgH2 for c in comp]
            comp_table=make_sheet_table(other_names, comp_scaled,inventory_unit,inventory_format, other_sources)
            PP_sheet.append(layout(f"Compression from {st.session_state.characteristic_h2_produced[0]} to {st.session_state.requirements[0]}","1 kgH2 compressed"))
            PP_sheet.append(comp_table)
        if purif[0]!=0:
            purif_scaled=[p/kgH2 for p in purif]
            purif_table=make_sheet_table(other_names, purif_scaled,inventory_unit,inventory_format, other_sources)
            PP_sheet.append(layout(f"Purification from {st.session_state.characteristic_h2_produced[2]} to {st.session_state.requirements[1]}","1 kgH2 purified"))
            PP_sheet.append(purif_table)

    if st.session_state.scenario[0][10][1] == "None":
        distrib_sheet = [([], [], [])]
    else:
        distrib_scaled=[d/kgH2 for d in distrib]
        distrib_table=comp_table=make_sheet_table(other_names, distrib_scaled,inventory_unit,inventory_format, other_sources)
        distrib_sheet = [layout(f"Distribution by {st.session_state.scenario[0][10][1]}","1 kgH2 distributed"),distrib_table]
        supply[2]=0

    if st.session_state.scenario[0][9] == "None":
        storage_sheet = [([], [], [])]
    else:
        storage_scaled=[s/kgH2 for s in storage]
        storage_table=make_sheet_table(other_names, storage_scaled,inventory_unit,inventory_format, other_sources)
        storage_sheet = [layout(f"Storage in {st.session_state.scenario[0][9]}","1 kgH2 stored"),storage_table]
        supply[3]=0
    
    if st.session_state.enduse_process is None:
        enduse_sheet = [([], [], [])]
    else:
        enduse_table=make_sheet_table(other_names, enduse,inventory_unit,inventory_format, other_sources)
        enduse_sheet = [layout(f" {st.session_state.enduse_process}",st.session_state.FU),enduse_table]
        supply[5]=0
    

    if inventory[3][0] is None:
        EL_sheet=(layout("Hydrogen Production","1 kgH2"),(['SMR'], ['1 kgH2'], ["background (ecoinvent or personal modeling)"]))
        stackEL_sheet = [([], [], [])]
        cellEL_sheet = [([], [], [])]
        bopEL_sheet = [([], [], [])]
    else:
        EL,stackEL,cellEL_inv,bopEL=inventory[3][0]
        EL_table=make_sheet_table(EL_names, EL,inventory_consEL_detailed_unit,inventory_consEL_detailed_format, EL_sources)
        EL_sheet=[layout("Hydrogen Production","1 kgH2"),EL_table]
        
        bopEL_table=make_sheet_table(bop_names, bopEL,inventory_bop_detailed_unit,[".2g"]*len(bopEL), ["background (ecoinvent or personal modeling)"]*len(bop_names))
        bopEL_sheet = [layout(f"Manufacturing of {st.session_state.scenario[0][5]} BoP (maturity: {st.session_state.scenario[0][6]})","1 kgH2/h"),bopEL_table]

        # --- with this block (Cell EL = 9 tables, one per component) ---
        cellEL_tables = []
        for k in range(len(cellEL_inv)):
            cellEL_names_k, cellEL_k = cellEL_inv[k]  # component k -> [names, values]
            if cellEL_names_k[0]!='-- Not concerned --':
                cellEL_table_k=make_sheet_table(cellEL_names_k, cellEL_k,[" kg"] * len(cellEL_k),[".2g"] * len(cellEL_k), ["background (ecoinvent or personal modeling)"] * len(cellEL_names_k))

                cellEL_tables.append(layout(component_name_detailed[k],"1 m2 active area"))
                cellEL_tables.append(cellEL_table_k)

                
            else:
                if k<=5: #for listing element of the cell that are included in the system ()
                    stackEL[k]=0
                

        cellEL_sheet = cellEL_tables  # IMPORTANT: list of (names, qty, sources) => multiple tables in one sheet
        stackEL_table=make_sheet_table(stack_names, stackEL,[" m2 active area"]*len(stackEL),[".2g"]*len(stackEL), ["see Cell"]*len(stack_names))
        stackEL_sheet = [layout(f"Manufacturing of {st.session_state.scenario[0][5]} stack (maturity: {st.session_state.scenario[0][6]})",f"1 electrolyser system ({st.session_state.scenario[0][7]} kgH2/h)"),stackEL_table]


    if inventory[3][1] is None:
        FC_sheet=[([], [], [])]
        stackFC_sheet = [([], [], [])]
        cellFC_sheet = [([], [], [])]
        bopFC_sheet = [([], [], [])]
        supply[4]=0


    else:
        FC,stackFC,cellFC_inv,bopFC=inventory[3][1]
        FC_table=make_sheet_table(FC_names, FC,inventory_consFC_detailed_unit,inventory_consFC_detailed_format, FC_sources)
        FC_sheet=[layout("Electricity Production","33 kWh"),FC_table]

        bopFC_table=make_sheet_table(bop_names, bopFC,inventory_bop_detailed_unit,[".2g"]*len(bopFC), ["background (ecoinvent or personal modeling)"]*len(bop_names))
        bopFC_sheet= [layout(f"Manufacturing of {st.session_state.scenario[0][12]} BoP (maturity: {st.session_state.scenario[0][13]})","1 kgH2/h"),bopFC_table]

        cellFC_tables = []
        for k in range(len(cellFC_inv)):
            cellFC_names_k, cellFC_k = cellFC_inv[k]  # component k -> [names, values]
            if cellFC_names_k[0]!='-- Not concerned --':
                cellFC_table_k=make_sheet_table(cellFC_names_k, cellFC_k,[" kg"] * len(cellFC_k),[".2g"] * len(cellFC_k), ["background (ecoinvent or personal modeling)"] * len(cellFC_names_k))

                cellFC_tables.append(layout(component_name_detailed[k],"1 m2 active area"))
                cellFC_tables.append(cellFC_table_k)

            else:
                if k<=5: #for listing element of the cell that are included in the system ()
                    stackFC[k]=0

        cellFC_sheet = cellFC_tables  # IMPORTANT: list of (names, qty, sources) => multiple tables in one sheet
        stackFC_table=make_sheet_table(stack_names, stackFC,[" m2 active area"]*len(stackFC),[".2g"]*len(stackFC), ["see Cell"]*len(stack_names))

        stackFC_sheet=[layout(f"Manufacturing of {st.session_state.scenario[0][12]} stack (maturity: {st.session_state.scenario[0][13]})",f"1 fuel cell system ({st.session_state.scenario[0][14]} kW)"),stackFC_table]

        
    elec_mix=pst.mix_name_to_list(st.session_state.scenario[0][16],True)
    elec_table=make_sheet_table(elec_names,elec_mix,[" kWh"]*len(elec_mix),[".2g"]*len(elec_mix), ["background (ecoinvent or personal modeling)"]*len(elec_names))
    elec_sheet=[layout("Electricity Production","1 kWh"),elec_table]
    if st.session_state.scenario[0][18] == '-- Select --':
        heat_sheet=[([], [], [])]
    else:
        heat_mix=pst.mix_name_to_list(st.session_state.scenario[0][18],False)
        heat_table=make_sheet_table(heat_names, heat_mix,[" kWh"]*len(heat_mix),[".2g"]*len(heat_mix), ["background (ecoinvent or personal modeling)","see electricity","background (ecoinvent or personal modeling)"])
        heat_sheet=[layout("Heat Production","1 kWh"),heat_table]

 
    supply_table=make_sheet_table(supply_names,supply,[" kgH2"]*4+[" kWh electricity"]+[st.session_state.FU[2:]],[".3g"]*len(supply),["see other tables"]*len(stack_names))
    supply_sheet=[layout("End-use application of the H2",f"{st.session_state.FU}"),supply_table]

    sheets = {
        "Supply chain": supply_sheet,
        # "SC element - A": (sca_names, sca_qty, sca_src),
        # "SC element - B": (scb_names, scb_qty, scb_src),
        "Hydrogen Production (EL)": EL_sheet,
        "Post-Processing": PP_sheet,
        "Distribution": distrib_sheet,
        "Storage": storage_sheet,
        "Hydrogen Reconversion (FC)": FC_sheet,
        "End-Use Processes": enduse_sheet,


        "Stack EL": stackEL_sheet,
        "Cell EL": cellEL_sheet,
        "BoP EL": bopEL_sheet,
        "Stack FC": stackFC_sheet,
        "Cell FC": cellFC_sheet,
        "BoP FC": bopFC_sheet,
        "Electricity": elec_sheet,
        "Heat": heat_sheet,
    }

    sheets = {
        name: tables
        for name, tables in sheets.items()
        if any(len(n) or len(q) or len(s) for (n, q, s) in tables)
    }
    

    xlsx_bytes = build_inventory_excel_bytes(sheets)


    return xlsx_bytes

def ask_inventory(inventory):
    xlsx_bytes=build_inventories(inventory)

    st.download_button(
        "Download inventory (Excel)",
        data=xlsx_bytes,
        file_name=f"inventory_{st.session_state.scenario[0][0]}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


