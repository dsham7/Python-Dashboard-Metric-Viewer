import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from callbacks import insights_callbacks
import plotly.graph_objs as go
from callbacks import insights_callbacks
dash.register_page(__name__, path="/insights", title="Insights")
# Dummy figures
fig_timeframe_corr = go.Figure()
fig_timeseries_corr = go.Figure()
fig_forecast = go.Figure()

# Dropdown dummy options
timeseries_options = [
    {"label": "Series A", "value": "A"},
    {"label": "Series B", "value": "B"},
]
timeframe_options = [
    {"label": "Last 28 days", "value": "28d"},
    {"label": "Last 56 days", "value": "56d"},
]

layout = dbc.Container(
    [
        dbc.Row(
            [
                html.Div(id='initial-message'),
                # Top left: Timeframe correlations + timeseries dropdown
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label("Select Timeseries", style={"margin-right": "10px"}),
                                        dcc.Dropdown(
                                            id="timeseries-dropdown",
                                            options=timeseries_options,
                                            value=timeseries_options[0]["value"],
                                            clearable=False,
                                            style={"width": "100%",'margin':'10px'},
                                        ),
                                    ],
                                    style={"display": "flex", "align-items": "center", "margin-bottom": "10px"},
                                ),
                                dcc.Graph(id="timeframe-corr-plot", figure=fig_timeframe_corr),
                            ]
                        )
                    ],
                    width=6,
                ),
                # Top right: Timeseries correlations + timeframe dropdown
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label("Select Timeframe", style={"margin-right": "10px"}),
                                        dcc.Dropdown(
                                            id="timeframe-dropdown",
                                            options=timeframe_options,
                                            value=timeframe_options[0]["value"],
                                            clearable=False,
                                            style={"width": "100%",'margin':'10px'},
                                        ),
                                    ],
                                    style={"display": "flex", "align-items": "center", "margin-bottom": "10px"},
                                ),
                                dcc.Graph(id="timeseries-corr-plot", figure=fig_timeseries_corr),
                            ]
                        )
                    ],
                    width=6,
                ),
            ],
            style={"margin-bottom": "20px"},
        ),
        dbc.Row(
            [
                # Bottom: Timeseries Forecast spanning both columns
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label("Show full history", style={"margin-right": "10px"}),
                                        dbc.Switch(
                                            id="show-historical-switch",
                                            value=True,
                                            label="",
                                        ),
                                    ],
                                    style={"display": "flex", "align-items": "center", "margin-bottom": "10px"},
                                ),
                                dcc.Graph(id="forecast-plot", figure=fig_forecast),
                            ]
                        )
                    ],
                    width=6,
                ),
            ]
        ),
    ],
    fluid=True,
)