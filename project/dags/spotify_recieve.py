import boto3
import psycopg2
import ast
from queries import create_table, search_table, insert_query
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
    QueueUrl = 'https://sqs.us-east-1.amazonaws.com/653639613428/spotify'
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
    outfile = open('spotify_data_lake.txt', 'a')
    now = datetime.now().replace(microsecond=0)
    outfile.write(f'{now} - {data_dict} \n')

    # Making sure spotify table is created
    PG_CURS.execute(create_table)
    # Querying the database for "played_at"
    PG_CURS.execute(search_table)

    # Fetching all the "played_at" values
    result = PG_CURS.fetchall()
    # Storing the last 20 "played_at" value as a list inside a list.
    played_at_lists = [list(i) for i in result]

    # For loop to get each song from the dictionary
    for song in data_dict["items"]:
        # If a songs 'played_at' value is in the list
        # Pass these songs because they are already in the database
        if [song['played_at']] in played_at_lists:
            pass
        # Otherwise, grab data and save them to the database
        else:
            # Saving Data to Variables
            name = song["track"]["name"]
            artist_names = song["track"]["album"]["artists"][0]["name"]
            album_name = song["track"]["album"]["name"]
            duration_ms = song['track']['duration_ms']
            played_at = song["played_at"]

            # Saving variables as a tuple to add to the database
            record_to_insert = (name, artist_names, album_name, duration_ms, played_at)
            # Executing adding data to the Database
            PG_CURS.execute(insert_query, record_to_insert)
    # Print each time a Message from the Queue has gone through.
    print('[x] Received!')
    # Saving changes to the database
    PG_CONN.commit()
    # Deleting the message from the queue now that everything is done
    sqs.delete_message(QueueUrl=QueueUrl, ReceiptHandle=receipt_handle)

recieve_q()