from dash import Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import dcc, html, ALL, ctx, callback
import dash_daq as daq
import dash
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import uuid
import base64
import io
from utils import tf_label_to_tuple, Timeframe_corr, Series_corr, forc, stats_by_ser, TIMEFRAME_COLORS

@dash.callback(
    Output("initial-message",'children'),
    Input("saved-timeseries-data", "data"),
)
def initial_msg(data):
    if len(data)==0:
        msg = 'This page updates when you save at least two timeseries on the Overview page'
    else:
        msg = []
    return msg

@dash.callback(
    Output("timeframe-corr-plot", "figure"),
    Input("saved-timeseries-data", "data"),
    Input("timeseries-dropdown", "value"),
    Input("timeframe-dropdown", "value"),
)
def update_timeframe_corr_plot(data, timeseries, timeframe):
    if data is None or not isinstance(data, dict) or len(data) == 0 or timeseries not in data:
        return px.imshow([[0]]) # Return an empty figure, or you can return a loading figure

    df = pd.DataFrame(data[timeseries]) # series_df
    df['Date'] = pd.to_datetime(df['Date'])
    tf_label = 'Last 28 days' if timeframe == '28d' else 'Last 56 days'
    tf_tuple, _ = tf_label_to_tuple(df,tf_label)
    corr_df = Timeframe_corr(df, tf_tuple)
    fig = px.imshow(corr_df, text_auto=".1f")
    fig.update_layout(title=f"Timeframe correlation for {timeseries}, {tf_label}")
    return fig

@dash.callback(
    Output("timeseries-corr-plot", "figure"),
    Input("saved-timeseries-data", "data"),
    Input("timeframe-dropdown", "value"),
)
def update_timeseries_corr_plot(data, timeframe):
    if data is None or not isinstance(data, dict) or len(data) == 0:
        return px.imshow([[0]]) # Return an empty figure, or you can return a loading figure

    ts_dict = {}
    for timeseries in data.keys():
        ts_dict.update({timeseries:pd.DataFrame(data[timeseries])})
    tf_label = 'Last 28 days' if timeframe == '28d' else 'Last 56 days'
    _, overall_tf_tuple = tf_label_to_tuple(ts_dict[list(ts_dict.keys())[0]],tf_label)
    # get overall tf tuple for ex. start and end dates for either 
    corr_df = Series_corr(ts_dict, overall_tf_tuple, tf_label)
    fig = px.imshow(corr_df, text_auto=".1f")
    fig.update_layout(title=f"Timeseries correlation for {tf_label}")
    return fig

@dash.callback(
    Output("forecast-plot", "figure"),
    Input("saved-timeseries-data", "data"),
    Input('show-historical-switch','value'),
)
def update_forecast_plot(data,history_switch):
    if data is None or not isinstance(data, dict) or len(data) == 0:
        placeholder_fig = go.Figure()
        placeholder_fig.update_layout(
            title = "Timeseries Forecast",
            xaxis_title="X-axis",
            yaxis_title="Y-axis",
            annotations=[
                dict(
                    text="Graph will appear here",
                    x=0.5, y=0.5,
                    xref="paper", yref="paper",
                    showarrow=False,
                    font=dict(size=16, color="gray")
                )
            ]
        )
        return placeholder_fig

    ts_dict = {}
    forc_dict = {}
    for timeseries in data.keys():
        df = pd.DataFrame(data[timeseries])
        ts_dict.update({timeseries:df})
        forc_dict.update({timeseries:forc(df)})
    
    combined_df = pd.concat(
        [df.assign(Timeseries=name) for name, df in ts_dict.items()],
        ignore_index=True
        )    
    stats, st_df = stats_by_ser(combined_df) # make the stats before adding forecasting
    stats_text = stats.round(1).to_string()
    stats_text = stats_text.replace("\n", "<br>")
    
    combined_forc = pd.concat(
        [df.assign(Timeseries=name) for name, df in forc_dict.items()],
        ignore_index = True
    )
    forc_start = combined_forc['Date'].min()
    forc_end = combined_forc['Date'].max()
    
    combined_df = pd.concat([combined_df, combined_forc], ignore_index=True)
    combined_df = combined_df.sort_values(by='Date')
    if history_switch == False:
        recent_history_date = forc_start - pd.Timedelta('21d')
        combined_df = combined_df[combined_df['Date']>=recent_history_date]

    fig = px.line(
            combined_df,
            x="Date",
            y="Value",
            color="Timeseries",   # Different colors for each timeseries
            title="Timeseries Forecast"
        )
    
    for period in stats.columns[:2]:
        x_color = TIMEFRAME_COLORS[period]
        x_start = st_df.loc[st_df[period]==1,'Date'].iloc[0]
        x_end = st_df.loc[st_df[period]==1,'Date'].iloc[-1]
        fig.add_vrect(
                        x0=x_start,
                        x1=x_end,
                        fillcolor=x_color,
                        opacity=1,
                        layer="below",
                        line_width=0,
                        annotation_text=period,
                        annotation_position="bottom left",
                        annotation=dict(
                            font_size=10,
                            font_color="black"
                        )
                    )    
    
    fig.add_vrect(
                    x0=forc_start,
                    x1=forc_end,
                    fillcolor="#F3E5F5",
                    opacity=1,
                    layer="below",
                    line_width=0,
                    annotation_text="Forecast",
                    annotation_position="top left",
                    annotation=dict(
                        font_size=10,
                        font_color="black"
                    )
                )
    fig.add_annotation(
        text=stats_text,
        x=0.02, y=0.95,   # position (adjust as needed)
        showarrow=False,
        xref="paper", yref="paper",xanchor="left",yanchor="top",
        bgcolor="white", bordercolor="black", borderwidth=1, borderpad=4,
        font=dict(family="Courier New, monospace", size=12)
    )
    return fig


@dash.callback(
    Output("timeseries-dropdown", "options"),
    Output("timeseries-dropdown", "value"),
    Input("saved-timeseries-data", "data"),
)
def populate_dropdown_ts(data):
    if data is None or not isinstance(data, dict) or len(data)==0:
        return [],[]
    else:
        return [{"label": s, "value": s} for s in data.keys()],list(data.keys())[0] if len(data.keys())!=0 else []
    
