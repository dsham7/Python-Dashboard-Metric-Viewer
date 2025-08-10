import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Business Metric Viewer"
from metric_viewer_v3.pages.overview import layout as overview_layout
from metric_viewer_v3.pages.insights import layout as insights_layout
# server = app.server

# Navigation bar
navbar = dbc.NavbarSimple(
    brand="Business Metric Viewer",
    brand_href="/",
    color="primary",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Overview", href="/")),
        dbc.NavItem(dbc.NavLink("Insights", href="/insights")),
    ],
)

# App layout with dcc.Location for page routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

# Callback for page routing
@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.dependencies.Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/insights':
        # Replace with insights_layout when available
        return html.Div([
            # html.H2("Insights"),
            # html.P("Insights page layout goes here.")
            insights_layout
        ])
    else:
        return overview_layout

if __name__ == '__main__':
    app.run(host='localhost',port='5000',debug=True)