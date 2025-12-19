import streamlit as st

# Physical Constants #
def physical_constant():
    st.session_state.Faraday=96485 #C/mol
    st.session_state.electron_exchanged=2 # number of electrons exchanged in the electrolysis reaction
    st.session_state.M_H2=0.002016 #kg/mol
    st.session_state.V_electrolysis=1.25 #[V] standard potential of the electrolysis of water 
    st.session_state.LHV_hydrogen=33.3 #kWh/kg
    
