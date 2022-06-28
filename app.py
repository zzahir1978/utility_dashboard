import calendar  # Core Python Module
from datetime import datetime  # Core Python Module
from deta import Deta
import plotly.graph_objects as go  # pip install plotly
import plotly.express as px  # pip install plotly-express
from plotly.subplots import make_subplots
import streamlit as st  # pip install streamlit
from streamlit_option_menu import option_menu  # pip install streamlit-option-menu

#import database as db  # local import

# -------------- SETTINGS --------------
e_usages = ["kWh"]
e_costs = ["RM Electricity"]
w_usages = ["m3"]
w_costs = ["RM Water"]
currency = "RM"
page_title = "Utilities Dashboard"
page_icon = ":bar_chart:"  # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
layout = "centered"     # alternatively used "wide"
# --------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_icon + " " + page_title)

# --- DROP DOWN VALUES FOR SELECTING THE PERIOD ---
years = [datetime.today().year, datetime.today().year + 1]
months = list(calendar.month_name[1:])

# --- DATABASE INTERFACE ---
DETA_KEY = "c0jo61nr_BhSm5qHprUP75vRSdEmumYfoS1KMCtQW"
# Initialize with a project key
deta = Deta(DETA_KEY)
# This is how to create/connect a database
db = deta.Base("utilities_reports")

def insert_period(period, e_usages, e_costs, w_usages, w_costs, comment):
    """Returns the user on a successful user creation, otherwise raises and error"""
    return db.put({"key": period, "e_usage": e_usages, "e_cost": e_costs, "w_usage": w_usages, "w_cost": w_costs, "comment": comment})

def fetch_all_periods():
    """Returns a dict of all periods"""
    res = db.fetch()
    return res.items

def get_period(period):
    """If not found, the function will return None"""
    return db.get(period)

def get_all_periods():
    items = db.fetch_all_periods()
    periods = [item["key"] for item in items]
    return periods
    
# --- HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- NAVIGATION MENU ---
selected = option_menu(
    menu_title=None,
    options=["Data Visualization","Data Entry"],
    icons=["bar-chart-fill","pencil-fill"] ,  # https://icons.getbootstrap.com/
    orientation="horizontal",
)

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
            db.insert_period(period, e_usages, e_costs, w_usages, w_costs, comment)
            st.success("Data saved!")

# --- DATA VISUALISATION ---
if selected == "Data Visualization":
    st.header("Utilities Summary")
    entries = fetch_all_periods()

    total_e_usage = sum([sum(entry['e_usage'].values()) for entry in entries])
    total_e_cost = sum([sum(entry['e_cost'].values()) for entry in entries])
    total_w_usage = sum([sum(entry['w_usage'].values()) for entry in entries])
    total_w_cost = sum([sum(entry['w_cost'].values()) for entry in entries])
    total_cost = total_e_cost + total_w_cost
    e_rate = total_e_cost/total_e_usage
    w_rate = total_w_cost/total_w_usage

    col1, col2, col3 = st.columns(3)
    col1.metric("Electricity Cost:", f" {'RM'}{total_e_cost:,.2f}")
    col2.metric("Water Cost:", f" {'RM'}{total_w_cost:,.2f}")
    col3.metric("Total Costs:", f"{'RM'}{total_cost:,.2f}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Electricity Usage:", f"{total_e_usage} {'kWh'}")
    col2.metric("Water Usage:", f"{total_w_usage} {'m3'}")
    
    with st.expander("Click To View Utilities Rates:"):
        col1, col2 = st.columns(2)
        col1.metric("Electricity Rate:", f"{'RM'}{e_rate:,.2f} {'kWh'}")
        col2.metric("Water Rate:", f"{'RM'}{w_rate:,.2f} {'m3'}")

    st.header("Utilities Graphs")

    fig_1 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
    fig_1.add_trace(go.Bar(x = ['Electricity','Water'], y = [total_e_cost,total_w_cost],name='',text=[total_e_cost,total_w_cost]))
    fig_1.update_layout(title_text='Total Utilities Cost (RM)',title_x=0.5,
        font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),yaxis_title=None,showlegend=False)
    fig_1.update_annotations(font=dict(family="Helvetica", size=10))
    fig_1.update_xaxes(title_text='Utility', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
    fig_1.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')

    fig_2 = make_subplots(shared_xaxes=True, specs=[[{'secondary_y': True}]])
    fig_2.add_trace(go.Bar(x = ['Electricity','Water'], y = [total_e_usage,total_w_usage],name='',text=[total_e_usage,total_w_usage]))
    fig_2.update_layout(title_text='Total Utilities Usage (kWh & m3)',title_x=0.5,
        font=dict(family="Helvetica", size=10),xaxis=dict(tickmode="array"),plot_bgcolor="rgba(0,0,0,0)",yaxis=(dict(showgrid=False)),yaxis_title=None,showlegend=False)
    fig_2.update_annotations(font=dict(family="Helvetica", size=10))
    fig_2.update_xaxes(title_text='Utility', showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
    fig_2.update_yaxes(showgrid=False, zeroline=False, showline=True, linewidth=2, linecolor='black')
    # Chart Presentation
    left_column, right_column = st.columns(2)
    right_column.plotly_chart(fig_1, use_container_width=True)
    left_column.plotly_chart(fig_2, use_container_width=True)

            # Create sankey chart
            #label = list(usages.keys()) + ["Total usage"] + list(costs.keys())
            #source = list(range(len(usages))) + [len(usages)] * len(costs)
            #target = [len(usages)] * len(usages) + [label.index(costs) for cost in costs.keys()]
            #value = list(usages.values()) + list(costs.values())

            # Data to dict, dict to sankey
            #link = dict(source=source, target=target, value=value)
            #node = dict(label=label, pad=20, thickness=30, color="#E694FF")
            #data = go.Sankey(link=link, node=node)

            # Plot it!
            #fig = go.Figure(data)
            #fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
            #st.plotly_chart(fig, use_container_width=True)