import calendar                                 # Core Python Module
from datetime import datetime                   # Core Python Module
from deta import Deta
import plotly.graph_objects as go               # pip install plotly
import plotly.express as px                     # pip install plotly-express
from plotly.subplots import make_subplots
import streamlit as st                          # pip install streamlit
from streamlit_option_menu import option_menu   # pip install streamlit-option-menu
import streamlit.components.v1 as components
import streamlit_authenticator as stauth        # pip install streamlit-authenticator
import json
import pandas as pd
from collections import Counter
import os

# ---SETTINGS---
page_title = "Utilities Dashboard"
page_icon = ":bulb:"                      # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
layout = "wide"                         # alternatively used "centered"
# --------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_icon + " " + page_title)

# Utility Database Interface
DETA_KEY = 'c0jo61nr_Fk3geHfjZYDv53FuxFYaEPjhitTawRVz'              
deta = Deta(DETA_KEY)
db2 = deta.Base('utility_db')

def insert_util(uti, dat2, exps, usa, comment):
    """Returns the user on a successful user creation, otherwise raises and error"""
    return db2.put({'utility': uti, 'date': dat2, 'expense': exps, 'usage': usa, 'comment': comment})

def fetch_all_utils():
    """Returns a dict of all date"""
    res = db2.fetch()
    return res.items

# Creating Utility Table Dataframe
df2 = fetch_all_utils()
df2 = json.dumps(df2)
df2 = pd.read_json(df2)
# Creating new columns
expense_1 = df2['expense'].map(Counter).groupby(df2['key']).sum()
expense_1 = df2['expense'].apply(lambda x: x.get('Cost')).dropna()
usage_1 = df2['usage'].map(Counter).groupby(df2['key']).sum()
usage_1 = df2['usage'].apply(lambda x: x.get('Usage')).dropna()
utility_1 = df2['utility'].map(Counter).groupby(df2['key']).sum()
utility_1 = df2['utility'].apply(lambda x: x.get('uti')).dropna()
date_2 = df2['date'].map(Counter).groupby(df2['key']).sum()
date_2 = df2['date'].apply(lambda x: x.get('dat2')).dropna()
# Combined all new columns
df2_new = pd.merge(date_2, utility_1, left_index=True, right_index=True)
df2_new = pd.merge(df2_new, expense_1, left_index=True, right_index=True)
df2_new = pd.merge(df2_new, usage_1, left_index=True, right_index=True)
df2_new['date'] = pd.to_datetime(df2_new['date'])
df2_new = df2_new.sort_values(by='date')
df2_new['date'] = df2_new['date'].astype(str).str.replace('T','-', regex=True)
# Creating Utility Tables
df_TNB = df2_new[(df2_new['utility'] == 'TNB')]
df_AIR = df2_new[(df2_new['utility'] == 'Air Selangor')]
df_DIGI = df2_new[(df2_new['utility'] == 'DiGi')]
df_TM = df2_new[(df2_new['utility'] == 'TM')]
df_IWK = df2_new[(df2_new['utility'] == 'IWK')]
# ----
total_tnb = df_TNB['expense'].sum()
bill_tnb = df_TNB['expense'].__len__()
total_kwh = df_TNB['usage'].sum()
total_air = df_AIR['expense'].sum()
bill_air = df_AIR['expense'].__len__()
total_m3 = df_AIR['usage'].sum()
total_digi = df_DIGI['expense'].sum()
bill_digi = df_DIGI['expense'].__len__()
total_tm = df_TM['expense'].sum()
bill_tm = df_TM['expense'].__len__()
total_iwk = df_IWK['expense'].sum()
bill_iwk = df_IWK['expense'].__len__()

#selected = option_menu(menu_title = None, options = ['Summary', 'TNB', 'Air Selangor', 'DiGi', 'TM', 'IWK'], icons = ['grid-1x2', 'grid-1x2', 'grid-1x2', 'grid-1x2','grid-1x2', 'grid-1x2'], orientation='horizontal')
with st.sidebar:
    selected = st.radio('Please select page accordingly:', ('Summary', 'TNB', 'Air Selangor', 'DiGi', 'TM', 'IWK'))

if selected == 'Summary':
    st.header('Summary:')
    col1, col2, col3 = st.columns(3)
    col1.metric('TNB', f'RM{total_tnb:,.2f}')
    col2.metric('Air Selangor', f'RM{total_air:,.2f}')
    col3.metric('DiGi', f'RM{total_digi:,.2f}')
    col1.metric('TM', f'RM{total_tm:,.2f}')
    col2.metric('IWK', f'RM{total_iwk:,.2f}')
    col3.metric('Total Utility Cost', f'RM{(total_tnb+total_air+total_tm+total_digi+total_iwk):,.2f}')

if selected == 'TNB':
    st.header('TNB')
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric('RM', f'{total_tnb:,.2f}')
    col2.metric('No. Of Bills', f'{bill_tnb}')
    col3.metric('Average Cost', f'{(total_tnb/bill_tnb):,.2f}')
    col4.metric('kWh', f'{total_kwh:,.0f}')
    col5.metric('TNB Rate (RM/kWh)', f'{(total_tnb/total_kwh):,.2f}')
    # Graph
    fig_tnb = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
    fig_tnb.add_trace(go.Bar(x = df_TNB['date'], y = df_TNB['expense'],name='RM'))
    fig_tnb.add_trace(go.Scatter(x = df_TNB['date'], y = df_TNB['usage'],name='kWh',
        fill='tozeroy',mode='lines',line = dict(color='red', width=1)), secondary_y=True)
    fig_tnb.add_trace(go.Scatter(x = df_TNB['date'], y = df_TNB['usage'],name='kWh',
        mode='lines',line = dict(color='black', width=2)), secondary_y=True)
    fig_tnb.update_layout(height=350,title_text='Annual Electricity Consumption (RM VS kWh)',title_x=0.5,
        font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),yaxis_title=None,showlegend=False)
    fig_tnb.update_annotations(font=dict(family="Helvetica", size=10))
    fig_tnb.update_xaxes(title_text='Month', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
    fig_tnb.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
    st.plotly_chart(fig_tnb, use_container_width=True)
    # Table
    fig_table_tnb = go.Figure(data=[go.Table(columnwidth=[1,1,1,1], header=dict(values=list(df_TNB.columns),fill_color='paleturquoise',align='center'),
                        cells=dict(values=[df_TNB.date, df_TNB.utility, df_TNB.expense, df_TNB.usage],fill_color='lavender',align='center'))])
    fig_table_tnb.update_layout(margin=dict(t=5,b=5,l=5,r=5))
    st.plotly_chart(fig_table_tnb, use_container_width=True)

if selected == 'Air Selangor':
    st.header('Air Selangor')
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric('RM', f'{total_air:,.2f}')
    col2.metric('No. Of Bills', f'{bill_air}')
    col3.metric('Average Cost', f'{(total_air/bill_air):,.2f}')
    col4.metric('m3', f'{total_m3:,.0f}')
    col5.metric('Air Selangor Rate (RM/m3)', f'{(total_air/total_m3):,.2f}')
    # Graph
    fig_air = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
    fig_air.add_trace(go.Bar(x = df_AIR['date'], y = df_AIR['expense'],name='RM'))
    fig_air.add_trace(go.Scatter(x = df_AIR['date'], y = df_AIR['usage'],name='m3',
        fill='tozeroy',mode='lines',line = dict(color='red', width=1)), secondary_y=True)
    fig_air.add_trace(go.Scatter(x = df_AIR['date'], y = df_AIR['usage'],name='m3',
        mode='lines',line = dict(color='black', width=2)), secondary_y=True)
    fig_air.update_layout(height=350,title_text='Annual Water Consumption (RM VS m3)',title_x=0.5,
        font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),yaxis_title=None,showlegend=False)
    fig_air.update_annotations(font=dict(family="Helvetica", size=10))
    fig_air.update_xaxes(title_text='Month', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
    fig_air.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
    st.plotly_chart(fig_air, use_container_width=True)
    # Table
    fig_table_air = go.Figure(data=[go.Table(columnwidth=[1,1,1,1], header=dict(values=list(df_AIR.columns),fill_color='paleturquoise',align='center'),
                        cells=dict(values=[df_AIR.date, df_AIR.utility, df_AIR.expense, df_AIR.usage],fill_color='lavender',align='center'))])
    fig_table_air.update_layout(margin=dict(t=5,b=5,l=5,r=5))
    st.plotly_chart(fig_table_air, use_container_width=True)

if selected == 'DiGi':
    st.header('DiGi')
    col1, col2, col3 = st.columns(3)
    col1.metric('RM', f'{total_digi:,.2f}')
    col2.metric('No. Of Bills', f'{bill_digi}')
    col3.metric('Average Cost', f'{(total_digi/bill_digi):,.2f}')
    # Graph
    fig_digi = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
    fig_digi.add_trace(go.Bar(x = df_DIGI['date'], y = df_DIGI['expense'],name='RM'))
    fig_digi.update_layout(height=350,title_text='Annual DiGi Consumption (RM)',title_x=0.5,
        font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),yaxis_title=None,showlegend=False)
    fig_digi.update_annotations(font=dict(family="Helvetica", size=10))
    fig_digi.update_xaxes(title_text='Month', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
    fig_digi.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
    st.plotly_chart(fig_digi, use_container_width=True)
    # Table
    fig_table_digi = go.Figure(data=[go.Table(columnwidth=[1,1,1,1], header=dict(values=list(df_DIGI.columns),fill_color='paleturquoise',align='center'),
                        cells=dict(values=[df_DIGI.date, df_DIGI.utility, df_DIGI.expense, df_DIGI.usage],fill_color='lavender',align='center'))])
    fig_table_digi.update_layout(margin=dict(t=5,b=5,l=5,r=5))
    st.plotly_chart(fig_table_digi, use_container_width=True)

if selected == 'TM':
    st.header('TM')
    col1, col2, col3 = st.columns(3)
    col1.metric('RM', f'{total_tm:,.2f}')
    col2.metric('No. Of Bills', f'{bill_tm}')
    col3.metric('Average Cost', f'{(total_tm/bill_tm):,.2f}')
    # Graph
    fig_tm = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
    fig_tm.add_trace(go.Bar(x = df_TM['date'], y = df_TM['expense'],name='RM'))
    fig_tm.update_layout(height=350,title_text='Annual TM Consumption (RM)',title_x=0.5,
        font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),yaxis_title=None,showlegend=False)
    fig_tm.update_annotations(font=dict(family="Helvetica", size=10))
    fig_tm.update_xaxes(title_text='Month', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
    fig_tm.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
    st.plotly_chart(fig_tm, use_container_width=True)
    # Table
    fig_table_tm = go.Figure(data=[go.Table(columnwidth=[1,1,1,1], header=dict(values=list(df_TM.columns),fill_color='paleturquoise',align='center'),
                        cells=dict(values=[df_TM.date, df_TM.utility, df_TM.expense, df_TM.usage],fill_color='lavender',align='center'))])
    fig_table_tm.update_layout(margin=dict(t=5,b=5,l=5,r=5))
    st.plotly_chart(fig_table_tm, use_container_width=True)

if selected == 'IWK':
    st.header('IWK')
    col1, col2, col3 = st.columns(3)
    col1.metric('RM', f'{total_iwk:,.2f}')
    col2.metric('No. Of Bills', f'{bill_iwk}')
    col3.metric('Average Cost', f'{(total_iwk/bill_iwk):,.2f}')
    # Table
    fig_table_iwk = go.Figure(data=[go.Table(columnwidth=[1,1,1,1], header=dict(values=list(df_IWK.columns),fill_color='paleturquoise',align='center'),
                        cells=dict(values=[df_IWK.date, df_IWK.utility, df_IWK.expense, df_IWK.usage],fill_color='lavender',align='center'))])
    fig_table_iwk.update_layout(margin=dict(t=5,b=5,l=5,r=5))
    st.plotly_chart(fig_table_iwk, use_container_width=True)

# --- HIDE STREAMLIT STYLE ---

hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)