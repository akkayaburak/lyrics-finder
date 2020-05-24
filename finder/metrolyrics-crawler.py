from re import findall, DOTALL, sub
from string import ascii_lowercase
from bs4 import BeautifulSoup

from base_crawler import CrawlerType2


class MetroLyricsCrawler(CrawlerType2):
    def __init__(self, name, start_url, url_list, number_of_threads):
        super().__init__(name, start_url, url_list, number_of_threads)

    def get_song_details(self, raw_html):

        soup = BeautifulSoup(raw_html,'html.parser')
        for span in soup("span"):
            span.decompose()
        for h4 in soup("h4"):
            h4.decompose()
        lyrics = soup.find_all("div",class_="js-lyric-text")
        lyrics = lyrics[0].text
        lyrics = sub(r'\n\s*\n', '\n\n', lyrics)
        #print(lyrics)

        """
        lyrics = findall(
            r'<div id="lyrics-body-text" class="js-lyric-text">\n(.*?)</div>\n</div>\n<p',
            raw_html,
            DOTALL
        )

        if len(lyrics) == 0:
            lyrics = findall(
                r'<div id="lyrics-body-text" class="js-lyric-text">(.*?)</div>', #(.*?)</div>(.*?)</div>(.*?)</div>(.*?)</div>(.*?)</div>(.*?)</div>(.*?)</div>(.*?)</div>(.*?)</div>(.*?)</div>(.*?)</div>(.*?)</div>(.*?)</div>(.*?)</div>(.*?)</div>',
                raw_html,
                DOTALL
            )[0]
        else:
            lyrics = lyrics[0]

        lyrics = sub(
            r'<div class="author">.*?</div>.*?<p class=.*?',
            '',
            lyrics
        ).replace(
            '<p class=\'verse\'>',
            ''
        ).replace(
            '<br>',
            '\n'
        ).replace(
            '</p>',
            '\n\n'
        )
        
        album = findall(
            r'<em>from.*?>(.*?)<',
            raw_html,
            DOTALL
        )

        album = album[0] if len(album) > 0 else ''
        lyricists = findall(
            r'<p class="writers"><strong>Songwriters</strong><br/>(.*?)</',
            raw_html,
            DOTALL
        )

        lyricists = lyricists[0].strip(' \n').split(', ') if len(
            lyricists) > 0 else []

        other_artists = findall(
            r'<p class="fea.*?span.*?>(.*?)</',
            raw_html,
            DOTALL
        )

        other_artists = other_artists[0].split(', ') if len(
            other_artists) > 0 else []
       """
        return lyrics

    def get_artist_with_url(self, raw_html):
        data = findall(
            r'<tr itemscope itemtype="https://schema.org/MusicGroup">.*?<a '
            r'href="(.*?)".*?">(.*?)</a>.*?</tr>',
            raw_html,
            DOTALL
        )

        result = []

        for url, artist in data:
            result.append(
                (
                    url.replace('https://www.metrolyrics.com', ''),
                    artist.replace(' Lyrics', '').strip(' \n')
                )
            )

        return result

    def get_pages_for_artist(self, raw_html):
        area_of_interest = findall(
            r'<span class="pages">(.*?)</span>',
            raw_html,
            DOTALL
        )

        if len(area_of_interest) == 0:
            return []
        else:
            area_of_interest = area_of_interest[0]

        links = findall(
            r'<a href="(.*?)"',
            area_of_interest,
            DOTALL
        )

        return [link.replace('https://www.metrolyrics.com', '') for link in
                links]

    def get_songs(self, raw_html):
        area_of_interest = findall(
            r'<tbody>(.*?)</tbody>',
            raw_html,
            DOTALL
        )

        if len(area_of_interest) == 0:
            return []

        area_of_interest = area_of_interest[0]

        _songs_with_url = findall(
            r'<tr>.*?<td>.*?<a href="(.*?)" .*?>(.*?)</a>',
            area_of_interest,
            DOTALL
        )

        songs_with_url = []

        for url, song in _songs_with_url:
            songs_with_url.append(
                (
                    url.replace('https://www.metrolyrics.com', ''),
                    song.replace(' Lyrics', '').strip(' \n'))
            )

        return songs_with_url


def main():
    pages_dict = {
        '1': 8,  # 8
        'a': 100,  # 85
        'b': 100,  # 81
        'c': 100,  # 81
        'd': 100,  # 81
        'e': 80,  # 42
        'f': 72,  # 39
        'g': 81,  # 42
        'h': 76,  # 37
        'i': 42,  # 21
        'j': 100,  # 77
        'k': 100,  # 47
        'l': 100,  # 62
        'm': 100,  # 94
        'n': 74,  # 36
        'o': 40,  # 17
        'p': 96,  # 50
        'q': 7,  # 3
        'r': 100,  # 57
        's': 100,  # 100
        't': 100,  # 100
        'u': 17,  # 8
        'v': 38,  # 18
        'w': 46,  # 26
        'x': 6,  # 3
        'y': 34,  # 13
        'z': 17  # 8
    }

    l = ['1', ] + list(ascii_lowercase)

    list_of_url = []

    for x in l:
        for y in range(1, pages_dict[x] + 1):
            list_of_url.append(
                '/artists-{0}-{1}.html'.format(
                    x,
                    y
                )
            )

    crawler = MetroLyricsCrawler(
        'Metro Lyrics Crawler',
        'http://www.metrolyrics.com',
        list_of_url,
        1
    )

    crawler.run()


if __name__ == "__main__":
    main()
