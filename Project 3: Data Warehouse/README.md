# Project Datawarehouse

## Project description
    Sparkify has grown their user base and song database and want to move their processes and data onto the cloud.Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.. The goal of the current project is to build an ETL pipeline that extracts their data from S3, stage the data in Redshift, and transforms data to create a star schema optimized for queries on song play analysis so that their analytics team can continue to uncover insights into what songs their users are listening to.

## Project Datasets
    These two datasets that reside in S3 will be used as the source for the project.The first dataset is a subset of real data from the Million Song Dataset. Each file is in JSON format and contains metadata about a song and the artist of that song.The second dataset consists of log files in JSON format generated by this event simulator based on the songs in the dataset above. These simulate app activity logs from an imaginary music streaming app based on configuration settings.

Song data: s3://udacity-dend/song_data
Log data: s3://udacity-dend/log_data
Log data json path: s3://udacity-dend/log_json_path.json

## How to run
1. To run this project you will need to fill the following information, and save it as dwh.cfg in the project root folder.

[CLUSTER]
HOST=''
DB_NAME=''
DB_USER=''
DB_PASSWORD=''
DB_PORT=5439

[IAM_ROLE]
ARN=

[S3]
LOG_DATA='s3://udacity-dend/log_data'
LOG_JSONPATH='s3://udacity-dend/log_json_path.json'
SONG_DATA='s3://udacity-dend/song_data'

[AWS]
KEY=
SECRET=


2. Run the following command to install the dependencies ( for macos )

    $brew install awscli $pip install boto3 botocore pandas psycopg2 psycopg2-binary

3. Follow along create_cluster notebook to set up the needed infrastructure for this project.

4. Run the create_tables script to set up the database staging and analytical tables
 
    $ python create_tables.py
    
5. Finally, run the etl script to extract data from the files in S3, stage it in redshift, and finally store it in the dimensional tables
    
    $ python etl.py
    
## Project structure
This project includes four files:

1. create_table.py is where fact and dimension tables for the star schema in Redshift are created.
2. etl.py is where data gets loaded from S3 into staging tables on Redshift and then processed into the analytics tables on Redshift.
3. sql_queries.py where SQL statements are defined, which are then used by etl.py, create_table.py and analytics.py.
4. README.md is current file.

## Database schema design
Staging Tables

    staging_events
    staging_songs
    
Fact Table

    songplays - records in event data associated with song plays i.e. records with page NextSong -       songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent

Dimension Tables

    users - users in the app - user_id, first_name, last_name, gender, level
    songs - songs in music database - song_id, title, artist_id, year, duration
    artists - artists in music database - artist_id, name, location, lattitude, longitude
    time - timestamps of records in songplays broken down into specific units - start_time, hour,         day, week, month, year, weekday
    
## Queries and Results
Number of rows in each table:

    Table->rows
    staging_events->8056
    staging_songs->14896
    artists->10025
    songplays->333
    songs->14896
    time->333
    users->104

## Steps followed on this project

Create Table Schemas

1. Schemas designed for fact and dimension tables
2. SQL CREATE statement written for each of these tables in sql_queries.py
3. Completed logic in create_tables.py to connect to the database and create these tables
4. Write SQL DROP statements to drop tables in the beginning of - create_tables.py if the tables already exist.
5. Launched redshift cluster and created an IAM role that has read access to S3.
6. Added redshift database and IAM role info to dwh.cfg.
7. Tested create_tables.py using query editor in redshift database. 

Build ETL Pipeline

1. Implement the logic in etl.py to load data from S3 to staging tables on Redshift.
2. Implement the logic in etl.py to load data from staging tables to analytics tables on Redshift.
3. Test by running etl.py after running create_tables.py and running analytic queries on your Redshift database to compare your results with the expected results.
4. Delete your redshift cluster when finished.