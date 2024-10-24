import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Pumpkin's Tip Tracker",
    page_icon="🎃",
    layout="wide",
    initial_sidebar_state="expanded"
)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)
client = gspread.authorize(credentials)

sheet = client.open("Tip Tracker").sheet1

headers = ['Date', 'Credit Card Tips', 'Cash Pocketed', 'Bartender Tip Out', 'Total']

first_row = sheet.row_values(1)
if not first_row:
    sheet.insert_row(headers, index=1)

st.title("🎃 Pumpkin's Very Own - Tip Tracker")
st.markdown("---")

with st.form("tip_form"):
    st.header("Enter Today's Tips")
    col1, col2 = st.columns(2)
    with col1:
        input_date = st.date_input("Date", date.today())
        credit_card_tips = st.number_input("Credit Card Tips ($)", min_value=0.0, format="%.2f")
    with col2:
        cash_pocketed = st.number_input("Cash Pocketed ($)", min_value=0.0, format="%.2f")
        bartender_tip_out = st.number_input("Bartender Tip Out ($)", min_value=0.0, format="%.2f")
        
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        total = credit_card_tips + cash_pocketed - bartender_tip_out
        formatted_date = input_date.strftime("%a, %b %d, %Y")
        st.toast(f"Congrats! You made ${total:.2f} on {formatted_date}!", icon="🎉")
        st.balloons()
        
        row = [str(input_date), credit_card_tips, cash_pocketed, bartender_tip_out, total]
        sheet.append_row(row, value_input_option='USER_ENTERED')

st.markdown("---")

st.header("Tip History")

data = sheet.get_all_records()

if data:
    df = pd.DataFrame(data)
    
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime("%a, %b %d, %Y")
    numeric_cols = ['Credit Card Tips', 'Cash Pocketed', 'Bartender Tip Out', 'Total']
    for col in numeric_cols:
        df[col] = df[col].astype(float)
    
    df.index = df.index + 1
    df_styled = df.style.format({
        'Credit Card Tips': '${:,.2f}',
        'Cash Pocketed': '${:,.2f}',
        'Bartender Tip Out': '${:,.2f}',
        'Total': '${:,.2f}'
    })
    
    df_styled = df_styled.background_gradient(subset=['Total'], cmap='Greens')
    
    st.dataframe(df_styled, use_container_width=True)
else:
    st.write("No tip data available yet.")
