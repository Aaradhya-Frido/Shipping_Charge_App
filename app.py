import streamlit as st
import pickle
import numpy as np
import pandas as pd

df = pd.read_excel(
    io = 'C:\\Users\\AaradhyaSaxena\\OneDrive - Arcatron Mobility Pvt Ltd\\Transform_App\\Shipping Charges\Rates.xlsx'
)
def show_details():
    st.title("Shipping Charges Calculator")
    st.write("Enter the Required details below")

show_details()

# ----Main Details---- #

Item_Cost = st.number_input(
    "Enter the Item Cost Sent",
    min_value=0.1,  # minimum value, can be set to any float value
    value= 0.5 ,  # default value
    step=0.01  # increment step
)

Courier = st.selectbox(
    "Select the Courier Partner",
    options=df["courier_name"].dropna().unique()
)

Weight = st.number_input(
    "Enter the Courier Weight in Kgs",
    min_value=0.1,  # minimum value, can be set to any float value
    value= 0.5 ,  # default value
    step=0.01  # increment step
)

Zone = st.selectbox(
    "Select the Zone",
    # options=df["Zone"].dropna().unique()
    options=df.columns[3:8]
)

Payment_Type = st.selectbox(
    "Select the Payment Type",
    options=df["Payment_type"].dropna().unique()
)

Shipment_Type = st.selectbox(
    "Select the Shipment Type",
    options=df["Shipment_Type"].dropna().unique()
)

# Define a mapping from zone to corresponding Zone_offset
zone_column_mapping = {
    'A': 'A_step',
    'B': 'B_step',
    'C': 'C_step',
    'D': 'D_step',
    'E': 'E_step'
}


# Look up the value in the DataFrame
if Zone and Courier:
    selected_row = df[df['courier_name'] == Courier]  # Filter the row for the selected courier
    zone_value = selected_row[Zone].values[0] 
    base_value = zone_value
    
    selected_column = zone_column_mapping.get(Zone, 'A_step')
    
    zone_value_offset = selected_row[selected_column].values[0] 

    weight_diff = max(0, Weight - selected_row['Base_Weight'].values[0])  # Ensure non-negative
    off_set_Value = round(weight_diff / selected_row['Offset_Weight'].values[0]) * zone_value_offset
    COD_value = 0
    if Payment_Type == 'COD':
        COD_value = max(Item_Cost * selected_row['cod_ratio'].values[0],selected_row['cod_min'].values[0])
    RTO = 0
    if Shipment_Type == 'RTO':
        RTO = base_value + off_set_Value

    cost = base_value + off_set_Value + COD_value + RTO
        # Display the result
    st.write(f"The cost for {Courier} in the {Zone} zone is: {cost}")