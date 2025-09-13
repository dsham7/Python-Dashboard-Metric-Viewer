from dash import Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
from utils import DefaultParams, MockTimeSeriesParams
from dash import dcc, html, ALL, ctx, callback
import dash_daq as daq
import dash
import os
import plotly.express as px
import pandas as pd
import uuid
import base64
import io
from data.mock_data import generate_timeseries
from utils import process_upload_data
import plotly.graph_objects as go
import plotly.express as px

@dash.callback(
    Output('upload-container-wrapper', 'style'),
    Input('data-switch', 'value')
)
def hide_upload_container(switch_value):
    if switch_value:
        return {'display': 'none'}  # Hide the upload container
    else:
        return {'display': 'block'}  # Show the upload container


def placeholder_plot():
    placeholder_fig = go.Figure()
    placeholder_fig.update_layout(
        title = "Timeseries",
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


# assume you already have your light_palette and DefaultParams defined somewhere
light_palette = {
    "Light blue": "#E3F2FD",
    "Light pink": "#FCE4EC",
    "Light green": "#E8F5E9",
    "Light orange": "#FFF3E0",
    "Light purple": "#F3E5F5",
    "Light cyan": "#E0F7FA",
    "Light yellow": "#FFFDE7",
    "Light lime": "#F1F8E9",
    "Light grey": "#ECEFF1",
    "Almost white": "#FAFAFA"
}


# === Helper functions to build per-column cells ===
def make_timeframe_cell(col_id, timeframe_name=""):
    return html.Td(
        [
            dcc.Input(
                id={"type": "timeframe-name", "index": col_id},
                type="text",
                placeholder="Timeframe Name",
                value=timeframe_name,
                style={"width": "250px", "margin": "0px 10px"},
            ),
            # Delete button is placed in the header row (to keep it consistent)
            html.Button(
                "Delete",
                id={"type": "delete-col-btn", "index": col_id},
                n_clicks=0,
                style={"marginLeft": "5px", "color": "red"},
            ),
        ]
    )


def make_color_cell(col_id, color="#E3F2FD"):
    return html.Td(
        dcc.Dropdown(
            id={"type": "color-dropdown", "index": col_id},
            options=[{"label": k, "value": v} for k, v in light_palette.items()],
            value=color,
            style={"width": "250px"},
        )
    )


def make_date_cell(col_id, start_date=DefaultParams().global_timeframe[0], end_date=DefaultParams().global_timeframe[-1]):
    return html.Td(
        dcc.DatePickerRange(
            id={"type": "date-picker-range", "index": col_id},
            start_date=start_date,
            end_date=end_date,
            display_format="YYYY-MM-DD",
        )
    )


# === Callback ===
@dash.callback(
    Output("table-body", "children"),
    Output("col-store", "data"),
    Input("add-col-btn", "n_clicks"),
    Input({"type": "delete-col-btn", "index": ALL}, "n_clicks"),
    Input({"type": "timeframe-name", "index": ALL}, "value"),
    Input({"type": "color-dropdown", "index": ALL}, "value"),
    Input({"type": "date-picker-range", "index": ALL}, "start_date"),
    Input({"type": "date-picker-range", "index": ALL}, "end_date"),
    State("col-store", "data"),
    prevent_initial_call=True,
)
def update_table(add_clicks, delete_clicks, timeframe_names, colors, start_dates, end_dates, col_data):
    triggered = ctx.triggered_id

    if col_data is None:
        col_data = []

    # Add column
    if triggered == "add-col-btn":
        new_id = str(uuid.uuid4())
        col_data.append({
            "id": new_id,
            "timeframe_name": "",
            "color": "#E3F2FD",
            "start_date": DefaultParams().global_timeframe[0],
            "end_date": DefaultParams().global_timeframe[-1]
        })

    # Delete column
    elif isinstance(triggered, dict) and triggered.get("type") == "delete-col-btn":
        col_id = triggered["index"]
        col_data = [c for c in col_data if c["id"] != col_id]

    # Update column data
    elif triggered and any(t in triggered["type"] for t in ["timeframe-name", "color-dropdown", "date-picker-range"]):
        for i in range(len(col_data)):
            col_data[i]["timeframe_name"] = timeframe_names[i]
            col_data[i]["color"] = colors[i]
            col_data[i]["start_date"] = start_dates[i]
            col_data[i]["end_date"] = end_dates[i]

    # Build table rows: one <tr> per field
    rows = [
        html.Tr(
            [html.Th("Timeframe Name")]
            + [make_timeframe_cell(c["id"], c["timeframe_name"]) for c in col_data]
        ),
        html.Tr(
            [html.Th("Color")]
            + [make_color_cell(c["id"], c["color"]) for c in col_data]
        ),
        html.Tr(
            [html.Th("Date Range")]
            + [make_date_cell(c["id"], c["start_date"], c["end_date"]) for c in col_data]
        ),
    ]

    return rows, col_data



# store the uploaded csv data
@dash.callback(
    Output('uploaded-data-store', 'data'),
    Input('file-upload', 'contents'),
    State('file-upload', 'filename'),
    prevent_initial_call=True,
)
def store_uploaded_data(uploaded_contents, filename):
    if uploaded_contents is None:
        raise PreventUpdate
    
    try:
        content_type, content_string = uploaded_contents.split(',')
        decoded = base64.b64decode(content_string)
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None
        
        print('File uploaded:', filename)
        return df.to_dict('records')
    except Exception as e:
        print("Upload error:", e)
        return None

@dash.callback(
    Output('session-data', 'data'),
    Input('data-switch', 'value'),
    Input('trend-type-dropdown', 'value'),
    Input('fluctuations-dropdown', 'value'),
    Input('uploaded-data-store', 'data'),
    prevent_initial_call=True,
)
def update_session_data(data_switch_value, trend_type, fluctuation_type,uploaded_data):
    if not data_switch_value:  # Use uploaded data
        if uploaded_data is None:
            print('Please upload a file first')
            return []#, placeholder_plot() # Return an empty list for session data and placeholder plot
        else:
            processed_data, error_message = process_upload_data(uploaded_data)
        
            if error_message:
                print(f'Error processing uploaded data: {error_message}')
                return []#, placeholder_plot() # Return an empty list and a placeholder if there's an error
            else:
                return processed_data.to_dict('records')#, px.line(processed_data, x='Date', y='Value') # Return processed data and plot
    
    else:  # Generate mock data
        data = generate_timeseries(trend_type, fluctuation_type, params=MockTimeSeriesParams())
        return data.to_dict('records')


@dash.callback(
    Output('saved-timeseries-data', 'data'),
    Output('timeseries-label-input', 'value'),
    Input('save-timeseries-btn', 'n_clicks'),
    State('timeseries-label-input', 'value'),
    State('session-data', 'data'),
    State('saved-timeseries-data', 'data'),
    prevent_initial_call=True
)
def save_timeseries(n_clicks, label, timeseries_data, saved_data):
    if label and label != "Timeseries Label":
        saved_data[label] = timeseries_data
        return saved_data, ""  # Clear the input after saving
    else:
        return dash.no_update, dash.no_update


@dash.callback(
    Output('overview-figure', 'figure'),
    Input('session-data', 'data'),
    Input("apply-changes-btn", "n_clicks"),
    State("col-store", "data"),
    # prevent_initial_call=True
)
def update_figure(data, n_clicks, col_data):
    if data is None or not data:
        fig = placeholder_plot()
        return fig
    else:
        df = pd.DataFrame(data)
        # print(data)
        fig = px.line(df, x='Date', y='Value')
        
    # Extract custom timeframes and colors from table
        if col_data:
            # Add shaded regions for each custom timeframe
            for col in col_data:
                fig.add_vrect(
                    x0=col["start_date"],
                    x1=col["end_date"],
                    fillcolor=col["color"],
                    opacity=1,
                    layer="below",
                    line_width=0,
                    annotation_text=col["timeframe_name"],
                    annotation_position="top left",
                    annotation=dict(
                        font_size=10,
                        font_color="black"
                    )
                )

    return fig


@dash.callback(
    Output("saved-timeseries-message", "children"),
    Input("saved-timeseries-data", "data")
)
def update_saved_timeseries_message(data):
    if len(data) == 0:
        return "No timeseries saved yet!"
    else:
        labels = ", ".join(data.keys())
        return f"Saved timeseries labels: {labels}"
