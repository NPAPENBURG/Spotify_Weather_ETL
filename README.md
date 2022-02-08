
# Spotify-Recommender App

#### The purpose of this was to gain experince creating a near production ETL Pipeline using Spotifys API and a Weather API


## API Endpoints
###
| Method        | Endpoint        | Body         | Notes                                                      |
| :-----------: | :-------------: | :-----:      | :---:                                                      |
| GET           |  /              | Recent Songs | Talks to the Spotify API and gets the recently played songs|
| GET           |  /              | Weather      | Talks to the Weather API and gets the current weather      |


## Dependencies Used
- pandas
- python-dotenv
- requests
- spotipy
- psycopg2
- ast
- boto3
- airflow

## Instructions for Cloning, Installing, and Running Locally
- Step 1: Get Spotify API key at https://developer.spotify.com/documentation/web-api/quick-start/
- Step 2: Get Weather Api at https://openweathermap.org/api
- Step 3: Get API from Amazon SQS at https://console.aws.amazon.com/sqs/
- Step 4: Get a free PostgreSQL database at https://www.elephantsql.com/
- Step 5: Clone repository
    `$ git clone https://github.com/NPAPENBURG/Spotify_Weather_ETL`
- Step 6: Start VM
    `$ pipenv shell`
- Step 7: Install package dependencies
    `$ pipenv install pandas, python-dotenv, requests, spotipy, psycopg2, ast, boto3, airflow
- Step 8: Add API information into the dag files
- Step 9: Run the Dags
