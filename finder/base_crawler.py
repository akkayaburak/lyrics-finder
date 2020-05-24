from queue import LifoQueue
from threading import Thread
import db_operations as db_operations
import print_util as print_util
from network_manager import open_request
from print_util import Colors

class BaseCrawler:
    def __init__(self, name, start_url, number_of_threads, max_err=10,
                 delay_request=False):
        """
        Base class for all other crawlers. This class contains all information
        that will be common in all crawlers.
        :param name: Name of crawler
        :param start_url: Base URL of website
        :param number_of_threads: Number of threads to use to crawl
        :param max_err: Max number of allowed errors for a crawl
        :param delay_request: Whether to delay while making requests or not
        """
        self.delay_request = delay_request
        self.name = name
        self.start_url = start_url
        self.number_of_threads = number_of_threads
        self.max_allowed_errors = max_err
class CrawlerType2(BaseCrawler):
    def __init__(self, name, start_url, list_of_urls, number_of_threads,
                 delayed_request=False, max_allowed_error=3):
        super().__init__(name, start_url, number_of_threads,
                         delay_request=delayed_request,
                         max_err=max_allowed_error)
        self.url_list = list_of_urls
        self.task_queue = LifoQueue()
        db_operations.create()

    def run(self):
        """
        Function to be called by subclasses to start crawler
        """
        # Crawl cycle starts
        print_util.print_info(
            'Starting crawl with {0}'.format(
                self.name
            ),
            Colors.BLACK
        )
        # Add URLs to task queue
        for url in self.url_list:
            self.task_queue.put(
                {
                    'type': 0,
                    'url': url,
                    'n_errors': 0
                }
            )
        # Start all threads
        threads = []
        for n in range(1, self.number_of_threads + 1):
            temp_thread = Thread(
                target=self.threader,
                args=(n,)
            )
            threads.append(temp_thread)
            temp_thread.start()
        # Wait for threads to finish
        for temp_thread in threads:
            temp_thread.join()
            # Crawl cycle ends

    def threader(self, thread_id):
        """
        Worker function
        :param thread_id: As usual
        """
        while not self.task_queue.empty():

            task = self.task_queue.get()
            if task['n_errors'] >= self.max_allowed_errors:
                print_util.print_warning(
                    '{0} --> Too many errors in task {1}. Skipping.'.format(
                        thread_id,
                        task
                    )
                )
                continue

            print_util.print_info(
                '{0} --> New task : {1}'.format(
                    thread_id,
                    task
                )
            )

            try:
                if task['type'] == 0:
                    self.get_artists(
                        thread_id,
                        task['url']
                    )
                elif task['type'] == 1:
                    self.get_artist(
                        thread_id,
                        task['url'],
                        task['artist']
                    )
                elif task['type'] == 2:
                    self.get_songs_from_page(
                        thread_id,
                        task['url'],
                        task['artist']
                    )
                elif task['type'] == 3:
                    self.get_song(
                        thread_id,
                        task['url'],
                        task['song'],
                        task['artist']
                    )
                print_util.print_info(
                    '{0} --> Task complete : {1}'.format(
                        thread_id,
                        task
                    ),
                    Colors.GREEN
                )
            except Exception as e:
                print_util.print_error(
                    '{0} --> Error : {1}'.format(
                        thread_id,
                        e
                    )
                )
                task['n_errors'] += 1
                self.task_queue.put(task)

    def get_artists(self, thread_id, url):

        """
        Method to get artists from a URL
        :param thread_id: As usual
        :param url: As usual
        """
        complete_url = self.start_url + url
        raw_html = open_request(complete_url, delayed=self.delay_request)

        artists_with_url = self.get_artist_with_url(raw_html)

        for artist_url, artist in artists_with_url:
            self.task_queue.put(
                {
                    'type': 1,
                    'url': artist_url,
                    'artist': artist,
                    'n_errors': 0
                }
            )

    def get_artist(self, thread_id, url, artist):
        """
        Get songs for artist from URL in two parts:
            1. Get songs from first page (:param url)
            2. Add all other pages to task queue
        :param thread_id:
        :param url:
        :param artist:
        """
        complete_url = self.start_url + url
        raw_html = open_request(complete_url, delayed=self.delay_request)

        pages = self.get_pages_for_artist(raw_html)

        # Add all songs from current page
        for song_url, song in self.get_songs(raw_html):
            self.task_queue.put(
                {
                    'type': 3,
                    'url': song_url,
                    'song': song,
                    'artist': artist,
                    'n_errors': 0
                }
            )

        # Add rest of pages in task queue
        for page in pages[1:]:
            self.task_queue.put(
                {
                    'type': 2,
                    'url': page,
                    'artist': artist,
                    'n_errors': 0
                }
            )

    def get_songs_from_page(self, thread_id, url, artist):
        """
        Get songs from other pages of artist
        :param thread_id: As usual
        :param url: As usual
        :param artist: As usual
        """
        complete_url = self.start_url + url
        raw_html = open_request(complete_url, delayed=self.delay_request)

        for song_url, song in self.get_songs(raw_html):
            self.task_queue.put(
                {
                    'type': 3,
                    'url': song_url,
                    'song': song,
                    'artist': artist,
                    'n_errors': 0
                }
            )

    def get_song(self, thread_id, url, song, artist):
        """
        Get song from a URL
        :param thread_id: As usual
        :param url: As usual
        :param song: As usual
        :param artist: Artist of song
        """
        if db_operations.exists_song(self.start_url, url):
            print_util.print_warning(
                '{0} --> Song {1} already exists. Skipping.'.format(
                    thread_id,
                    song
                )
            )
        complete_url = self.start_url + url
        raw_html = open_request(complete_url, delayed=self.delay_request)

        lyrics = self.get_song_details(
            raw_html
        )

        db_operations.save(
            song,
            url,
            self.start_url,
            lyrics,
            artist
        )

    def get_song_details(self, raw_html):
        return (
            'album',
            'lyrics',
            [
                'lyricist1',
                'lyricist2'
            ],
            [
                'additional_artist1',
                'additional_artist2',
            ]
        )

    def get_artist_with_url(self, raw_html):
        return [
            ('url1', 'artist1'),
            ('url2', 'artist2')
        ]

    def get_pages_for_artist(self, raw_html):
        return [
            'url1',
            'url2'
        ]

    def get_songs(self, raw_html):
        return [
            ('url1', 'song1'),
            ('url2', 'song2')
        ]