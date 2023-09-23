import streamlit as st
import pandas as pd
from google.cloud import bigquery
import pandas_gbq
from datetime import datetime, timedelta

st.set_page_config(layout="wide")


###

days_mapping = {
    'Monday': 'lunedì',
    'Tuesday': 'martedì',
    'Wednesday': 'mercoledì',
    'Thursday': 'giovedì',
    'Friday': 'venerdì',
    'Saturday': 'sabato',
    'Sunday': 'domenica'
}


def generate_dataframe():
    today = datetime.now().date()
    
    # Generate dates for 30 days starting from today
    dates = [(today + timedelta(days=i)) for i in range(31)]
    
    # Extract day names from the dates in English and map to Italian
    giorni = [days_mapping[date.strftime('%A')] for date in dates]
    
    data_template = {
        "notte": [""] * 31,
        "casa": [""] * 31,
        "informazioni": [""] * 31
    }
    
    df = pd.DataFrame({
        "data": [date.strftime('%d/%m') for date in dates],
        "giorno": giorni,
        **data_template
    })
    
    return df

# Info ID
project_id = "bigquery-to-streamlit"
dataset_id = "turni-babbuz"
table_id = "df"

###

st.title("Turni Babbuz")

# SQL query to select data from the table
sql = """
SELECT * 
FROM `{}.{}`
""".format(dataset_id, table_id)

# Load data into a DataFrame
df = pandas_gbq.read_gbq(sql, project_id=project_id)

st.dataframe(df.head(10))

# df = generate_dataframe()

# df = df.set_index("data")

# def color_rows(row):
#     color = '#e6ffe6' if row['giorno'] in ['sabato', 'domenica'] else ''  # '#90ee90' is light green
#     return ['background-color: {}'.format(color) for _ in row]

# df = df.style.apply(color_rows, axis=1)

# df = st.data_editor(df,use_container_width=True, disabled=("data","giorno"))



