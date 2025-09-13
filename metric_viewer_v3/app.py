import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True, use_pages=True)
app.title = "Business Metric Viewer"
from components.navbar import navbar

app.layout = html.Div([
    dcc.Store(id="saved-timeseries-data", data={}, storage_type="memory"), 
    dcc.Location(id='url', refresh=False),
    navbar,
    dash.page_container
])

if __name__ == '__main__':
    app.run(host='localhost',port='5000',debug=True)
