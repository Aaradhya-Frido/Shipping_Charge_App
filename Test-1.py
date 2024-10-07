import pandas as pd
import streamlit as st
import numpy  as np
from datetime import datetime

st.title("Shipping Charge Calculator")

def read_file(uploaded_file):
    """Read uploaded file into a DataFrame."""
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.xlsx'):
            return pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.txt'):
            return pd.read_csv(uploaded_file, sep='\t')  # Assuming tab-separated values
        elif uploaded_file.name.endswith('.tsv'):
            return pd.read_csv(uploaded_file, sep='\t')  # For TSV files
        else:
            st.error("Unsupported file format")
            return pd.DataFrame()  # Return empty DataFrame if format is unsupported
    else:
        st.error("No file uploaded")
        return pd.DataFrame()  # Return empty DataFrame if no file is uploaded


# Get the current year
current_year = datetime.today().year
current_month = datetime.today().month

# Create a dropdown for month selection
month = st.selectbox(
    "Select a month:",
    options=[(i, datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)],  # Month options
    format_func=lambda x: x[1]  # Display month name
)

# Create a dropdown for year selection
year = st.selectbox(
    "Select a year:",
    options=list(range(current_year, 2101)),  # Year options from 2000 to 2100
)
selected_date = datetime(year, month[0], 1)

file_path = 'Agreement.xlsx'  # Update with your file path
# options = 'options'  # Sheet name to read from

# Read the sheet into a DataFrame
df_options = pd.read_excel(file_path, sheet_name='options' )

# Assuming the options are in the first column of the DataFrame
options = df_options.iloc[:, 0].tolist()  # Convert the first column to a list


platform =  st.selectbox("Select Platform",options)

uploaded_file = st.file_uploader(f"**Choose a Bill of {platform} for {selected_date.strftime('%B %Y')} file**", type=["xlsx", "csv", "txt", "tsv"], accept_multiple_files=False)

if uploaded_file is not None:
    # Read the uploaded file using the function
    df_uploaded = read_file(uploaded_file)
    
    # Display the DataFrame if it's not empty
    if not df_uploaded.empty:
        st.success(f"Successfully loaded the file for {platform} in {selected_date.strftime('%B %Y')}!")
    else:
        st.warning("The uploaded file is empty or unsupported.")

if st.button("Process"):
    if platform == "WareIQ":
        df_sheets = pd.read_excel(file_path, sheet_name=platform)
        def calculate_shipping_charges(row):

            # Extract values from row
            courier_name = row['courier_name']
            zone = row['zone']
            weight_charged = row['weight_charged']
            
            # Find the matching rows in df_sheets
            matching_row = df_sheets[(df_sheets['courier_name'] == courier_name) & (df_sheets['zone'] == zone)]
            
            if not matching_row.empty:
                base_weight = matching_row['Base_Weight'].values[0]

                # Use the provided formula logic here
                base_charges = (
                    matching_row.loc[:, 'Base_Charges'].values[0]  # Replace with actual column for charges
                )
                Offset_charges = (
                    matching_row.loc[:, 'Offset_charges'].values[0]  # Replace with actual column for charges
                )

                # Check condition and calculate additional charges if necessary
                if base_weight >= weight_charged:  # Replace with actual column for L
                    return base_charges
                else:
                    additional_charges = (np.ceil((weight_charged - base_weight)/ matching_row.loc[:, 'Offset_Weight'].values[0]) * Offset_charges)  # Replace with actual column for M
                    return base_charges + additional_charges
            return 0  # Default if no match found

        # Apply the function to create the 'shipping charges' column
        df_uploaded['shipping_charges_cal'] = df_uploaded.apply(calculate_shipping_charges, axis=1)

            # Create the 'RTO' column based on status
        df_uploaded['RTO_cal'] = df_uploaded.apply(lambda row: row['shipping_charges_cal'] if row['status'] == 'RTO' else 0, axis=1)

        # Create the 'cod charges' column based on payment mode
        df_uploaded['cod_charges_cal'] = df_uploaded.apply(lambda row: 27 if row['payment_mode'] == 'COD' else 0, axis=1)
        
        # Calculate total charges
        df_uploaded['total_charges_cal'] = df_uploaded[['shipping_charges_cal', 'RTO_cal', 'cod_charges_cal']].sum(axis=1)
        df_uploaded['total_charges_without_COD_Frido'] = df_uploaded[['shipping_charges_cal', 'RTO_cal']].sum(axis=1)
        df_uploaded['total_charges_without_COD_WAREIQ'] = df_uploaded[['Forward', 'RTO']].sum(axis=1)
        df_uploaded["net_difference"]=df_uploaded[['total_charges_cal','Total']].diff(axis=1).iloc[:, -1]
        df_uploaded["net_difference_without_COD"]=df_uploaded[['total_charges_without_COD_Frido','total_charges_without_COD_WAREIQ']].diff(axis=1).iloc[:, -1]
        st.write("Updated DataFrame with shipping charges:")
        st.dataframe(df_uploaded)

        # Calculate and display sums
        total_sum = df_uploaded['Total'].sum()
        total_charges_sum = df_uploaded['total_charges_cal'].sum()
        net_difference_sum = df_uploaded['net_difference'].sum()
        net_difference_sum_without_COD = df_uploaded["net_difference_without_COD"].sum()
        # Print the sums
        st.write(f"Total Cost Charged by WareIQ: {total_sum:.2f}")
        st.write(f"Total Cost Charged by Frido: {total_charges_sum:.2f}")
        st.write(f"Total Charge Differences: {net_difference_sum:.2f}")
        st.write(f"Total Charge Differences without COD: {net_difference_sum_without_COD:.2f}")

    elif platform == "Bluedart":
        df_sheets = pd.read_excel(file_path, sheet_name=platform)
    elif platform == "Delhivery":
        df_sheets = pd.read_excel(file_path, sheet_name=platform)
    elif platform == "Goswift":
        df_sheets = pd.read_excel(file_path, sheet_name=platform)
    elif platform == "Shipyaari":
        df_sheets = pd.read_excel(file_path, sheet_name=platform)
    elif platform == "Zippee":
        df_sheets = pd.read_excel(file_path, sheet_name=platform)
    else:
        st.print("No Platform is selected")
        


