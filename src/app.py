import dash
from dash import html
from dash.dependencies import Output, Input
from dash import dcc
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

# read in data
data = pd.read_csv("/Users/mahinthankugendiran/Desktop/CrimeBahaviourProject/crime_behavior_app/src/clean_crime_canada_dataset.csv")
data["year"] = data["year"].astype(int)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Group 4 - Data Analytics Project"
server = app.server

app.layout = dbc.Container(
    html.Div([
        html.Hr(),
        dbc.Row([
            dbc.Col(
                [
                    html.Label("Years"),
                    dcc.Dropdown(
                        id="year-selector",
                        options=[{"label": year, "value": year} for year in data["year"].unique()],
                        value=data["year"].max(),
                        clearable=False
                    ),
                ],
                md=3,
            ),
            dbc.Col(
                [
                    html.Label("Locations"),
                    dcc.Dropdown(
                        id="location-selector",
                        options=[{"label": location, "value": location} for location in data["location"].unique()],
                        placeholder="Select a location",
                    ),
                ],
                md=3,
            ),
            dbc.Col(
                [
                    html.Label("Types of Crimes"),
                    dcc.Dropdown(
                        id="crimes-type-selector",
                        options=[{"label": type, "value": type} for type in data["type_of_crime"].unique()],
                        placeholder="Select a crime type",
                    ),
                ],
                md=3,
            ),
            dbc.Col(
                html.Div([
                    html.H4("Total Crimes", className="card-title"),
                    html.P(id="incidents-total"),
                ]),
                md=3,
            ),
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.H5()
            ], md=7),
            dbc.Col(dcc.Tabs(
                id="low-high-selector",
                children=[
                    dcc.Tab(label="Highest", value="highest"),
                    dcc.Tab(label="Lowest", value="lowest")
                ],
                value='highest',  # default value
            ), md=5),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(
                id="graphs-by-selection",
            ), md=7),
            dbc.Col(dcc.Graph(
                id="graphs-top-n-results",
            ), md=5),
        ]),
    ])
)

# Define the second callback
@app.callback(
    [
        Output("incidents-total", "children"),
        Output("graphs-by-selection", "figure"),
        Output("graphs-top-n-results", "figure"),
    ],
    [
        Input("year-selector", "value"),
        Input("location-selector", "value"),
        Input("crimes-type-selector", "value"),
        Input("low-high-selector", "value"),
    ]
)
def update_graphs(selected_year: int, selected_location: str, selected_type: str, radioButtonValue: str):
    incidents_total = data[data["year"] == selected_year]["incidents"].sum(numeric_only=True)
    if isinstance(selected_year, int) and selected_year is not None and selected_year >= 0:
        # year, location, type filters selected
        if selected_location is not None and len(selected_location) > 0 and selected_type is not None and len(selected_type) > 0:
            filtered_df = data.loc[(data["year"] == selected_year) & (data["location"] == selected_location) & (data["type_of_crime"] == selected_type)]

            assert isinstance(filtered_df, object)
            filtered_df["x"] = str(selected_year) + "," + selected_location + "," + selected_type# filtered_df["year"].astype(str) + ", " + filtered_df["location"] + ", " + filtered_df["type_of_crime"]
            fig1 = px.bar(
                filtered_df,
                title=f"Number of {selected_type} Crimes in {selected_year} in {selected_location}",
                x='x',
                y='incidents',
                labels={
                    'x': 'Year, Location, Type of Crime',
                    'incidents': 'No. of Crimes'
                },
                color_discrete_sequence=px.colors.qualitative.Alphabet
            )
            filtered_df = data.loc[(data["year"] == selected_year) & (data["type_of_crime"] == selected_type)]
            incidents_by_locations = filtered_df.groupby("location").sum(numeric_only=True)["incidents"]
            if radioButtonValue == "highest":
                top5_crimes_by_location = incidents_by_locations.nlargest(5)
                fig2 = px.pie(
                    names=top5_crimes_by_location.index,
                    values=top5_crimes_by_location.values,
                    title=f"Highest crimes in {selected_year} in {selected_type}",
                    color_discrete_sequence=px.colors.qualitative.Dark2
                )
            else:
                top5_crimes_by_location = incidents_by_locations.nsmallest(5)
                fig2 = px.pie(
                    names=top5_crimes_by_location.index,
                    values=top5_crimes_by_location.values,
                    title=f"Lowest crimes in {selected_year} in {selected_type}",
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
            # year and location selected, type is not selected
        elif (selected_location is not None and len(selected_location) > 0) and (selected_type is None):
            filtered_df = data.loc[(data["year"] == selected_year) & (data["location"] == selected_location)]
            incidents_by_crime_type = filtered_df.groupby("type_of_crime").sum(numeric_only=True)["incidents"]
            fig1 = px.bar(
                incidents_by_crime_type,
                title=f"Number of Crimes by Type in {selected_year} in {selected_location}",
                x=incidents_by_crime_type.index,
                y='incidents',
                labels={
                    'type_of_crime': 'Type of Crimes',
                    'incidents': 'No. of Crimes'
                },
                color_discrete_sequence=px.colors.qualitative.Light24
            )
            if radioButtonValue == "highest":
                top5_crimes_by_type = incidents_by_crime_type.nlargest(5)
                fig2 = px.pie(
                    names=top5_crimes_by_type.index,
                    values=top5_crimes_by_type.values,
                    title=f"Highest crimes in {selected_year} in {selected_location}",
                    color_discrete_sequence=px.colors.qualitative.Dark2
                )
            else:
                top5_crimes_by_type = incidents_by_crime_type.nsmallest(5)
                fig2 = px.pie(
                    names=top5_crimes_by_type.index,
                    values=top5_crimes_by_type.values,
                    title=f"Lowest crimes in {selected_year} in {selected_location}",
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
            # year and type are selected, location is not selected
        elif (selected_location is None) and (selected_type is not None and len(selected_type) > 0):
            filtered_df = data.loc[(data["year"] == selected_year) & (data["type_of_crime"] == selected_type)]
            incidents_by_locations = filtered_df.groupby("location").sum(numeric_only=True)["incidents"]
            fig1 = px.bar(
                incidents_by_locations,
                title=f"Number of Crimes by locations in {selected_year} in {selected_type}",
                x=incidents_by_locations.index,
                y='incidents',
                labels={
                    'location': 'Locations',
                    'incidents': 'No. of Crimes'
                },
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            if radioButtonValue == "highest":
                top5_crimes_by_location = incidents_by_locations.nlargest(5)
                fig2 = px.pie(
                    names=top5_crimes_by_location.index,
                    values=top5_crimes_by_location.values,
                    title=f"Highest crimes in {selected_year} in {selected_type}",
                    color_discrete_sequence=px.colors.qualitative.Dark2
                )
            else:
                top5_crimes_by_location = incidents_by_locations.nsmallest(5)
                fig2 = px.pie(
                    names=top5_crimes_by_location.index,
                    values=top5_crimes_by_location.values,
                    title=f"Lowest crimes in {selected_year} in {selected_type}",
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
        # only year is selected, in the dashboard landing page view
        else:
            incidents_by_year = data.groupby("year").sum(numeric_only=True)["incidents"]
            fig1 = px.line(
                incidents_by_year,
                title=f"Number of all types of crimes by Year in all the locations",
                x=incidents_by_year.index,
                y='incidents',
                labels={
                    'year': 'Years',
                    'incidents': 'No. of Crimes'
                },
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            if radioButtonValue == "highest":
                top_5_crimes_by_year = incidents_by_year.nlargest(5)
                # Plot the top 5 crimes by year in a pie chart
                fig2 = px.pie(
                    names=top_5_crimes_by_year.index,
                    values=top_5_crimes_by_year.values,
                    title="Highest crimes recorded years",
                    color_discrete_sequence=px.colors.qualitative.Dark2
                )
            else:
                top_5_crimes_by_year = incidents_by_year.nsmallest(5)
                # Plot the lowest 5 crimes by year in a pie chart
                fig2 = px.pie(
                    names=top_5_crimes_by_year.index,
                    values=top_5_crimes_by_year.values,
                    title="Lowest crimes recorded years",
                    color_discrete_sequence=px.colors.qualitative.Safe
                )

    return incidents_total, fig1, fig2


if __name__ == "__main__":
    app.run_server(debug=True)
