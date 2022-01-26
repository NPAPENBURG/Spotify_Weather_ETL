import boto3
import psycopg2
import ast
from queries import weather_create_table, weather_insert_query
from datetime import datetime


# Variables to connect to postgresql
DBNAME = 'iymiryxu'
USER = 'iymiryxu'
PASSWORD = 'UEoTjdSGpoVGDP6HE2p6BDwQa3ldFFDa'
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
    sqs = boto3.client('sqs', region_name='us-east-1',
                       aws_access_key_id="AKIAZQL7U7P2KZDZG5HU",
                       aws_secret_access_key="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")
    # Url for the SQS queue
    QueueUrl = 'https://sqs.us-east-1.amazonaws.com/653639613428/weather'
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
