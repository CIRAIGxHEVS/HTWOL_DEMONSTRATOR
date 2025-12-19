import streamlit as st
from PIL import Image


st.subheader("Frequently Asked Question")

with st.expander("What is included in the calculations?"):
    st.write("The supply chain of water electrolysis is represented in the figure 1 below. It can include Electricity Generation, Hydrogen Production (Electrolyser), Post Processing for reaching H2 requirements, Storage&Distribution and Hydrogen Reconversion (Fuel Cell). The system boundaries depend on the functional unit selected.")
    image = Image.open("images/SB.png") 
    st.image(image, caption="Figure 1: Scope of the LCA of water electrolysis. The processes of the supply chain and the functional unit selected depends on the final application of the H2.")
    st.write("More specifically, for electrolysers and fuel cells, the model integrates the whole life of the technology from raw material extraction to the end-of life, including manufacturing of the stack, manufacturing of the equipment, or use phase. These processes are represented in Figure 2")
    image = Image.open("images/modular_structure.png") 
    st.image(image, caption="Figure 2: Process Tree of the FC&EL technologie (modular structure). The same color are used in the contribution analyses to help you identify the contribution of each life cycle stage depending on the configurations modeled.")


with st.expander("How to use this tool?"):

    st.write("The tool is composed of different subsections that you can find on the left of your screen.")
    st.write("Section Contribution Analysis enables to quickly assess the environmental impacts and hotspots of pre-set configurations available in our database. You are kindly ask to select: \n (a) the functional unit - you can select your functional unit among all the potential end-use service provided by the hydrogen. \n  (b) the LCIA method \n (c) A configuration for all the modules include in the system boundaries. Depending on the FU selected, it covers the type of electrolyser, of storage, of distribution, of fuel cell. It also includes the energy mix.es selected and the hydrogen requirements. \n (d) The level of details for the contribution analysis.")

    st.write("Section Comparison Analyses enable to compare two water electrolysis systems - or to compare a water electrolysis system with an other technology providing equivalent functionality. ") 
    
    st.write("Sections Electrolyser / Fuel Cell / Energy Mixes Personalization enable to create or modify your own scenarios by changing all the parameters available in the model. You are asked to initialize your model with pre-set configurations available, before being able to modify any parameter. Once it is done, parameters are classified by life stages. You are free to modify the values of the parameters by clicking under 'Please select a life cycle stage' and for each of them modify the parameters according to your interest. In the Equipment category, the Balance of Plant is described by a list of equipment - characterized by their name and their power. You can add or delete some equipment, and change their power size. In the Use Phase, you can modify the electricity mix by selecting the percentage of each source among Wind, PV, Hydro,Nuclear and the current average European mix (RER). Your personalized scenario can be saved and used in one of the two calculation sections. They can also be exported for being reused later.") 

