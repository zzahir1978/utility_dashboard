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
    # Year 2022
    df_2022 = df[(df['key'] >= "2022-01-01") & (df['key'] <="2022-12-01")]
    df_2022 = df_2022.sort_values(by='key')
    df_ecost_2022 = df_2022['e_cost'].map(Counter).groupby(df_2022['key']).sum().reset_index()
    df_ecost_2022 = df_ecost_2022['e_cost'].apply(lambda x: x.get('RM_e')).dropna()
    df_wcost_2022 = df_2022['w_cost'].map(Counter).groupby(df_2022['key']).sum().reset_index()
    df_wcost_2022 = df_wcost_2022['w_cost'].apply(lambda x: x.get('RM_w')).dropna()
    df_eusage_2022 = df_2022['e_usage'].map(Counter).groupby(df_2022['key']).sum().reset_index()
    df_eusage_2022 = df_eusage_2022['e_usage'].apply(lambda x: x.get('kWh')).dropna()
    df_wusage_2022 = df_2022['w_usage'].map(Counter).groupby(df_2022['key']).sum().reset_index()
    df_wusage_2022 = df_wusage_2022['w_usage'].apply(lambda x: x.get('m3')).dropna()
    df_digi_zahir_2022 = df_2022['digi_zahir'].map(Counter).groupby(df_2022['key']).sum().reset_index()
    df_digi_zahir_2022 = df_digi_zahir_2022['digi_zahir'].apply(lambda x: x.get('RM_d1')).dropna()
    df_digi_ani_2022 = df_2022['digi_ani'].map(Counter).groupby(df_2022['key']).sum().reset_index()
    df_digi_ani_2022 = df_digi_ani_2022['digi_ani'].apply(lambda x: x.get('RM_d2')).dropna()
    df_streamyx_2022 = df_2022['streamyx'].map(Counter).groupby(df_2022['key']).sum().reset_index()
    df_streamyx_2022 = df_streamyx_2022['streamyx'].apply(lambda x: x.get('RM_s')).dropna()
    # Year 2021
    df_2021 = df[(df['key'] >= "2021-01-01") & (df['key'] <="2021-12-01")]
    df_2021 = df_2021.sort_values(by='key')
    df_ecost_2021 = df_2021['e_cost'].map(Counter).groupby(df_2021['key']).sum().reset_index()
    df_ecost_2021 = df_ecost_2021['e_cost'].apply(lambda x: x.get('RM_e')).dropna()
    df_wcost_2021 = df_2021['w_cost'].map(Counter).groupby(df_2021['key']).sum().reset_index()
    df_wcost_2021 = df_wcost_2021['w_cost'].apply(lambda x: x.get('RM_w')).dropna()
    df_eusage_2021 = df_2021['e_usage'].map(Counter).groupby(df_2021['key']).sum().reset_index()
    df_eusage_2021 = df_eusage_2021['e_usage'].apply(lambda x: x.get('kWh')).dropna()
    df_wusage_2021 = df_2021['w_usage'].map(Counter).groupby(df_2021['key']).sum().reset_index()
    df_wusage_2021 = df_wusage_2021['w_usage'].apply(lambda x: x.get('m3')).dropna()
    df_streamyx_2021 = df_2021['streamyx'].map(Counter).groupby(df_2021['key']).sum().reset_index()
    df_streamyx_2021 = df_streamyx_2021['streamyx'].apply(lambda x: x.get('RM_s')).dropna()
    # Year 2020
    df_2020 = df[(df['key'] >= "2020-01-01") & (df['key'] <="2020-12-01")]
    df_2020 = df_2020.sort_values(by='key')
    df_ecost_2020 = df_2020['e_cost'].map(Counter).groupby(df_2020['key']).sum().reset_index()
    df_ecost_2020 = df_ecost_2020['e_cost'].apply(lambda x: x.get('RM_e')).dropna()
    df_wcost_2020 = df_2020['w_cost'].map(Counter).groupby(df_2020['key']).sum().reset_index()
    df_wcost_2020 = df_wcost_2020['w_cost'].apply(lambda x: x.get('RM_w')).dropna()
    df_eusage_2020 = df_2020['e_usage'].map(Counter).groupby(df_2020['key']).sum().reset_index()
    df_eusage_2020 = df_eusage_2020['e_usage'].apply(lambda x: x.get('kWh')).dropna()
    df_wusage_2020 = df_2020['w_usage'].map(Counter).groupby(df_2020['key']).sum().reset_index()
    df_wusage_2020 = df_wusage_2020['w_usage'].apply(lambda x: x.get('m3')).dropna()
    df_streamyx_2020 = df_2020['streamyx'].map(Counter).groupby(df_2020['key']).sum().reset_index()
    df_streamyx_2020 = df_streamyx_2020['streamyx'].apply(lambda x: x.get('RM_s')).dropna()
    # Year 2019
    df_2019 = df[(df['key'] >= "2019-01-01") & (df['key'] <="2019-12-01")]
    df_2019 = df_2019.sort_values(by='key')
    df_ecost_2019 = df_2019['e_cost'].map(Counter).groupby(df_2019['key']).sum().reset_index()
    df_ecost_2019 = df_ecost_2019['e_cost'].apply(lambda x: x.get('RM_e')).dropna()
    df_wcost_2019 = df_2019['w_cost'].map(Counter).groupby(df_2019['key']).sum().reset_index()
    df_wcost_2019 = df_wcost_2019['w_cost'].apply(lambda x: x.get('RM_w')).dropna()
    df_eusage_2019 = df_2019['e_usage'].map(Counter).groupby(df_2019['key']).sum().reset_index()
    df_eusage_2019 = df_eusage_2019['e_usage'].apply(lambda x: x.get('kWh')).dropna()
    df_wusage_2019 = df_2019['w_usage'].map(Counter).groupby(df_2019['key']).sum().reset_index()
    df_wusage_2019 = df_wusage_2019['w_usage'].apply(lambda x: x.get('m3')).dropna()
    # Year 2018
    df_2018 = df[(df['key'] >= "2018-01-01") & (df['key'] <="2018-12-01")]
    df_2018 = df_2018.sort_values(by='key')
    df_ecost_2018 = df_2018['e_cost'].map(Counter).groupby(df_2018['key']).sum().reset_index()
    df_ecost_2018 = df_ecost_2018['e_cost'].apply(lambda x: x.get('RM_e')).dropna()
    df_eusage_2018 = df_2018['e_usage'].map(Counter).groupby(df_2018['key']).sum().reset_index()
    df_eusage_2018 = df_eusage_2018['e_usage'].apply(lambda x: x.get('kWh')).dropna()
    # Year 2017
    df_2017 = df[(df['key'] >= "2017-01-01") & (df['key'] <="2017-12-01")]
    df_2017 = df_2017.sort_values(by='key')
    df_ecost_2017 = df_2017['e_cost'].map(Counter).groupby(df_2017['key']).sum().reset_index()
    df_ecost_2017 = df_ecost_2017['e_cost'].apply(lambda x: x.get('RM_e')).dropna()
    df_eusage_2017 = df_2017['e_usage'].map(Counter).groupby(df_2017['key']).sum().reset_index()
    df_eusage_2017 = df_eusage_2017['e_usage'].apply(lambda x: x.get('kWh')).dropna()
    # Year 2016
    df_2016 = df[(df['key'] >= "2016-01-01") & (df['key'] <="2016-12-01")]
    df_2016 = df_2016.sort_values(by='key')
    df_ecost_2016 = df_2016['e_cost'].map(Counter).groupby(df_2016['key']).sum().reset_index()
    df_ecost_2016 = df_ecost_2016['e_cost'].apply(lambda x: x.get('RM_e')).dropna()
    df_eusage_2016 = df_2016['e_usage'].map(Counter).groupby(df_2016['key']).sum().reset_index()
    df_eusage_2016 = df_eusage_2016['e_usage'].apply(lambda x: x.get('kWh')).dropna()
    # Year 2015
    df_2015 = df[(df['key'] >= "2015-01-01") & (df['key'] <="2015-12-01")]
    df_2015 = df_2015.sort_values(by='key')
    df_ecost_2015 = df_2015['e_cost'].map(Counter).groupby(df_2015['key']).sum().reset_index()
    df_ecost_2015 = df_ecost_2015['e_cost'].apply(lambda x: x.get('RM_e')).dropna()
    df_eusage_2015 = df_2015['e_usage'].map(Counter).groupby(df_2015['key']).sum().reset_index()
    df_eusage_2015 = df_eusage_2015['e_usage'].apply(lambda x: x.get('kWh')).dropna()
    # Year 2014
    df_2014 = df[(df['key'] >= "2014-01-01") & (df['key'] <="2014-12-01")]
    df_2014 = df_2014.sort_values(by='key')
    df_ecost_2014 = df_2014['e_cost'].map(Counter).groupby(df_2014['key']).sum().reset_index()
    df_ecost_2014 = df_ecost_2014['e_cost'].apply(lambda x: x.get('RM_e')).dropna()
    df_eusage_2014 = df_2014['e_usage'].map(Counter).groupby(df_2014['key']).sum().reset_index()
    df_eusage_2014 = df_eusage_2014['e_usage'].apply(lambda x: x.get('kWh')).dropna()
    
    
    # --- DATA ENTRY ---
    if selected == "Data Entry":
        st.header(f"Monthly Data Entry:")
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            col1.selectbox("Select Month:", months, key="month")
            col2.selectbox("Select Year:", years, key="year")

            "---"
            with st.expander("Electricity Usage"):
                for e_usage in e_usages:
                    st.number_input(f"{e_usage}:", min_value=0, format="%i", step=10, key=e_usage)
            with st.expander("Electricity Cost"):
                for e_cost in e_costs:
                    st.number_input(f"{e_cost}:", min_value=0, format="%i", step=10, key=e_cost)
            
            with st.expander("Water Usage"):
                for w_usage in w_usages:
                    st.number_input(f"{w_usage}:", min_value=0, format="%i", step=10, key=w_usage)
            with st.expander("Water Cost"):
                for w_cost in w_costs:
                    st.number_input(f"{w_cost}:", min_value=0, format="%i", step=10, key=w_cost)
            
            with st.expander("DiGi Zahir Cost"):
                for digi_zahir in digi_zahirs:
                    st.number_input(f"{digi_zahir}:", min_value=0, format="%i", step=10, key=digi_zahir)
            with st.expander("DiGi Ani Cost"):
                for digi_ani in digi_anis:
                    st.number_input(f"{digi_ani}:", min_value=0, format="%i", step=10, key=digi_ani)
            with st.expander("Streamyx Cost"):
                for streamyx in streamyxs:
                    st.number_input(f"{streamyx}:", min_value=0, format="%i", step=10, key=streamyx)

            with st.expander("Comment"):
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

    # --- DATA VISUALISATION ---
    if selected == "Data Overview":
        st.header("Summary")
        
        entries = fetch_all_periods()

        total_e_usage = sum([sum(entry['e_usage'].values()) for entry in entries])
        total_e_cost = sum([sum(entry['e_cost'].values()) for entry in entries])
        total_w_usage = sum([sum(entry['w_usage'].values()) for entry in entries])
        total_w_cost = sum([sum(entry['w_cost'].values()) for entry in entries])
        total_digi_zahir_cost = sum([sum(entry['digi_zahir'].values()) for entry in entries])
        total_digi_ani_cost = sum([sum(entry['digi_ani'].values()) for entry in entries])
        total_streamyx_cost = sum([sum(entry['streamyx'].values()) for entry in entries])
        total_telcos = total_digi_zahir_cost + total_digi_ani_cost + total_streamyx_cost
        total_cost = total_e_cost + total_w_cost + total_digi_zahir_cost + total_digi_ani_cost + total_streamyx_cost
        e_rate = total_e_cost/total_e_usage
        w_rate = total_w_cost/total_w_usage

        st.subheader("Total Cost:")
        col1, col2, col3 = st.columns(3)
        col1.metric("Electricity Cost:", f"RM{total_e_cost:,.2f}")
        col2.metric("Water Cost:", f"RM{total_w_cost:,.2f}")
        col3.metric("Telco Cost:", f"RM{(total_digi_zahir_cost+total_digi_ani_cost+total_streamyx_cost):,.2f}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Costs:", f"RM{total_cost:,.2f}")

        st.subheader("Total Usage:")
        col1, col2, col3 = st.columns(3)
        col1.metric("Electricity Usage:", f"{total_e_usage:,.0f}kWh")
        col2.metric("Water Usage:", f"{total_w_usage:,.0f}m3")
        
        st.subheader("Graphs:")
        # BAR CHART
        fig_1 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
        fig_1.add_trace(go.Bar(x = ['Electricity'], y = [total_e_cost],name=''))
        fig_1.add_trace(go.Bar(x = ['Water'], y = [total_w_cost],name=''))
        fig_1.add_trace(go.Bar(x = ['DiGi Zahir'], y = [total_digi_zahir_cost],name=''))
        fig_1.add_trace(go.Bar(x = ['DiGi Ani'], y = [total_digi_ani_cost],name=''))
        fig_1.add_trace(go.Bar(x = ['Streamyx'], y = [total_streamyx_cost],name=''))
        fig_1.update_layout(title_text='Total Utilities Cost (RM)',title_x=0.5, height=350,
            font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",
            yaxis=(dict(showgrid=False)),yaxis_title=None,showlegend=False)
        fig_1.update_annotations(font=dict(family="Helvetica", size=10))
        fig_1.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
        fig_1.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
        # PIE CHART
        fig_pie_main = make_subplots(specs=[[{"type": "domain"}]])
        fig_pie_main.add_trace(go.Pie(
            values=[total_e_cost,total_w_cost,total_digi_zahir_cost,total_digi_ani_cost,total_streamyx_cost],
            labels=['Electricity','Water','DiGi Zahir','Digi Ani','Streamyx'],textposition='inside',textinfo='label+percent'),row=1, col=1)
        fig_pie_main.update_annotations(font=dict(family="Helvetica", size=10))
        fig_pie_main.update_layout(height=350,showlegend=False,title_text='Total Utility Cost (%)',title_x=0.5,font=dict(family="Helvetica", size=10))
        # Chart Presentation
        col1, col2 = st.columns(2)
        col1.plotly_chart(fig_1, use_container_width=True)
        col2.plotly_chart(fig_pie_main, use_container_width=True)

        with st.expander("Utilities Rates:"):
            col1, col2 = st.columns(2)
            col1.metric("Electricity Rate:", f"RM{(total_e_cost/total_e_usage):,.2f}")
            col2.metric("Water Rate:", f"RM{(total_w_cost/total_w_usage):,.2f}")
        
        st.subheader("Annual Data By Type of Utility:")

        with st.expander("Electricity:"):
            # Graph Electricity Cost VS Usage
            fig_yearly_e = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_yearly_e.add_trace(go.Bar(x = ['2014','2015','2016','2017','2018','2019','2020','2021','2022'], 
                y = [df_ecost_2014.sum(),df_ecost_2015.sum(),df_ecost_2016.sum(),df_ecost_2017.sum(),df_ecost_2018.sum(),df_ecost_2019.sum(),
                    df_ecost_2020.sum(),df_ecost_2021.sum(),df_ecost_2022.sum()],name='RM'))
            fig_yearly_e.add_trace(go.Scatter(x = ['2014','2015','2016','2017','2018','2019','2020','2021','2022'], 
                y = [df_ecost_2014.sum(),df_ecost_2015.sum(),df_ecost_2016.sum(),df_ecost_2017.sum(),df_ecost_2018.sum(),df_ecost_2019.sum(),
                    df_ecost_2020.sum(),df_ecost_2021.sum(),df_ecost_2022.sum()],name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_yearly_e.add_trace(go.Bar(x = ['2014','2015','2016','2017','2018','2019','2020','2021','2022'], 
                y = [df_eusage_2014.sum(),df_eusage_2015.sum(),df_eusage_2016.sum(),df_eusage_2017.sum(),df_eusage_2018.sum(),df_eusage_2019.sum(),
                    df_eusage_2020.sum(),df_eusage_2021.sum(),df_eusage_2022.sum()],name='kWh'))
            fig_yearly_e.add_trace(go.Scatter(x = ['2014','2015','2016','2017','2018','2019','2020','2021','2022'], 
                y = [df_eusage_2014.sum(),df_eusage_2015.sum(),df_eusage_2016.sum(),df_eusage_2017.sum(),df_eusage_2018.sum(),df_eusage_2019.sum(),
                    df_eusage_2020.sum(),df_eusage_2021.sum(),df_eusage_2022.sum()],name='kWh',
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
                values=[df_ecost_2014.sum(),df_ecost_2015.sum(),df_ecost_2016.sum(),df_ecost_2017.sum(),df_ecost_2018.sum(),df_ecost_2019.sum(),
                        df_ecost_2020.sum(),df_ecost_2021.sum(),df_ecost_2022.sum()],
                labels=['2014','2015','2016','2017','2018','2019','2020','2021','2022'],textposition='inside',textinfo='label+percent'),row=1, col=1)
            fig_pie_yearly_ecost.update_annotations(font=dict(family="Helvetica", size=10))
            fig_pie_yearly_ecost.update_layout(height=350,showlegend=False,title_text='Annual Electricity Cost (%)',title_x=0.5,font=dict(family="Helvetica", size=10))            
            # PIE CHART Usage
            fig_pie_yearly_eusage = make_subplots(specs=[[{"type": "domain"}]])
            fig_pie_yearly_eusage.add_trace(go.Pie(
                values=[df_eusage_2014.sum(),df_eusage_2015.sum(),df_eusage_2016.sum(),df_eusage_2017.sum(),df_eusage_2018.sum(),df_eusage_2019.sum(),
                        df_eusage_2020.sum(),df_eusage_2021.sum(),df_eusage_2022.sum()],
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
                y = [df_wcost_2019.sum(),df_wcost_2020.sum(),df_wcost_2021.sum(),df_wcost_2022.sum()],name='RM'))
            fig_yearly_w.add_trace(go.Scatter(x = ['2019','2020','2021','2022'], 
                y = [df_wcost_2019.sum(),df_wcost_2020.sum(),df_wcost_2021.sum(),df_wcost_2022.sum()],name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_yearly_w.add_trace(go.Bar(x = ['2019','2020','2021','2022'], 
                y = [df_wusage_2019.sum(),df_wusage_2020.sum(),df_wusage_2021.sum(),df_wusage_2022.sum()],name='m3'))
            fig_yearly_w.add_trace(go.Scatter(x = ['2019','2020','2021','2022'], 
                y = [df_wusage_2019.sum(),df_wusage_2020.sum(),df_wusage_2021.sum(),df_wusage_2022.sum()],name='m3',
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
                values=[df_wcost_2019.sum(),df_wcost_2020.sum(),df_wcost_2021.sum(),df_wcost_2022.sum()],
                labels=['2019','2020','2021','2022'],textposition='inside',textinfo='label+percent'),row=1, col=1)
            fig_pie_yearly_wcost.update_annotations(font=dict(family="Helvetica", size=10))
            fig_pie_yearly_wcost.update_layout(height=350,showlegend=False,title_text='Annual Water Cost (%)',title_x=0.5,font=dict(family="Helvetica", size=10))
            # PIE CHART Usage
            fig_pie_yearly_wusage = make_subplots(specs=[[{"type": "domain"}]])
            fig_pie_yearly_wusage.add_trace(go.Pie(
                values=[df_wusage_2019.sum(),df_wusage_2020.sum(),df_wusage_2021.sum(),df_wusage_2022.sum()],
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
            col1.metric("Total Costs:",f"RM{(df_ecost_2022.sum()+df_wcost_2022.sum()+df_digi_zahir_2022.sum()+df_digi_ani_2022.sum()+df_streamyx_2022.sum()):,.2f}")
            col2.metric("Electricity Cost:", f"RM{df_ecost_2022.sum():,.2f}")
            col3.metric("Water Cost:", f"RM{df_wcost_2022.sum():,.2f}")
            col1, col2, col3 = st.columns(3)
            col1.metric("DiGi Zahir Cost:", f"RM{df_digi_zahir_2022.sum():,.2f}")
            col2.metric("DiGi Ani Cost:", f"RM{df_digi_ani_2022.sum():,.2f}")
            col3.metric("Streamyx Cost:", f"RM{df_streamyx_2022.sum():,.2f}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Usage:", f"{df_eusage_2022.sum():,.0f}kWh")
            col2.metric("Water Usage:", f"{df_wusage_2022.sum():,.0f}m3")
            # Graph Yr 2022
            fig_2022 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_2022.add_trace(go.Bar(x = ['Electricity'], y = [df_ecost_2022.sum()],name=''))
            fig_2022.add_trace(go.Bar(x = ['Water'], y = [df_wcost_2022.sum()],name=''))
            fig_2022.add_trace(go.Bar(x = ['DiGi Zahir'], y = [df_digi_zahir_2022.sum()],name=''))
            fig_2022.add_trace(go.Bar(x = ['DiGi Ani'], y = [df_digi_ani_2022.sum()],name=''))
            fig_2022.add_trace(go.Bar(x = ['Streamyx'], y = [df_streamyx_2022.sum()],name=''))
            fig_2022.update_layout(title_text='Total Utility Cost (RM)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_2022.update_annotations(font=dict(family="Helvetica", size=10))
            fig_2022.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_2022.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # PIE CHART
            fig_pie_2022 = make_subplots(specs=[[{"type": "domain"}]])
            fig_pie_2022.add_trace(go.Pie(
                values=[df_ecost_2022.sum(), df_wcost_2022.sum(), df_digi_zahir_2022.sum(), df_digi_ani_2022.sum(), df_streamyx_2022.sum()],
                labels=['Electricity','Water','DiGi Zahir','Digi Ani','Streamyx'],textposition='inside',textinfo='label+percent'),row=1, col=1)
            fig_pie_2022.update_annotations(font=dict(family="Helvetica", size=10))
            fig_pie_2022.update_layout(height=350,showlegend=False,title_text='Total Utility Cost (%)',title_x=0.5,font=dict(family="Helvetica", size=10))
            # Chart Presentation
            col1, col2 = st.columns(2)
            col1.plotly_chart(fig_2022, use_container_width=True)
            col2.plotly_chart(fig_pie_2022, use_container_width=True)
            # Cost VS Usage
            fig_e_2022 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_e_2022.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2022,name='RM'))
            fig_e_2022.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2022,name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_e_2022.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2022,name='kWh'))
            fig_e_2022.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2022,name='kWh',
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
            fig_w_2022.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_wcost_2022,name='RM'))
            fig_w_2022.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_wcost_2022,name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_w_2022.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_wusage_2022,name='m3'))
            fig_w_2022.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_wusage_2022,name='m3',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_w_2022.update_layout(title_text='Monthly Water (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_w_2022.update_annotations(font=dict(family="Helvetica", size=10))
            fig_w_2022.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_w_2022.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_w_2022, use_container_width=True)
        
        with st.expander("Click to View Year 2021 Data:"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Cost:", f"RM{df_ecost_2021.sum():,.2f}")
            col2.metric("Water Cost:", f"RM{df_wcost_2021.sum():,.2f}")
            col3.metric("Streamyx Cost:", f"RM{df_streamyx_2021.sum():,.2f}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Costs:", f"RM{(df_ecost_2021.sum()+df_wcost_2021.sum()+df_streamyx_2021.sum()):,.2f}")
            col2.metric("Electricity Usage:", f"{df_eusage_2021.sum():,.0f}kWh")
            col3.metric("Water Usage:", f"{df_wusage_2021.sum():,.0f}m3")
            # Graph Yr 2021
            fig_2021 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_2021.add_trace(go.Bar(x = ['Electricity'], y = [df_ecost_2021.sum()],name=''))
            fig_2021.add_trace(go.Bar(x = ['Water'], y = [df_wcost_2021.sum()],name=''))
            fig_2021.add_trace(go.Bar(x = ['Streamyx'], y = [df_streamyx_2021.sum()],name=''))
            fig_2021.update_layout(title_text='Total Utility Cost (RM)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_2021.update_annotations(font=dict(family="Helvetica", size=10))
            fig_2021.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_2021.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # PIE CHART
            fig_pie_2021 = make_subplots(specs=[[{"type": "domain"}]])
            fig_pie_2021.add_trace(go.Pie(
                values=[df_ecost_2021.sum(), df_wcost_2021.sum(), df_streamyx_2021.sum()],
                labels=['Electricity','Water','Streamyx'],textposition='inside',textinfo='label+percent'),row=1, col=1)
            fig_pie_2021.update_annotations(font=dict(family="Helvetica", size=10))
            fig_pie_2021.update_layout(height=350,showlegend=False,title_text='Total Utility Cost (%)',title_x=0.5,font=dict(family="Helvetica", size=10))
            # Chart Presentation
            col1, col2 = st.columns(2)
            col1.plotly_chart(fig_2021, use_container_width=True)
            col2.plotly_chart(fig_pie_2021, use_container_width=True)
            # Cost VS Usage
            fig_e_2021 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_e_2021.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2021,name='RM'))
            fig_e_2021.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2021,name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_e_2021.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2021,name='kWh'))
            fig_e_2021.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2021,name='kWh',
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
            fig_w_2021.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_wcost_2021,name='RM'))
            fig_w_2021.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_wcost_2021,name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_w_2021.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_wusage_2021,name='m3'))
            fig_w_2021.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_wusage_2021,name='m3',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_w_2021.update_layout(title_text='Monthly Water (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_w_2021.update_annotations(font=dict(family="Helvetica", size=10))
            fig_w_2021.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_w_2021.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_w_2021, use_container_width=True)
        
        with st.expander("Click to View Year 2020 Data:"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Cost:", f"RM{df_ecost_2020.sum():,.2f}")
            col2.metric("Water Cost:", f"RM{df_wcost_2020.sum():,.2f}")
            col3.metric("Streamyx Cost:", f"RM{df_streamyx_2020.sum():,.2f}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Costs:", f"RM{(df_ecost_2020.sum()+df_wcost_2020.sum()+df_streamyx_2020.sum()):,.2f}")
            col2.metric("Electricity Usage:", f"{df_eusage_2020.sum():,.0f}kWh")
            col3.metric("Water Usage:", f"{df_wusage_2020.sum():,.0f}m3")
            # Graph Yr 2020
            fig_2020 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_2020.add_trace(go.Bar(x = ['Electricity'], y = [df_ecost_2020.sum()],name=''))
            fig_2020.add_trace(go.Bar(x = ['Water'], y = [df_wcost_2020.sum()],name=''))
            fig_2020.add_trace(go.Bar(x = ['Streamyx'], y = [df_streamyx_2020.sum()],name=''))
            fig_2020.update_layout(title_text='Total Utility Cost (RM)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_2020.update_annotations(font=dict(family="Helvetica", size=10))
            fig_2020.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_2020.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # PIE CHART
            fig_pie_2020 = make_subplots(specs=[[{"type": "domain"}]])
            fig_pie_2020.add_trace(go.Pie(
                values=[df_ecost_2020.sum(), df_wcost_2020.sum(), df_streamyx_2020.sum()],
                labels=['Electricity','Water','Streamyx'],textposition='inside',textinfo='label+percent'),row=1, col=1)
            fig_pie_2020.update_annotations(font=dict(family="Helvetica", size=10))
            fig_pie_2020.update_layout(height=350,showlegend=False,title_text='Total Utility Cost (%)',title_x=0.5,font=dict(family="Helvetica", size=10))
            # Chart Presentation
            col1, col2 = st.columns(2)
            col1.plotly_chart(fig_2020, use_container_width=True)
            col2.plotly_chart(fig_pie_2020, use_container_width=True)
            # Cost VS Usage
            fig_e_2020 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_e_2020.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2020,name='RM'))
            fig_e_2020.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2020,name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_e_2020.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2020,name='kWh'))
            fig_e_2020.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2020,name='kWh',
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
            fig_w_2020.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_wcost_2020,name='RM'))
            fig_w_2020.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_wcost_2020,name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_w_2020.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_wusage_2020,name='m3'))
            fig_w_2020.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_wusage_2020,name='m3',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_w_2020.update_layout(title_text='Monthly Water (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_w_2020.update_annotations(font=dict(family="Helvetica", size=10))
            fig_w_2020.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_w_2020.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_w_2020, use_container_width=True)
        
        with st.expander("Click to View Year 2019 Data:"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Cost:", f"RM{df_ecost_2019.sum():,.2f}")
            col2.metric("Water Cost:", f"RM{df_wcost_2019.sum():,.2f}")
            col3.metric("Total Costs:", f"RM{(df_ecost_2019.sum()+df_wcost_2019.sum()):,.2f}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Usage:", f"{df_ecost_2019.sum():,.0f}kWh")
            col2.metric("Water Usage:", f"{df_wusage_2019.sum():,.0f}m3")
            # Graph Yr 2019
            fig_2019 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_2019.add_trace(go.Bar(x = ['Electricity'], y = [df_ecost_2019.sum()],name=''))
            fig_2019.add_trace(go.Bar(x = ['Water'], y = [df_wcost_2019.sum()],name=''))
            fig_2019.update_layout(title_text='Total Utility Cost (RM)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_2019.update_annotations(font=dict(family="Helvetica", size=10))
            fig_2019.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_2019.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # PIE CHART
            fig_pie_2019 = make_subplots(specs=[[{"type": "domain"}]])
            fig_pie_2019.add_trace(go.Pie(
                values=[df_ecost_2019.sum(), df_wcost_2019.sum()],
                labels=['Electricity','Water'],textposition='inside',textinfo='label+percent'),row=1, col=1)
            fig_pie_2019.update_annotations(font=dict(family="Helvetica", size=10))
            fig_pie_2019.update_layout(height=350,showlegend=False,title_text='Total Utility Cost (%)',title_x=0.5,font=dict(family="Helvetica", size=10))
            # Chart Presentation
            col1, col2 = st.columns(2)
            col1.plotly_chart(fig_2019, use_container_width=True)
            col2.plotly_chart(fig_pie_2019, use_container_width=True)
            # Cost VS Usage
            fig_e_2019 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_e_2019.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2019,name='RM'))
            fig_e_2019.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2019,name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_e_2019.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2019,name='kWh'))
            fig_e_2019.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2019,name='kWh',
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
            fig_w_2019.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_wcost_2019,name='RM'))
            fig_w_2019.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_wcost_2019,name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_w_2019.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_wusage_2019,name='m3'))
            fig_w_2019.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_wusage_2019,name='m3',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_w_2019.update_layout(title_text='Monthly Water (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_w_2019.update_annotations(font=dict(family="Helvetica", size=10))
            fig_w_2019.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_w_2019.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_w_2019, use_container_width=True)
            
        
        with st.expander("Click to View Year 2018 Data:"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Cost:", f"RM{df_ecost_2018.sum():,.2f}")
            col2.metric("Electricity Usage:", f"{df_eusage_2018.sum():,.0f}kWh")
            # Graph Yr 2018
            # Cost VS Usage
            fig_cost_2018 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_cost_2018.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2018,name='RM'))
            fig_cost_2018.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2018,name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2018.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2018,name='kWh'))
            fig_cost_2018.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2018,name='kWh',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2018.update_layout(title_text='Monthly Electricity (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_cost_2018.update_annotations(font=dict(family="Helvetica", size=10))
            fig_cost_2018.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_cost_2018.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_cost_2018, use_container_width=True)
        
        with st.expander("Click to View Year 2017 Data:"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Cost:", f"RM{df_ecost_2017.sum():,.2f}")
            col2.metric("Electricity Usage:", f"{df_eusage_2017.sum():,.0f}kWh")
            # Graph Yr 2017
            # Cost VS Usage
            fig_cost_2017 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_cost_2017.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2017,name='RM'))
            fig_cost_2017.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2017,name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2017.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2017,name='kWh'))
            fig_cost_2017.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2017,name='kWh',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2017.update_layout(title_text='Monthly Electricity Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_cost_2017.update_annotations(font=dict(family="Helvetica", size=10))
            fig_cost_2017.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_cost_2017.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_cost_2017, use_container_width=True)
        
        with st.expander("Click to View Year 2016 Data:"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Cost:", f"RM{df_ecost_2016.sum():,.2f}")
            col2.metric("Electricity Usage:", f"{df_eusage_2016.sum():,.0f}kWh")
            # Graph Yr 2016
            # Cost VS Usage
            fig_cost_2016 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_cost_2016.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2016,name='RM'))
            fig_cost_2016.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2016,name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2016.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2016,name='kWh'))
            fig_cost_2016.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2016,name='kWh',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2016.update_layout(title_text='Monthly Electricity (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_cost_2016.update_annotations(font=dict(family="Helvetica", size=10))
            fig_cost_2016.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_cost_2016.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_cost_2016, use_container_width=True)
        
        with st.expander("Click to View Year 2015 Data:"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Cost:", f"RM{df_ecost_2015.sum():,.2f}")
            col2.metric("Electricity Usage:", f"{df_eusage_2015.sum():,.0f}kWh")
            # Graph Yr 2015
            # Cost VS Usage
            fig_cost_2015 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_cost_2015.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2015,name='RM'))
            fig_cost_2015.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2015,name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2015.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2015,name='kWH'))
            fig_cost_2015.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2015,name='kWH',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2015.update_layout(title_text='Monthly Electricity (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_cost_2015.update_annotations(font=dict(family="Helvetica", size=10))
            fig_cost_2015.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_cost_2015.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_cost_2015, use_container_width=True)
        
        with st.expander("Click to View Year 2014 Data:"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Electricity Cost:", f"RM{df_ecost_2014.sum():,.2f}")
            col2.metric("Electricity Usage:", f"{df_eusage_2014.sum():,.0f}kWh")
            # Graph Yr 2014
            # Cost VS Usage
            fig_cost_2014 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
            fig_cost_2014.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2014,name='RM'))
            fig_cost_2014.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_ecost_2014,name='RM',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2014.add_trace(go.Bar(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2014,name='kWh'))
            fig_cost_2014.add_trace(go.Scatter(x = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], y = df_eusage_2014,name='kWh',
                mode='lines',line = dict(color='red', width=1)), secondary_y=False)
            fig_cost_2014.update_layout(title_text='Monthly Electricity (Cost VS Usage)',title_x=0.5,
                font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),
                yaxis_title=None,showlegend=False, height=350)
            fig_cost_2014.update_annotations(font=dict(family="Helvetica", size=10))
            fig_cost_2014.update_xaxes(title_text='', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            fig_cost_2014.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
            # Chart Presentation
            st.plotly_chart(fig_cost_2014, use_container_width=True)

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
