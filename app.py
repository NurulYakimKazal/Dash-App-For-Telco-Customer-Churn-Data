import dash
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import regex as re
import plotly.graph_objects as go
from dash import Input, Output, State, html, dcc
from dash.exceptions import PreventUpdate

# Data Loading Section

df = pd.read_csv('Telco-Customer-Churn.csv')
df.columns = [' '.join(re.findall('[a-zA-Z][A-Z]{1}|[a-zA-Z][^A-Z]+', x[0].upper() + x[1:])) for x in df.columns]
senior_citizen_map = {0: 'No', 1: 'Yes'}
df['Senior Citizen'] = df['Senior Citizen'].map(senior_citizen_map)
df.loc[df['Total Charges'] == ' ', 'Total Charges'] = 0.0
df['Total Charges'] = df['Total Charges'].astype('float')

all_var = list(df.columns)
cat_var = [x for x in all_var if ((df[x].dtype == 'object') and x not in ('Customer ID', 'Churn'))]
num_var = [x for x in all_var if df[x].dtype != 'object']

for i in cat_var:
    df[i] = df[i].apply(lambda x: x.title() if x.isupper == False else x)

data_type = ['Categorical', 'Numerical', 'Categorical Vs Numerical', 'Numerical Vs Numerical']

all_options_num = {x: [y for y in num_var if y != x] for x in num_var}

churn_table = pd.DataFrame(df.groupby('Churn')['Churn'].count())
churn_table = churn_table.rename(columns={'Churn': 'Count'}).reset_index()

churned_cust = churn_table.loc[churn_table['Churn'] == 'Yes', 'Count'].values[0]
total_cust = churned_cust + churn_table.loc[churn_table['Churn'] == 'No', 'Count'].values[0]
churn_rate = (churned_cust / total_cust) * 100


# Helper Functions

def indicator_graph(value, range):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={'suffix': '%'},
            domain={'x': [0.1, 0.9], 'y': [0.1, 0.9]},
            gauge={'axis': {'range': range, 'tickcolor': 'black', 'tick0': 10, 'dtick': 20, 'tickwidth': 0.005},
                   'bar': {'color': 'darkorange', 'thickness': 0.6},
                   'bordercolor': 'black',
                   'borderwidth': 0.5}
        )
    )
    fig.update_layout(
        font={'size': 8, 'color': 'black'},
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)'
    )
    return fig


def bar_graph_ver(column_name):
    fig = go.Figure()
    color_map = {'No': 'dodgerblue', 'Yes': 'darkorange'}
    for i in df['Churn'].unique():
        fig.add_trace(
            go.Histogram(
                histfunc='count',
                x=df.loc[df['Churn'] == i][column_name],
                marker=dict(
                    color=color_map[i]
                ),
                name=i,
                customdata=[column_name for i in df[column_name].unique()],
                hovertemplate=
                '<i style="color:white;"><b>%{customdata}:</b> %{x}</i><br>' +
                '<i style="color:white;"><b>Count:</b> %{y}</i><br>' +
                '<extra></extra>'
            )
        )
    fig.update_layout(
        xaxis=dict(
            showline=False,
            showgrid=False,
            zeroline=False,
            showticklabels=True,
            tickfont=dict(
                family='Arial',
                size=12,
                color='black'
            )
        ),
        yaxis=dict(
            showline=False,
            showgrid=False,
            zeroline=False,
            showticklabels=True,
            tickfont=dict(
                family='Arial',
                size=12,
                color='black'
            )
        ),
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)'
    )
    return fig


# App Initialization

plotly_logo = 'https://images.plot.ly/logo/new-branding/plotly-logomark.png'

app = dash.Dash(external_stylesheets=[dbc.themes.YETI],
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}])

app.title = 'Telco Customer Churn'

app.config.suppress_callback_exceptions = True

# Navbar

navbar = dbc.Navbar([
    dbc.Container([
        html.A([
            dbc.Row([
                dbc.Col(html.Img(src=plotly_logo, height='25px')),
                dbc.Col(dbc.NavbarBrand('Telco Customer Churn Dashboard', className='ms-2',
                                        style={'fontWeight': 550, 'color': 'black'}))
            ], align='center', className='g-0')
        ], href='https://plotly.com', style={'textDecoration': 'none'})
    ])
], color='secondary')

# Title Section

title_header = dbc.CardHeader(
    id='title-header',
    className='border-bottom border-secondary d-flex align-items-center justify-content-center',
    style={'height': '50%', 'textAlign': 'center', 'fontSize': '20px', 'fontWeight': 500, 'color': 'black'}
)

title_body = dbc.CardBody([
    dbc.Row([
        dbc.Col([
            html.P(
                children=['This dashboard is built for visualizing the exploratory data analysis of ',
                          html.A(
                              children=['Telco Customer Churn'],
                              href='https://www.kaggle.com/datasets/blastchar/telco-customer-churn',
                              style={'textDecoration': 'none'}
                          ),
                          ' dataset. (Data Source: ',
                          html.A(
                              children=['Kaggle'],
                              href='https://www.kaggle.com',
                              style={'textDecoration': 'none'}
                          ),
                          ')'
                          ],
                className='m-0 p-0',
                style={'textAlign': 'left', 'fontSize': '12.5px', 'fontWeight': 500, 'color': 'black'}
            )
        ], width=12, className='m-0 p-0 d-flex align-items-center justify-content-center', style={'height': '100%'})
    ], className='m-0 p-0 d-flex align-items-center justify-content-center', style={'height': '100%', 'width': '100%'})
], className='vstack gap-0 bg-opacity-10 m-0 p-0 d-flex align-items-center justify-content-center',
    style={'height': '50%'})

# KPI Section

churn_rate_header = dbc.CardHeader(
    'Overall Churn Rate',
    className='border-bottom border-secondary d-flex align-items-center justify-content-center',
    style={'height': '17%', 'textAlign': 'center', 'fontSize': '13px', 'fontWeight': 500, 'color': 'black'}
)

churn_dist_header = dbc.CardHeader(
    'Overall Churn Distribution',
    className='border-bottom border-secondary d-flex align-items-center justify-content-center',
    style={'height': '17%', 'textAlign': 'center', 'fontSize': '13px', 'fontWeight': 500, 'color': 'black'}
)

churn_rate_body = dbc.CardBody([
    dcc.Graph(
        figure=indicator_graph(churn_rate, [0, 100]),
        className='d-flex align-items-center justify-content-center',
        style={'height': '100%', 'width': '100%'}
    )
], className='bg-opacity-10 d-flex align-items-center justify-content-center', style={'height': '83%'})

churn_dist_body = dbc.CardBody([
    dcc.Graph(
        figure=bar_graph_ver('Churn'),
        className='d-flex align-items-center justify-content-center',
        style={'height': '100%', 'width': '100%'}
    )
], className='bg-opacity-10 d-flex align-items-center justify-content-center mt-0 mb-0',
    style={'height': '83%', 'marginLeft': '15px', 'marginRight': '15px'})

# Selector Section

selector_header = dbc.CardHeader(
    'Selector',
    className='border-bottom border-secondary d-flex align-items-center justify-content-center',
    style={'height': '8.25%', 'textAlign': 'center', 'fontSize': '13px', 'fontWeight': 500, 'color': 'black'}
)

selector_body = dbc.CardBody([
    dbc.Row([
        dbc.Col([
            html.Label('Select Data Type', style={'fontSize': '12px', 'fontWeight': 500, 'color': 'black'}),
            dcc.Dropdown(
                id='data-type',
                options=[{'label': x, 'value': x} for x in data_type],
                value=data_type[0],
                multi=False,
                clearable=False,
                style={'width': '100%', 'fontSize': '11.5px', 'fontWeight': 500, 'color': 'black'}
            )
        ], width=12, className='vstack gap-0 d-flex align-items-start justify-content-center',
            style={'height': '100%', 'textAlign': 'left'})
    ], className='m-0 p-0 d-flex align-items-center justify-content-end', style={'height': '14%', 'width': '100%'}),
    dbc.Row([
        dbc.Col([
            html.Label('Select Variable', style={'fontSize': '12px', 'fontWeight': 500, 'color': 'black'}),
            dcc.Dropdown(
                id='var',
                multi=False,
                clearable=False,
                style={'width': '100%', 'fontSize': '11.5px', 'fontWeight': 500, 'color': 'black'}
            )
        ], width=12, className='vstack gap-0 d-flex align-items-start justify-content-center',
            style={'height': '100%', 'textAlign': 'left'})
    ], className='m-0 p-0 d-flex align-items-center justify-content-end', style={'height': '14%', 'width': '100%'}),
    dbc.Row([
        dbc.Col([
            html.Label('Select Categorical Variable', style={'fontSize': '12px', 'fontWeight': 500, 'color': 'black'}),
            dcc.Dropdown(
                id='cat-var',
                options=[{'label': x, 'value': x} for x in cat_var],
                value=cat_var[0],
                multi=False,
                clearable=False,
                style={'width': '100%', 'fontSize': '11.5px', 'fontWeight': 500, 'color': 'black'}
            )
        ], width=12, className='vstack gap-0 d-flex align-items-start justify-content-center',
            style={'height': '100%', 'textAlign': 'left'})
    ], className='m-0 p-0 d-flex align-items-center justify-content-end', style={'height': '14%', 'width': '100%'}),
    dbc.Row([
        dbc.Col([
            html.Label('Select Numerical Variable', style={'fontSize': '12px', 'fontWeight': 500, 'color': 'black'}),
            dcc.Dropdown(
                id='num-var',
                options=[{'label': x, 'value': x} for x in num_var],
                value=num_var[0],
                multi=False,
                clearable=False,
                style={'width': '100%', 'fontSize': '11.5px', 'fontWeight': 500, 'color': 'black'}
            )
        ], width=12, className='vstack gap-0 d-flex align-items-start justify-content-center',
            style={'height': '100%', 'textAlign': 'left'})
    ], className='m-0 p-0 d-flex align-items-center justify-content-end', style={'height': '14%', 'width': '100%'}),
    dbc.Row([
        dbc.Col([
            html.Label('Select X-Axis', style={'fontSize': '12px', 'fontWeight': 500, 'color': 'black'}),
            dcc.Dropdown(
                id='x-axis',
                options=list(all_options_num.keys()),
                value=list(all_options_num.keys())[0],
                multi=False,
                clearable=False,
                style={'width': '100%', 'fontSize': '11.5px', 'fontWeight': 500, 'color': 'black'}
            )
        ], width=12, className='vstack gap-0 d-flex align-items-start justify-content-center',
            style={'height': '100%', 'textAlign': 'left'})
    ], className='m-0 p-0 d-flex align-items-center justify-content-end', style={'height': '14%', 'width': '100%'}),
    dbc.Row([
        dbc.Col([
            html.Label('Select Y-Axis', style={'fontSize': '12px', 'fontWeight': 500, 'color': 'black'}),
            dcc.Dropdown(
                id='y-axis',
                multi=False,
                clearable=False,
                style={'width': '100%', 'fontSize': '11.5px', 'fontWeight': 500, 'color': 'black'}
            )
        ], width=12, className='vstack gap-0 d-flex align-items-start justify-content-center',
            style={'height': '100%', 'textAlign': 'left'})
    ], className='m-0 p-0 d-flex align-items-center justify-content-end', style={'height': '14%', 'width': '100%'}),
    dbc.Row([
        dbc.Col([
            dbc.Button(
                'Apply',
                color='primary',
                id="button"
            )
        ], width=12, className='d-flex align-items-center justify-content-center',
            style={'height': '100%', 'textAlign': 'left'}),
    ], className='m-0 p-0 d-flex align-items-center justify-content-end', style={'height': '16%', 'width': '100%'})
], className='vstack gap-0 p-0 d-flex align-items-end justify-content-center',
    style={'height': '91.75%', 'marginTop': '5px', 'marginBottom': '5px', 'marginLeft': '10px', 'marginRight': '10px'})

# Categorical Content

cat_main_header = dbc.CardHeader(
    id='cat-main-header',
    className='border-bottom border-secondary d-flex align-items-center justify-content-center',
    style={'height': '17%', 'textAlign': 'center', 'fontSize': '13px', 'fontWeight': 500, 'color': 'black'}
)

no_churn_header = dbc.CardHeader(
    id='no-header',
    className='border-bottom border-secondary d-flex align-items-center justify-content-center',
    style={'height': '17%', 'textAlign': 'center', 'fontSize': '13px', 'fontWeight': 500, 'color': 'black'}
)

yes_churn_header = dbc.CardHeader(
    id='yes-header',
    className='border-bottom border-secondary d-flex align-items-center justify-content-center',
    style={'height': '17%', 'textAlign': 'center', 'fontSize': '13px', 'fontWeight': 500, 'color': 'black'}
)

cat_main_body = dbc.CardBody([
    dcc.Loading(
        children=[
            dcc.Graph(
                id='cat-main-body',
                className='d-flex align-items-center justify-content-center',
                style={'height': '100%', 'width': '100%'}
            )
        ],
        type='dot',
        color='steelblue',
        parent_style={'height': '100%', 'width': '100%'}
    )
], className='bg-opacity-10 d-flex align-items-center justify-content-center', style={'height': '83%'})

no_churn_body = dbc.CardBody([
    dcc.Loading(
        children=[
            dcc.Graph(
                id='no',
                className='d-flex align-items-center justify-content-center',
                style={'height': '100%', 'width': '100%'}
            )
        ],
        type='dot',
        color='steelblue',
        parent_style={'height': '100%', 'width': '100%'}
    )
], className='bg-opacity-10 d-flex align-items-center justify-content-center', style={'height': '83%'})

yes_churn_body = dbc.CardBody([
    dcc.Loading(
        children=[
            dcc.Graph(
                id='yes',
                className='d-flex align-items-center justify-content-center',
                style={'height': '100%', 'width': '100%'}
            )
        ],
        type='dot',
        color='steelblue',
        parent_style={'height': '100%', 'width': '100%'}
    )
], className='bg-opacity-10 d-flex align-items-center justify-content-center', style={'height': '83%'})

cat = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([cat_main_header, cat_main_body], className='bg-secondary',
                     style={'height': '100%', 'width': '100%'})
        ], width=12, className='m-0',
            style={'height': '250px', 'paddingTop': '5px', 'paddingBottom': '5px', 'paddingLeft': '5px',
                   'paddingRight': '5px'})
    ], className='m-0 p-0'),
    dbc.Row([
        dbc.Col([
            dbc.Card([no_churn_header, no_churn_body], className='bg-secondary',
                     style={'height': '100%', 'width': '100%'})
        ], width=6, className='m-0',
            style={'height': '250px', 'paddingTop': '5px', 'paddingBottom': '10px', 'paddingLeft': '5px',
                   'paddingRight': '5px'}),
        dbc.Col([
            dbc.Card([yes_churn_header, yes_churn_body], className='bg-secondary',
                     style={'height': '100%', 'width': '100%'})
        ], width=6, className='m-0',
            style={'height': '250px', 'paddingTop': '5px', 'paddingBottom': '10px', 'paddingLeft': '5px',
                   'paddingRight': '5px'})
    ], className='m-0 p-0')
], className='m-0 p-0', fluid=True)

# Numerical Content

num_main_header = dbc.CardHeader(
    id='num-main-header',
    className='border-bottom border-secondary d-flex align-items-center justify-content-center',
    style={'height': '8.25%', 'textAlign': 'center', 'fontSize': '13px', 'fontWeight': 500, 'color': 'black'}
)

num_main_body = dbc.CardBody([
    dcc.Loading(
        children=[
            dcc.Graph(
                id='num-main-body',
                className='d-flex align-items-center justify-content-center',
                style={'height': '100%', 'width': '100%'}
            )
        ],
        type='dot',
        color='steelblue',
        parent_style={'height': '100%', 'width': '100%'}
    )
], className='bg-opacity-10 d-flex align-items-center justify-content-center', style={'height': '91.75%'})

num = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([num_main_header, num_main_body], className='bg-secondary',
                     style={'height': '100%', 'width': '100%'})
        ], width=12, className='m-0',
            style={'height': '500px', 'paddingTop': '5px', 'paddingBottom': '10px', 'paddingLeft': '5px',
                   'paddingRight': '5px'})
    ], className='m-0 p-0')
], className='m-0 p-0', fluid=True)

# Categorical Vs Numerical Content

catnum_main_header = dbc.CardHeader(
    id='catnum-main-header',
    className='border-bottom border-secondary d-flex align-items-center justify-content-center',
    style={'height': '8.25%', 'textAlign': 'center', 'fontSize': '13px', 'fontWeight': 500, 'color': 'black'}
)

catnum_main_body = dbc.CardBody([
    dcc.Loading(
        children=[
            dcc.Graph(
                id='catnum-main-body',
                className='d-flex align-items-center justify-content-center',
                style={'height': '100%', 'width': '100%'}
            )
        ],
        type='dot',
        color='steelblue',
        parent_style={'height': '100%', 'width': '100%'}
    )
], className='bg-opacity-10 d-flex align-items-center justify-content-center', style={'height': '91.75%'})

catnum = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([catnum_main_header, catnum_main_body], className='bg-secondary',
                     style={'height': '100%', 'width': '100%'})
        ], width=12, className='m-0',
            style={'height': '500px', 'paddingTop': '5px', 'paddingBottom': '10px', 'paddingLeft': '5px',
                   'paddingRight': '5px'})
    ], className='m-0 p-0')
], className='m-0 p-0', fluid=True)

# Numerical Vs Numerical Content

num2_main_header = dbc.CardHeader(
    id='num2-main-header',
    className='border-bottom border-secondary d-flex align-items-center justify-content-center',
    style={'height': '8.25%', 'textAlign': 'center', 'fontSize': '13px', 'fontWeight': 500, 'color': 'black'}
)

num2_main_body = dbc.CardBody([
    dcc.Loading(
        children=[
            dcc.Graph(
                id='num2-main-body',
                className='d-flex align-items-center justify-content-center',
                style={'height': '100%', 'width': '100%'}
            )
        ],
        type='dot',
        color='steelblue',
        parent_style={'height': '100%', 'width': '100%'}
    )
], className='bg-opacity-10 d-flex align-items-center justify-content-center', style={'height': '91.75%'})

num2 = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([num2_main_header, num2_main_body], className='bg-secondary',
                     style={'height': '100%', 'width': '100%'})
        ], width=12, className='m-0',
            style={'height': '500px', 'paddingTop': '5px', 'paddingBottom': '10px', 'paddingLeft': '5px',
                   'paddingRight': '5px'})
    ], className='m-0 p-0')
], className='m-0 p-0', fluid=True)

# App Layout

app.layout = dbc.Container([
    navbar,
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([title_header, title_body], className='bg-secondary',
                                 style={'height': '100%', 'width': '100%'})
                    ], width=12, className='m-0',
                        style={'height': '111px', 'paddingTop': '10px', 'paddingBottom': '5px', 'paddingLeft': '6px',
                               'paddingRight': '6px'})
                ], className='m-0 p-0'),
                dbc.Row([
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([churn_rate_header, churn_rate_body], className='bg-secondary',
                                         style={'height': '100%', 'width': '100%'})
                            ], width=12, className='m-0',
                                style={'height': '250px', 'paddingTop': '5px', 'paddingBottom': '5px',
                                       'paddingLeft': '5px', 'paddingRight': '6px'})
                        ], className='m-0 p-0'),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([churn_dist_header, churn_dist_body], className='bg-secondary',
                                         style={'height': '100%', 'width': '100%'})
                            ], width=12, className='m-0',
                                style={'height': '250px', 'paddingTop': '5px', 'paddingBottom': '10px',
                                       'paddingLeft': '5px', 'paddingRight': '6px'})
                        ], className='m-0 p-0')
                    ], width={'size': 12, 'order': 2}, sm={'size': 6, 'order': 2}, lg={'size': 3, 'order': 'first'},
                        className='m-0 p-0'),
                    dbc.Col(
                        id='content',
                        width={'size': 12, 'order': 'last'}, sm={'size': 12, 'order': 'last'},
                        lg={'size': 6, 'order': 2},
                        className='m-0 p-0'),
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([selector_header, selector_body], className='bg-secondary',
                                         style={'height': '100%', 'width': '100%'})
                            ], width=12, className='m-0',
                                style={'height': '500px', 'paddingTop': '5px', 'paddingBottom': '10px',
                                       'paddingLeft': '5px', 'paddingRight': '6px'})
                        ], className='m-0 p-0')
                    ], width={'size': 12, 'order': 'first'}, sm={'size': 6, 'order': 'first'},
                        lg={'size': 3, 'order': 'last'}, className='m-0 p-0')
                ], className='m-0 p-0 gx-0')
            ], width=12, sm=12, md=12, lg=12, xl=10, className='offset-xl-1 ps-1 pe-1')
        ], className='m-0 p-0')
    ], className='bg-white bg-opacity-10 m-0 p-0', fluid=True)
], className='m-0 p-0', fluid=True)


# App Callbacks

@app.callback(
    Output('var', 'disabled'),
    Output('cat-var', 'disabled'),
    Output('num-var', 'disabled'),
    Output('x-axis', 'disabled'),
    Output('y-axis', 'disabled'),
    Input('data-type', 'value')
)
def update_disabled_dropdown(selected_value):
    if selected_value is None:
        raise PreventUpdate
    else:
        disabled_true = True
        disabled_false = False
        if (selected_value == 'Categorical') or (selected_value == 'Numerical'):
            return disabled_false, disabled_true, disabled_true, disabled_true, disabled_true
        elif selected_value == 'Categorical Vs Numerical':
            return disabled_true, disabled_false, disabled_false, disabled_true, disabled_true
        else:
            return disabled_true, disabled_true, disabled_true, disabled_false, disabled_false


@app.callback(
    Output('var', 'options'),
    Output('var', 'value'),
    Input('data-type', 'value')
)
def update_options_value_variable(selected_value):
    if selected_value is None:
        raise PreventUpdate
    else:
        if selected_value == 'Categorical':
            options = [{'label': x, 'value': x} for x in cat_var]
            value = options[0]['value']
            return options, value
        elif selected_value == 'Numerical':
            options = [{'label': x, 'value': x} for x in num_var]
            value = options[0]['value']
            return options, value
        else:
            raise PreventUpdate


@app.callback(
    Output('y-axis', 'options'),
    Output('y-axis', 'value'),
    Input('x-axis', 'value')
)
def update_options_value_yaxis(selected_value):
    if selected_value is None:
        raise PreventUpdate
    else:
        options = [{'label': x, 'value': x} for x in all_options_num[selected_value]]
        value = options[0]['value']
        return options, value


@app.callback(
    Output('title-header', 'children'),
    Input('button', 'n_clicks'),
    State('data-type', 'value')
)
def update_title_header(n_clicks, selected_value):
    if selected_value is None:
        raise PreventUpdate
    else:
        title_header = '{} Data'.format(selected_value)
        return title_header


@app.callback(
    Output('content', 'children'),
    Input('button', 'n_clicks'),
    State('data-type', 'value')
)
def update_content(n_clicks, selected_value):
    if selected_value is None:
        raise PreventUpdate
    else:
        if selected_value == 'Categorical':
            return cat
        elif selected_value == 'Numerical':
            return num
        elif selected_value == 'Categorical Vs Numerical':
            return catnum
        else:
            return num2


@app.callback(
    Output('cat-main-header', 'children'),
    Output('no-header', 'children'),
    Output('yes-header', 'children'),
    Input('button', 'n_clicks'),
    State('var', 'value')
)
def update_cat_main_header(n_clicks, selected_value):
    if selected_value is None:
        raise PreventUpdate
    else:
        main_header = '{} Distribution W.R.T Churn'.format(selected_value)
        no_header = '% by {} (Churn = No)'.format(selected_value)
        yes_header = '% by {} (Churn = Yes)'.format(selected_value)
        return main_header, no_header, yes_header


@app.callback(
    Output('cat-main-body', 'figure'),
    Input('button', 'n_clicks'),
    State('var', 'value')
)
def update_cat_main_body(n_clicks, selected_value):
    if selected_value is None:
        raise PreventUpdate
    else:
        fig = go.Figure()
        color_map = {'No': 'dodgerblue', 'Yes': 'darkorange'}
        for i in df['Churn'].unique():
            fig.add_trace(
                go.Histogram(
                    histfunc='count',
                    y=df.loc[df['Churn'] == i][selected_value],
                    marker=dict(
                        color=color_map[i]
                    ),
                    name=i,
                    customdata=[selected_value for i in df[selected_value].unique()],
                    hovertemplate=
                    '<i style="color:white;"><b>%{customdata}:</b> %{y}</i><br>' +
                    '<i style="color:white;"><b>Count:</b> %{x}</i><br>' +
                    '<extra></extra>'
                )
            )
        fig.update_layout(
            font=dict(
                family='Arial',
                color='black'
            ),
            xaxis=dict(
                title='Count',
                showline=False,
                showgrid=False,
                zeroline=False,
                showticklabels=True,
                tickfont=dict(
                    family='Arial',
                    size=11,
                    color='black'
                )
            ),
            yaxis=dict(
                showline=False,
                showgrid=False,
                zeroline=False,
                showticklabels=True,
                tickfont=dict(
                    family='Arial',
                    size=11,
                    color='black'
                )
            ),
            legend=dict(
                title='Churn',
                orientation='h',
                yanchor='bottom',
                y=1,
                xanchor='right',
                x=1,
                font=dict(
                    family='Arial',
                    size=10,
                    color='black'
                )
            ),
            bargap=0.2,
            barmode='group',
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)'
        )
        return fig


@app.callback(
    Output('no', 'figure'),
    Input('button', 'n_clicks'),
    State('var', 'value')
)
def update_no(n_clicks, selected_value):
    if selected_value is None:
        raise PreventUpdate
    else:
        fig = go.Figure()
        fig.add_trace(
            go.Pie(
                labels=df.loc[df['Churn'] == 'No', selected_value].value_counts().index,
                values=df.loc[df['Churn'] == 'No', selected_value].value_counts().values
            )
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont=dict(
                family='Arial',
                color='white'
            ),
            marker=dict(
                colors=['dodgerblue' for x in df.loc[df['Churn'] == 'No', selected_value].unique()],
                line=dict(
                    color='white',
                    width=1
                )
            ),
            hovertemplate=
            '<i style="color:white;"><b>%{label}</b></i><br>' +
            '<i style="color:white;">%{percent}</i><br>' +
            '<extra></extra>'
        )
        fig.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)'
        )
        return fig


@app.callback(
    Output('yes', 'figure'),
    Input('button', 'n_clicks'),
    State('var', 'value')
)
def update_yes(n_clicks, selected_value):
    if selected_value is None:
        raise PreventUpdate
    else:
        fig = go.Figure()
        fig.add_trace(
            go.Pie(
                labels=df.loc[df['Churn'] == 'Yes', selected_value].value_counts().index,
                values=df.loc[df['Churn'] == 'Yes', selected_value].value_counts().values
            )
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont=dict(
                family='Arial',
                color='white'
            ),
            marker=dict(
                colors=['darkorange' for x in df.loc[df['Churn'] == 'Yes', selected_value].unique()],
                line=dict(
                    color='white',
                    width=1
                )
            ),
            hovertemplate=
            '<i style="color:white;"><b>%{label}</b></i><br>' +
            '<i style="color:white;">%{percent}</i><br>' +
            '<extra></extra>'
        )
        fig.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)'
        )
        return fig


@app.callback(
    Output('num-main-header', 'children'),
    Input('button', 'n_clicks'),
    State('var', 'value')
)
def update_num_main_header(n_clicks, selected_value):
    if selected_value is None:
        raise PreventUpdate
    else:
        main_header = '{} Distribution W.R.T Churn'.format(selected_value)
        return main_header


@app.callback(
    Output('num-main-body', 'figure'),
    Input('button', 'n_clicks'),
    State('var', 'value')
)
def update_num_main_body(n_clicks, selected_value):
    if selected_value is None:
        raise PreventUpdate
    else:
        fig = go.Figure()
        color_map = {'No': 'dodgerblue', 'Yes': 'darkorange'}
        for i in df['Churn'].unique():
            fig.add_trace(
                go.Histogram(
                    histfunc='count',
                    x=df.loc[df['Churn'] == i][selected_value],
                    marker=dict(
                        color=color_map[i]
                    ),
                    name=i,
                    customdata=[selected_value for i in df[selected_value].unique()],
                    hovertemplate=
                    '<i style="color:white;"><b>%{customdata}:</b> %{x}</i><br>' +
                    '<i style="color:white;"><b>Count:</b> %{y}</i><br>' +
                    '<extra></extra>'
                )
            )
        if selected_value == 'Tenure':
            fig.update_layout(
                xaxis_title='{} (in Month)'.format(selected_value)
            )
        else:
            fig.update_layout(
                xaxis_title='{}'.format(selected_value),
                xaxis_tickformat='$'
            )
        fig.update_layout(
            font=dict(
                family='Arial',
                color='black'
            ),
            xaxis=dict(
                showline=True,
                showgrid=True,
                zeroline=False,
                linewidth=1.5,
                gridwidth=0.5,
                showticklabels=True,
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='black'
                )
            ),
            yaxis=dict(
                title='Count',
                showline=True,
                showgrid=True,
                zeroline=False,
                linewidth=1.5,
                gridwidth=0.5,
                showticklabels=True,
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='black'
                )
            ),
            legend=dict(
                title='Churn',
                orientation='h',
                yanchor='bottom',
                y=1,
                xanchor='right',
                x=1,
                font=dict(
                    family='Arial',
                    size=10,
                    color='black'
                )
            ),
            bargap=0.2,
            barmode='group',
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)'
        )
        return fig


@app.callback(
    Output('catnum-main-header', 'children'),
    Input('button', 'n_clicks'),
    State('cat-var', 'value'),
    State('num-var', 'value')
)
def update_catnum_main_header(n_clicks, selected_value1, selected_value2):
    if ((selected_value1 is None) or (selected_value2 is None)):
        raise PreventUpdate
    else:
        main_header = '{} vs {} W.R.T. Churn'.format(selected_value1, selected_value2)
        return main_header


@app.callback(
    Output('catnum-main-body', 'figure'),
    Input('button', 'n_clicks'),
    State('cat-var', 'value'),
    State('num-var', 'value')
)
def update_catnum_main_body(n_clicks, selected_value1, selected_value2):
    if ((selected_value1 is None) or (selected_value2 is None)):
        raise PreventUpdate
    else:
        fig = go.Figure()
        color_map = {'No': 'dodgerblue', 'Yes': 'darkorange'}
        for i in df['Churn'].unique():
            fig.add_trace(
                go.Box(
                    x=df.loc[df['Churn'] == i][selected_value1],
                    y=df.loc[df['Churn'] == i][selected_value2],
                    marker=dict(
                        color=color_map[i]
                    ),
                    name=i,
                    customdata=np.stack(([selected_value1 for z in df[selected_value1]],
                                         [selected_value2 for z in df[selected_value2]]), axis=-1),
                    hovertemplate=
                    '<i style="color:white;"><b>%{customdata[0]}:</b> %{x}</i><br>' +
                    '<i style="color:white;"><b>%{customdata[1]}:</b> %{y}</i><br>' +
                    '<extra></extra>'
                )
            )
        if selected_value2 == 'Tenure':
            fig.update_layout(
                yaxis_title='{} (in Month)'.format(selected_value2)
            )
        else:
            fig.update_layout(
                yaxis_title='{}'.format(selected_value2),
                yaxis_tickformat='$'
            )
        fig.update_layout(
            font=dict(
                family='Arial',
                color='black',
            ),
            xaxis=dict(
                title='{}'.format(selected_value1),
                showline=False,
                showgrid=False,
                zeroline=False,
                showticklabels=True,
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='black'
                )
            ),
            yaxis=dict(
                showline=False,
                showgrid=True,
                zeroline=False,
                gridwidth=1.5,
                showticklabels=True,
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='black'
                )
            ),
            legend=dict(
                title='Churn',
                orientation='h',
                yanchor='bottom',
                y=1,
                xanchor='right',
                x=1,
                font=dict(
                    family='Arial',
                    size=12,
                    color='black'
                )
            ),
            boxmode='group',
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)'
        )
        return fig


@app.callback(
    Output('num2-main-header', 'children'),
    Input('button', 'n_clicks'),
    State('x-axis', 'value'),
    State('y-axis', 'value')
)
def update_num2_main_header(n_clicks, selected_value1, selected_value2):
    if ((selected_value1 is None) or (selected_value2 is None)):
        raise PreventUpdate
    else:
        main_header = '{} vs {} W.R.T. Churn'.format(selected_value1, selected_value2)
        return main_header


@app.callback(
    Output('num2-main-body', 'figure'),
    Input('button', 'n_clicks'),
    State('x-axis', 'value'),
    State('y-axis', 'value')
)
def update_num2_main_body(n_clicks, selected_value1, selected_value2):
    if ((selected_value1 is None) or (selected_value2 is None)):
        raise PreventUpdate
    else:
        fig = go.Figure()
        color_map = {'No': 'dodgerblue', 'Yes': 'darkorange'}
        for i in df['Churn'].unique():
            fig.add_trace(
                go.Scatter(
                    x=df.loc[df['Churn'] == i][selected_value1],
                    y=df.loc[df['Churn'] == i][selected_value2],
                    mode='markers',
                    marker=dict(
                        color=color_map[i]
                    ),
                    name=i,
                    customdata=np.stack(([selected_value1 for z in df[selected_value1]],
                                         [selected_value2 for z in df[selected_value2]]), axis=-1),
                    hovertemplate=
                    '<i style="color:white;"><b>%{customdata[0]}:</b> %{x}</i><br>' +
                    '<i style="color:white;"><b>%{customdata[1]}:</b> %{y}</i><br>' +
                    '<extra></extra>'
                )
            )
        if selected_value1 == 'Tenure':
            fig.update_layout(
                xaxis_title='{} (in Month)'.format(selected_value1)
            )
        else:
            fig.update_layout(
                xaxis_title='{}'.format(selected_value1),
                xaxis_tickformat='$'
            )
        if selected_value2 == 'Tenure':
            fig.update_layout(
                yaxis_title='{} (in Month)'.format(selected_value2)
            )
        else:
            fig.update_layout(
                yaxis_title='{}'.format(selected_value2),
                yaxis_tickformat='$'
            )
        fig.update_layout(
            font=dict(
                family='Arial',
                color='black'
            ),
            xaxis=dict(
                showline=True,
                showgrid=True,
                zeroline=False,
                linewidth=2.5,
                gridwidth=1.5,
                showticklabels=True,
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='black'
                )
            ),
            yaxis=dict(
                showline=True,
                showgrid=True,
                zeroline=False,
                linewidth=2.5,
                gridwidth=1.5,
                showticklabels=True,
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='black'
                )
            ),
            legend=dict(
                title='Churn',
                orientation='h',
                yanchor='bottom',
                y=1,
                xanchor='right',
                x=1,
                font=dict(
                    family='Arial',
                    size=12,
                    color='black'
                )
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)'
        )
        return fig

if __name__ == '__main__':
    app.run_server(debug=True)