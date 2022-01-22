import pika, sys, os
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

    # Setting up connection to RABBITMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    # Making sure that the queue "spotify-queue" is created
    channel.queue_declare(queue='spotify-queue')

    def callback(ch, method, properties, body):
        """This is the inner function to Main that cleans the
        queue message, transforms it a dictionary, and runs the
        loop to save it to the database.
        """
        # Turning the queued message into a string to prepare it for a dictionary.
        string = str(body).replace("\\", "").lstrip('b').lstrip("'").rstrip("'")
        # Turning the string into a dictionary
        data_dict = ast.literal_eval(string)

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
        print(played_at_lists)

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

    channel.basic_consume(queue='spotify-queue', on_message_callback=callback, auto_ack=True)
    # Message for on how to exit this script
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
recieve_q()