# import streamlit as st
# import pandas as pd
# from google.cloud import bigquery
# import pandas_gbq
# from datetime import datetime, timedelta

# st.set_page_config(layout="wide")


# days_mapping = {
#     'Monday': 'lunedì',
#     'Tuesday': 'martedì',
#     'Wednesday': 'mercoledì',
#     'Thursday': 'giovedì',
#     'Friday': 'venerdì',
#     'Saturday': 'sabato',
#     'Sunday': 'domenica'
# }

# project_id = "bigquery-to-streamlit"
# dataset_id = "turni_babbuz"
# table_id = "df"

# st.title("Turni Babbuz")

# # SQL query to select data from the table and order by date
# sql = """
# SELECT * 
# FROM `{}.{}`
# ORDER BY data
# """.format(dataset_id, table_id)

# # Load data into a DataFrame
# df = pandas_gbq.read_gbq(sql, project_id=project_id)

# # Check if the dataframe's first row is "yesterday's date"
# yesterday = datetime.now().date() - timedelta(days=1)
# st.write(yesterday)
# st.write(df.dtypes)
# if df['data'].iloc[0] == yesterday:
#     # Remove the first row (yesterday's date)
#     df = df.iloc[1:].reset_index(drop=True)

# df = df.set_index("data")

# def color_rows(row):
#     color = '#e6ffe6' if row['giorno'] in ['sabato', 'domenica'] else ''  
#     return ['background-color: {}'.format(color) for _ in row]

# df = df.style.apply(color_rows, axis=1)

# df = st.data_editor(df,use_container_width=True, disabled=("data","giorno"))

# if st.button('Save to BigQuery'):
#     df.to_gbq('{}.{}'.format(dataset_id, table_id), project_id, if_exists='replace')
#     st.success("Data saved to BigQuery successfully!")

import streamlit as st
import pandas as pd
from google.cloud import bigquery
import pandas_gbq
from datetime import datetime, timedelta

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

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.write(f"Current Time (UTC): {current_time}")


# SQL query to select data from the table and order by date
sql = f"""
SELECT * 
FROM `{dataset_id}.{table_id}`
ORDER BY data
"""

# Load data into a DataFrame
df = pandas_gbq.read_gbq(sql, project_id=project_id)

# Check if the dataframe's first row is "yesterday's date"
yesterday = datetime.now().date() - timedelta(days=1)

if df['data'].iloc[0] == yesterday:
    # Remove the first row (yesterday's date)
    df = df.iloc[1:].reset_index(drop=True)
    
    # Add a new day after the last date in the dataframe
    new_date = df['data'].iloc[-1] + timedelta(days=1)
    new_day_name = days_mapping[new_date.strftime('%A')]
    new_row = {
        'data': new_date,
        'giorno': new_day_name,
        'notte': "",
        'casa': "",
        'informazioni': ""
    }

    new_row_df = pd.DataFrame.from_dict(new_row, orient='columns',index=[0])

    df = pd.concat([df, new_row_df], ignore_index=True)

df = df.set_index("data")

def color_rows(row):
    color = '#e6ffe6' if row['giorno'] in ['sabato', 'domenica'] else ''  
    return ['background-color: {}'.format(color) for _ in row]

df = df.style.apply(color_rows, axis=1)

df = st.data_editor(df,use_container_width=True, disabled=("data","giorno"))

if st.button('Salva'):
    df.to_gbq('{}.{}'.format(dataset_id, table_id), project_id, if_exists='replace')
    st.success("Salvataggio riuscito!")

