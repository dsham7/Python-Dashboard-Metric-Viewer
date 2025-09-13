import dash
from dash import dcc, html
from dash import Input, Output
import dash_bootstrap_components as dbc
import dash_daq as daq
import plotly.express as px
from data.mock_data import generate_timeseries
from utils import DefaultParams, MockTimeSeriesParams
import numpy as np
import pandas as pd
from callbacks import overview_callbacks
import plotly.graph_objects as go

dash.register_page(__name__, path="/", title="Overview")

def timeseries_plot(trend_type, fluctuation):
    df = pd.DataFrame(generate_timeseries(trend_type.lower(),fluctuation.lower(),MockTimeSeriesParams()))
    df.columns = ['date', 'value']
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    fig = px.line(df)
    return fig

layout = html.Div(
    [
        html.Div(
            [
                dcc.Store(id="col-store", data=[]),
                dcc.Store(id="session-data", data=None),
                dcc.Store(id='uploaded-data-store', data=None),
                # Boolean Switch
                daq.ToggleSwitch(
                    id="data-switch",
                    label=["Upload data", "Mock data"],
                    value=False,  # False: 'Upload data', True: 'Mock data'
                    style={"width": "100%"},
                ),
                html.Div(id="upload-container-wrapper",
                    children=[
                        dcc.Upload(
                            id="file-upload",
                            children=html.Div(["Drag and Drop or ", html.A("Select CSV File")]),
                            style={
                                "width": "100%",
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                "margin": "10px 0px",
                            },
                            multiple=False,
                        )
                    ],),

                # Edit parameters
                dbc.Accordion(
                    [
                        dbc.AccordionItem(
                            title="Edit Timeframes",
                            children=[
                                html.Div(
                                    id="table-container",
                                    children=[
                                        html.Table(
                                            [
                                                html.Tbody(
                                                    id="table-body",
                                                ),
                                            ],
                                            style={
                                                "width": "auto",      # table takes width
                                                "tableLayout": "fixed"  # equal column widths
                                            },
                                        ),
                                        html.Button(
                                            "+ Add Timeframe",
                                            id="add-col-btn",
                                            n_clicks=0
                                        ),
                                        html.Button(
                                            "Apply Changes",
                                            id="apply-changes-btn",
                                            n_clicks=0
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        dbc.AccordionItem(
                            title="Edit Timeseries",
                            children=[
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.Label("Trend Type"),
                                                dcc.Dropdown(
                                                    id="trend-type-dropdown",
                                                    options=[
                                                        {"label": o, "value": o}
                                                        for o in [
                                                            "Stable",
                                                            "Increasing",
                                                            "Decreasing",
                                                            "Cyclical",
                                                            "Random",
                                                        ]
                                                    ],
                                                    value="Increasing",
                                                    style={"width": "100%"},
                                                ),
                                            ],
                                            width=6,
                                        ),
                                        dbc.Col(
                                            [
                                                html.Label("Fluctuations"),
                                                dcc.Dropdown(
                                                    id="fluctuations-dropdown",
                                                    options=[
                                                        {"label": o, "value": o}
                                                        for o in ["Low", "High", "None"]
                                                    ],
                                                    value="Low",
                                                    style={"width": "100%"},
                                                ),
                                            ],
                                            width=6,
                                        ),
                                    ]
                                ),
                                
                            ]
                        ),

                    ],
                    start_collapsed=True,  # All closed by default
                    style={"margin": "10px 0px"},
                ),
                dbc.Row([
                                    html.Button(
                                        "Save this Timeseries as:",
                                        id="save-timeseries-btn",
                                        n_clicks=0,
                                        style={"width": "auto", "padding": "5px", "margin":"5px"}
                                    ),
                                        dcc.Input(
                                            id="timeseries-label-input",
                                            type="text",
                                            placeholder="Timeseries Label",
                                            style={"width": "auto","padding": "5px","margin": "5px"}
                                        )
                                    ],
                                    style={"display": "flex", "justify-content": "center"},
                                ),
                                dbc.Row(
                                    html.Div(id="saved-timeseries-message", 
                                             children = "No timeseries saved yet!",
                                             style={"textAlign": "center", "width": "100%"}),
                                    style={"justify-content": "center"}
                                ),
                # Plot
                dcc.Graph(
                    id="overview-figure",
                ),
                
            ],
            style={"padding": "24px"},
        ),
    ]
)
