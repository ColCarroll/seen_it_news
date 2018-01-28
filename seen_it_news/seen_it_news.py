from collections import namedtuple
from contextlib import contextmanager
import logging
from urllib.parse import urlparse, urlunparse
import sqlite3

import arrow
import humanize
import pytz
import requests
import tweepy
import mediacloud

from .config import app_config


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('seen_it_news')

Media = namedtuple('Media', ('name', 'id', 'netloc'))

class DB(object):
    """Tiny sqlite3 db to keep a history of things searched for"""
    @contextmanager
    def get_conn(self):
        """Secretly creates the table if it does not exist"""
        conn = sqlite3.connect(app_config.DB_FILE)
        conn.execute('''CREATE TABLE IF NOT EXISTS words
                        (word varchar unique, success bool)''')
        try:
            yield conn
        finally:
            conn.close()

    def exists(self, word):
        with self.get_conn() as conn:
            try:
                next(conn.execute('SELECT 1 FROM words WHERE word = ? LIMIT 1', (word,)))
                return True
            except StopIteration:
                return False

    def add(self, word, success):
        with self.get_conn() as conn:
            conn.execute('INSERT INTO words VALUES (?, ?)', (word, success))
            conn.commit()

    def delete(self, word):
        with self.get_conn() as conn:
            conn.execute('DELETE FROM words WHERE word = ?', (word,))
            conn.commit()


def get_twitter_api():
    auth = tweepy.OAuthHandler(app_config.consumer_key, app_config.consumer_secret)
    auth.set_access_token(app_config.access_token, app_config.access_token_secret)
    api = tweepy.API(auth)
    return api


def normalize_url(url):
    """Strips trailing metadata from a url"""
    replace = {'params': '', 'query': '', 'fragment': ''}
    return urlunparse(urlparse(url)._replace(**replace))


class FindFirstMention(object):
    media_list = (
        Media('The Wall Street Journal', 1150, 'www.wsj.com'),
        Media('USA Today', 4, 'www.usatoday.com'),
        Media('The LA Times', 6, 'www.latimes.com'),
        Media('The Mercury News', 35, 'www.mercurynews.com'),
        Media('The NY Daily News', 8, 'www.nydailynews.com'),
        Media('The NY Post', 7, 'nypost.com'),
        Media('The Washington Post', 2, 'www.washingtonpost.com'),
        Media('The Dallas Morning News', 12, 'www.dallasnews.com'),
        Media('The Chicago Tribune', 9, 'www.chicagotribune.com'),
        Media('The Houston Chronicle', 10, 'www.chron.com'),
        Media('The Guardian', 1751, 'www.guardian.co.uk'),
        Media('FOX News', 1092, 'www.foxnews.com'),
    )

    def __init__(self, word, mention_datetime=None):
        self.word = word
        self.mc_client = mediacloud.api.MediaCloud(app_config.MC_API_KEY)
        if mention_datetime is None:
            self.mention_datetime = arrow.now().datetime
        else:
            self.mention_datetime = pytz.utc.localize(mention_datetime)

    def media_mention(self, media):
        try:
            hits = self.mc_client.storyList(self.word, solr_filter='media_id:{}'.format(media.id))
            if hits:
                for hit in sorted(hits, key=lambda j: j['publish_date']):
                    r = requests.get(hit['url'])
                    if r.ok and urlparse(r.url).netloc == media.netloc:
                        return (
                            media,
                            hit['title'],
                            normalize_url(r.url),
                            arrow.get(hit['publish_date']).datetime
                            )
        except Exception as exc:
            logger.error(exc)
        return None

    def all_mentions(self):
        for media in self.media_list:
            mention = self.media_mention(media)
            if mention is not None:
                yield mention

    def to_string(self, result):
        if result is not None:
            media, title, url, date = result
            return '@NYT_first_said {} was saying "{}" for {} before the New York Times did:\n{}'.format(
                media.name, self.word, humanize.naturaldelta(self.mention_datetime - date), url)

    def first_mention(self):
        mentions = list(self.all_mentions())
        if mentions:
            return self.to_string(min(mentions, key=lambda j: j[-1]))
        else:
            return self.to_string(None)


def hipster_media(word, mention_datetime):
    """Find the first use of a word"""
    finder = FindFirstMention(word, mention_datetime)
    return finder.first_mention()


def run():
    db = DB()
    api = get_twitter_api()
    for latest in api.user_timeline('NYT_first_said'):
        word = latest.text.strip()

        if ' ' in word or db.exists(word):
            logger.info('{} already exists!'.format(word))
            return
        logger.info('Searching for {}!'.format(word))
        first_mention = hipster_media(word, latest.created_at)
        if first_mention is None:
            logger.info('No mention of {}'.format(word))
            success = False
        else:
            logger.info(first_mention)
            api.update_status(first_mention, latest.id)
            success = True
        db.add(word, success)
