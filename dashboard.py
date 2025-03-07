import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash import callback_context
import psycopg2
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
import json
import io
import base64
from psycopg2 import pool
import traceback
import altair as alt
import time
from dash import dash_table
import numpy as np
from calendar import month_abbr
import requests
import sys

#loading the .json file for the chloropleth as it has all the boundaries for the provinces
with open("C:/Users/syedk/Documents/updated_investigation_project/investigation_new_2/investigation_project_v2-master/za.json") as f:
    geojson_data = json.load(f)

# Database connection
conn = psycopg2.connect(
    host="localhost", port="5432", database="homicide_main",
    user="postgres", password="Khiz1234")

engine = create_engine("postgresql://postgres:Khiz1234@localhost:5432/homicide_main")

# Define options for provinces in South Africa and the corresponding cities present in those provinces
provinces = {
    'Western Cape': ['Cape Town', 'Stellenbosch', 'George', 'Beauford West', 'Mossel Bay', 'Worcester', 'Knysna', 'Swellendam', 'Ladismith', 'Laingsburg'],
    'Eastern Cape': ['Port Elizabeth', 'East London', 'Grahamstown', 'Komani', 'KwaMaqoma', 'Tarkhastad', 'Tlokoeng', 'Qonce'],
    'Gauteng': ['Johannesburg', 'Pretoria', 'Soweto', 'Refilwe', 'Roodepoort', 'Vanderbijlpark', 'Krugersdorp', 'Alberton', 'Thembisa', 'Benoni'],
    'Northern Cape' : ['Kimberley', 'Britstown', 'Hopetown', 'Garies', 'De Aar', 'Prieska', 'Pofadder', 'Victoria West', 'Nababeep'],
    'Free State' : ['Bethlehem', 'Heilbron', 'Reitz', 'Senekal', 'Frankfort', 'Vrede', 'Excelsior', 'Frankfort', 'Cornelia', 'Warden'],
    'Mpumalanga': ['Ermalo', 'Komatipoort', 'eNtokozweni', 'eMakhazeni', 'eMalahleni', 'Emgwenya', 'Sabie', 'Mbombela', 'Pilgrims Rest'],
    'KwaZulu-Natal' : ['Durban', 'Ixopo', 'Ubombo', 'KwaDukuza', 'Richmond', 'Bulwer', 'Wartburg', 'Newcastle', 'Umzimkulu'],
    'Limpopo' : ['Polokwane', 'Bela-Bela', 'Phalaborwa', 'Haenertsberg', 'Lephalale', 'Mokopane', 'Louis Trichardt', 'Tzaneen', 'Hoedspruit' ],
    'North West' : ['Mahikeng', 'Chirstiana', 'Rustenburg', 'Schweizer-Reneke', 'Ganyesa', 'Koster', 'Delareyville', 'Bloemhof', 'Brits']
    # Add more provinces and towns here
}

#Define race options for victim race
race_options = [
    {'label': 'African', 'value': 'African'},
    {'label': 'White', 'value': 'White'},
    {'label': 'Coloured', 'value': 'Coloured'},
    {'label': 'Indian/Asian', 'value': 'Indian/Asian'},
    {'label': 'Other', 'value': 'Other'}
]

#Define relationship options for perpetrator relationship
relationship_options = [
    {'label': 'Family', 'value': 'Family'},
    {'label': 'Friend', 'value': 'Friend'},
    {'label': 'Acquaintance', 'value': 'Acquaintance'},
    {'label': 'Stranger', 'value': 'Stranger'},
    {'label': 'Affair', 'value': 'Affair'},
    {'label': 'Criminal', 'value': 'Criminal'},
    {'label': 'Ex-partner', 'value': 'Ex-partner'},
    {'label': 'Labourer', 'value': 'Labourer'},
    {'label': 'Neighbour', 'value': 'Neighbour'},
    {'label': 'Police', 'value': 'Police'},
    {'label': 'Romantic partner', 'value': 'Romantic partner'},
    {'label': 'Spouse', 'value': 'Spouse'},
    {'label': 'Unknown', 'value': 'Unknown'},
    {'label': 'Other', 'value': 'Other'}
]

#Define boolean options for sexual assault, intimate femicide, multiple murders, suspect arrested, suspect convicted, robbery and extreme violence
bool_options = [
    {'label': 'Yes', 'value': 'Y'},
    {'label': 'No', 'value': 'N'},
    {'label': 'Unknown', 'value': 'Unknown'}
]

#This is to make the months in a year be in month rather than alphabetical order
def get_month_order(month):
    return list(month_abbr).index(month[:3].title())

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)



# Navbar which shows all the functionality of the dashboard
navbar = dbc.NavbarSimple(
    brand="Homicide Media Tracker",
    color="primary",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Data Entry", href="/")),
        dbc.NavItem(dbc.NavLink("Data Import", href="/import")),
        dbc.NavItem(dbc.NavLink("Data Display", href="/display")),
        dbc.NavItem(dbc.NavLink("Delete Data", href = "/delete_table")),
        dbc.NavItem(dbc.NavLink("Duplicate Data", href = "/duplicate_data")),
        dbc.NavItem(dbc.NavLink("Data Visualization", href="/visualization")),
        dbc.NavItem(dbc.NavLink("Custom Data Visualization", href="/custom_visualization"))
    ]
)

# Footer
footer = html.Footer(
    "Homicide Media Tracker © 2024",
    style={'text-align': 'center', 'padding': '20px', 'background': '#f1f1f1'}
)

# Data Entry Layout
data_entry_layout = dbc.Container([
    dbc.Card([
        dbc.CardHeader("Homicide Data Entry"),
        dbc.CardBody([
            dbc.Row([dbc.Col([dbc.Label("News Report URL"), dbc.Input(id='url-input', type='text', placeholder="Enter news report URL")], width=6)]),
            dbc.Row([dbc.Col([dbc.Label("News Outlet"), dbc.Input(id='outlet-input', type='text', placeholder="Enter news outlet")], width=6),
                     dbc.Col([dbc.Label("Date of Publication"), dbc.Input(id='publication-date-input', type='date')], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Author"), dbc.Input(id='author-input', type='text', placeholder="Enter author name")], width=6),
                     dbc.Col([dbc.Label("Headline"), dbc.Input(id='headline-input', type='text', placeholder="Enter headline")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Number of Subs"), dbc.Input(id='subs-input', type='text', placeholder="Enter Number of Subs")], width=6),
                     dbc.Col([dbc.Label("Wire Service"), dbc.Input(id='wire-input', type='text', placeholder="Enter Wire Service")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Victim Name"), dbc.Input(id='victim-name-input', type='text', placeholder="Enter victim name")], width=6),
                     dbc.Col([dbc.Label("Date of Death"), dbc.Input(id='death-date-input', type='date')], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Age of Victim"), dbc.Input(id='victim-age-input', type='number', placeholder="Enter victim age")], width=6),
                     dbc.Col([dbc.Label("Race of Victim"), dcc.Dropdown(id='race-dropdown', options=race_options, placeholder="Select race")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Type of Location"), dbc.Input(id='location-type-input', type='text', placeholder="Enter type of location")], width=6),
                     dbc.Col([dbc.Label("Province"), dcc.Dropdown(id='province-dropdown', options=[{'label': k, 'value': k} for k in provinces.keys()], placeholder="Select a province")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Town"), dcc.Dropdown(id='town-dropdown', placeholder="Select a town")], width=6),
                     dbc.Col([dbc.Label("Sexual Assault"), dcc.Dropdown(id='sexual-assault-dropdown', options=bool_options, placeholder="Select option")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Mode of Death"), dbc.Input(id='mode-of-death-input', type='text', placeholder="Enter mode of death")], width=6),
                     dbc.Col([dbc.Label("Robbery"), dcc.Dropdown(id='robbery-dropdown', options=bool_options, placeholder="Select option")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Suspect Arrested"), dcc.Dropdown(id='suspect-arrested-dropdown', options=bool_options, placeholder="Select option")], width=6),
                     dbc.Col([dbc.Label("Suspect Convicted"), dcc.Dropdown(id='suspect-convicted-dropdown', options=bool_options, placeholder="Select option")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Perpetrator Name"), dbc.Input(id='perp-name-input', type='text', placeholder="Enter perpetrator name")], width=6),
                     dbc.Col([dbc.Label("Perp Relationship"), dcc.Dropdown(id='relationship-dropdown', options=relationship_options, placeholder="Select relationship")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Multiple Murders"), dcc.Dropdown(id='multi-murder-dropdown', options=bool_options, placeholder="Select option")], width=6),
                     dbc.Col([dbc.Label("Extreme Violence"), dcc.Dropdown(id='extreme-violence-dropdown', options=bool_options, placeholder="Select option")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Row([dbc.Col([dbc.Label("Intimate Femicide"), dcc.Dropdown(id='intimate-femicide-dropdown', options=bool_options, placeholder="Select option")], width=6),
                     dbc.Col([dbc.Label("Notes"), dbc.Textarea(id='notes-input', placeholder="Enter additional notes")], width=6)], style={'margin-bottom': '15px'}),
            dbc.Button("Submit", id="submit-button", color="success", className="mt-3"),
            html.Div(id="output-message", className="mt-3"),
            dbc.Button("Export to CSV", id="export-button", color="secondary", className="mt-3"),
            dcc.Download(id="download-dataframe-csv"),
            html.Hr(),
        ]),
    ], className="mb-4")
])
#Data display layout
data_display_layout = dbc.Container([
    dbc.Card([
        dbc.CardHeader("Homicide Data Display"),
        dbc.CardBody([ 
                        # Grouped and organized checklist for column selection
            dbc.Row([
                dbc.Col([
                    dcc.Checklist(
                        id='column-checklist-1',
                        options=[{'label': col, 'value': col} for col in ['article_id', 'news_report_url', 'news_report_platform', 'date_of_publication', 'author', 'news_report_headline', 'wire_service', 'no_of_subs']],
                        value=['article_id', 'news_report_url', 'news_report_platform', 'date_of_publication', 'author', 'news_report_headline', 'wire_service', 'no_of_subs'],
                        labelStyle={'display': 'block'}
                    ),
                ], width=4),

                dbc.Col([
                    dcc.Checklist(
                        id='column-checklist-2',
                        options=[{'label': col, 'value': col} for col in ['victim_name', 'date_of_death', 'age_of_victim', 'race_of_victim', 'type_of_location', 'place_of_death_town', 'place_of_death_province']],
                        value=['victim_name', 'date_of_death', 'age_of_victim', 'race_of_victim', 'type_of_location', 'place_of_death_town', 'place_of_death_province'],
                        labelStyle={'display': 'block'}
                    ),
                ], width=4),

                dbc.Col([
                    dcc.Checklist(
                        id='column-checklist-3',
                        options=[{'label': col, 'value': col} for col in ['sexual_assault', 'mode_of_death_specific', 'robbery_y_n_u', 'suspect_arrested', 'suspect_convicted', 'perpetrator_name', 'perpetrator_relationship_to_victim', 'multiple_murder', 'extreme_violence_y_n_m_u', 'intimate_femicide_y_n_u', 'notes']],
                        value=['sexual_assault', 'mode_of_death_specific', 'robbery_y_n_u', 'suspect_arrested', 'suspect_convicted', 'perpetrator_name', 'perpetrator_relationship_to_victim', 'multiple_murder', 'extreme_violence_y_n_m_u', 'intimate_femicide_y_n_u', 'notes'],
                        labelStyle={'display': 'block'}
                    ),
                ], width=4)
            ], className="mb-3"),

            
            dbc.Button("Display Table", id = 'display-button', color = "success", className = "mt-3" ),
            
            # Display message container (for error or informational messages)
            html.Div(id='message-container', className="mt-3"),
            html.Div(id='table-container',  className="mt-3")
        ]),
    ], className="mb-4")
])
app.layout = dbc.Container([
    data_display_layout
])

#Data import layout
data_import_layout = dbc.Container([
    dbc.Card([
        dbc.CardHeader("Homicide Data Import"),
        dbc.CardBody([
            html.H3("Upload CSV to Import Data in to the Current Table"),
            dcc.Upload(id='upload-data-1', children=html.Div(['Drag and Drop or ', html.A('Select a CSV File')]), style={'width': '100%', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'}, multiple=False, accept=".csv"),
            html.Div(id='upload-output-1'),
            html.Hr(),
            html.H3("Upload CSV to Import Data in to a New Table"),
            dcc.Upload(id='upload-data-2', children=html.Div(['Drag and Drop or ', html.A('Select a CSV File')]), style={'width': '100%', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'}, multiple=False, accept=".csv"),
            html.Div(id='upload-output-2')
        ])
    ])

])
app.layout = dbc.Container([
    data_import_layout
])
# Data Visualization Layout
data_visualization_layout = dbc.Container([
    dbc.Card([
        dbc.CardHeader("Homicide Data Visualization"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Select Plot Category"),
                    dcc.Dropdown(
                        id='plot-category-dropdown',
                        options=[{'label': 'Homicides Over Time', 'value': 'homicides_over_time'}, {'label': 'Geographical Distribution', 'value': 'geographical_distribution'}, {'label': 'Demographic Insights', 'value': 'demographic_insights'}, {'label': 'Victim Perpetrator Relationship', 'value': 'victim_perpetrator_relationship'}, {'label' : 'Multivariate Comparisons', 'value' : 'multivariate_comparisons'}],
                        placeholder="Select a plot category"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("Select Plot Type"),
                    dcc.Dropdown(
                        id='plot-type-dropdown',
                        options=[],
                        placeholder="Select a plot type"
                    )
                ], width=6),
            ]),
            html.Div(id='plot-container', style={'textAlign': 'center', 'margin': '20px'})
        ]),
    ], className="mb-4")
])

# Layout for Custom Visualizations (with just bar graph for now)
custom_visualization_layout = dbc.Container([
    dbc.Card([
        dbc.CardHeader("Custom Data Visualization"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Select X-Axis"),
                    dcc.Dropdown(
                        id='x-axis-dropdown',
                        options=[{'label': 'Victim Age', 'value': 'age'},
                                 {'label': 'Province', 'value': 'province'},
                                 {'label': 'Race', 'value': 'race'},
                                 {'label': 'Perpetrator Relationship', 'value': 'VIC SUSP RELATIONSHIP'}],
                        placeholder="Select X-Axis"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("Select Y-Axis"),
                    dcc.Dropdown(
                        id='y-axis-dropdown',
                        options=[{'label': 'Count', 'value': 'count'}],  # For a bar graph, we only allow 'count' for now.
                        placeholder="Select Y-Axis",
                        value='count'  # Default to 'count'
                    )
                ], width=6),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Generate Bar Graph", id='generate-bar-graph-button', color="primary", className="mt-3")
                ], width=12)
            ]),
            dcc.Graph(id='custom-bar-graph', style={'textAlign': 'center', 'margin': '20px'})
        ]),
    ], className="mb-4")
])

#Duplicate data layout
duplicates_table_layout = dbc.Container([
    dbc.Card([
        dbc.CardHeader("Duplicate Data"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Input(
                        id='duplicate-column-input',
                        type='text',
                        placeholder='Enter column names separated by commas',
                        style={'width': '100%'}
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Button("Check for Duplicates", id='check-duplicates-button', n_clicks=0, color="warning", className="me-2"),
                    dbc.Button("Delete duplicates", id='delete-duplicates-button', n_clicks=0, color="danger"),
                ], width=6, className="d-flex justify-content-end")
            ], className="mb-3"),
            
            html.Div(id='duplicates-message', className="mb-3")
            ]),
        dbc.Col([
            dbc.Button("Display Duplicate Deleted Data", id = 'display-duplicate-button', color = "success", className="mt-3"),
            html.Div(id='duplicate-table-container', className = "mt-3")
        ]),
        ],className = "mb-4"),
    ])
app.layout = dbc.Container([
    duplicates_table_layout
])

#Layout for deleting data
delete_table_layout = dbc.Container([
    dbc.Card([
        dbc.CardHeader("Delete Data"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Input(
                        id='delete-record-input',
                        type='number',
                        placeholder='Enter the article_id which needs to be deleted',
                        style={'width': '100%'}
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Button("Delete Data", id='delete-record-button', n_clicks=0, color="danger"),
                ], width=6, className="d-flex justify-content-end")
            ], className="mb-3"),
            html.Div(id="delete-status",className = "mt-3"),
            dbc.Button("Display Delete Table", id = 'display-delete-button', color = 'success', className= "mt-3"),
           # html.Div(id='update-table-container', className = "mt-3"),
            html.Div(id='delete-table-container', className = "mt-3")
            ]),
        ],className = "mb-4")
])
app.layout = dbc.Container([
    delete_table_layout
])


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content'),
    footer
])


# Callbacks to switch pages
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/display':
        return data_display_layout
    elif pathname == '/visualization':
        return data_visualization_layout
    elif pathname == '/import':
        return data_import_layout
    elif pathname == '/custom_visualization':
        return custom_visualization_layout
    elif pathname == '/delete_table':
        return delete_table_layout
    elif pathname == '/duplicate_data':
        return duplicates_table_layout
    else:
        return data_entry_layout
    
# Province-Town Callback
@app.callback(
    Output('town-dropdown', 'options'),
    Input('province-dropdown', 'value'),
    prevent_initial_call=True
)

#Updating dropdown
def update_town_dropdown(province_value):
    if province_value:
        return [{'label': town, 'value': town} for town in provinces[province_value]]
    return []

# Handle Data Submission
@app.callback(
    Output('output-message', 'children'),
    Input('submit-button', 'n_clicks'),
    State('url-input', 'value'),
    State('outlet-input', 'value'),
    State('publication-date-input', 'value'),
    State('author-input', 'value'),
    State('headline-input', 'value'),
    State('subs-input', 'value'),
    State('wire-input', 'value'),
    State('victim-name-input', 'value'),
    State('death-date-input', 'value'),
    State('victim-age-input', 'value'),
    State('race-dropdown', 'value'),
    State('location-type-input', 'value'),
    State('province-dropdown', 'value'),
    State('town-dropdown', 'value'),
    State('sexual-assault-dropdown', 'value'),
    State('mode-of-death-input', 'value'),
    State('robbery-dropdown', 'value'),
    State('suspect-arrested-dropdown', 'value'),
    State('suspect-convicted-dropdown', 'value'),
    State('perp-name-input', 'value'),
    State('relationship-dropdown', 'value'),
    State('multi-murder-dropdown', 'value'),
    State('extreme-violence-dropdown', 'value'),
    State('intimate-femicide-dropdown', 'value'),
    State('notes-input', 'value'),
    prevent_initial_call=True
)
#Insert data in to table code
def submit_form(n_clicks, url, outlet, pub_date, author, headline, subs, wire, victim_name, death_date,
                victim_age, race, location_type, town, province, sexual_assault, mode_of_death, 
                robbery, suspect_arrested, suspect_convicted, perp_name, relationship,
                multi_murder, extreme_violence, femicide, notes):
    if n_clicks is None:
        return ""

    cur = conn.cursor()

    # Prepare the SQL insert statement
    insert_query = '''INSERT INTO homicide_news
            (news_report_url, news_report_platform, date_of_publication, author, news_report_headline, no_of_subs, 
            wire_service, victim_name, date_of_death, age_of_victim, race_of_victim, type_of_location, 
            place_of_death_town, place_of_death_province, sexual_assault, mode_of_death_specific, robbery_y_n_u, 
            suspect_arrested, suspect_convicted, perpetrator_name, perpetrator_relationship_to_victim, 
            multiple_murder, extreme_violence_y_n_m_u, intimate_femicide_y_n_u, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''


    values = (url, outlet, pub_date, author, headline, subs, wire, victim_name, death_date,
            victim_age, race, location_type, province, town, sexual_assault, mode_of_death, 
            robbery, suspect_arrested, suspect_convicted, perp_name, relationship, 
            multi_murder, extreme_violence, femicide, notes)

        
    # Execute the insertion
    cur.execute(insert_query, values)
    conn.commit()  # Ensure the transaction is committed
    cur.close()  # Close the cursor
    conn.close() #close connection

    return "Data successfully inserted!"

# Handle CSV Export
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("export-button", "n_clicks"),
    prevent_initial_call=True
)
#CSV export functionality for the dashboard
def export_csv(n_clicks):
    if n_clicks:
        with psycopg2.connect(
            host="localhost", port="5432", database="homicide_main",
            user="postgres", password="Khiz1234"
        ) as conn:
            query = "SELECT * FROM homicide_news"
            df = pd.read_sql(query, conn)
            return dcc.send_data_frame(df.to_csv, "homicide_news.csv")



# Handle CSV Upload to the same table 
@app.callback(
    Output('upload-output-1', 'children'),
    Input('upload-data-1', 'contents'),
    prevent_initial_call=True
)
#CSV upload functionality of the dashboard
def upload_csv(contents):
    if contents:
        # Split the contents into metadata and base64-encoded data
        content_type, content_string = contents.split(',')
        
        # Decode the base64-encoded string
        decoded = base64.b64decode(content_string)

        try:
            # Specify semicolon as the delimiter and handle bad lines
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep=';', on_bad_lines='skip')
            print(df.head())  # Print first few rows for debugging
            
            # Try appending the data to the database
            df.to_sql('homicide_news', engine, if_exists='append', index=False)
            return "CSV data appended successfully."

        except pd.errors.ParserError as e:
            return f"Parsing error: {e}"

        except UnicodeDecodeError as e:
            return f"Decoding error: {e}"

        except Exception as e:
            return f"An error occurred: {e}"
    return "No contents provided."

#Handle CSV upload to a new table
@app.callback(
    Output('upload-output-2', 'children'),
    Input('upload-data-2', 'contents'),
    prevent_initial_call= True
)

#uploading CSV to a new table functionality of the dashboard 
def upload_csv_to_new_table(contents):
    if contents:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep = ';', on_bad_lines='skip')
            df.to_sql('homicide_complete', engine, if_exists='append', index = False)
            return "CSV data appended to a table homicide_complete successfully."
        except pd.errors.ParserError as e:
            return f"Parsing error: {e}"
        except UnicodeDecodeError as e:
            return f"An error occured: {e}"
        except Exception as e:
            return f"An error occurred: {e}"
    return "No contents provided"

#Callback to handle the table display in the database
@app.callback(
    [Output('message-container', 'children'),
    Output('table-container', 'children')],
    [Input('display-button', 'n_clicks'),
     Input('column-checklist-1', 'value'),
     Input('column-checklist-2', 'value'),
     Input('column-checklist-3', 'value')],
    prevent_initial_call=True
)

#Display table functionality while allowing users to display specific columns in the table 
def update_data_display(display_clicks, selected_columns_1, selected_columns_2, selected_columns_3):
    ctx = dash.callback_context
    if not ctx.triggered:
        print("No input was triggered.")
        return dash.no_update, dash.no_update
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    print(f"Triggered by: {triggered_id}")

    # Define the original column order
    original_column_order = [
        'article_id', 'news_report_url', 'news_report_platform', 'date_of_publication', 'author',
        'news_report_headline', 'wire_service', 'no_of_subs', 'victim_name', 'date_of_death',
        'age_of_victim', 'race_of_victim', 'type_of_location', 'place_of_death_town', 'place_of_death_province',
        'sexual_assault', 'mode_of_death_specific', 'robbery_y_n_u', 'suspect_arrested', 'suspect_convicted',
        'perpetrator_name', 'perpetrator_relationship_to_victim', 'multiple_murder', 'extreme_violence_y_n_m_u',
        'intimate_femicide_y_n_u', 'notes'
    ]

    # Combine selected columns from all checklists
    selected_columns = (selected_columns_1 or []) + (selected_columns_2 or []) + (selected_columns_3 or [])

    # Maintain the original order of the selected columns
    ordered_selected_columns = [col for col in original_column_order if col in selected_columns]

    # Ensure that columns are dynamically updated with every interaction
    if triggered_id == 'display-button':
        # Reset the table and message
        message, table = display_selected_columns(display_clicks, ordered_selected_columns)
        print(f"display_selected_columns returned: message='{message}', table={'not None' if table is not None else 'None'}")
        return message, table
    
    print("No condition was met.")
    return dash.no_update, dash.no_update


#Display the column that are selected in the table function
def display_selected_columns(n_clicks, selected_columns):
    if n_clicks is None or n_clicks == 0:
        return "Please click the 'Display Table' button to show data", None
    
    if not selected_columns:
        return "No columns selected. Please select at least one column", None

    try:
        with psycopg2.connect(
            host="localhost", port="5432", database="homicide_main",
            user="postgres", password="Khiz1234"
        ) as conn:
            # Build the SQL query dynamically based on selected columns
            query = f"SELECT {', '.join(selected_columns)} FROM homicide_news"  
            df = pd.read_sql_query(query, conn)

        # Debugging: print the selected columns and the dataframe
        print(f"Selected columns: {selected_columns}")
        print(df.head())  # Ensure the dataframe has the correct data

        if df.empty:
            return "No data found for the selected columns.", None
        # Update the DataTable with the selected columns
        table = dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict('records'),
            page_size=50,  # Show 50 rows per page
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )

        return None, table  # Return the updated table
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return "An error occurred while fetching data.", None

#This is the duplicates tab, it will do all the procesisng for the duplicates data
#Callback handles the duplicate data for the dashboard
@app.callback(
    [Output('duplicates-message', 'children'),
     Output('duplicate-table-container', 'children')],
    [Input('check-duplicates-button', 'n_clicks'),
     Input('delete-duplicates-button', 'n_clicks'),
     Input('display-duplicate-button', 'n_clicks')],
    [State('duplicate-column-input', 'value')],
    prevent_initial_call=True
 )
#Duplicate display page update
def update_duplicates_display(check_clicks, delete_duplicates_clicks, display_duplicates_clicks, duplicate_columns):
    ctx = dash.callback_context
    if not ctx.triggered:
        print("No input was triggered.")
        return dash.no_update, dash.no_update
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    print(f"Triggered by: {triggered_id}")

    if triggered_id == 'check-duplicates-button':
        message = check_duplicates(check_clicks, duplicate_columns)
        return message, dash.no_update
    elif triggered_id == 'delete-duplicates-button':
        message, table = delete_duplicates(delete_duplicates_clicks, duplicate_columns)
        return message, table
    elif triggered_id == 'display-duplicate-button':
        message, table = display_duplicates_table(display_duplicates_clicks)
        print(f"display duplicate columns returned: message='{message}', table={'not None' if table is not None else 'None'}")
        return message, table

    print("No condition was met.")
    return dash.no_update, dash.no_update

#Checking duplicates in each field function.
def check_duplicates(n_clicks, columns):
    if n_clicks is None or n_clicks == 0:
        return ""

    if not columns:
        return "Please enter one or more columns to check for duplicates."

    column_list = [col.strip() for col in columns.split(',')]
    
    try:
    
        with psycopg2.connect(
            host="localhost", port="5432", database="homicide_main",
            user="postgres", password="Khiz1234"
        ) as conn:
            query = f"""
                SELECT {', '.join(column_list)}, COUNT(*) 
                FROM homicide_news
                GROUP BY {', '.join(column_list)}
                HAVING COUNT(*) > 1
            """
            df = pd.read_sql(query, conn)
        if df.empty:
            return "No duplicate records found based on the selected columns."
        else:
            return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
    except Exception as e:
        return f"An error ocurred : {str(e)}"
    
#Deleting duplicates in the field and inserting it into a duplicates table
def delete_duplicates(n_clicks, column_name):
    if n_clicks == 0 or not column_name:
        return '', dash.no_update
    
    try:
        with psycopg2.connect(
            host="localhost", port="5432", database="homicide_main",
            user="postgres", password="Khiz1234"
        ) as conn:
            with conn.cursor() as cursor:
                # Check if the column exists
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='homicide_news' AND column_name='{column_name}'
                """)
                if not cursor.fetchone():
                    return f"Column '{column_name}' not found.", dash.no_update

                # Create duplicates table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS duplicates (
                        LIKE homicide_news INCLUDING ALL
                    )
                """)

                # Insert duplicates into the duplicates table, ignoring conflicts
                cursor.execute(f"""
                    INSERT INTO duplicates
                    SELECT * FROM homicide_news
                    WHERE {column_name} IN (
                        SELECT {column_name}
                        FROM homicide_news
                        GROUP BY {column_name}
                        HAVING COUNT(*) > 1
                    )
                    ON CONFLICT (article_id) DO NOTHING
                """)

                # Count the number of duplicates
                cursor.execute(f"""
                    SELECT COUNT(*) FROM (
                        SELECT {column_name}
                        FROM homicide_news
                        GROUP BY {column_name}
                        HAVING COUNT(*) > 1
                    ) as subquery
                """)
                duplicate_count = cursor.fetchone()[0]

                # Delete duplicates from the main table
                cursor.execute(f"""
                    DELETE FROM homicide_news
                    WHERE ctid NOT IN (
                        SELECT MIN(ctid)
                        FROM homicide_news
                        GROUP BY {column_name}
                    )
                """)
                conn.commit()

            return f"{duplicate_count} duplicate groups found. Duplicates removed from main table and saved to 'duplicates' table."
    except Exception as e:
        print(f"Error in delete_duplicates: {str(e)}")  # Log the error
        return f"An error occurred: {str(e)}", dash.no_update

#Displaying the duplicates table 
def display_duplicates_table(n_clicks):    
    if n_clicks is None or n_clicks == 0:
        return "Please click the 'Display Duplicate Table' button to show data"
    
    try:
        with psycopg2.connect(
            host="localhost", port="5432", database="homicide_main",
            user="postgres", password="Khiz1234"
        ) as conn:
            query = '''SELECT * FROM duplicates'''
            print(f"Executing query: {query}")
            df = pd.read_sql_query(query, conn)
        
        print(f"Query executed successfully. Dataframe shape: {df.shape}")
        if df.empty:
            print("The resulting dataframe is empty.")
            return "No data found.",None
        
        table = dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict('records'),
            page_size=50,  # Show 20 rows per page
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )
        
        print("Table created successfully.")
        return "", table  # Return only the table, no message needed
    except Exception as e:
        error_msg = f"Error in display_duplicates_table: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return f"An error occurred: {error_msg}", None

#This is the delete tab
#Here we are deleting the data depending on their article_id
def delete_record(n_clicks, article_id):
    if not article_id or n_clicks == 0:
        return '', dash.no_update
    count_in_delete = -1
    count_in_homicide = -1
    
    try:
        article_id = int(article_id)

        with psycopg2.connect(
                host="localhost", port="5432", database="homicide_main",
                user="postgres", password="Khiz1234"
        ) as conn:
            with conn.cursor() as cursor:
                # Check if record exists in homicide_news
                cursor.execute("SELECT COUNT(*) FROM homicide_news WHERE article_id = %s", (article_id,))
                count_in_homicide = cursor.fetchone()[0]
                print(count_in_homicide)

                # Check if record exists in delete_dash
                cursor.execute("SELECT COUNT(*) FROM delete_dash WHERE article_id = %s", (article_id,))
                count_in_delete = cursor.fetchone()[0]
                print(count_in_delete)

                if count_in_homicide == 0 and count_in_delete == 0:
                    return html.Div(f"No record found with the article_id {article_id} in either table.") 
                
                if count_in_delete > 0:
                    return html.Div(f"Record with article_id {article_id} has already been deleted and is in the delete_dash table.")

                if count_in_homicide > 0:
                    # Fetch the records to be deleted
                    cursor.execute("SELECT * FROM homicide_news WHERE article_id = %s", (article_id,))
                    records = cursor.fetchall()

                    # Insert fetched records into the delete table
                    cursor.execute("""CREATE TABLE IF NOT EXISTS delete_dash (
                        LIKE homicide_news INCLUDING ALL
                    )""")

                    for record in records:
                        cursor.execute("""
                            INSERT INTO delete_dash (article_id, news_report_url, news_report_headline, 
                            news_report_platform, date_of_publication, author, wire_service, no_of_subs, victim_name, 
                            date_of_death, race_of_victim, age_of_victim, place_of_death_province, place_of_death_town, 
                            type_of_location, sexual_assault, mode_of_death_specific, robbery_y_n_u, perpetrator_name, 
                            perpetrator_relationship_to_victim, suspect_arrested, suspect_convicted, multiple_murder, 
                            intimate_femicide_y_n_u, extreme_violence_y_n_m_u, notes) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            record)

                    # Delete the records from the original table
                    cursor.execute("DELETE FROM homicide_news WHERE article_id = %s", (article_id,))
                    conn.commit()

                    return html.Div(f"Record(s) with article_id {article_id} has been deleted. {count_in_homicide} record(s) were affected.")

    except ValueError:
        return html.Div("Invalid article_id. Please enter a valid integer."), dash.no_update
    except Exception as e:
        error_msg = f"Error in delete_record: {str(e)}"
        print(error_msg)
        return html.Div(f"An error occurred: {error_msg}"), dash.no_update

#Displaying delete table
def display_delete_table(n_clicks):
    if n_clicks is None or n_clicks == 0:
        return html.Div("Please click the 'Display Delete Table' button to show data")

    try:
        with psycopg2.connect(
                host="localhost", port="5432", database="homicide_main",
                user="postgres", password="Khiz1234"
        ) as conn:
            query = '''SELECT * FROM delete_dash'''
            df = pd.read_sql_query(query, conn)

        if df.empty:
            return html.Div("No data found in delete_dash.")

        table = dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict('records'),
            page_size=50,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )

        return table

    except Exception as e:
        error_msg = f"Error in display_delete_table: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return html.Div(f"An error occurred: {error_msg}")

# Callbacks to handle the delete functionality
@app.callback(
    Output('delete-status', 'children'),
    Input('delete-record-button', 'n_clicks'),
    State('delete-record-input', 'value'),
    prevent_initial_call = True
)
# Handling the delete function 
def handle_delete(n_clicks, article_id):
    if n_clicks is None or n_clicks == 0:
        return dash.no_update

    # Delete the record and return status message
    return delete_record(n_clicks, article_id)

#Handling the delete table and its display
@app.callback(
    Output('delete-table-container', 'children'),
    Input('display-delete-button', 'n_clicks'),
    prevent_initial_call=True
)
def update_table(n_clicks):
    return display_delete_table(n_clicks)

#Callbacks to manage the data visualization functionality 
@app.callback(
    Output('plot-type-dropdown', 'options'),
    Input('plot-category-dropdown', 'value'),
    prevent_initial_call=True
)
#Handles the dropdown menu for the different data visualisation techniques
def update_plot_type_dropdown(category_value):
    if category_value == 'homicides_over_time':
        return [{'label': 'Line Plot', 'value': 'line_plot'}, {'label': 'Bar Chart', 'value': 'bar_chart'}]
    elif category_value == 'geographical_distribution':
        return [{'label': 'Choropleth Map', 'value': 'choropleth_map'}]
    elif category_value == 'demographic_insights':
        return [
            {'label': 'Bar Chart (Race Breakdown)', 'value': 'race_bar_chart'}, 
            {'label': 'Age Distribution Histogram', 'value': 'age_histogram'},
            {'label': 'Gender Comparison Plot', 'value': 'gender_comparison'}
        ]
    elif category_value == 'victim_perpetrator_relationship':
        return [{'label': 'Relationship Bar Chart', 'value': 'relationship_bar_chart'}, {'label': 'Heatmap', 'value': 'relationship_heatmap'}]
    elif category_value == 'multivariate_comparisons':
        return [{'label': 'Scatter Plot', 'value': 'scatter_plot'}, {'label': 'Bubble Plot', 'value': 'bubble_plot'}]
    return []

# Render Plot Based on Selected Category and Plot Type
@app.callback(
    Output('plot-container', 'children'),
    Input('plot-category-dropdown', 'value'),
    Input('plot-type-dropdown', 'value'),
    prevent_initial_call=True
)

def render_plot(category_value, plot_type_value):

    if not category_value or not plot_type_value:
        return "Please select a plot type."
    try:
        fig = None
    # Homicides Over Time
   
        if category_value == 'homicides_over_time':
                query = """
                    SELECT "VICTIM NAME", MONTH 
                    FROM open_day_homicide_data
                    GROUP BY "VICTIM NAME", MONTH
                """
                df = pd.read_sql(query, conn)
                
                # Check if df is empty before proceeding
                if df.empty:
                    print("No data returned from the database.")
                    return html.Div("No data available to display.")
                
                # Convert month names to datetime objects
                df['date'] = pd.to_datetime(df['month'], format='%B', errors='coerce')
                
                # If the above fails, try with abbreviated month names
                if df['date'].isnull().all():
                    df['date'] = pd.to_datetime(df['month'], format='%b', errors='coerce')
                
                # If there are still null values, print the problematic entries
                if df['date'].isnull().any():
                    print("Problematic month entries:")
                    print(df[df['date'].isnull()]['month'].unique())
                
                # Check if any valid dates were created
                if df['date'].isnull().all():
                    print("All month entries are invalid.")
                    return html.Div("Unable to process month data for plotting.")
                
                # Group by month and get the count
                data = df.groupby('month').size().reset_index(name='count')
                
                # Add the datetime column for sorting
                data['date'] = pd.to_datetime(data['month'], format='%B', errors='coerce')
                if data['date'].isnull().all():
                    data['date'] = pd.to_datetime(data['month'], format='%b', errors='coerce')
                
                # Sort the data by date
                data = data.sort_values('date')
                
                # Check if there is any data left after sorting
                if data.empty:
                    print("No valid data to plot after grouping and sorting.")
                    return html.Div("No data available to display.")
                
                # Plot based on plot_type_value
                if plot_type_value == 'line_plot':
                    fig = px.line(data, x='month', y='count', title='Homicides Over Time')
                elif plot_type_value == 'bar_chart':
                    fig = px.bar(data, x='month', y='count', title='Homicides Over Time')
                
                # Set the x-axis tick order
                fig.update_xaxes(categoryorder='array', categoryarray=data['month'])


# Geographical Distribution
        elif category_value == 'geographical_distribution':
            query = """
                SELECT province, COUNT(DISTINCT "VICTIM NAME" || ' ' || MONTH::text) as count 
                FROM open_day_homicide_data
                GROUP BY province
            """
            df = pd.read_sql(query, conn)
            
            if plot_type_value == 'choropleth_map':
                fig = px.choropleth(df, 
                        geojson=geojson_data, 
                        locations='province',  # Use lowercase 'province'
                        featureidkey="properties.name", 
                        color='count', 
                        color_continuous_scale="Reds", 
                        title='Homicides by Province',
                        scope='africa')

    # Focus on South Africa
                fig.update_geos(fitbounds="locations", visible = False)  

    # Update layout: background color, centered title, and margins
                fig.update_layout(
                    paper_bgcolor="white",  # Change background around the map to blue
                    title={
                        'text': 'Homicides by Province',
                        'x': 0.5,  # Center the title
                        'xanchor': 'center',
                        'yanchor': 'top'
                    },
                    margin={"r": 0, "t": 50, "l": 0, "b": 0}  # Adjust margins for spacing
                )


        # Demographic Insights
        elif category_value == 'demographic_insights':
            if plot_type_value == 'race_bar_chart':
                query = """
                    SELECT race, COUNT(DISTINCT "VICTIM NAME" || ' ' || MONTH::text) as count 
                    FROM open_day_homicide_data 
                    GROUP BY race 
                """
                df = pd.read_sql(query, conn)
                fig = px.bar(df, x='race', y='count', title='Race Breakdown of Victims', color_discrete_sequence=['red']) 

            elif plot_type_value == 'age_histogram':
                query = """
                    SELECT DISTINCT ON ("VICTIM NAME", MONTH) age
                    FROM open_day_homicide_data
                    WHERE age != -1
                """
                df = pd.read_sql(query, conn)
                if df.empty:
                    return "No valid age data available."
                
                fig = px.histogram(df, x='age', nbins=20, title='Age Distribution of Homicide Victims')

            elif plot_type_value == 'gender_comparison':
                query = """
                    SELECT "SUSPECT GENDER", COUNT(DISTINCT "VICTIM NAME" || ' ' || MONTH::text) as count 
                    FROM open_day_homicide_data
                    WHERE "SUSPECT GENDER" IS NOT NULL
                    GROUP BY "SUSPECT GENDER"
                """
                df = pd.read_sql(query, conn)
                fig = px.bar(df, x="SUSPECT GENDER", y='count', title='Gender Comparison of Perpetrators')

        # Category: Victim-Perpetrator Relationship
        elif category_value == 'victim_perpetrator_relationship':
            if plot_type_value == 'relationship_bar_chart':
                query = """
                    SELECT "VIC SUSP RELATIONSHIP", COUNT(DISTINCT "VICTIM NAME" || ' ' || MONTH::text) as count 
                    FROM open_day_homicide_data 
                    WHERE "VIC SUSP RELATIONSHIP"IS NOT NULL
                    GROUP BY "VIC SUSP RELATIONSHIP"
                """
                df = pd.read_sql(query, conn)

                fig = px.bar(df, 
                            x="VIC SUSP RELATIONSHIP", 
                            y='count', 
                            title='Homicides by Victim-Perpetrator Relationship')

            elif plot_type_value == 'relationship_heatmap':
                query = """
                    SELECT "VIC SUSP RELATIONSHIP", "MODE OF DEATH", COUNT(DISTINCT "VICTIM NAME" || ' ' || MONTH::text) as count 
                    FROM open_day_homicide_data 
                    WHERE "VIC SUSP RELATIONSHIP" IS NOT NULL AND "MODE OF DEATH" IS NOT NULL
                    GROUP BY "VIC SUSP RELATIONSHIP", "MODE OF DEATH"
                """
                df = pd.read_sql(query, conn)

                fig = px.density_heatmap(df, 
                                        x="VIC SUSP RELATIONSHIP", 
                                        y="MODE OF DEATH", 
                                        z='count', 
                                        title='Relationship vs Mode of Death Heatmap')

        #Multivariable plot which shows the correlation between different fields
        elif category_value == 'multivariate_comparisons':
            if plot_type_value == 'scatter_plot':
                query = """
                    SELECT "LOCATION (HOME/PUBLIC/WORK/UNKNOWN)", COUNT(DISTINCT "VICTIM NAME"|| ' ' || MONTH::text) as homicide_count 
                    FROM open_day_homicide_data
                    WHERE "LOCATION (HOME/PUBLIC/WORK/UNKNOWN)" IS NOT NULL 
                    GROUP BY "LOCATION (HOME/PUBLIC/WORK/UNKNOWN)"
                """
                df = pd.read_sql(query, conn)
                
                #Scatter plot of location type vs homicide count
                fig = px.scatter(
                    df,
                    x="LOCATION (HOME/PUBLIC/WORK/UNKNOWN)", 
                    y='homicide_count',
                    title='Location Type vs Homicide Count',
                    labels={
                        "LOCATION (HOME/PUBLIC/WORK/UNKNOWN)": 'Location Type',
                        'homicide_count': 'Homicide Count'
                    },
                    size='homicide_count',  # Size of points by homicide count
                    color='homicide_count'  # Color points by homicide count
                )
                fig.update_traces(marker_size=10) 
                fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))

            elif plot_type_value == 'bubble_plot':
                query = """
                    SELECT "MODE OF DEATH", "SUSPECT CONVICTED", COUNT(DISTINCT "VICTIM NAME" || ' ' || MONTH::text) as count 
                    FROM open_day_homicide_data
                    WHERE "MODE OF DEATH" IS NOT NULL AND "SUSPECT CONVICTED" IS NOT NULL
                    GROUP BY "MODE OF DEATH", "SUSPECT CONVICTED"
                """
                df = pd.read_sql(query, conn)
                # Define color mapping
                color_map = {
                    'Y': 'blue',
                    'N': 'red',
                    'Unknown': 'purple'
                }

                fig = px.scatter(df, 
                                x="MODE OF DEATH", 
                                y="SUSPECT CONVICTED", 
                                size='count', 
                                color='SUSPECT CONVICTED',
                                color_discrete_map=color_map,
                                hover_data=['count'],
                                title='Mode of Death vs Conviction Rates with Frequency Bubble Size')

                # Adjust the layout for better readability
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0.1)',  # Light gray background
                    paper_bgcolor='rgba(0,0,0,0.1)',
                    font_color='#333333',  # Dark gray font color
                    legend_title_text='Suspect Convicted'
                )

                # Update marker properties for better visibility
                fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
                # Update y-axis to show full labels
                fig.update_yaxes(
                    ticktext=['Yes', 'No', 'Unknown'],
                    tickvals=['Y', 'N', 'U']
                )

        if fig:
            return dcc.Graph(figure=fig)
        else:
            return html.Div("Unable to create plot. Please try a different selection.")
    except Exception as e:
        return html.Div(f"An erro occured: {str(e)}")
        #return "Please select a plot type."

#Callback to handle the custom data visualisation in which the user can visualise different aspects of the data 
#and see the correlation between the different fields in the data
@app.callback(
    Output('custom-bar-graph', 'figure'),
    [Input('generate-bar-graph-button', 'n_clicks')],
    [State('x-axis-dropdown', 'value'), State('y-axis-dropdown', 'value')]
)

def update_custom_bar_graph(n_clicks, x_axis, y_axis):
    if n_clicks is None or x_axis is None:
        # If no button click or no x-axis selected, return an empty figure
        return {}

    # Quote the x_axis for the SQL query if necessary
    if ' ' in x_axis or '-' in x_axis or x_axis.isupper():
        query_x_axis = f'"{x_axis}"'
    else:
        query_x_axis = x_axis

    # Construct the query to count unique murders, grouping by x_axis
    query = f"""
    SELECT {query_x_axis}, COUNT(DISTINCT "VICTIM NAME") as count
    FROM open_day_homicide_data
    GROUP BY {query_x_axis}
    """

    # Fetch data from the database
    try:
        df = pd.read_sql(query, con=engine)
        print(df)  # For debugging: print the data frame to check if it contains data
    except Exception as e:
        print(f"Error in executing query: {e}")
        return {}

    if df.empty:
        print(f"No data returned for query: {query}")
        return {}  # Return an empty figure if the query returned no data

    # Ensure the column name for Plotly matches the DataFrame column
    x_axis_label = x_axis.strip('"')

    # Create a bar graph
    fig = px.bar(df, x=x_axis_label, y='count', title=f'Bar Graph of {x_axis_label} vs {y_axis}')
    fig.update_layout(xaxis_title=x_axis_label, yaxis_title='Count')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)