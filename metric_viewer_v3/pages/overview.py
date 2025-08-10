import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_daq as daq

# /D:/Data Science/VS Projects/Python Dashboard Metric Viewer/metric_viewer_v3/pages/overview.py


dash.register_page(__name__, path="/", title="Overview")

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
                            dcc.Graph(id="overview-figure"),
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