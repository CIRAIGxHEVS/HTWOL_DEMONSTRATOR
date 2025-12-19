import pandas as pd
import io
import streamlit as st
import utils.H2_preset as pst
import ast

legend = [
    "Active_Surface [m2]",
    "cell_per_stack [unit]",
    "Degradation_rate [%]",
    "Degradation Max [%]",
    "Recycling Rate [-]",
    "Thickness Hydrogen Electrode [um]",
    "Ratio Surface Hydrogen Electrode (Surface Element / Active Area)",
    "Material Hydrogen Electrode",
    "Additif Hydrogen Electrode (Load [mg/cm2] - Material)",
    "Thickness Oxygen Electrode [um]",
    "Ratio Surface Oxygen Electrode (Surface Element / Active Area)",
    "Material Oxygen Electrode",
    "Additive Oxygen Electrode (Load [mg/cm2] - Material)",
    "Thickness Barrier Layer [um]",
    "Ratio Surface Barrier Layer (Surface Element / Active Area)",
    "Material Barrier Layer",
    "Additive Barrier Layer (Load [mg/cm2] - Material)",  
    "Thickness Contact Layer [um]",
    "Ratio Surface Contact Layer (Surface Element / Active Area)",
    "Material Contact Layer",
    "Additive Contact Layer (Load [mg/cm2] - Material)", 
    "Thickness Electrolyte [um]",
    "Ratio Surface Electrolyte (Surface Element / Active Area)",
    "Material Electrolyte",
    "Additive Electrolyte (Load [mg/cm2] - Material)",
    "Thickness Bipolar Plate [um]",
    "Ratio Surface Bipolar Plate (Surface Element / Active Area)",
    "Material Bipolar Plate",
    "Additive Bipolar Plate (Load [mg/cm2] - Material)",
    "Quantity Frame and Screw [kg/m2]",
    "Material Frame",
    "Quantity Current Collector [kg/m2]",
    "Material Current Collector",
    "Quantity Sealant [kg/m2]",
    "Material Sealant",
    "Thickness End Plates [um]",
    "Ratio Surface End Plates (Surface Element / Active Area)",
    "Material End Plates",
    "Coating End Plates (Load [mg/cm2] - Material)",
    "Lifetime BoP",
    "Compressor [kW/(kgH2/h)]",
    "HEX [m2/(kgH2/h)]",
    "Chiller [kW/(kgH2/h)]",
    "Rectifier [kW/(kgH2/h)]",
    "Separator [m3/(kgH2/h)]",
    "Pump [kW/(kgH2/h)]",
    "Piping [kg/(kgH2/h)]",
    "Instrumentation [kW/(kgH2/h)]",
    "tank [kg/(kgH2/h)]",
    "container [m3/(kgH2/h)]",
    "BoL Voltage [V]",
    "Current Density [A/m2]",
    "Fuel Utilization [-]",
    "Heat Demand [kWh/kgH2]",
    "Water Demand [kg/kgH2]",
    "KOH [kg/kgH2]",
    "Heat Produced [kWh/kgH2]",
    "H2 Leakage [-]",
    "Pressure of the H2 [bar]",
    "Temperature Stack [K]",
    "Purity of the H2 [%]"
]



def export_dict(FC):
    if "dictionary" not in st.session_state:
        pst.dictionary()
        pst.key_dictionary()
    if FC:
        dict=st.session_state.dictionary[3]
    else:
        dict=st.session_state.dictionary[2]
    df = pd.DataFrame(index=legend)

    for model_name, values in dict.items():
        if model_name == '-- Select --':
            continue  # skip this model
        df[model_name] = values

    df.reset_index(inplace=True)
    df.columns.values[0] = 'Legend'

    # Write to in-memory buffer
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, sep=';')
    csv_data = csv_buffer.getvalue().encode('utf-8')
    
    return csv_data


def import_dict(uploaded_file,FC):
    if "dictionary" not in st.session_state:
        pst.dictionary()
        pst.key_dictionary()
    if FC:
        dict_nbr=3
    else:
        dict_nbr=2
    if uploaded_file is not None:
        try:
            # Read the file
            df = pd.read_csv(uploaded_file, sep=';')
            if 'Legend' not in df.columns:
                st.error("The file must contain a 'Legend' column. Please upload only file exported from HTWOL")
                return

            df.set_index('Legend', inplace=True)
            df = df.transpose()

            expected_length = len(legend)

            # Check each model and convert to dict
            imported_dict = {}
            for model, row in df.iterrows():
                values = row.tolist()
                if len(values) != expected_length:
                    st.warning(f"Model '{model}' has incorrect length ({len(values)} instead of {expected_length}). Skipped.")
                else:
                    imported_dict[model] = values

            for model, values in imported_dict.items():
                if model not in st.session_state.dictionary[dict_nbr]:
                    st.session_state.dictionary[dict_nbr][model] = values
                else:
                    st.info(f"Model '{model}' already exists and was not replaced.")

            st.success("Import completed.")

        except Exception as e:
            st.error(f"Error while importing: {str(e)}")
            
            

legend_scenario = [
    "Functional Unit",
    "Aggregation",
    "Pressure",
    "Purity",
    "Baseline",
    "Technology",
    "Maturity",
    "Size",
    "Model",
    "Storage",
    "Distrib",
    "Baseline_FC",
    "Technology_FC",
    "Maturity_FC",
    "Size_FC",
    "Model_FC",
    "Elec",
    "Recovery",
    "Heat",
    "LCIA Method",
    "Name"
]
            

def import_scenario(uploaded_file):
    if uploaded_file is not None:
        try:
            # Read the file
            df = pd.read_csv(uploaded_file, sep=';')
            if 'Legend' not in df.columns:
                st.error("The file must contain a 'Legend' column. Please upload only file exported from HTWOL")
                return

            df.set_index('Legend', inplace=True)
            df = df.transpose()

            expected_length = len(legend_scenario)

            # Collect the first (and only) row as a list
            values = df.iloc[0].tolist()
            
            for i in [2, 7, 14]:
                try:
                    values[i] = float(values[i])
                except ValueError:
                    st.warning(f"Element {i+1} could not be converted to float: {values[i]}")
            
            for i in [1, 9, 10]:  # 0-indexed: 1,9,10
                try:
                    if isinstance(values[i], str):
                        values[i] = ast.literal_eval(values[i])
                    elif not isinstance(values[i], list):
                        values[i] = values[i]
                except Exception as e:
                    st.warning(f"Element {i+1} could not be converted to list: {values[i]} ({e})") 
                    
            try:
                if isinstance(values[17], str):
                    values[17] = values[17].strip().lower() in ['true', '1', 'yes']
                elif not isinstance(values[17], bool):
                    values[12] = bool(values[17])
            except Exception as e:
                st.warning(f"Element 13 could not be converted to boolean: {values[12]} ({e})")     
            if len(values) != expected_length:
                st.warning(f"The uploaded scenario has incorrect length ({len(values)} instead of {expected_length}). Skipped.")
                return
            else:
                imported_list = values  # just a single list of values     
            
            st.success("Import completed.")
            return imported_list
            
        except Exception as e:
            st.error(f"Error reading file: {e}")
            
            
            
def export_scenario():
    if "scenario" not in st.session_state:
        st.warning("No scenario found in session state.")
        return



    scenario_data = st.session_state.scenario[0]
    
    if isinstance(scenario_data[0], (int, float, str)):
        scenario_data = [scenario_data]
        
    df = pd.DataFrame(scenario_data, columns=legend_scenario)
    df = df.transpose()
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Legend'}, inplace=True)

    # Write to in-memory buffer
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, sep=';')
    csv_data = csv_buffer.getvalue().encode('utf-8')
    
    return csv_data


