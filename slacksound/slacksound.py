#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: slacksound.py
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
Main code for slacksound

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging
import os
import json
import argparse
import time

from collections import namedtuple
from slackapi import Slack
from spotifyclient import SpotifyClient

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

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
LOGGER_BASENAME = '''slacksound'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


SlackSound = namedtuple('Config', ['playlist',
                                   'reaction',
                                   'channel',
                                   'count'])


def get_arguments():
    """
    This get us the cli arguments.
    Returns the args as parsed from the argsparser.
    """
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(description='''Create playlists democratically by reactions in Slack''')
    parser.add_argument('--log-config',
                        '-l',
                        action='store',
                        dest='logger_config',
                        help='The location of the logging config json file',
                        default='')
    parser.add_argument('--log-level',
                        '-L',
                        help='Provide the log level. Defaults to INFO.',
                        dest='log_level',
                        action='store',
                        default='INFO',
                        choices=['DEBUG',
                                 'INFO',
                                 'WARNING',
                                 'ERROR',
                                 'CRITICAL'])
    parser.add_argument('--credentials',
                        dest='credentials',
                        action='store',
                        default=False,
                        required=False)
    args = parser.parse_args()
    return args


def setup_logging(args):
    """
    This sets up the logging.
    Needs the args to get the log level supplied
    Args:
        args: The arguments returned gathered from argparse
    """
    # This will configure the logging, if the user has set a config file.
    # If there's no config file, logging will default to stdout.
    if args.logger_config:
        # Get the config for the logger. Of course this needs exception
        # catching in case the file is not there and everything. Proper IO
        # handling is not shown here.
        configuration = json.loads(open(args.logger_config).read())
        # Configure the logger
        logging.config.dictConfig(configuration)
    else:
        handler = logging.StreamHandler()
        handler.setLevel(args.log_level)
        formatter = logging.Formatter(('%(asctime)s - '
                                       '%(name)s - '
                                       '%(levelname)s - '
                                       '%(message)s'))
        handler.setFormatter(formatter)
        LOGGER.addHandler(handler)


def get_credentials(filename=False):
    """
    Reads credentials file

    Locates credentials fire in ~/.slacksound and loads them. This file must be
    a INI file

    :return: ConfigParser instance
    """
    if filename:
        credentials_file = filename
    else:
        credentials_file = '{home}/.slacksound'.format(home=os.path.expanduser('~'))

    LOGGER.info("Using credentials file %s", credentials_file)
    if not os.path.isfile(credentials_file):
        raise OSError('File not found')
    config = configparser.ConfigParser()
    config.read(credentials_file)
    return config


def connect_spotify(credentials):
    spotify = SpotifyClient(client_id=credentials.get('spotify', 'client_id'),
                            client_secret=credentials.get('spotify', 'client_secret'),
                            username=credentials.get('spotify', 'username'),
                            password=credentials.get('spotify', 'password'),
                            callback=credentials.get('spotify', 'callback_url'),
                            scope=credentials.get('spotify', 'scope'))
    return spotify


def sanitize_title(title):
    return title.split('(')[0].strip()


def get_config_details(credentials):
    config = SlackSound(playlist=credentials.get('spotify', 'playlist'),
                        reaction=credentials.get('slack', 'reaction'),
                        channel=credentials.get('slack', 'channel'),
                        count=int(credentials.get('slack', 'count')))
    return config


def main():
    """
    Main method.
    This method holds what you want to execute when
    the script is run on command line.
    """
    args = get_arguments()
    setup_logging(args)
    credentials = get_credentials(args.credentials)
    config_details = get_config_details(credentials)
    spotify = connect_spotify(credentials)
    slack = Slack(credentials.get('slack', 'token'), bot=True)
    slack_playlist = slack.get_group_by_name(config_details.channel)
    spotify.delete_tracks_playlist(config_details.playlist)
    slack.post_message("Jukebox started!", config_details.channel)

    while True:
        print(slack.client.rtm_read())
        time.sleep(1)
        for message in slack_playlist.history.messages:
            if message.unix_time >= start_time:
                for reaction in message.reaction:
                    for attachment in message.attachments:
                        sanitized_title = sanitize_title(attachment.title)
                    song_id = spotify.get_song_id_by_name(sanitized_title)
                    if song_id not in spotify.get_songs_in_playlist(config_details.playlist):
                        if reaction.count >= config_details.count and reaction.name == config_details.reaction:
                            try:
                                spotify.add_song_to_playlist(song_id,
                                                             config_details.playlist)
                                slack.post_message(
                                    "Song {} added".format(sanitized_title),
                                    'testapi')
                            except AttributeError:
                                slack.post_message("Couldn't find the song",
                                                   config_details.channel)
                            break


if __name__ == '__main__':
    start_time = time.time()
    main()
