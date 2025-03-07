import psycopg2
import psycopg2.extras
from config import config

def copy_from_csv(cursor, csv_file_path):
     with open(csv_file_path, 'r', encoding='ISO-8859-1') as file:
        # Copy data from the CSV file to the table
        cursor.execute('SET datestyle = "ISO, DMY";')
        cursor.copy_expert("""COPY homicide_news(
                            news_report_url,
                            news_report_headline,
                            news_report_platform,
                            date_of_publication,
                            author,
                            wire_service,
                            no_of_subs,
                            victim_name,
                            date_of_death,
                            race_of_victim,
                            age_of_victim,
                            place_of_death_province,
                            place_of_death_town,
                            type_of_location,
                            sexual_assault,
                            mode_of_death_specific,
                            robbery_y_n_u,
                            perpetrator_name,
                            perpetrator_relationship_to_victim,
                            suspect_arrested,
                            suspect_convicted,
                            multiple_murder,
                            intimate_femicide_y_n_u,
                            extreme_violence_y_n_m_u,
                            notes
                            )
        FROM STDIN WITH CSV HEADER DELIMITER ';'""", file)
        print("Data copied successfully to homicide_news.")

    

def copy_from_open_day_csv(cursor, csv_file_path):
    # Open the CSV file
    with open(csv_file_path, 'r', encoding='ISO-8859-1') as file:
        # Copy data from the CSV file to the table
        cursor.execute('SET datestyle = "ISO, DMY";')
        cursor.copy_expert("""COPY open_day_homicide_data (
                            "VICTIM NAME",
                            MONTH,
                            DAY,
                            YEAR,
                            AGE,
                            OCCUPATION,
                            RACE,
                            "PLACE OF DEATH",
                            "LOCATION (HOME/PUBLIC/WORK/UNKNOWN)",
                            "CITY/AREA",
                            PROVINCE, 
                            "SEXUAL ASSAULT",
                            "MODE OF DEATH",
                            ROBBERY, 
                            "SUSPECT ARRESTED",
                            "SUSPECT CONVICTED",
                            "SUSPECT NAME",
                            "SUSPECT GENDER",
                            "VIC SUSP RELATIONSHIP",
                            "NO OF SUSPECTS",
                            "INTIMATE FEMICIDE",
                            "MULTIPLE MURDER",
                            "EXTREME VIOLENCE",
                            "NOTES",
                            "MEDIA COVERAGE URL OR NAME",
                            "MEDIA CODE",
                            "DATE OF ARTICLE",
                            "AUTHOR",
                            "PDF NAME",
                            "CLIPPING PDF NAME",
                            "ARTICLE COUNT",
                            "SAPA/WIRE"
                            )
        FROM STDIN WITH CSV HEADER DELIMITER ';'""", file)
        print("Data copied successfully to Open_day_homicide_data.")

def create_homicide_news_table(cursor):
    # Drop the table if it already exists and create a new one
    cursor.execute("DROP TABLE IF EXISTS homicide_news CASCADE")
    create_script_homicide = '''CREATE TABLE homicide_news (
                            article_id SERIAL PRIMARY KEY,
                            news_report_url VARCHAR(255),
                            news_report_headline VARCHAR(255),
                            news_report_platform VARCHAR(255),
                            date_of_publication DATE,
                            author VARCHAR(255),
                            wire_service VARCHAR(255),
                            no_of_subs INT,
                            victim_name VARCHAR(255),
                            date_of_death DATE,
                            race_of_victim VARCHAR(255),
                            age_of_victim INT,
                            place_of_death_province VARCHAR(100),
                            place_of_death_town VARCHAR(255),
                            type_of_location VARCHAR(255),
                            sexual_assault VARCHAR(255),
                            mode_of_death_specific VARCHAR(100),
                            robbery_y_n_u VARCHAR(10),
                            perpetrator_name VARCHAR(255),
                            perpetrator_relationship_to_victim VARCHAR(255),
                            suspect_arrested VARCHAR(255),
                            suspect_convicted VARCHAR(255),
                            multiple_murder VARCHAR(10),
                            intimate_femicide_y_n_u VARCHAR(10),
                            extreme_violence_y_n_m_u VARCHAR(10),
                            notes VARCHAR(1000)
                            )'''
    cursor.execute(create_script_homicide)
    print("homicide_news Table created successfully.")

def create_open_day_homicide_table(cursor):
    # Drop the table if it already exists and create a new one
    cursor.execute("DROP TABLE IF EXISTS open_day_homicide_data CASCADE")
    create_script_open_day = '''CREATE TABLE open_day_homicide_data (                               
                            article_id SERIAL PRIMARY KEY,
                            "VICTIM NAME" VARCHAR(255),
                            MONTH VARCHAR(60),
                            DAY VARCHAR(50),
                            YEAR INT,
                            AGE INT,
                            OCCUPATION VARCHAR(255),
                            RACE VARCHAR(50),
                            "PLACE OF DEATH" VARCHAR(255),
                            "LOCATION (HOME/PUBLIC/WORK/UNKNOWN)" VARCHAR(255),
                            "CITY/AREA" VARCHAR(100),
                            PROVINCE VARCHAR(100), 
                            "SEXUAL ASSAULT" VARCHAR(50),
                            "MODE OF DEATH" VARCHAR(100),
                            ROBBERY VARCHAR(50), 
                            "SUSPECT ARRESTED" VARCHAR(255),
                            "SUSPECT CONVICTED" VARCHAR(255),
                            "SUSPECT NAME" VARCHAR(255),
                            "SUSPECT GENDER" VARCHAR(50),
                            "VIC SUSP RELATIONSHIP" VARCHAR(255),
                            "NO OF SUSPECTS" VARCHAR(50),
                            "INTIMATE FEMICIDE" VARCHAR(50),
                            "MULTIPLE MURDER" VARCHAR(50),
                            "EXTREME VIOLENCE" VARCHAR(50),
                            "NOTES" VARCHAR(1000),
                            "MEDIA COVERAGE URL OR NAME" VARCHAR(1000),
                            "MEDIA CODE" VARCHAR(255),
                            "DATE OF ARTICLE" VARCHAR(100),
                            "AUTHOR" VARCHAR(255),
                            "PDF NAME"VARCHAR(255),
                            "CLIPPING PDF NAME" VARCHAR(255),
                            "ARTICLE COUNT" INT,
                            "SAPA/WIRE" VARCHAR(50)
                            )'''
    cursor.execute(create_script_open_day)
    print("open_day_homicide_data Table created successfully.")

def connect_and_create_tables():
    connection = None
    csr = None
    try:
        # Get database connection parameters from config
        params = config()
        print('Connecting to the PostgreSQL database ...')
        connection = psycopg2.connect(**params)
        csr = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Create the two tables
        create_homicide_news_table(csr)
        create_open_day_homicide_table(csr)

        # Load data from CSV for the first table (homicide_news)
        csv_file_path = 'C:/Users/syedk/Documents/updated_investigation_project/investigation_new_2/investigation_project_v2-master/homicide_news_data.csv'
        copy_from_csv(csr, csv_file_path)
        
        open_day_csv_file_path = 'C:/Users/syedk/Documents/updated_investigation_project/investigation_new_2/investigation_project_v2-master/Open_day_data.csv'
        copy_from_open_day_csv(csr, open_day_csv_file_path)

        # Commit the changes
        connection.commit()

    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if csr is not None:
            csr.close()
        if connection is not None:
            connection.close()
            print('Database connection terminated.')

if __name__ == "__main__":
    connect_and_create_tables()
