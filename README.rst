============================
slacksound
============================

Create playlists democratically by reactions in Slack


* Documentation: https://slacksound.readthedocs.org/en/latest

Features
--------

* Get Youtube videos reactions from message attachments and add the song to
a Spotify playlist.


How does it work
----------------

The application acts as a middle man between Slack and Spotify by getting the
reactions count from a message's attachment and then looking up the title on
Spotify's. If the title has been found, it will add the one that has best
popularity to the queue.

In order to the bot pick up the song, a user must paste a Youtube URL in the
channel. The bot will start looking for reactions on that URL and get the title
of the video which it will be used as a search text for Spotify.

A message will be shown back to the channel whether the bot could add the song
to the playlist or not.

It is worth mention that the tracks of the playlist will be removed at every
time the bot it is started. This is by design as it in a jukebox.
