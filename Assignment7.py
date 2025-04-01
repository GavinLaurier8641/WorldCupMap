# Load packages
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

# Create Data set
wc_data = pd.DataFrame({
    "Winner": ["URY", "ITA", "ITA", "URY", "DEU", "BRA", "BRA", "GBR", "BRA", "DEU", "ARG", "ITA", "ARG", "DEU", "BRA", "FRA", "BRA", "ITA", "ESP", "DEU", "FRA", "ARG"],
    "Runner Up": ["ARG", "CZE", "HUN", "BRA", "HUN", "SWE", "CZE", "DEU", "ITA", "NLD", "NLD", "DEU", "DEU", "ARG", "ITA", "BRA", "DEU", "FRA", "NLD", "ARG", "CRO", "FRA"],
    "Year": [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022]
})

code_to_country = {
    "URY": "Uruguay",
    "ITA": "Italy",
    "DEU": "Germany",
    "BRA": "Brazil",
    "GBR": "England",
    "ARG": "Argentina",
    "CZE": "Czechoslovakia",
    "HUN": "Hungary",
    "SWE": "Sweden",
    "NLD": "Netherlands",
    "FRA": "France",
    "ESP": "Spain",
    "CRO": "Croatia"
}

wc_data["Winner Full"] = wc_data["Winner"].map(code_to_country)
wc_data["Runner Up Full"] = wc_data["Runner Up"].map(code_to_country)

# Create Dashboard
app = dash.Dash()

app.layout = html.Div([
    html.H1("World Cup Finals Map", style={"textAlign": "center", "color": "black", 'font-weight': 'bold', "font-family":"Arial black"}),

    html.Div([
        html.Label("Select Mode:", style={"color": "black", 'font-weight': 'bold'}),
        dcc.RadioItems(
            id="mode-radio",
            options=[
                {"label": "All-time Winners", "value": "all"},
                {"label": "Specific Year", "value": "year"}
            ],
            value="all",
            labelStyle={'display': 'inline-block', 'margin-right': '20px', "color": "black"}
        ),
    ], style={"margin-bottom": "20px"}),

    html.Div([
        html.Label("Select Year:", style={"color": "black", 'font-weight': 'bold'}),
        dcc.Dropdown(
            id="year-dropdown",
            options=[{"label": y, "value": y} for y in wc_data["Year"].unique()],
            value=1930,
            clearable=False
        )
    ], id="year-dropdown-container", style={"width": "45%", "margin-bottom": "30px", "display": "none"}),

    html.Div([
        html.Label("Select a country and view the number of times it has won the World Cup:",
            style={"color": "black", 'font-weight': 'bold'}),

        dcc.Dropdown(
            id="country-dropdown",
            options=[{"label": c, "value": c} for c in sorted(wc_data["Winner Full"].unique())],
            placeholder="Select a country",
            style={"width": "45%"}
        ),

        html.Div(id="country-win-output", style={"color": "black", "margin-top": "10px", "fontSize": 18})
    ]),


    dcc.Graph(id="map-chart", style={"margin-top":"30px"})
], style={"background":"white",
        "padding": "20px"})



@app.callback(
    Output("year-dropdown-container", "style"),
    Input("mode-radio", "value")
)
def toggle_dropdown_visibility(mode):
    if mode == "year":
        return {"width": "45%", "margin-bottom": "30px", "display": "block"}
    return {"display": "none"}

@app.callback(
    Output("country-win-output", "children"),
    Input("country-dropdown", "value")
)

def display_country_wins(country):
    if not country:
        return ""
    count = wc_data[wc_data["Winner Full"] == country].shape[0]
    
    return f"{country} has won the World Cup {count} time{'s' if count != 1 else ''}."

@app.callback(
    Output("map-chart", "figure"),
    Input("mode-radio", "value"),
    Input("year-dropdown", "value")
)

def update_choropleth(mode, year):
    if mode == "all":
        all_winners = wc_data[["Winner"]].drop_duplicates()
        all_winners["Country"] = all_winners["Winner"]
        all_winners["Result"] = "Past Winner"

        fig = px.choropleth(
            all_winners,
            locations="Country",
            locationmode="ISO-3",
            color="Country",
            color_discrete_map={"Past Winner": "green"},
            scope="world",
            width=1025,
            height=550
            )
        
        fig.update_layout(
            title=dict(
                text="All-Time World Cup Winners",
                x=0.5,
                y=0.95,
                xanchor='center',
                yanchor='top',
                font=dict(
                    size=24,
                    color='black',
                    family='Arial Black'
                )
            ),
            legend=dict(
                x=1,
                y=1
            )
)
    else:
        filtered_data = wc_data[wc_data["Year"] == year]
        if filtered_data.empty:
            return px.choropleth(title=f"No data for {year}")

        selected = pd.DataFrame({
            "Country": [filtered_data["Winner"].values[0], filtered_data["Runner Up"].values[0]],
            "Result": ["Winner", "Runner Up"]
        })

        fig = px.choropleth(
            selected,
            locations="Country",
            locationmode="ISO-3",
            color="Result",
            color_discrete_map={"Winner": "gold", "Runner Up": "blue"},
            scope="world",
            width=1025,
            height=550
        )

        fig.update_layout(
            title=dict(
                text=f"World Cup Finalists - {year}",
                x=0.5,
                y=0.95,
                xanchor='center',
                yanchor='top',
                font=dict(
                    size=24,
                    color='black',
                    family='Arial Black'
                    )
                ),

            legend=dict(
                x=1,
                y=1
            )
            )

    return fig
if __name__ == '__main__':
    app.run_server(debug=True)

