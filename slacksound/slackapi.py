#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: slackapi.py
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
Main code for slackapi

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
        """
        Initialise object. If bot is true it will use the RTM API

        Args:
            token: string
            bot: boolean
        """
        self.client = SlackClient(token)
        if bot:
            self.client = SlackClient(token)
            self.client.rtm_connect()
        self.__channels = []
        self.__users = []
        self.__groups = []

    @property
    def channels(self, **kwargs):
        """
        Gets all channels in a Slack team.

        Args:
            **kwargs: extra kwargs

        Returns: list of Channel objects
        """
        if not self.__channels:
            channels_list = self.client.api_call("channels.list", **kwargs)
            for channel in channels_list.get('channels', {}):
                self.__channels.append(Channel(self, channel))
        return self.__channels

    @property
    def groups(self, **kwargs):
        """
        Gets all groups in a Slack team.

        Args:
            **kwargs: extra kwargs

        Returns: list of Group objects

        """
        if not self.__groups:
            groups_list = self.client.api_call("groups.list", **kwargs)
            for group in groups_list.get('groups', {}):
                self.__groups.append(Group(self, group))
        return self.__groups

    @property
    def users(self, **kwargs):
        """
        Gets all users in a Slack team.

        Args:
            **kwargs: extra kwargs

        Returns: list of Member objects

        """
        if not self.__users:
            users_list = self.client.api_call("users.list", **kwargs)
            for user in users_list.get('members', []):
                self.__users.append(Member(user))
        return self.__users

    def get_channel_by_name(self, channel_name):
        """
        Gets one channel in a Team

        Args:
            channel_name: string

        Returns: Channel object

        """
        channel_object = None
        for channel in self.channels:
            if channel.name_normalized == channel_name:
                channel_object = channel
        return channel_object

    def get_group_by_name(self, group_name):
        """
        Gets one group in a Team

        Args:
            group_name: string

        Returns: Group object

        """
        group_object = None
        for group in self.groups:
            if group.name_normalized == group_name:
                group_object = group
        return group_object

    def post_message(self, message, channel):
        """
        Posts a message in a group or channel as the user who is owner of the
        token

        Args:
            message: string
            channel: string

        Returns:

        """
        self.client.api_call("chat.postMessage",
                             channel=channel,
                             text=message,
                             as_user=True)
        return True


class Member(object):
    """
    Model for a Member

    Not all attributes are populated here though.

    https://api.slack.com/types/user
    """
    def __init__(self, member_details):
        """
        Initialise object

        Args:
            member_details: dictionary
        """
        self._member_details = member_details

    @property
    def color(self):
        """
        Used in some clients to display a colored username.

        Returns: string
        """
        return self._member_details.get('color', None)

    @property
    def deleted(self):
        """
        Active/Inactive users

        Returns: boolean
        """
        return self._member_details.get('deleted', None)

    @property
    def member_id(self):
        """
        Member ID

        Returns: string

        """
        return self._member_details.get('id', None)

    @property
    def is_admin(self):
        """
        Whether this user is admin or not

        Returns: boolean

        """
        return self._member_details.get('is_admin', None)

    @property
    def email(self):
        """
        Email of the member

        Returns: string

        """
        return self._member_details.get('profile').get('email', None)


class Group(object):
    """
    Model for a group

    Not all attributes are populated here though.

    https://api.slack.com/types/group
    """
    def __init__(self, slack_instance, group_details):
        """
        Initialise object

        Args:
            slack_instance: SlackClient instance
            group_details: dictionary
        """
        self._slack_instance = slack_instance
        self._group_details = group_details

    @property
    def group_id(self):
        """
        Group ID

        Returns: string

        """
        return self._group_details.get('id', None)

    @property
    def name(self):
        """
        Name of the group

        Returns: string

        """
        return self._group_details.get('name', None)

    @property
    def is_general(self):
        """
        Whether the group is general or not

        Returns: boolean

        """
        return self._group_details.get('is_general', None)

    @property
    def name_normalized(self):
        """
        Normalized name of the group

        Returns: string

        """
        return self._group_details.get('name_normalized', None)

    @property
    def created(self):
        """
        Unix time converted to datetime object

        Returns: datetime object

        """
        unix_timestamp = self._group_details.get('created', None)
        date = datetime.fromtimestamp(float(unix_timestamp),
                                      tzlocal.get_localzone())
        return date

    @property
    def history(self):
        """
        Chat history of the group

        Returns: list of Message objects

        """
        ch_history = self._slack_instance.client.api_call(
                                    method="groups.history",
                                    channel=self.group_id)
        return [Message(history_message) for history_message in
                ch_history.get('messages')]


class Channel(object):
    """
    Model for a Channel

    Not all attributes are populated here though.

    https://api.slack.com/types/channel
    """
    def __init__(self, slack_instance, channel_details):
        """
        Initialise object

        Args:
            slack_instance: SlackClient instance
            channel_details: dictionary
        """
        self.__slack_instance = slack_instance
        self._channel_details = channel_details

    @property
    def channel_id(self):
        """
        Channel ID

        Returns: string

        """
        return self._channel_details.get('id', None)

    @property
    def name(self):
        """
        Name of the channel

        Returns: string

        """
        return self._channel_details.get('name', None)

    @property
    def is_general(self):
        """
        Whether the channel is general or not

        Returns: boolean

        """
        return self._channel_details.get('is_general', None)

    @property
    def name_normalized(self):
        """
        Normalized name of the channel

        Returns: string

        """
        return self._channel_details.get('name_normalized', None)

    @property
    def created(self):
        """
        Unix time converted to datetime object

        Returns: datetime object

        """
        unix_timestamp = self._channel_details.get('created', None)
        date = datetime.fromtimestamp(float(unix_timestamp),
                                      tzlocal.get_localzone())
        return date

    @property
    def history(self):
        """
        Chat history of the channel

        Returns: list of Message objects

        """
        ch_history = self.__slack_instance.client.api_call(
                                    method="channels.history",
                                    channel=self.channel_id)
        return [Message(history_message) for history_message in
                ch_history.get('messages')]


class Message(object):
    """
    Model for a Message

    Not all attributes are populated here though.

    https://api.slack.com/events/message
    """
    def __init__(self, message_details):
        """
        Initialise object

        Args:
            message_details: dictionary
        """
        self._message_details = message_details

    @property
    def text(self):
        """
        Text of the message

        Returns: string

        """
        return self._message_details.get('text', None)

    @property
    def type(self):
        """
        SubType of the Message

        Returns: string

        """
        return self._message_details.get('type', None)

    @property
    def attachments(self):
        """
        Attachments for a Message, if any

        Returns: list of Attachment objects

        """
        return [Attachment(m_attachment) for m_attachment in
                self._message_details.get('attachments', [])]

    @property
    def user(self):
        """
        ID of the user speaking or sent the message

        Returns: string

        """
        return self._message_details.get('user', None)

    @property
    def datetime(self):
        """
        Unix time converted to datetime object

        Returns: datetime object

        """
        unix_timestamp = self._message_details.get('ts', None)
        date = datetime.fromtimestamp(float(unix_timestamp),
                                      tzlocal.get_localzone())
        return date

    @property
    def unix_time(self):
        """
        Unix time. Useful for time comparison

        Returns: float

        """
        return float(self._message_details.get('ts', None))

    @property
    def reaction(self):
        """
        Reactions of the message

        Returns: list of Reaction objects

        """
        return [Reaction(reaction) for reaction
                in self._message_details.get('reactions', [])]


class Reaction(object):
    """
    Model for a Reaction

    These are Emoji icons for a message
    """

    def __init__(self, reaction_details):
        """
        Initialise object

        Args:
            reaction_details: dictionary
        """
        self._reaction_details = reaction_details

    @property
    def count(self):
        """
        Count of a reaction

        Returns: integer

        """
        return self._reaction_details.get('count', None)

    @property
    def name(self):
        """
        Name of the reaction

        Returns: string

        """
        return self._reaction_details.get('name', None)

    @property
    def users(self):
        """
        User IDs who reacted on the reaction

        Returns: list of user ID

        """
        return self._reaction_details.get('users', [])


class Attachment(object):
    """
    Model for an Attachment

    Not all attributes are populated here though.

    https://api.slack.com/docs/message-attachments
    """
    def __init__(self, attachment_details):
        """
        Initialise object

        Args:
            attachment_details: dictionary
        """
        self._attachment_details = attachment_details

    @property
    def author_link(self):
        """
        A valid URL that will hyperlink the author_name text mentioned above.

        Returns: string

        """
        return self._attachment_details.get('author_link', None)

    @property
    def author_name(self):
        """
        Small text used to display the author's name.

        Returns: string

        """
        return self._attachment_details.get('author_name', None)

    @property
    def title(self):
        """
        Title of the attachment

        Returns: string

        """
        return self._attachment_details.get('title', None)
