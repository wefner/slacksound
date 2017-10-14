
from spotifylib import Spotify
import logging


# This is the main prefix used for logging
LOGGER_BASENAME = '''spotifyclient'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class SpotifyClient(object):
    def __init__(self,
                 client_id,
                 client_secret,
                 username,
                 passsword,
                 callback,
                 scope):
        self._logger = logging.getLogger('{base}.{suffix}'
                                         .format(base=LOGGER_BASENAME,
                                                 suffix=self.__class__.__name__)
                                         )
        self._username = username
        self._spotify = Spotify(client_id=client_id,
                                client_secret=client_secret,
                                username=self._username,
                                password=passsword,
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
