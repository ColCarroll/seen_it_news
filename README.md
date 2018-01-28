Seen It News
============

Inspired by the wonderful [@NYT_first_said](https://twitter.com/NYT_first_said), this project uses
the MIT Center for Civic Media's [Media Cloud project](https://mediacloud.org/) to find the earliest
mention of a word in major English language newspapers. It uses this to issue a smugly superior
tweet.


Installation
------------

I do not have a `setup.py` for this, so you need to install from source:
```
$ git clone git@github.com:ColCarroll/seen_it_news.git
$ cd seen_it_news  # and probably activate a virtual environment
$ pip install -r requirements.txt
```

There should be a file called `.config.json` configuring the project. The useful
[grift](https://github.com/kensho-technologies/grift) library will complain intelligently about
each setting that you need to fill in. At the very least, you will need an API key for Media Cloud,
which you get by [signing up for a free account](https://tools.mediacloud.org/#/user/signup), and 
credentials for twitter, which 
[digital ocean's tutorial](https://www.digitalocean.com/community/tutorials/how-to-create-a-twitter-app)
does a good job of describing.


Quickstart
----------

After installing and configuring, just `python seen_it_news` should check up to 20 recent tweets,
and respond to those it can. Data is stored in a sqlite database (`history.db`, by default), and
everything is logged to stdout.


Can it be used for anything useful?
-----------------------------------

Yes! You can get the string it plans to tweet with `first_mention`:

```
>>> from seen_it_news import FindFirstMention

>>> finder = FindFirstMention('vernatsch')

>>> print(finder.first_mention())
@NYT_first_said The Mercury News was saying "vernatsch" for 8 years before the New York Times did:
https://www.mercurynews.com/2009/03/10/wine-why-isnt-this-one-on-every-restaurants-list/
```

You can also get all historical uses as a generator of tuples (which makes it easier to use elsewhere):

```
>>> for mention in finder.all_mentions():
...:     print(mention)
...: 
(Media(name='The Wall Street Journal', id=1150, netloc='www.wsj.com'), 'Fall Wines: Go Red, but Light', 'https://www.wsj.com/articles/SB10000872396390443686004577635632300446956', datetime.datetime(2012, 9, 15, 0, 39, 5, tzinfo=tzutc()))
(Media(name='The Mercury News', id=35, netloc='www.mercurynews.com'), "Wine: Why isn't this one on every restaurant's list?", 'https://www.mercurynews.com/2009/03/10/wine-why-isnt-this-one-on-every-restaurants-list/', datetime.datetime(2009, 3, 10, 11, 44, 39, tzinfo=tzutc()))

```

That still does not seem very useful
------------------------------------

Ouch! But fair! See Media Cloud's ["Press and Publications"](https://mediacloud.org/publications/) page
for more academic uses of the project.
