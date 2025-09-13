# d:\\Data Science\\Void Projects\\metric_viewer_v3\\components\\navbar.py
import dash_bootstrap_components as dbc

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