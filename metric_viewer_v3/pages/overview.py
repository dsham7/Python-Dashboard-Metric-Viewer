import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_daq as daq
import plotly.express as px
# from app import app  # Import the Dash app instance
from data.mock_data import generate_timeseries
from utils import DefaultParams, MockTimeSeriesParams
import numpy as np
import pandas as pd
# /D:/Data Science/VS Projects/Python Dashboard Metric Viewer/metric_viewer_v3/pages/overview.py


dash.register_page(__name__, path="/", title="Overview")

def timeseries_plot():
    df = pd.DataFrame(generate_timeseries(MockTimeSeriesParams()))
    df.columns = ['date', 'value']
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    fig = px.line(df)
    return fig

layout = html.Div(
    [
        # Boolean Switch
        html.Div(
            [
                daq.ToggleSwitch(
                    id="data-switch",
                    label=["Upload data", "Mock data"],
                    value=False,  # False: 'Upload data', True: 'Mock data'
                    style={"width": "100%"},
                ),
            ],
            style={"padding": "24px 0"},
        ),
        
        # Accordions:
        html.Div(
            dbc.Accordion([
                dbc.AccordionItem(title= "Edit Timeframes",
                        children= html.Div(id="edit-timeframes-content"),
                id="accordion-timeframes",
                style={"width": "100%"},
            ),
            
                dbc.AccordionItem(title= "Edit Timeseries",
                        children= html.Div(id="edit-timeseries-content"),
                id="accordion-timeseries",
                style={"width": "100%"},
            )],
            start_collapsed=True,
            always_open=False,
            style={"padding": "12px 0"},
        )),
        # Tabs with Plotly Figure
        html.Div(
            dbc.Tabs(
                [
                    dbc.Tab(
                        label="Timeseries Plot",
                        tab_id="tab-1",
                        children=[
                            dcc.Graph(id="overview-figure",figure=timeseries_plot()),
                        ],
                    ),
                    
                    # Add more tabs as needed
                ],
                id = "tabs",
                active_tab="tab-1",
                style={"width": "100%"},
            ),
            style={"padding": "24px 0"},
        ),
    ],
    style={
        "width": "100%",
        "maxWidth": "1200px",
        "margin": "0 auto",
        "padding": "32px",
        "boxSizing": "border-box",
    },
)