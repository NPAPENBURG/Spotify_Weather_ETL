

try:
    from datetime import timedelta
    from airflow import DAG
    from airflow.operators.python_operator import PythonOperator
    from datetime import datetime
    import requests
    import boto3
    import psycopg2
    import ast
    from queries import weather_create_table, weather_insert_query
    from datetime import datetime

    print("All Dag modules are ok ......")
except Exception as e:
    print("Error  {} ".format(e))

def get_weather():
# base URL
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
    CITY = "Hickory"
    API_KEY = ""
    # upadting the URL
    URL = BASE_URL + "q=" + CITY + "&appid=" + API_KEY
    # HTTP request
    data = requests.get(URL)
    # getting data in the json format
    data_dict = data.json()
    

    sqs = boto3.resource('sqs', region_name='',
                    aws_access_key_id="", 
                    aws_secret_access_key="")

    queue = sqs.get_queue_by_name(QueueName='weather')
    
    queue.send_message(MessageBody=f'{data_dict}')


# Variables to connect to postgresql
DBNAME = ''
USER = ''
PASSWORD = ''
HOST = 'castor.db.elephantsql.com'

# Connecting to PostgresSQL
PG_CONN = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
PG_CURS = PG_CONN.cursor()

def recieve_q():
    """ This function is going to connect to the RabbitMQ
    message queue and received all messages stored in the queue.
    Once the message is received it is turned into a dictionary.
    The dictionary is then looped through for each song to see if
    it is already in the PostgresSQL database. If the song is in the Database
    the loop skips that song. If the song is not in the Database it gets added.
    """
    # Getting SQS account keys
    sqs = boto3.client('sqs', region_name='',
                       aws_access_key_id="",
                       aws_secret_access_key="")
    # Url for the SQS queue
    QueueUrl = ''
    # Receiving one message from the queue
    response = sqs.receive_message(
        QueueUrl=QueueUrl,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    # Getting the data from the SQS queue message
    data = response['Messages'][0]['Body']
    # Getting the receipt handle. This will be used to delete the message from queue below
    receipt_handle = response['Messages'][0]['ReceiptHandle']
    # Turning the data back into a dict
    data_dict = ast.literal_eval(data)

    # Saving data to the datalake
    outfile = open('weather_data_lake.txt', 'a')
    now = datetime.now().replace(microsecond=0)
    outfile.write(f'{now} - {data_dict} \n')

    # Making sure spotify table is created
    PG_CURS.execute(weather_create_table)


    # Saving Data to Variables

    temp_int = int(data_dict['main']['temp'])
    feels_like_int = int(data_dict['main']['feels_like'])


    weather_desc = data_dict['weather'][0]['description']
    temp = (temp_int - 273) * 1.8 + 32

    feels_like = (feels_like_int - 273) * 1.8 + 32
    humidity = data_dict['main']['humidity']
    date = datetime.now().replace(microsecond=0)

    # Saving variables as a tuple to add to the database
    record_to_insert = (weather_desc, temp, feels_like, humidity, date)
    # Executing adding data to the Database
    PG_CURS.execute(weather_insert_query, record_to_insert)
    # Print each time a Message from the Queue has gone through.
    print('[x] Received!')
    # Saving changes to the database
    PG_CONN.commit()
    # Deleting the message from the queue now that everything is done
    sqs.delete_message(QueueUrl=QueueUrl, ReceiptHandle=receipt_handle)

with DAG(
        dag_id="weather_dag",
        schedule_interval="*/2 * * * *",
        default_args={
            "owner": "airflow",
            "retries": 1,
            "retry_delay": timedelta(minutes=5),
            "start_date": datetime(2022, 1, 16),
        },
        catchup=False) as f:

    send = PythonOperator(
        task_id="send",
        python_callable=get_weather,
        provide_context=True,
    )

    recieve = PythonOperator(
        task_id="recieve",
        python_callable=recieve_q,
        provide_context=True,
    )


send >> recieve
