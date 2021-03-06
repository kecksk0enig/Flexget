from __future__ import unicode_literals, division, absolute_import
import re
import logging

from flexget import plugin
from flexget.event import event
from flexget.plugins.plugin_urlrewriting import UrlRewritingError
from flexget.utils.tools import urlopener
from flexget.utils.soup import get_soup

log = logging.getLogger('FTDB')


class UrlRewriteFTDB(object):
    """FTDB RSS url_rewrite"""

    def url_rewritable(self, task, entry):
        #url = entry['url']
        if re.match(r'^http://www\.frenchtorrentdb\.com/[^/]+(?!/)[^/]+&rss=1', (entry['url'])):
            return True
        return False

    def url_rewrite(self, task, entry):
        old_url = entry['url']
        page_url = old_url.replace('DOWNLOAD', 'INFOS')
        page_url = page_url.replace('&rss=1', '')

        new_url = self.parse_download_page(page_url)
        log.debug('PAGE URL NEEDED : %s' % page_url)
        log.debug('%s OLD is rewrited to NEW %s' % (old_url, new_url))
        entry['url'] = new_url

    def parse_download_page(self, page_url):
        page = urlopener(page_url, log)
        try:
            soup = get_soup(page)
        except Exception as e:
            raise UrlRewritingError(e)
        tag_a = soup.find("a", {"class": "dl_link"})
        if not tag_a:
            raise UrlRewritingError(
                'FTDB Unable to locate download link from url %s and tag_a is : %s' % (page_url, tag_a)
            )
        torrent_url = "http://www.frenchtorrentdb.com" + tag_a.get('href') + "&js=1"
        log.debug('TORRENT URL is : %s' % torrent_url)
        return torrent_url


@event('plugin.register')
def register_plugin():
    plugin.register(UrlRewriteFTDB, 'frenchtorrentdb', groups=['urlrewriter'], api_ver=2)
