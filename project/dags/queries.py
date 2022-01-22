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