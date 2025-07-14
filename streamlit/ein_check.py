from src.EIn_lookup.ein_check import EIN_LOOKUP
import json
import streamlit as st
import os



def main():    
    st.title("EIN Lookup Tool")

    # st.text("Enter the EIN number to look up the business information.")
    ein_input = st.text_input("EIN Number", placeholder="Enter EIN (e.g., 12-3456789)")
    if st.button("Lookup"):
        if ein_input:
            ein_lookup = EIN_LOOKUP(ein=ein_input)
            result = ein_lookup.return_validation_json()
            if result:
                st.json(result)
            else:
                st.error("No data found for the provided EIN.")
        else:
            st.warning("Please enter a valid EIN number.")
    
    # Input for EIN

if __name__ == "__main__":
    main()
