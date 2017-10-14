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
import tzlocal
from slackclient import SlackClient
from datetime import datetime


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
LOGGER_BASENAME = '''slackapi'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class Slack(object):
    def __init__(self, token, bot=False):
        self.client = SlackClient(token)
        if bot:
            self.client = SlackClient(token)
            self.client.rtm_connect()
        self.__channels = []
        self.__users = []
        self.__groups = []

    @property
    def channels(self, **kwargs):
        if not self.__channels:
            channels_list = self.client.api_call("channels.list", **kwargs)
            for channel in channels_list.get('channels', {}):
                self.__channels.append(Channel(self, channel))
        return self.__channels

    @property
    def groups(self, **kwargs):
        if not self.__groups:
            groups_list = self.client.api_call("groups.list", **kwargs)
            for group in groups_list.get('groups', {}):
                self.__groups.append(Group(self, group))
        return self.__groups

    @property
    def users(self, **kwargs):
        if not self.__users:
            users_list = self.client.api_call("users.list", **kwargs)
            for user in users_list.get('members', []):
                self.__users.append(Member(user))
        return self.__users

    def get_channel_by_name(self, channel_name):
        channel_object = None
        for channel in self.channels:
            if channel.name_normalized == channel_name:
                channel_object = channel
        return channel_object

    def get_group_by_name(self, group_name):
        group_object = None
        for group in self.groups:
            if group.name_normalized == group_name:
                group_object = group
        return group_object

    def get_bot_id_by_name(self, bot_name):
        api_call = self.client.api_call("users.list")
        users = api_call.get('members')
        bot_id = None
        for user in users:
            if 'name' in user and user.get('name') == bot_name:
                bot_id = user.get('id')
        return bot_id

    def post_message(self, message, channel):
        self.client.api_call("chat.postMessage",
                              channel=channel,
                              text=message,
                              as_user=True)
        return True


class Member(object):
    def __init__(self, member_details):
        self._member_details = member_details

    @property
    def color(self):
        return self._member_details.get('color', None)

    @property
    def deleted(self):
        return self._member_details.get('deleted', None)

    @property
    def member_id(self):
        return self._member_details.get('id', None)

    @property
    def is_admin(self):
        return self._member_details.get('is_admin', None)

    @property
    def email(self):
        return self._member_details.get('profile').get('email', None)


class Group(object):
    def __init__(self, slac_instance, group_details):
        self._slack_instance = slac_instance
        self._group_details = group_details

    @property
    def group_id(self):
        return self._group_details.get('id', None)

    @property
    def name(self):
        return self._group_details.get('name', None)

    @property
    def is_general(self):
        return self._group_details.get('is_general', None)

    @property
    def name_normalized(self):
        return self._group_details.get('name_normalized', None)

    @property
    def created(self):
        unix_timestamp = self._group_details.get('created', None)
        date = datetime.fromtimestamp(unix_timestamp, tzlocal.get_localzone())
        return date

    @property
    def history(self):
        ch_history = self._slack_instance.client.api_call(
                                    method="groups.history",
                                    channel=self.group_id)
        return History(ch_history)


class Channel(object):
    def __init__(self, slack_instance, channel_details):
        self.__slack_instance = slack_instance
        self._channel_details = channel_details

    @property
    def channel_id(self):
        return self._channel_details.get('id', None)

    @property
    def name(self):
        return self._channel_details.get('name', None)

    @property
    def is_general(self):
        return self._channel_details.get('is_general', None)

    @property
    def name_normalized(self):
        return self._channel_details.get('name_normalized', None)

    @property
    def created(self):
        unix_timestamp = self._channel_details.get('created', None)
        date = datetime.fromtimestamp(unix_timestamp, tzlocal.get_localzone())
        return date

    @property
    def history(self):
        ch_history = self.__slack_instance.client.api_call(
                                    method="channels.history",
                                    channel=self.channel_id)
        return History(ch_history)


class History(object):
    def __init__(self, history_details):
        self._history_details = history_details

    @property
    def messages(self):
        return [Message(history_message) for history_message in
                self._history_details.get('messages')]


class Message(object):
    def __init__(self, message_details):
        self._message_details = message_details

    @property
    def text(self):
        return self._message_details.get('text', None)

    @property
    def type(self):
        return self._message_details.get('type', None)

    @property
    def attachments(self):
        return [Attachment(m_attachment) for m_attachment in
                self._message_details.get('attachments', [])]

    @property
    def user(self):
        return self._message_details.get('user', None)

    @property
    def datetime(self):
        unix_timestamp = self._message_details.get('ts', None)
        date = datetime.fromtimestamp(float(unix_timestamp),
                                      tzlocal.get_localzone())
        return date

    @property
    def unix_time(self):
        return float(self._message_details.get('ts', None))

    @property
    def reaction(self):
        return [Reaction(reaction) for reaction
                in self._message_details.get('reactions', [])]


class Reaction(object):
    def __init__(self, reaction_details):
        self._reaction_details = reaction_details

    @property
    def count(self):
        return self._reaction_details.get('count', None)

    @property
    def name(self):
        return self._reaction_details.get('name', None)

    @property
    def users(self):
        return self._reaction_details.get('users', None)


class Attachment(object):
    def __init__(self, attachment_details):
        self._attachment_details = attachment_details

    @property
    def author_link(self):
        return self._attachment_details.get('author_link', None)

    @property
    def from_url(self):
        return self._attachment_details.get('from_url', None)

    @property
    def from_url(self):
        return self._attachment_details.get('from_url', None)

    @property
    def author_name(self):
        return self._attachment_details.get('author_name', None)

    @property
    def title(self):
        return self._attachment_details.get('title', None)
