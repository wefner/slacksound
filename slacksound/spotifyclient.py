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
        if not self._playlists:
            self._playlists = self._spotify.user_playlists(self._username)
        return self._playlists

    def get_song_id_by_name(self, song_title):
        song_uri = None
        songs = self._spotify.search(q=song_title, limit=5, type='track')
        self._logger.debug('song title: {}'.format(song_title))
        for song in songs.get('tracks').get('items'):
            song_uri = song.get('uri')
        return song_uri

    def add_song_to_playlist(self, song_id, playlist_name):
        for playlist in self.playlists.get('items'):
            if playlist.get('name') == playlist_name:
                print("adding song")
                self._spotify.user_playlist_add_tracks(user=self._username,
                                                 playlist_id=playlist.get('uri'),
                                                 tracks=[song_id])
        return True

    def get_songs_in_playlist(self, playlist_name):
        songs_playlist = None
        for playlist in self.playlists.get('items'):
            if playlist.get('name') == playlist_name:
                songs_playlist = self._spotify.user_playlist_tracks(user=self._username,
                                                              playlist_id=playlist.get('id'))
        return [track.get('track').get('uri')
                for track in songs_playlist.get('items')]

    def get_plalist_id_by_name(self, playlist_name):
        for playlist in self.playlists.get('items'):
            if playlist.get('name') == playlist_name:
                return playlist.get('id')

    def delete_tracks_playlist(self, playlist):
        playlist_id = self.get_plalist_id_by_name(playlist)
        self._spotify.user_playlist_remove_all_occurrences_of_tracks(self._username,
                                                                     playlist_id,
                                                                     self.get_songs_in_playlist(playlist))
