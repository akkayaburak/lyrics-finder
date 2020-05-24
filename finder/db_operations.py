from html import unescape
from psycopg2 import connect


def get_connection():
    conn = connect(database='', user='', password='',
                   host='', port='')
    return conn, conn.cursor()


def create():
    sql = '''CREATE TABLE IF NOT EXISTS songs (
              id BIGSERIAL PRIMARY KEY NOT NULL ,
              song TEXT,
              song_url VARCHAR(512),
              start_url VARCHAR(512),
              lyrics TEXT,
              singers TEXT,
              last_crawled TIMESTAMP,
              last_updated TIMESTAMP
            );'''

    conn, cur = get_connection()
    cur.execute(sql)
    conn.commit()
    conn.close()


def save(song, song_url, start_url, lyrics, singers,):
    song, lyrics, singers = unescape(song), \
                                                       unescape(lyrics), \
                                                       unescape(str(singers)),

    sql = """SELECT id FROM songs WHERE song_url=%s AND start_url=%s;"""

    conn, cur = get_connection()

    cur.execute(
        sql,
        (
            song_url,
            start_url
        )
    )

    result = cur.fetchall()
    if len(result) == 0:
        sql = """INSERT INTO songs(
                    song, song_url, start_url, lyrics,
                    singers, last_updated, last_crawled
                  )
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP,
                 CURRENT_TIMESTAMP) RETURNING id;"""

        cur.execute(
            sql,
            (
                song,
                song_url,
                start_url,
                lyrics,
                str(singers)
            )
        )
    else:
        sql = """UPDATE songs SET song=%s, song_url=%s,
         start_url=%s, lyrics=%s, singers=%s, 
         last_updated=CURRENT_TIMESTAMP,
        last_crawled=CURRENT_TIMESTAMP WHERE id=%s RETURNING id;"""

        cur.execute(
            sql,
            (
                song,
                song_url,
                start_url,
                lyrics,
                str(singers),
                result[0][0]
            )
        )

    result = cur.fetchall()[0][0]
    conn.commit()
    conn.close()
    return result


def load(id):
    sql = """SELECT * FROM songs WHERE id=%s;"""

    conn, cur = get_connection()

    cur.execute(
        sql,
        (
            id,
        )
    )
    result = cur.fetchall()

    conn.close()

    return result[0][1:]


def update_last_crawl(start_url, url):
    sql = """UPDATE songs SET last_crawled=CURRENT_TIMESTAMP WHERE
start_url=%s AND song_url=%s"""

    conn, cur = get_connection()

    cur.execute(
        sql,
        (
            start_url,
            url
        )
    )

    conn.commit()
    conn.close()


def number_of_songs(start_url, url):
    sql = """SELECT count(*) FROM songs WHERE start_url=%s AND song_url=%s"""

    conn, cur = get_connection()

    cur.execute(
        sql,
        (
            start_url,
            url
        )
    )

    result = cur.fetchall()[0][0]
    conn.close()
    return result


def exists_song(start_url, url):
    conn, cur = get_connection()

    cur.execute(
        'SELECT * FROM songs WHERE start_url=%s AND song_url=%s;',
        (
            start_url,
            url
        )
    )

    result = cur.fetchall()

    conn.close()

    return len(result) > 0
