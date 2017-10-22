=====
Usage
=====


Slack
-----
The first step is to create a Slack bot. Instructions
can be found `here <https://api.slack.com/bot-users>`_ under the title
``How do I create custom bot users for my workspace?``

You can give it a name and assign an avatar to it. This will make it easier later
when reading messages from it on your channel.

Once your bot is created, it will generate a token for you in order to
communicate to Slack API.


Spotify
-------
The second step is to register an APP in your Spotify account. You can follow
the instructions on how to do this in `here <http://spotifylib.readthedocs.io/en/latest/usage.html#instructions>`_


Configuration
-------------
Once you have all the details, you are going to need to create a configuration
file so that the CLI can get all the parameters.

By default, the program will look into a hidden file named ``.slacksound``
under your home directory but you can also specify the location manually.

.. code-block:: bash

    slacksound --configuration /Users/slack/myconfig.cfg


The configuration must be like as per below:

.. code-block:: ini

    [spotify]
    username = <username>
    password = <password>
    client_id = <client_id>
    client_secret = <client_secret>
    playlist = <playlist_name>
    callback_url = <callback_url>
    scope = <scope>

    [slack]
    token = <bot_token>
    channel = <channel_name>
    reaction = <emoji_reaction>
    count = <number_of_reaction_counts>

