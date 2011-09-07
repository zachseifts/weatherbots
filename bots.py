#!/usr/bin/env python

from random import choice
from urllib2 import HTTPError

import tweepy

from config import bots
from lib.objects import RedisConnector
from lib.objects import NoDataInRedis

class Bot(object):
    def __init__(self, **kwargs):
        self.consumer_key = kwargs.get('consumer_key')
        self.consumer_secret = kwargs.get('consumer_secret')
        self.access_key = kwargs.get('access_key')
        self.access_secret = kwargs.get('access_secret')
        self.bot_name = kwargs.get('bot_name')
        self.city_names = kwargs.get('city_names')
        self.hash_tags = kwargs.get('hash_tags')

        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_key, self.access_secret)
        self.api = tweepy.API(auth)
        self.update()

    def update(self):
        r = RedisConnector()
        temp = r.get(self.bot_name + ':current:temp')
        cond = r.get(self.bot_name + ':current:cond')
        today_high = r.get(self.bot_name + ':today:high')
        today_low = r.get(self.bot_name + ':today:low')
        tom_high = r.get(self.bot_name + ':tomorrow:high')
        tom_low = r.get(self.bot_name + ':tomorrow:low')
        if (temp and cond and tom_high and tom_low):
            tweet = "It's %sF and %s in %s. High today: %sF, low: %sF High tomorrow:  %sF, low: %sF %s"
            name = choice(self.city_names.split(','))
            self.tweet = tweet % (temp, cond, name, today_high, today_low, tom_high, tom_low, self.hash_tags)
            try:
                self.api.update_status(self.tweet)
            except HTTPError:
                # fail whale ftw
                pass
            except tweepy.error.TweepError:
                # duplicate tweet.
                pass
        else:
            raise NoDataInRedis


if __name__ == '__main__':
    for bot in bots:
        Bot(consumer_key = bot['consumer_key'],
            consumer_secret = bot['consumer_secret'],
            access_key = bot['access_key'],
            access_secret = bot['access_secret'],
            bot_name = bot['bot_name'],
            city_names = bot['city_names'],
            hash_tags = bot['hash_tags'])

