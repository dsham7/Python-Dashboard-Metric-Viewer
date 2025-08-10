import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Placeholder figures for demonstration
import plotly.graph_objs as go
dash.register_page(__name__, path="/insights", title="Insights")
# Dummy figures
fig_timeframe_corr = go.Figure()
fig_timeseries_corr = go.Figure()
fig_forecast = go.Figure()

# Dropdown options (replace with your actual options)
timeseries_options = [
    {"label": "Series A", "value": "A"},
    {"label": "Series B", "value": "B"},
]
timeframe_options = [
    {"label": "Last 7 Days", "value": "7d"},
    {"label": "Last 30 Days", "value": "30d"},
]

layout = dbc.Container(
    [
        dbc.Row(
            [
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
                                            style={"width": "60%"},
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
                                            style={"width": "60%"},
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
                                        html.Label("Show Historical Data", style={"margin-right": "10px"}),
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
                    width=12,
                ),
            ]
        ),
    ],
    fluid=True,
)