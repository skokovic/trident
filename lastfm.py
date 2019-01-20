#
# http://www.last.fm/api/show/geo.getTopTracks
#
from pprint import pprint
import urllib, urllib.request
from urllib.request import urlopen
from bs4 import BeautifulSoup



try:
    import json
except ImportError:
    import simplejson as json


def get_url(page):
    start_link = page.find("data-youtube-url")
    if start_link == -1:
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1: end_quote]
    return url


class LastFM:
    def __init__(self):
        self.API_URL = "http://ws.audioscrobbler.com/2.0/"
        self.API_KEY = "072e9dca8fea49aed6c3c1a3d02d200d"

    def send_request(self, args, **kwargs):
        # Request specific args
        kwargs.update(args)
        # Global args
        kwargs.update({
            "api_key": self.API_KEY,
            "format": "json"
        })
        try:
            # Create an API Request
            url = self.API_URL + "?" + urllib.parse.urlencode(kwargs)
            # Send Request and Collect it
            data = urlopen(url)
            # Print it
            response_data = json.load(data)
            # Close connection
            data.close()
            return response_data
        except urllib.error.HTTPError as e:
            print("HTTP error: %d" % e.code)
        except urllib.error.URLError as e:
            print("Network error: %s" % e.reason.args[1])



    def get_top_artists(self, method, dict):
        # find the key
        args = {
            "method": method,
            "limit": 3
        }
        for key in dict.keys():
            args[key] = dict[key]

        response_data = self.send_request(args)

        if "geo" in method:
            print("Top artists in " + dict["country"] + ":")
        else:
            print("Top artists in " + dict["tag"] + " genre:")
        # Get the first artist from the JSON response and print their name
        for artist in response_data["topartists"]["artist"]:
            print(artist["name"])

    def get_chart_artists(self, method):
        args = {
            "method": method,
            "limit": 3
        }
        response_data = self.send_request(args)

        # Get the first artist from the JSON response and print their name
        print("Top artists in the charts:")
        for artist in response_data["artists"]["artist"]:
            print(artist["name"])

    def get_similar_tracks(self, method, dict):
        args = {
            "method": method,
            "limit": 10
        }
        for key in dict.keys():
            args[key] = dict[key]

        response_data = self.send_request(args)

        # Get the first artist from the JSON response and print their name
        print("Similar tracks of " + dict["artist"] + " - " + dict["track"] + ":")
        for song in response_data["similartracks"]["track"]:
            print(song["artist"]["name"] + " - " + song["name"])

    def get_artist_top_tracks(self, method, dict):
        args = {
            "method": method,
            "limit": 5
        }
        for key in dict.keys():
            args[key] = dict[key]

        response_data = self.send_request(args)

        # Get the first artist from the JSON response and print their name

        for artist in response_data["toptracks"]["track"]:
            print(artist["artist"]["name"] + " - " + artist["name"])

    def get_movie_album(self, method, dict):
        args = {
            "method": method,
            "limit": 1
        }
        for key in dict.keys():
            args[key] = dict[key]

        response_data = self.send_request(args)

        youtube_links = []

        # Get the first artist from the JSON response and print their name
        if response_data["results"]["albummatches"]["album"] is not None:
            album = response_data["results"]["albummatches"]["album"][0]
            print(album["artist"] + " - " + album["name"])
            print(album["url"])

            conn = urlopen(album["url"])
            html = conn.read()

            soup = BeautifulSoup(html)
            links = soup.find_all('a')

            for tag in links:
                link = tag.get('href', None)
                if link is not None:
                    if "www.youtube.com" in link:
                        youtube_links.append(link)


        return(youtube_links)
