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
#import database as db                          # local import

# ---STREAMLIT SECRET SETTINGs---
# Everything is accessible via the st.secrets dict:
#st.write("DB username:", st.secrets["db_username"])
#st.write("DB password:", st.secrets["db_password"])
#st.write("My cool secrets:", st.secrets["my_cool_secrets"]["things_i_like"])
# And the root-level secrets are also accessible as environment variables:
#st.write("Has environment variables been set:",os.environ["db_username"] == st.secrets["db_username"])

# ---SETTINGS---
e_usages = ["kWh"]
e_costs = ["RM_e"]
w_usages = ["m3"]
w_costs = ["RM_w"]
digi_zahirs = ["RM_d1"]
digi_anis = ["RM_d2"]
streamyxs = ["RM_s"]
currency = "RM"
page_title = "Utilities Dashboard"
page_icon = ":ledger:"                      # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
layout = "centered"                         # alternatively used "wide"
# --------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_icon + " " + page_title)

# --- HIDE STREAMLIT STYLE ---

hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- DROP DOWN VALUES FOR SELECTING THE PERIOD ---
years = [datetime.today().year, datetime.today().year + 1]
months = list(calendar.month_name[1:])

# --- INFORMATION DATABASE INTERFACE ---
DETA_KEY = "c0jo61nr_BhSm5qHprUP75vRSdEmumYfoS1KMCtQW"
deta = Deta(DETA_KEY)                                   # Initialize with a project key
db = deta.Base("utilities_reports")                     # This is how to create/connect a database

def insert_period(period, e_usages, e_costs, w_usages, w_costs, digi_zahirs, digi_anis, streamyxs, comment):
    """Returns the user on a successful user creation, otherwise raises and error"""
    return db.put({"key": period, "e_usage": e_usages, "e_cost": e_costs, "w_usage": w_usages, "w_cost": w_costs, "digi_zahir": digi_zahirs, 
                   "digi_ani": digi_anis, "streamyx": streamyxs, "comment": comment})

def fetch_all_periods():
    """Returns a dict of all periods"""
    res = db.fetch()
    return res.items

def get_period(period):
    """If not found, the function will return None"""
    return db.get(period)

def get_all_periods():
    items = fetch_all_periods()
    periods = [item["key"] for item in items]
    return periods
    
# --- AUTHENTICATION DATABASE INTERFACE ---

DETA_KEY_1 = "c0jo61nr_P1wSYy8XFqjnwgyeWUXqU635PWYK4A85"
deta_1 = Deta(DETA_KEY_1)                           # Initialize with a project key
db_1 = deta_1.Base("users_db")                      # This is how to create/connect a database

def fetch_all_users():
    """Returns a dict of all users"""
    res = db_1.fetch()
    return res.items

# --- USER AUTHENTICATION ---
users = fetch_all_users()

usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]

authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "utility_dashboard", "abcdef", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    #st.subheader(f"Welcome {name}")
    authenticator.logout("Logout", "sidebar")
    st.sidebar.subheader(f"User ID: {username}")
    st.sidebar.subheader(f"User Name: {name}")
    
    # --- NAVIGATION MENU ---
    selected = option_menu(
        menu_title=None,
        options=["Data Overview","Data Entry","Data Query","Data Library"],
        icons=["globe","pencil-fill","search","archive"] ,                           # https://icons.getbootstrap.com/
        orientation="horizontal",
    )

    entries = fetch_all_periods()
    df = json.dumps(entries)
    df = pd.read_json(df)
    df['key'] = df['key'].str.replace('_','/')
    df['key']= pd.to_datetime(df['key'])
    # Creating new columns
    digi_ani_1 = df['digi_ani'].map(Counter).groupby(df['key']).sum()
    digi_ani_1 = df['digi_ani'].apply(lambda x: x.get('RM_d2')).dropna()
    digi_zahir_1 = df['digi_zahir'].map(Counter).groupby(df['key']).sum()
    digi_zahir_1 = df['digi_zahir'].apply(lambda x: x.get('RM_d1')).dropna()
    e_cost_1 = df['e_cost'].map(Counter).groupby(df['key']).sum()
    e_cost_1 = df['e_cost'].apply(lambda x: x.get('RM_e')).dropna()
    e_usage_1 = df['e_usage'].map(Counter).groupby(df['key']).sum()
    e_usage_1 = df['e_usage'].apply(lambda x: x.get('kWh')).dropna()
    streamyx_1 = df['streamyx'].map(Counter).groupby(df['key']).sum()
    streamyx_1 = df['streamyx'].apply(lambda x: x.get('RM_s')).dropna()
    w_cost_1 = df['w_cost'].map(Counter).groupby(df['key']).sum()
    w_cost_1 = df['w_cost'].apply(lambda x: x.get('RM_w')).dropna()
    w_usage_1 = df['w_usage'].map(Counter).groupby(df['key']).sum()
    w_usage_1 = df['w_usage'].apply(lambda x: x.get('m3')).dropna()
    # Combined all new columns
    df_new = pd.merge(df['key'], e_cost_1, left_index=True, right_index=True)
    df_new = pd.merge(df_new, e_usage_1, left_index=True, right_index=True)
    df_new = pd.merge(df_new, w_cost_1, left_index=True, right_index=True)
    df_new = pd.merge(df_new, w_usage_1, left_index=True, right_index=True)
    df_new = pd.merge(df_new, digi_zahir_1, left_index=True, right_index=True)
    df_new = pd.merge(df_new, digi_ani_1, left_index=True, right_index=True)
    df_new = pd.merge(df_new, streamyx_1, left_index=True, right_index=True)
    df_new = df_new.sort_values(by='key')
    df_new['key'] = df_new['key'].astype(str).str.replace('T','-', regex=True)
    # Creating yearly dataframe
    df_2014 = df_new[(df_new['key'] >= "2014-01-01") & (df_new['key'] <="2014-12-01")]
    df_2015 = df_new[(df_new['key'] >= "2015-01-01") & (df_new['key'] <="2015-12-01")]
    df_2016 = df_new[(df_new['key'] >= "2016-01-01") & (df_new['key'] <="2016-12-01")]
    df_2017 = df_new[(df_new['key'] >= "2017-01-01") & (df_new['key'] <="2017-12-01")]
    df_2018 = df_new[(df_new['key'] >= "2018-01-01") & (df_new['key'] <="2018-12-01")]
    df_2019 = df_new[(df_new['key'] >= "2019-01-01") & (df_new['key'] <="2019-12-01")]
    df_2020 = df_new[(df_new['key'] >= "2020-01-01") & (df_new['key'] <="2020-12-01")]
    df_2021 = df_new[(df_new['key'] >= "2021-01-01") & (df_new['key'] <="2021-12-01")]
    df_2022 = df_new[(df_new['key'] >= "2022-01-01") & (df_new['key'] <="2022-12-01")]
    
    # --- DATA VISUALISATION ---
    if selected == "Data Overview":
        st.header("Summary")
        st.subheader("Total Cost:")
        col1, col2, col3 = st.columns(3)
        col1.metric("Electricity Cost:", f"RM{df_new['e_cost'].sum():,.2f}")
        col2.metric("Water Cost:", f"RM{df_new['w_cost'].sum():,.2f}")
        col3.metric("Telco Cost:", f"RM{(df_new['digi_zahir'].sum()+df_new['digi_ani'].sum()+df_new['streamyx'].sum()):,.2f}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Costs:", f"RM{(df_new['e_cost'].sum()+df_new['w_cost'].sum()+df_new['digi_zahir'].sum()+df_new['digi_ani'].sum()+df_new['streamyx'].sum()):,.2f}")

        st.subheader("Total Usage:")
        col1, col2, col3 = st.columns(3)
        col1.metric("Electricity Usage:", f"{df_new['e_usage'].sum():,.0f}kWh")
        col2.metric("Water Usage:", f"{df_new['w_usage'].sum():,.0f}m3")
        
        st.subheader("Graphs:")
        # BAR CHART
        fig_1 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
        fig_1.add_trace(go.Bar(x = ['Electricity'], y = [df_new['e_usage'].sum()],name=''))
        fig_1.add_trace(go.Bar(x = ['Water'], y = [df_new['w_cost'].sum()],name=''))
        fig_1.add_trace(go.Bar(x = ['DiGi Zahir'], y = [df_new['digi_zahir'].sum()],name=''))
        fig_1.add_trace(go.Bar(x = ['DiGi Ani'], y = [df_new['digi_ani'].sum()],name=''))
        fig_1.add_trace(go.Bar(x = ['Streamyx'], y = [df_new['streamyx'].sum()],name=''))
        fig_1.update_layout(title_text='Total Utilities Cost (RM)',title_x=0.5, height=350,
            font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",
            yaxis=(dict(showgrid=False)),yaxis_title=None,showlegend=False)
        fig_1.update_annotations(font=dict(family="Helvetica", size=10))
        fig_1.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
        fig_1.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
        # PIE CHART
        fig_pie_main = make_subplots(specs=[[{"type": "domain"}]])
        fig_pie_main.add_trace(go.Pie(
            values=[df_new['e_cost'].sum(), df_new['w_cost'].sum(), df_new['digi_zahir'].sum(), df_new['digi_ani'].sum(), df_new['streamyx'].sum()],
            labels=['Electricity','Water','DiGi Zahir','Digi Ani','Streamyx'],textposition='inside',textinfo='label+percent'),row=1, col=1)
        fig_pie_main.update_annotations(font=dict(family="Helvetica", size=10))
        fig_pie_main.update_layout(height=350,showlegend=False,title_text='Total Utility Cost (%)',title_x=0.5,font=dict(family="Helvetica", size=10))
        # Chart Presentation
        col1, col2 = st.columns(2)
        col1.plotly_chart(fig_1, use_container_width=True)
        col2.plotly_chart(fig_pie_main, use_container_width=True)

        with st.expander("Utilities Rates:"):
            col1, col2 = st.columns(2)
            col1.metric("Electricity Rate:", f"RM{(df_new['e_cost'].sum()/df_new['e_usage'].sum()):,.2f}")
            col2.metric("Water Rate:", f"RM{(df_new['w_cost'].sum()/df_new['w_usage'].sum()):,.2f}")
        
        st.subheader("Annual Data By Type of Utility:")

        with st.expander("Electricity:"):
            # Graph Electricity Cost VS Usage
            fig_yearly_e = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_yearly_e.add_trace(go.Bar(x = ['2014','2015','2016','2017','2018','2019','2020','2021','2022'], 
                y = [df_2014['e_cost'].sum(),df_2015['e_cost'].sum(),df_2016['e_cost'].sum(),df_2017['e_cost'].sum(),df_2018['e_cost'].sum(),
                    df_2019['e_cost'].sum(),df_2020['e_cost'].sum(),df_2021['e_cost'].sum(),df_2022['e_cost'].sum()],name='RM'))
            fig_yearly_e.add_trace(go.Scatter(x = ['2014','2015','2016','2017','2018','2019','2020','2021','2022'], 
                y = [df_2014['e_cost'].sum(),df_2015['e_cost'].sum(),df_2016['e_cost'].sum(),df_2017['e_cost'].sum(),df_2018['e_cost'].sum(),
                    df_2019['e_cost'].sum(),df_2020['e_cost'].sum(),df_2021['e_cost'].sum(),df_2022['e_cost'].sum()],name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_yearly_e.add_trace(go.Bar(x = ['2014','2015','2016','2017','2018','2019','2020','2021','2022'], 
                y = [df_2014['e_usage'].sum(),df_2015['e_usage'].sum(),df_2016['e_usage'].sum(),df_2017['e_usage'].sum(),df_2018['e_usage'].sum(),
                    df_2019['e_usage'].sum(),df_2020['e_usage'].sum(),df_2021['e_usage'].sum(),df_2022['e_usage'].sum()],name='kWh'))
            fig_yearly_e.add_trace(go.Scatter(x = ['2014','2015','2016','2017','2018','2019','2020','2021','2022'], 
                y = [df_2014['e_usage'].sum(),df_2015['e_usage'].sum(),df_2016['e_usage'].sum(),df_2017['e_usage'].sum(),df_2018['e_usage'].sum(),
                    df_2019['e_usage'].sum(),df_2020['e_usage'].sum(),df_2021['e_usage'].sum(),df_2022['e_usage'].sum()],name='kWh',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_yearly_e.update_layout(title_text='Annual Electricity (Cost VS Usage)',title_x=0.5, height=350,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False)
            fig_yearly_e.update_annotations(font=dict(family="Helvetica", size=10))
            fig_yearly_e.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_yearly_e.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # PIE CHART Cost
            fig_pie_yearly_ecost = make_subplots(specs=[[{"type": "domain"}]])
            fig_pie_yearly_ecost.add_trace(go.Pie(
                values=[df_2014['e_cost'].sum(),df_2015['e_cost'].sum(),df_2016['e_cost'].sum(),df_2017['e_cost'].sum(),df_2018['e_cost'].sum(),
                    df_2019['e_cost'].sum(),df_2020['e_cost'].sum(),df_2021['e_cost'].sum(),df_2022['e_cost'].sum()],
                labels=['2014','2015','2016','2017','2018','2019','2020','2021','2022'],textposition='inside',textinfo='label+percent'),row=1, col=1)
            fig_pie_yearly_ecost.update_annotations(font=dict(family="Helvetica", size=10))
            fig_pie_yearly_ecost.update_layout(height=350,showlegend=False,title_text='Annual Electricity Cost (%)',title_x=0.5,font=dict(family="Helvetica", size=10))            
            # PIE CHART Usage
            fig_pie_yearly_eusage = make_subplots(specs=[[{"type": "domain"}]])
            fig_pie_yearly_eusage.add_trace(go.Pie(
                values=[df_2014['e_usage'].sum(),df_2015['e_usage'].sum(),df_2016['e_usage'].sum(),df_2017['e_usage'].sum(),df_2018['e_usage'].sum(),
                    df_2019['e_usage'].sum(),df_2020['e_usage'].sum(),df_2021['e_usage'].sum(),df_2022['e_usage'].sum()],
                labels=['2014','2015','2016','2017','2018','2019','2020','2021','2022'],textposition='inside',textinfo='label+percent'),row=1, col=1)
            fig_pie_yearly_eusage.update_annotations(font=dict(family="Helvetica", size=10))
            fig_pie_yearly_eusage.update_layout(height=350,showlegend=False,title_text='Annual Electricity Usage (%)',title_x=0.5,font=dict(family="Helvetica", size=10))
            # Chart Presentation
            st.plotly_chart(fig_yearly_e, use_container_width=True)
            col1, col2 = st.columns(2)
            col1.plotly_chart(fig_pie_yearly_ecost, use_container_width=True)
            col2.plotly_chart(fig_pie_yearly_eusage, use_container_width=True)

        with st.expander("Water:"):
            # Graph Water Cost
            fig_yearly_w = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_yearly_w.add_trace(go.Bar(x = ['2019','2020','2021','2022'], 
                y = [df_2019['w_cost'].sum(),df_2020['w_cost'].sum(),df_2021['w_cost'].sum(),df_2022['w_cost'].sum()],name='RM'))
            fig_yearly_w.add_trace(go.Scatter(x = ['2019','2020','2021','2022'], 
                y = [df_2019['w_cost'].sum(),df_2020['w_cost'].sum(),df_2021['w_cost'].sum(),df_2022['w_cost'].sum()],name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_yearly_w.add_trace(go.Bar(x = ['2019','2020','2021','2022'], 
                y = [df_2019['w_usage'].sum(),df_2020['w_usage'].sum(),df_2021['w_usage'].sum(),df_2022['w_usage'].sum()],name='m3'))
            fig_yearly_w.add_trace(go.Scatter(x = ['2019','2020','2021','2022'], 
                y = [df_2019['w_usage'].sum(),df_2020['w_usage'].sum(),df_2021['w_usage'].sum(),df_2022['w_usage'].sum()],name='m3',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_yearly_w.update_layout(title_text='Annual Water (Cost VS Usage)',title_x=0.5, height=350,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False)
            fig_yearly_w.update_annotations(font=dict(family="Helvetica", size=10))
            fig_yearly_w.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_yearly_w.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # PIE CHART Cost
            fig_pie_yearly_wcost = make_subplots(specs=[[{"type": "domain"}]])
            fig_pie_yearly_wcost.add_trace(go.Pie(
                values=[df_2019['w_cost'].sum(),df_2020['w_cost'].sum(),df_2021['w_cost'].sum(),df_2022['w_cost'].sum()],
                labels=['2019','2020','2021','2022'],textposition='inside',textinfo='label+percent'),row=1, col=1)
            fig_pie_yearly_wcost.update_annotations(font=dict(family="Helvetica", size=10))
            fig_pie_yearly_wcost.update_layout(height=350,showlegend=False,title_text='Annual Water Cost (%)',title_x=0.5,font=dict(family="Helvetica", size=10))
            # PIE CHART Usage
            fig_pie_yearly_wusage = make_subplots(specs=[[{"type": "domain"}]])
            fig_pie_yearly_wusage.add_trace(go.Pie(
                values=[df_2019['w_usage'].sum(),df_2020['w_usage'].sum(),df_2021['w_usage'].sum(),df_2022['w_usage'].sum()],
                labels=['2019','2020','2021','2022'],textposition='inside',textinfo='label+percent'),row=1, col=1)
            fig_pie_yearly_wusage.update_annotations(font=dict(family="Helvetica", size=10))
            fig_pie_yearly_wusage.update_layout(height=350,showlegend=False,title_text='Annual Water Usage (%)',title_x=0.5,font=dict(family="Helvetica", size=10))
            # Chart Presentation
            st.plotly_chart(fig_yearly_w, use_container_width=True)  
            col1, col2 = st.columns(2)
            col1.plotly_chart(fig_pie_yearly_wcost, use_container_width=True)
            col2.plotly_chart(fig_pie_yearly_wusage, use_container_width=True) 
                     
    # --- DATA LIBRARY ---
    if selected == "Data Library":
        st.header("Historical Data By Year")

        with st.expander("Click to View Year 2022 Data:"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Costs:",f"RM{(df_2022['e_cost'].sum()+df_2022['w_cost'].sum()+df_2022['digi_zahir'].sum()+df_2022['digi_ani'].sum()+df_2022['streamyx'].sum()):,.2f}")
            col2.metric("Electricity Cost:", f"RM{df_2022['e_cost'].sum():,.2f}")
            col3.metric("Water Cost:", f"RM{df_2022['w_cost'].sum():,.2f}")
            col1, col2, col3 = st.columns(3)
            col1.metric("DiGi Zahir Cost:", f"RM{df_2022['digi_zahir'].sum():,.2f}")
            col2.metric("DiGi Ani Cost:", f"RM{df_2022['digi_ani'].sum():,.2f}")
            col3.metric("Streamyx Cost:", f"RM{df_2022['streamyx'].sum():,.2f}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Usage:", f"{df_2022['e_usage'].sum():,.0f}kWh")
            col2.metric("Water Usage:", f"{df_2022['w_usage'].sum():,.0f}m3")
            # Graph Yr 2022
            fig_2022 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_2022.add_trace(go.Bar(x = ['Electricity'], y = [df_2022['e_cost'].sum()],name=''))
            fig_2022.add_trace(go.Bar(x = ['Water'], y = [df_2022['w_cost'].sum()],name=''))
            fig_2022.add_trace(go.Bar(x = ['DiGi Zahir'], y = [df_2022['digi_zahir'].sum()],name=''))
            fig_2022.add_trace(go.Bar(x = ['DiGi Ani'], y = [df_2022['digi_ani'].sum()],name=''))
            fig_2022.add_trace(go.Bar(x = ['Streamyx'], y = [df_2022['streamyx'].sum()],name=''))
            fig_2022.update_layout(title_text='Total Utility Cost (RM)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_2022.update_annotations(font=dict(family="Helvetica", size=10))
            fig_2022.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_2022.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # PIE CHART
            fig_pie_2022 = make_subplots(specs=[[{"type": "domain"}]])
            fig_pie_2022.add_trace(go.Pie(
                values=[df_2022['e_cost'].sum(), df_2022['w_cost'].sum(), df_2022['digi_zahir'].sum(), df_2022['digi_ani'].sum(), df_2022['streamyx'].sum()],
                labels=['Electricity','Water','DiGi Zahir','Digi Ani','Streamyx'],textposition='inside',textinfo='label+percent'),row=1, col=1)
            fig_pie_2022.update_annotations(font=dict(family="Helvetica", size=10))
            fig_pie_2022.update_layout(height=350,showlegend=False,title_text='Total Utility Cost (%)',title_x=0.5,font=dict(family="Helvetica", size=10))
            # Chart Presentation
            col1, col2 = st.columns(2)
            col1.plotly_chart(fig_2022, use_container_width=True)
            col2.plotly_chart(fig_pie_2022, use_container_width=True)
            # Cost VS Usage
            fig_e_2022 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_e_2022.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2022['e_cost'],name='RM'))
            fig_e_2022.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2022['e_cost'],name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_e_2022.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2022['e_usage'],name='kWh'))
            fig_e_2022.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2022['e_usage'],name='kWh',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_e_2022.update_layout(title_text='Monthly Electricity (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_e_2022.update_annotations(font=dict(family="Helvetica", size=10))
            fig_e_2022.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_e_2022.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_e_2022, use_container_width=True)
            # Cost VS Usage
            fig_w_2022 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_w_2022.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2022['w_cost'],name='RM'))
            fig_w_2022.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2022['w_cost'],name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_w_2022.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2022['w_usage'],name='m3'))
            fig_w_2022.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2022['w_usage'],name='m3',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_w_2022.update_layout(title_text='Monthly Water (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_w_2022.update_annotations(font=dict(family="Helvetica", size=10))
            fig_w_2022.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_w_2022.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_w_2022, use_container_width=True)
            # Table Dataframe
            if st.checkbox('Show Table Dataframes', key=2022):
                st.table(df_2022)
        
        with st.expander("Click to View Year 2021 Data:"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Cost:", f"RM{df_2021['e_cost'].sum():,.2f}")
            col2.metric("Water Cost:", f"RM{df_2021['w_cost'].sum():,.2f}")
            col3.metric("Streamyx Cost:", f"RM{df_2021['streamyx'].sum():,.2f}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Costs:", f"RM{(df_2021['e_cost'].sum()+df_2021['w_cost'].sum()+df_2021['streamyx'].sum()):,.2f}")
            col2.metric("Electricity Usage:", f"{df_2021['e_usage'].sum():,.0f}kWh")
            col3.metric("Water Usage:", f"{df_2021['w_usage'].sum():,.0f}m3")
            # Graph Yr 2021
            fig_2021 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_2021.add_trace(go.Bar(x = ['Electricity'], y = [df_2021['e_cost'].sum()],name=''))
            fig_2021.add_trace(go.Bar(x = ['Water'], y = [df_2021['w_cost'].sum()],name=''))
            fig_2021.add_trace(go.Bar(x = ['Streamyx'], y = [df_2021['streamyx'].sum()],name=''))
            fig_2021.update_layout(title_text='Total Utility Cost (RM)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_2021.update_annotations(font=dict(family="Helvetica", size=10))
            fig_2021.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_2021.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # PIE CHART
            fig_pie_2021 = make_subplots(specs=[[{"type": "domain"}]])
            fig_pie_2021.add_trace(go.Pie(
                values=[df_2021['e_cost'].sum(), df_2021['w_cost'].sum(), df_2021['streamyx'].sum()],
                labels=['Electricity','Water','Streamyx'],textposition='inside',textinfo='label+percent'),row=1, col=1)
            fig_pie_2021.update_annotations(font=dict(family="Helvetica", size=10))
            fig_pie_2021.update_layout(height=350,showlegend=False,title_text='Total Utility Cost (%)',title_x=0.5,font=dict(family="Helvetica", size=10))
            # Chart Presentation
            col1, col2 = st.columns(2)
            col1.plotly_chart(fig_2021, use_container_width=True)
            col2.plotly_chart(fig_pie_2021, use_container_width=True)
            # Cost VS Usage
            fig_e_2021 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_e_2021.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2021['e_cost'],name='RM'))
            fig_e_2021.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2021['e_cost'],name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_e_2021.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2021['e_usage'],name='kWh'))
            fig_e_2021.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2021['e_usage'],name='kWh',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_e_2021.update_layout(title_text='Monthly Electricity (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_e_2021.update_annotations(font=dict(family="Helvetica", size=10))
            fig_e_2021.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_e_2021.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_e_2021, use_container_width=True)
            # Cost VS Usage
            fig_w_2021 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_w_2021.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2021['w_cost'],name='RM'))
            fig_w_2021.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2021['w_cost'],name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_w_2021.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2021['w_usage'],name='m3'))
            fig_w_2021.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2021['w_usage'],name='m3',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_w_2021.update_layout(title_text='Monthly Water (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_w_2021.update_annotations(font=dict(family="Helvetica", size=10))
            fig_w_2021.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_w_2021.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_w_2021, use_container_width=True)
            # Table Dataframe
            if st.checkbox('Show Table Dataframes', key=2021):
                st.table(df_2021)
        
        with st.expander("Click to View Year 2020 Data:"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Cost:", f"RM{df_2020['e_cost'].sum():,.2f}")
            col2.metric("Water Cost:", f"RM{df_2020['w_cost'].sum():,.2f}")
            col3.metric("Streamyx Cost:", f"RM{df_2020['streamyx'].sum():,.2f}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Costs:", f"RM{(df_2020['e_cost'].sum()+df_2020['w_cost'].sum()+df_2020['streamyx'].sum()):,.2f}")
            col2.metric("Electricity Usage:", f"{df_2020['e_usage'].sum():,.0f}kWh")
            col3.metric("Water Usage:", f"{df_2020['w_usage'].sum():,.0f}m3")
            # Graph Yr 2020
            fig_2020 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_2020.add_trace(go.Bar(x = ['Electricity'], y = [df_2020['e_cost'].sum()],name=''))
            fig_2020.add_trace(go.Bar(x = ['Water'], y = [df_2020['w_cost'].sum()],name=''))
            fig_2020.add_trace(go.Bar(x = ['Streamyx'], y = [df_2020['streamyx'].sum()],name=''))
            fig_2020.update_layout(title_text='Total Utility Cost (RM)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_2020.update_annotations(font=dict(family="Helvetica", size=10))
            fig_2020.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_2020.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # PIE CHART
            fig_pie_2020 = make_subplots(specs=[[{"type": "domain"}]])
            fig_pie_2020.add_trace(go.Pie(
                values=[df_2020['e_cost'].sum(), df_2020['w_cost'].sum(), df_2020['streamyx'].sum()],
                labels=['Electricity','Water','Streamyx'],textposition='inside',textinfo='label+percent'),row=1, col=1)
            fig_pie_2020.update_annotations(font=dict(family="Helvetica", size=10))
            fig_pie_2020.update_layout(height=350,showlegend=False,title_text='Total Utility Cost (%)',title_x=0.5,font=dict(family="Helvetica", size=10))
            # Chart Presentation
            col1, col2 = st.columns(2)
            col1.plotly_chart(fig_2020, use_container_width=True)
            col2.plotly_chart(fig_pie_2020, use_container_width=True)
            # Cost VS Usage
            fig_e_2020 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_e_2020.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2020['e_cost'],name='RM'))
            fig_e_2020.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2020['e_cost'],name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_e_2020.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2020['e_usage'],name='kWh'))
            fig_e_2020.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2020['e_usage'],name='kWh',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_e_2020.update_layout(title_text='Monthly Electricity (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_e_2020.update_annotations(font=dict(family="Helvetica", size=10))
            fig_e_2020.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_e_2020.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_e_2020, use_container_width=True)
            # Cost VS Usage
            fig_w_2020 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_w_2020.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2020['w_cost'],name='RM'))
            fig_w_2020.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2020['w_cost'],name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_w_2020.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2020['w_usage'],name='m3'))
            fig_w_2020.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2020['w_usage'],name='m3',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_w_2020.update_layout(title_text='Monthly Water (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_w_2020.update_annotations(font=dict(family="Helvetica", size=10))
            fig_w_2020.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_w_2020.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_w_2020, use_container_width=True)
            # Table Dataframe
            if st.checkbox('Show Table Dataframes', key=2020):
                st.table(df_2020)
        
        with st.expander("Click to View Year 2019 Data:"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Cost:", f"RM{df_2019['e_cost'].sum():,.2f}")
            col2.metric("Water Cost:", f"RM{df_2019['w_cost'].sum():,.2f}")
            col3.metric("Total Costs:", f"RM{(df_2019['e_cost'].sum()+df_2019['w_cost'].sum()):,.2f}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Usage:", f"{df_2019['e_cost'].sum():,.0f}kWh")
            col2.metric("Water Usage:", f"{df_2019['w_usage'].sum():,.0f}m3")
            # Graph Yr 2019
            fig_2019 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_2019.add_trace(go.Bar(x = ['Electricity'], y = [df_2019['e_cost'].sum()],name=''))
            fig_2019.add_trace(go.Bar(x = ['Water'], y = [df_2019['w_cost'].sum()],name=''))
            fig_2019.update_layout(title_text='Total Utility Cost (RM)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_2019.update_annotations(font=dict(family="Helvetica", size=10))
            fig_2019.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_2019.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # PIE CHART
            fig_pie_2019 = make_subplots(specs=[[{"type": "domain"}]])
            fig_pie_2019.add_trace(go.Pie(
                values=[df_2019['e_cost'].sum(), df_2019['w_cost'].sum()],
                labels=['Electricity','Water'],textposition='inside',textinfo='label+percent'),row=1, col=1)
            fig_pie_2019.update_annotations(font=dict(family="Helvetica", size=10))
            fig_pie_2019.update_layout(height=350,showlegend=False,title_text='Total Utility Cost (%)',title_x=0.5,font=dict(family="Helvetica", size=10))
            # Chart Presentation
            col1, col2 = st.columns(2)
            col1.plotly_chart(fig_2019, use_container_width=True)
            col2.plotly_chart(fig_pie_2019, use_container_width=True)
            # Cost VS Usage
            fig_e_2019 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_e_2019.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2019['e_cost'],name='RM'))
            fig_e_2019.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2019['e_cost'],name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_e_2019.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2019['e_usage'],name='kWh'))
            fig_e_2019.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2019['e_usage'],name='kWh',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_e_2019.update_layout(title_text='Monthly Electricity (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_e_2019.update_annotations(font=dict(family="Helvetica", size=10))
            fig_e_2019.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_e_2019.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_e_2019, use_container_width=True)
            # Cost VS Usage
            fig_w_2019 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_w_2019.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2019['w_cost'],name='RM'))
            fig_w_2019.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2019['w_cost'],name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_w_2019.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2019['w_usage'],name='m3'))
            fig_w_2019.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2019['w_usage'],name='m3',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_w_2019.update_layout(title_text='Monthly Water (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_w_2019.update_annotations(font=dict(family="Helvetica", size=10))
            fig_w_2019.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_w_2019.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_w_2019, use_container_width=True)
            # Table Dataframe
            if st.checkbox('Show Table Dataframes', key=2019):
                st.table(df_2019)
            
        
        with st.expander("Click to View Year 2018 Data:"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Cost:", f"RM{df_2018['e_cost'].sum():,.2f}")
            col2.metric("Electricity Usage:", f"{df_2018['e_usage'].sum():,.0f}kWh")
            # Graph Yr 2018
            # Cost VS Usage
            fig_cost_2018 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_cost_2018.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2018['e_cost'],name='RM'))
            fig_cost_2018.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2018['e_cost'],name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2018.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2018['e_usage'],name='kWh'))
            fig_cost_2018.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2018['e_usage'],name='kWh',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2018.update_layout(title_text='Monthly Electricity (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_cost_2018.update_annotations(font=dict(family="Helvetica", size=10))
            fig_cost_2018.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_cost_2018.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_cost_2018, use_container_width=True)
            # Table Dataframe
            if st.checkbox('Show Table Dataframes', key=2018):
                st.table(df_2018)
        
        with st.expander("Click to View Year 2017 Data:"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Cost:", f"RM{df_2017['e_cost'].sum():,.2f}")
            col2.metric("Electricity Usage:", f"{df_2017['e_usage'].sum():,.0f}kWh")
            # Graph Yr 2017
            # Cost VS Usage
            fig_cost_2017 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_cost_2017.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2017['e_cost'],name='RM'))
            fig_cost_2017.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2017['e_cost'],name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2017.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2017['e_usage'],name='kWh'))
            fig_cost_2017.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2017['e_usage'],name='kWh',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2017.update_layout(title_text='Monthly Electricity Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_cost_2017.update_annotations(font=dict(family="Helvetica", size=10))
            fig_cost_2017.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_cost_2017.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_cost_2017, use_container_width=True)
            # Table Dataframe
            if st.checkbox('Show Table Dataframes', key=2017):
                st.table(df_2017)
        
        with st.expander("Click to View Year 2016 Data:"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Cost:", f"RM{df_2016['e_cost'].sum():,.2f}")
            col2.metric("Electricity Usage:", f"{df_2016['e_usage'].sum():,.0f}kWh")
            # Graph Yr 2016
            # Cost VS Usage
            fig_cost_2016 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_cost_2016.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2016['e_cost'],name='RM'))
            fig_cost_2016.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2016['e_cost'],name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2016.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2016['e_usage'],name='kWh'))
            fig_cost_2016.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2016['e_usage'],name='kWh',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2016.update_layout(title_text='Monthly Electricity (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_cost_2016.update_annotations(font=dict(family="Helvetica", size=10))
            fig_cost_2016.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_cost_2016.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_cost_2016, use_container_width=True)
            # Table Dataframe
            if st.checkbox('Show Table Dataframes', key=2016):
                st.table(df_2016)
        
        with st.expander("Click to View Year 2015 Data:"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Cost:", f"RM{df_2015['e_cost'].sum():,.2f}")
            col2.metric("Electricity Usage:", f"{df_2015['e_usage'].sum():,.0f}kWh")
            # Graph Yr 2015
            # Cost VS Usage
            fig_cost_2015 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_cost_2015.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2015['e_cost'],name='RM'))
            fig_cost_2015.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2015['e_cost'],name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2015.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2015['e_usage'],name='kWH'))
            fig_cost_2015.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2015['e_usage'],name='kWH',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2015.update_layout(title_text='Monthly Electricity (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_cost_2015.update_annotations(font=dict(family="Helvetica", size=10))
            fig_cost_2015.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_cost_2015.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_cost_2015, use_container_width=True)
            # Table Dataframe
            if st.checkbox('Show Table Dataframes', key=2015):
                st.table(df_2015)
        
        with st.expander("Click to View Year 2014 Data:"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Cost:", f"RM{df_2014['e_cost'].sum():,.2f}")
            col2.metric("Electricity Usage:", f"{df_2014['e_usage'].sum():,.0f}kWh")
            # Graph Yr 2014
            # Cost VS Usage
            fig_cost_2014 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_cost_2014.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2014['e_cost'],name='RM'))
            fig_cost_2014.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2014['e_cost'],name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2014.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2014['e_usage'],name='kWh'))
            fig_cost_2014.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_2014['e_usage'],name='kWh',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2014.update_layout(title_text='Monthly Electricity (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_cost_2014.update_annotations(font=dict(family="Helvetica", size=10))
            fig_cost_2014.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_cost_2014.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_cost_2014, use_container_width=True)
            # Table Dataframe
            if st.checkbox('Show Table Dataframes', key=2014):
                st.table(df_2014)
                
    # --- DATA ENTRY ---
    if selected == "Data Entry":
        st.header(f"Monthly Data Entry:")
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            col1.selectbox("Select Month:", months, key="month")
            col2.selectbox("Select Year:", years, key="year")

            "---"
            col1, col2 = st.columns(2)
            with col1:
                st.write('Electricity:')
            with col1:
                for e_usage in e_usages:
                    st.number_input(f"{e_usage}:", min_value=0, format="%i", step=10, key=e_usage)
            with col1:
                for e_cost in e_costs:
                    st.number_input(f"{e_cost}:", min_value=0.0, max_value=10000.0, step=1e-3, format="%.2f", key=e_cost)
            with col2:
                st.write('Water:')
            with col2:
                for w_usage in w_usages:
                    st.number_input(f"{w_usage}:", min_value=0, format="%i", step=10, key=w_usage)
            with col2:
                for w_cost in w_costs:
                    st.number_input(f"{w_cost}:", min_value=0.0, max_value=10000.0, step=1e-3, format="%.2f", key=w_cost)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write('Telco:')
            with col1:
                for digi_zahir in digi_zahirs:
                    st.number_input(f"{digi_zahir}:", min_value=0.0, max_value=10000.0, step=1e-3, format="%.2f", key=digi_zahir)
            with col1:
                for digi_ani in digi_anis:
                    st.number_input(f"{digi_ani}:", min_value=0.0, max_value=10000.0, step=1e-3, format="%.2f", key=digi_ani)
            with col1:
                for streamyx in streamyxs:
                    st.number_input(f"{streamyx}:", min_value=0.0, max_value=10000.0, step=1e-3, format="%.2f", key=streamyx)
            with col2:
                st.write('Comments:')
            with col2:
                comment = st.text_area("", placeholder="Enter a comment here ...")

            "---"
            submitted = st.form_submit_button("Save Data")
            if submitted:
                period = str(st.session_state["year"]) + "_" + str(st.session_state["month"])
                e_usages = {e_usage: st.session_state[e_usage] for e_usage in e_usages}
                e_costs = {e_cost: st.session_state[e_cost] for e_cost in e_costs}
                w_usages = {w_usage: st.session_state[w_usage] for w_usage in w_usages}
                w_costs = {w_cost: st.session_state[w_cost] for w_cost in w_costs}
                digi_zahirs = {digi_zahir: st.session_state[digi_zahir] for digi_zahir in digi_zahirs}
                digi_anis = {digi_ani: st.session_state[digi_ani] for digi_ani in digi_anis}
                streamyxs = {streamyx: st.session_state[streamyx] for streamyx in streamyxs}
                insert_period(period, e_usages, e_costs, w_usages, w_costs, digi_zahirs, digi_anis, streamyxs, comment)
                st.success("Data saved!")

    # --- DATA QUERY ---
    if selected == "Data Query":
        st.header("Data Query")
        with st.form("saved_periods"):
            period = st.selectbox("Select Period:", get_all_periods())
            submitted = st.form_submit_button("Click:")
            if submitted:
                # Get data from database
                period_data = get_period(period)
                # Create metrics
                month_e_costs = sum(period_data.get("e_cost").values())
                month_e_usages = sum(period_data.get("e_usage").values())
                month_w_costs = sum(period_data.get("w_cost").values())
                month_w_usages = sum(period_data.get("w_usage").values())
                month_digi_zahirs = sum(period_data.get("digi_zahir").values())
                month_digi_anis = sum(period_data.get("digi_ani").values())
                month_streamyx = sum(period_data.get("streamyx").values())
                comment = period_data.get("comment")

                total_monthly = month_e_costs + month_w_costs + month_digi_zahirs + month_digi_anis + month_streamyx

                col1, col2, col3 = st.columns(3)
                col1.metric("Electricity Cost:", f"{'RM'}{month_e_costs:,.2f}")
                col2.metric("Water Cost:", f"{'RM'}{month_w_costs:,.2f}")
                col3.metric("Streamyx Cost:", f"{'RM'}{month_streamyx:,.2f}")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("DiGi Zahir Cost:", f"{'RM'}{month_digi_zahirs:,.2f}")
                col2.metric("DiGi Ani Cost:", f"{'RM'}{month_digi_anis:,.2f}")
                col3.metric("Total Costs", f"{'RM'}{total_monthly:,.2f}")

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Electricity Usage", f"{month_e_usages:,.0f}{'kWh'}")
                col2.metric("Total Water Usage", f"{month_w_usages:,.0f}{'m3'}")
                st.text(f"Comment: {comment}")
