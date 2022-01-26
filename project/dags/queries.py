create_table = '''
        CREATE TABLE IF NOT EXISTS spotify(
        song_name VARCHAR(50) NOT NULL,
        artist VARCHAR(50) NOT NULL,
        album VARCHAR(50) NOT NULL,
        duration_ms INT NOT NULL,
        played_at VARCHAR(50) NOT NULL
        );
        '''

search_table = '''
        SELECT played_at
        FROM spotify
        ORDER BY played_at DESC
        LIMIT 20;
        '''

insert_query = """INSERT INTO spotify (song_name, artist, album, duration_ms, played_at) VALUES (%s,%s,%s,%s,%s)"""


weather_create_table = '''
        CREATE TABLE IF NOT EXISTS weather(
        weather_desc VARCHAR(50) NOT NULL,
        temp INTEGER NOT NULL,
        feels_like INTEGER NOT NULL,
        humidity INT NOT NULL,
        date VARCHAR(50) NOT NULL
        );
        '''

weather_insert_query = """INSERT INTO weather (weather_desc, temp, feels_like, humidity, date) VALUES (%s,%s,%s,%s,%s)"""