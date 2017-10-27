#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: spotifyclient.py
#
# Copyright 2017 Oriol Fabregas
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
Main code for spotifyclient

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
from spotifylib import Spotify
import logging

__author__ = '''Oriol Fabregas <fabregas.oriol@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''2017-10-13'''
__copyright__ = '''Copyright 2017, Oriol Fabregas'''
__credits__ = ["Oriol Fabregas"]
__license__ = '''MIT'''
__maintainer__ = '''Oriol Fabregas'''
__email__ = '''<fabregas.oriol@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".

# This is the main prefix used for logging
LOGGER_BASENAME = '''spotifyclient'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class SpotifyClient(object):
    def __init__(self,
                 client_id,
                 client_secret,
                 username,
                 password,
                 callback,
                 scope):
        """
        Initialise object to interact with Spotify API

        +info: https://github.com/wefner/spotifylib

        Args:
            client_id: string
            client_secret: string
            username: string
            password: string
            callback: string
            scope: string
        """
        self._logger = logging.getLogger('{base}.{suffix}'
                                         .format(base=LOGGER_BASENAME,
                                                 suffix=self.__class__.__name__)
                                         )
        self._username = username
        self._spotify = Spotify(client_id=client_id,
                                client_secret=client_secret,
                                username=username,
                                password=password,
                                callback=callback,
                                scope=scope)
        self._playlists = None

    @property
    def playlists(self):
        """
        Get all playlists for the user within its scope

        It also passes username and Spotify instance as it is needed for
        Playlist object

        Returns: list of Playlist objects
        """
        if not self._playlists:
            raw_playlists = self._spotify.user_playlists(self._username)
            self._playlists = [Playlist(self._username, self._spotify, playlist)
                               for playlist in raw_playlists.get('items')]
        return self._playlists

    def get_track_by_title(self, track_title, limit=5):
        """
        Looks up on Spotify for a text string and returns tracks if found

        The limit is an optional argument to retrieve more results

        Examples:
            'Eric Clapton - Cocaine'
            "Bon Jovi - Livin' On A Prayer"

        Args:
            track_title: string
            limit: integer

        Returns: list of Track objects

        """
        self._logger.debug('Looking for title: %s', track_title)
        songs = self._spotify.search(q=track_title.encode('utf-8'), limit=limit, type='track')
        return [Track(track) for track in songs.get('tracks', {}).get('items')]

    def get_playlist_by_name(self, playlist_name):
        """
        Looks into all playlists and returns the one that matched

        Args:
            playlist_name: string

        Returns: Playlist object

        """
        playlist = next((plist for plist in self.playlists
                         if plist.name == playlist_name), None)
        return playlist


class Track(object):
    """Model for a Track"""

    def __init__(self, track_details):
        """
        Initialise object

        Args:
            track_details: dictionary
        """
        self._track_details = track_details

    @property
    def uri(self):
        """
        URI of the track

        Returns: URI

        """
        return self._track_details.get('uri', None)

    @property
    def track_id(self):
        """
        Track ID

        Returns: string

        """
        return self._track_details.get('id', None)

    @property
    def popularity(self):
        """
        Popularity of the track

        Returns: integer

        """
        return self._track_details.get('popularity', None)

    @property
    def name(self):
        """
        Name of the track

        Returns: string

        """
        return self._track_details.get('name', None)

    @property
    def duration_ms(self):
        """
        Duration in milliseconds

        Returns: integer

        """
        return self._track_details.get('duration_ms', None)


class Playlist(object):
    """Playlist model"""

    def __init__(self, username, spotify_instance, playlist_details):
        """
        Initialise object

        Args:
            username: string
            spotify_instance: SpotifyClient object
            playlist_details: dictionary
        """
        self._logger = logging.getLogger('{base}.{suffix}'
                                         .format(base=LOGGER_BASENAME,
                                                 suffix=self.__class__.__name__)
                                         )
        self._username = username
        self._spotify = spotify_instance
        self._playlist_details = playlist_details

    @property
    def tracks(self):
        """
        Get all tracks in the playlist

        Returns: list of Track objects

        """
        songs_playlist = self._spotify.user_playlist_tracks(user=self._username,
                                                            playlist_id=self.playlist_id)
        return [Track(track.get('track')) for track
                in songs_playlist.get('items')]

    def delete_all_tracks(self):
        """
        Deletes all tracks that are in the playlist

        Returns: Snapshot ID

        """
        track_ids = [track.track_id for track in self.tracks]
        return self._spotify.user_playlist_remove_all_occurrences_of_tracks(self._username,
                                                                            self.playlist_id,
                                                                            track_ids)

    def add_track(self, track_id):
        """
        Add a track to the playlist

        Args:
            track_id: string

        Returns: Boolean

        """
        self._logger.info("Adding song %s", track_id)
        self._spotify.user_playlist_add_tracks(user=self._username,
                                               playlist_id=self.uri,
                                               tracks=[track_id])
        return True

    @property
    def href(self):
        """
        Link of the Playlist

        Returns: string

        """
        return self._playlist_details.get('href', None)

    @property
    def collaborative(self):
        """
        Whether it is collaborative or not

        Returns: boolean

        """
        return self._playlist_details.get('collaborative', None)

    @property
    def playlist_id(self):
        """
        Playlist ID

        Returns: string

        """
        return self._playlist_details.get('id', None)

    @property
    def name(self):
        """
        Name of the Playlist
        Returns:

        """
        return self._playlist_details.get('name', None)

    @property
    def public(self):
        """
        Whether it is a public playlist or not

        Returns: boolean

        """
        return self._playlist_details.get('public', None)

    @property
    def uri(self):
        """
        URI of the playlist

        Returns: string

        """
        return self._playlist_details.get('uri', None)
