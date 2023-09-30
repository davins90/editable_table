from hmac import new
import streamlit as st
import pandas as pd
from google.cloud import bigquery
import pandas_gbq
from datetime import datetime, timedelta
import yagmail
import os

st.set_page_config(layout="wide")

days_mapping = {
    'Monday': 'lunedì',
    'Tuesday': 'martedì',
    'Wednesday': 'mercoledì',
    'Thursday': 'giovedì',
    'Friday': 'venerdì',
    'Saturday': 'sabato',
    'Sunday': 'domenica'
}

project_id = "bigquery-to-streamlit"
dataset_id = "turni_babbuz"
table_id = "df"

st.title("Turni Babbuz")

st.markdown("Cliccate due volte sulla cella in corrispondenza del giorno scelto e selezionate (o digitate) il vostro nome. \n Una volta terminato, cliccate su **'Salva'** e attendente qualche secondo per il messaggio di conferma del salvataggio, in verde.")

# SQL query to select data from the table and order by date
sql = f"""
SELECT * 
FROM `{dataset_id}.{table_id}`
ORDER BY data
"""

# Load data into a DataFrame
df = pandas_gbq.read_gbq(sql, project_id=project_id)

# Check if the dataframe's first row is "yesterday's date"
# yesterday = datetime.now().date() - timedelta(days=1)

# if df['data'].iloc[0] == yesterday:
#     # Remove the first row (yesterday's date)
#     df = df.iloc[1:].reset_index(drop=True)
    
#     # Add a new day after the last date in the dataframe
#     new_date = df['data'].iloc[-1] + timedelta(days=1)
#     new_day_name = days_mapping[new_date.strftime('%A')]
#     new_row = {
#         'data': new_date,
#         'giorno': new_day_name,
#         'notte': None,
#         'casa': None,
#         'informazioni': None
#     }

#     new_row_df = pd.DataFrame([new_row])

#     df = pd.concat([df, new_row_df], ignore_index=True)

# First, ensure the 'data' column is of datetime type for comparison
df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')

# Get today's date
today = datetime.now().date()

# Initialize a counter for deleted rows
deleted_rows = 0

# Check if the dataframe's first row is before today's date
while df['data'].iloc[0].date() < today:
    # Remove the first row
    df = df.iloc[1:].reset_index(drop=True)
    deleted_rows += 1

# Add new rows equal to the number of deleted rows
for i in range(deleted_rows):
    new_date = df['data'].iloc[-1].date() + timedelta(days=1)
    # If new_date is not already in the dataframe
    if not (df['data'].dt.date == new_date).any():
        new_day_name = days_mapping[new_date.strftime('%A')]
        new_row = {
            'data': new_date.strftime('%d/%m/%Y'),  # Convert date to string in 'dd/mm/yyyy' format
            'giorno': new_day_name,
            'notte': None,
            'casa': None,
            'informazioni': None
        }

        new_row_df = pd.DataFrame([new_row])

        # Append the new_row to the dataframe
        df = pd.concat([df, new_row_df], ignore_index=True)

        # Update the last date for the next iteration
        # df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')

df['data'] = df['data'].dt.strftime('%d/%m/%Y')


df = df.set_index("data")

# def color_rows(row):
#     color = '#e6ffe6' if row['giorno'] in ['sabato', 'domenica'] else ''  
#     return ['background-color: {}'.format(color) for _ in row]

def color_rows(row):
    if not row['notte']:
        color = '#ffcccc'  # Light red
    # elif row['giorno'] in ['sabato', 'domenica']:
    #     color = '#e6ffe6'
    else:
        color = ''
    return ['background-color: {}'.format(color) for _ in row]


df = df.style.apply(color_rows, axis=1)

# df = st.data_editor(df,use_container_width=True, disabled=("data","giorno"))

df = st.data_editor(
    df,
    use_container_width=True, 
    disabled=("data","giorno"),
    column_config={
        "notte": st.column_config.SelectboxColumn(options=["...","Mamma","Nemi","Marta","Reby","Raky","Fili"," Sandi","Shad","Alex","DaniP","DaniF","DaniD"]),
        "casa": st.column_config.SelectboxColumn(options=["...","nemi","rebi","sandi","marta"])
    },
    hide_index=True,
    key="data_editor"
)

val = st.session_state["data_editor"]

if st.button('Salva',type="primary"):
    df.to_gbq('{}.{}'.format(dataset_id, table_id), project_id, if_exists='replace')
    st.success("Salvataggio riuscito!")

    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    receiver_email = os.environ.get('RECEIVER_EMAIL')

    user = yagmail.SMTP(user=sender_email, password=sender_password)

    user.send(to=receiver_email, subject="Modifica Turni Babbuz", contents=f"Modifica effettuata e salvata. Ecco cosa: {val}")

