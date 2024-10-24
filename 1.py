import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

# Set up Google Sheets API credentials
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# Load credentials from Streamlit secrets
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(credentials)

# Open the Google Sheet (replace 'Tip Tracker' with your Google Sheet name)
sheet = client.open("Tip Tracker").sheet1

st.title("Tip Tracker")

with st.form("tip_form"):
    input_date = st.date_input("Date", date.today())
    credit_card_tips = st.number_input("Credit Card Tips ($)", min_value=0.0, format="%.2f")
    cash_pocketed = st.number_input("Cash Pocketed ($)", min_value=0.0, format="%.2f")
    bartender_tip_out = st.number_input("Bartender Tip Out ($)", min_value=0.0, format="%.2f")
    
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        total = credit_card_tips + cash_pocketed - bartender_tip_out
        st.success(f"Total Tips for {input_date}: ${total:.2f}")
        
        # Append the data to Google Sheet
        row = [str(input_date), credit_card_tips, cash_pocketed, bartender_tip_out, total]
        sheet.append_row(row)

st.header("Tip History")
data = sheet.get_all_records()
df = pd.DataFrame(data)
st.dataframe(df)
