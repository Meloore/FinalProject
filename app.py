import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

df = pd.read_csv('https://raw.githubusercontent.com/Meloore/FinalProject/refs/heads/main/assets/Cleaned%20Animal%20Shelter%20Data.csv')

top_breeds_by_year = df.groupby(['Year', 'Breed']).size().reset_index(name='Count')
overall_top_breeds = df['Breed'].value_counts().nlargest(10).index
overall_data = df[df['Breed'].isin(overall_top_breeds)].groupby('Breed').size().reset_index(name='Count')

def get_top_breeds_for_year(year):
    year_data = top_breeds_by_year[top_breeds_by_year['Year'] == year].nlargest(10, 'Count')
    return year_data

years = top_breeds_by_year['Year'].unique()

def create_fig1(year='Overall'):
    if year == 'Overall':
        return px.bar(overall_data, x='Count', y='Breed', orientation='h')
    else:
        yearly_data = get_top_breeds_for_year(int(year))
        return px.bar(yearly_data, x='Count', y='Breed', orientation='h')

daily_intake_trends = df.groupby('Date').size().reset_index(name='Count')
fig2 = px.line(daily_intake_trends, x='Date', y='Count')
fig2.update_xaxes(rangeslider_visible=True)

sunburst_data = df.groupby(['Animal Type', 'Intake Type']).size().reset_index(name='Count')
sunburst_data['Equal Value'] = 1
sunburst_data['Transformed Count'] = np.log1p(sunburst_data['Count'])
fig3 = px.sunburst(sunburst_data, path=['Animal Type', 'Intake Type'], values='Transformed Count')

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Figure 1", href="/page-1")),
            dbc.NavItem(dbc.NavLink("Figure 2", href="/page-2")),
            dbc.NavItem(dbc.NavLink("Figure 3", href="/page-3")),
        ],
        brand="Animal Shelter Data Visualizations",
        color="primary",
        dark=True,
        fluid=False
    ),
    dbc.Container(
        html.Div(id='page-content', style={'height': '80vh'}),
        fluid=True
    )
])

@app.callback(
    [Output('page-content', 'children')],
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/page-1':
        return [dbc.Container([
            dbc.Card([
                dbc.CardHeader("Top 10 Breeds in the Animal Shelter"),
                dbc.CardBody([
                    html.Label("Select Year:"),
                    dcc.Dropdown(
                        id='year-dropdown',
                        options=[{'label': 'Overall', 'value': 'Overall'}] + [{'label': str(year), 'value': str(year)} for year in years],
                        value='Overall',
                        clearable=False,
                        className="mb-4",
                    ),
                    dcc.Graph(id='figure-1', figure=create_fig1())
                ])
            ], className="mb-4")
        ], fluid=True)]
    
    elif pathname == '/page-2':
        return [dbc.Container([
            dbc.Card([
                dbc.CardHeader("Daily Animal Intake Trends"),
                dbc.CardBody(dcc.Graph(figure=fig2))
            ], className="mb-4")
        ], fluid=True)]
    
    elif pathname == '/page-3':
        return [dbc.Container([
            dbc.Card([
                dbc.CardHeader("Types of Animals and Intake Types"),
                dbc.CardBody(dcc.Graph(figure=fig3, style={'height': '80vh'}))
            ], className="mb-4")
        ], fluid=True)]
    
    else:
        return [dbc.Row(
            dbc.Col(
                html.Div([
                    html.H3("Animal Shelter Data Dashboard", className="text-center mb-4"),
                    html.P(
                        "This dashboard provides key insights into animal shelter data, including the most common breeds housed annually, daily intake trends, and the primary methods of intake, such as strays or owner surrenders. By visualizing these aspects, users can easily identify patterns in the shelter’s operations and understand which animal types and breeds are more prevalent. These insights are designed to assist shelter management in making informed decisions to improve animal care and optimize resource allocation.",
                        className="text-center",
                        style={
                            'maxWidth': '800px',
                            'margin': '0 auto',
                            'lineHeight': '1.6',
                            'fontSize': '16px'
                        }
                    )
                ], className="d-flex flex-column justify-content-center align-items-center", style={'height': '100%'}),
                width=12
            ),
            className="h-100 align-items-center"
        )]

@app.callback(
    Output('figure-1', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_figure1(year):
    return create_fig1(year)

if __name__ == '__main__':
    app.run(debug=True)
