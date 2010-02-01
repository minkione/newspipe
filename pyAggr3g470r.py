#! /usr/local/bin/python
#-*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.4 $"
__date__ = "$Date: 2010/02/01 $"
__copyright__ = "Copyright (c) 2010 Cedric Bonhomme"
__license__ = "GPLv3"

import base64
import sqlite3
import cherrypy
import ConfigParser

from datetime import datetime
from cherrypy.lib.static import serve_file

config = ConfigParser.RawConfigParser()
config.read("./cfg/pyAggr3g470r.cfg")
path = config.get('global','path')

bindhost = "0.0.0.0"

cherrypy.config.update({ 'server.socket_port': 12556, 'server.socket_host': bindhost})

path = { '/css/style.css': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':path+'css/style.css'}}

htmlheader = """<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
                lang="en">\n<head>\n<link rel="stylesheet" type="text/css" href="/css/style.css"
                />\n<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n
                <title>pyAggr3g470r - RSS Feed Reader</title> </head>"""

htmlfooter =  """This software is under GPLv3 license.</div>
                </body></html>"""

htmlnav = """<body><h1><a name="top"><a href="/">pyAggr3g470r - RSS Feed Reader</a></a></h1><a
href="http://bitbucket.org/cedricbonhomme/pyaggr3g470r/">pyAggr3g470r (source code)</a>
"""


class Root:
    def index(self):
        """
        Main page containing the list of feeds and articles.
        """
        self.dic = self.load_feed()
        html = htmlheader
        html += htmlnav
        html += """<div class="right inner">\n"""
        html += """<form method=get action="q/"><input type="text" name="v" value=""><input
        type="submit" value="search"></form>\n"""
        html += """<a href="f/">Management of feed</a>\n"""
        html += "<hr />\n"
        html += "Your feeds:<br />\n"
        for rss_feed in self.dic.keys():
            html += """<a href="/#%s">%s</a><br />\n""" % (rss_feed.encode('utf-8'), \
                                    self.dic[rss_feed][0][5].encode('utf-8'))
        html += """</div>\n<div class="left inner">\n"""

        for rss_feed in self.dic.keys():
            html += '<h2><a name="' + rss_feed.encode('utf-8') + '">' + \
                        '<a href="' + self.dic[rss_feed][0][6].encode('utf-8') + \
                        '">' + self.dic[rss_feed][0][5].encode('utf-8') + "</a></a></h2>\n"

            # The main page display only 10 articles by feeds.
            for article in self.dic[rss_feed][:10]:
                html += article[1].encode('utf-8') + " - " + \
                        '<a href="' + article[3].encode('utf-8') + \
                        '">' + article[2].encode('utf-8') + "</a>" + \
                        """ - [<a href="/description/%s">description</a>]""" % (article[0].encode('utf-8'),) + \
                        "<br />\n"
            html += "<br />\n"

            html += """[<a href="/all_articles/%s">All articles</a>]""" % (rss_feed,)
            html += """<h4><a href="/#top">Top</a></h4>"""
            html += "<hr />\n"
        html += htmlfooter
        return html

    def f(self):
        """
        """
        return "Hello world !"

    def description(self, article_id):
        """
        Display the description of an article in a new Web page.
        """
        html = htmlheader
        html += htmlnav
        html += """</div> <div class="left inner">"""
        for rss_feed in self.dic.keys():
            for article in self.dic[rss_feed]:
                if article_id == article[0]:
                    html += article[4].encode('utf-8')
                    html += """<hr />\n<a href="%s">Complete story</a>""" % (article[3].encode('utf-8'),)
        html += "<br />" + htmlfooter
        return html

    def all_articles(self, feed_title):
        """
        Display all articles of a feed ('feed_title').
        """
        html = htmlheader
        html += htmlnav
        html += """</div> <div class="left inner">"""

        for article in self.dic[feed_title]:
            html += article[1].encode('utf-8') + " - " + \
                    '<a href="' + article[3].encode('utf-8') + \
                    '">' + article[2].encode('utf-8') + "</a>" + \
                    """ - [<a href="/description/%s">description</a>]""" % (article[0].encode('utf-8'),) + \
                    "<br />\n"

        html += """<h4><a href="/">All feeds</a></h4>"""
        html += htmlfooter
        return html

    def load_feed(self):
        """
        Load feeds in a dictionary.
        """
        list_of_articles = None
        try:
            conn = sqlite3.connect("./var/feed.db", isolation_level = None)
            c = conn.cursor()
            list_of_articles = c.execute("SELECT * FROM rss_feed").fetchall()
            c.close()
        except:
            pass

        # The key of dic is the title of the feed:
        # dic[feed_title] = (article_id, article_date, article_title, article_link, article_description, feed_title, feed_link)
        dic = {}
        if list_of_articles is not None:
            for article in list_of_articles:
                feed_id = base64.b64encode(article[5].encode('utf-8'))
                article_id = base64.b64encode(article[2].encode('utf-8'))

                article_tuple = (article_id, article[0], article[1], article[2], article[3], article[4], article[5])

                if feed_id not in dic:
                    dic[feed_id] = [article_tuple]
                else:
                    dic[feed_id].append(article_tuple)

            # sort articles by date for each feeds
            for feeds in dic.keys():
                dic[feeds].sort(lambda x,y: compare(y[1], x[1]))

            return dic
        return dic

    index.exposed = True
    f.exposed = True
    description.exposed = True
    all_articles.exposed = True


def compare(stringtime1, stringtime2):
    """
    Compare two dates in the format 'yyyy-mm-dd hh:mm:ss'.
    """
    date1, time1 = stringtime1.split(' ')
    date2, time2 = stringtime2.split(' ')

    year1, month1, day1 = date1.split('-')
    year2, month2, day2 = date2.split('-')

    hour1, minute1, second1 = time1.split(':')
    hour2, minute2, second2 = time2.split(':')

    datetime1 = datetime(year=int(year1), month=int(month1), day=int(day1), \
                        hour=int(hour1), minute=int(minute1), second=int(second1))

    datetime2 = datetime(year=int(year2), month=int(month2), day=int(day2), \
                        hour=int(hour2), minute=int(minute2), second=int(second2))

    if datetime1 < datetime2:
        return -1
    elif datetime1 > datetime2:
        return 1
    else:
        return 0


if __name__ == '__main__':
    root = Root()
    cherrypy.quickstart(root, config=path)