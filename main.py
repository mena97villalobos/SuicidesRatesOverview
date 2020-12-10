import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from translatable_text_en import *
import pandas as pd

from utils import *

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

originalData = pd.read_excel(SUICIDE_DATA_PATH)
dataHolder = DataHolder(originalData, [originalData[YEAR].min(), originalData[YEAR].max()])
multiAxisColumns = [SEX, AGE, GENERATION]

app.layout = html.Div([
    dbc.Navbar([
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src=app.get_asset_url(SUICIDE_LOGO), height="40px"), width=2),
                    dbc.Col(dbc.NavbarBrand(MAIN_TITLE, className="ml-10"), width=10, align="center"),
                ],
                align="center",
                no_gutters=True,
            ),
        )
    ],
        color="dark",
        dark=True,
    ),

    html.Br(),

    html.Div([
        html.Div([
            html.H3(YEAR_FILTER_LABEL),
            dcc.RangeSlider(
                id="year-filter",
                marks={i: str(i) for i in range(1985, 2017)},
                min=1985,
                max=2016,
                value=[1985, 2016]
            )
        ]),

        html.Br(),

        html.Div([
            html.H3(SUICIDES_COUNTRIES_GRAPH_LABEL),
            dcc.Dropdown(
                id='country-selection',
                options=[{'label': country, 'value': country} for country in
                         get_unique_column_values(originalData, COUNTRY)],
                multi=True,
                placeholder=COUNTRIES_FILTER_PLACEHOLDER,
            ),
            dcc.Graph(id='suicides-country')
        ]),

        html.Br(),

        dbc.Row([
            dbc.Col(
                html.Div([
                    html.H3(SUICIDES_GENERATION_GRAPH_LABEL),
                    dcc.Graph(id="pie-chart")
                ])
            ),
            dbc.Col(
                html.Div([
                    html.H3(SUICIDES_GENDER_YEAR_GRAPH_LABEL),
                    dcc.Graph(id="lines-chart")
                ]),
            )
        ]),

        html.Br(),

        html.Div([
            html.H3(SUICIDES_COUNTRY_MAP_GRAPH_LABEL),
            dcc.Graph(id="map-chart")
        ]),

        html.Div([
            html.H3(MULTI_AXIS_GRAPH_LABEL),
            dcc.Dropdown(
                id='multi-axis-selection',
                options=[{'label': column_name, 'value': column_name} for column_name in multiAxisColumns],
                value=multiAxisColumns[0],
                multi=False,
                placeholder=MULTI_AXIS_PLACEHOLDER
            ),
            dcc.Graph(id="multi-axis-graph")
        ])
    ], style={"marginLeft": "10px", "marginRight": "10px"})
])


@app.callback(
    Output('multi-axis-graph', 'figure'),
    [
        Input('multi-axis-selection', 'value'),
        Input('year-filter', 'value')
    ]
)
def update_multi_axis_graph(selected_column, years_selected):
    filtered_data = dataHolder.get_filtered_data(years_selected)
    graph_dataset = filtered_data[[selected_column, SUICIDES]].groupby([selected_column]).sum().reset_index()
    return create_graph_bar(graph_dataset, selected_column, SUICIDES)


@app.callback(
    Output('suicides-country', 'figure'),
    [
        Input('country-selection', 'value'),
        Input('year-filter', 'value')
    ])
def update_suicide_country_graph(countries_selected, years_selected):
    filtered_data = dataHolder.get_filtered_data(years_selected)
    suicides_country = filtered_data[[COUNTRY, SUICIDES]].groupby([COUNTRY]).sum().reset_index()

    if countries_selected is not None and countries_selected != []:
        suicides_country = suicides_country[suicides_country[COUNTRY].isin(countries_selected)]
    return create_graph_bar(suicides_country, COUNTRY, SUICIDES)


@app.callback(
    Output('pie-chart', 'figure'),
    Input('year-filter', 'value')
)
def update_generation_suicide_graph(years_selected):
    filtered_data = dataHolder.get_filtered_data(years_selected)

    generation_suicides = filtered_data[[GENERATION, SUICIDES]].groupby([GENERATION]).sum().reset_index()
    return px.pie(filtered_data, values=generation_suicides[SUICIDES], names=generation_suicides[GENERATION])


@app.callback(
    Output('lines-chart', 'figure'),
    Input('year-filter', 'value')
)
def update_line_chart(years_selected):
    filtered_data = dataHolder.get_filtered_data(years_selected)

    scatter_data = filtered_data[[YEAR, SEX, SUICIDES]].groupby([YEAR, SEX]).sum().reset_index()
    return px.line(scatter_data, x=YEAR, y=SUICIDES, color=SEX)


@app.callback(
    Output('map-chart', 'figure'),
    Input('year-filter', 'value')
)
def update_map_chart(years_selected):
    filtered_data = dataHolder.get_filtered_data(years_selected)

    map_data = filtered_data[[COUNTRY, SUICIDES]].groupby([COUNTRY]).sum().reset_index()
    return px.scatter_geo(
        map_data,
        locations=COUNTRY,
        locationmode='country names',
        color=COUNTRY,
        hover_name=SUICIDES,
        size=SUICIDES,
        projection="natural earth"
    )


if __name__ == '__main__':
    app.run_server(debug=True)
