# Copyright (c) 2008 Scott Paul Robertson (spr@scottr.org)
#
# tag_wrapper is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version
# 
# tag_wrapper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with tag_wrapper; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from tag_wrapper import dictionary_reverse, Tag, TagException
from mutagen.mp4 import MP4
import re

mp4_frame_mapping = {
        'trkn':     'tracknumber',  # tuple (x, total)
        'tvsh':     'show',
        'disk':     'discnumber',   # tuple (x, total)
        '\xa9cmt':  'comment',
        '\xa9wrt':  'composer',
        'purd':     'purchased',    # TODO: figure this out
        '\xa9alb':  'album',
        'tmpo':     'bpm',
        '\xa9grp':  'grouping',
        '\xa9day':  'date',         # TODO: figure this out
        'aART':     'album artist',
        'cpil':     'compilation',  # boolean
        'apID':     'apple id',
        #'covr':     'album cover', TODO
        'cprt':     'copyright',
        '\xa9ART':  'artist',
        '\xa9nam':  'title',
        'pgap':     'gapless',      #  boolean
        '\xa9gen':  'genre',
}

norm_frame_mapping = dictionary_reverse(mp4_frame_mapping)

class MP4Tag(Tag):
    """The Tag implementation for MP4 (iTunes) tags"""

    def _get_mp4_key(self, key):
        if key in norm_frame_mapping:
            return norm_frame_mapping[key]
        else:
            return key

    def _make_date_from_year(self, year):
        return "%s-01-01T07:00:00Z" % year

    def _get_year_from_date(self, date):
        return re.match(r'(\d{4})-', date).group(1)
    
    def __getitem__(self, key):
        """__getitem__: artist = tag['artist']
        """
        mp4_tag = self._tag[self._get_mp4_key(key)]
        if key == 'tracknumber' or key == 'discnumber':
            return ['/'.join(map(unicode, mp4_tag[0])),]
        elif key == 'date':
            return map(self._get_year_from_date, mp4_tag)
        if type(mp4_tag) != list:
            mp4_tag = [mp4_tag]
        return mp4_tag

    def __setitem__(self, key, value):
        if key == 'tracknumber' or key == 'discnumber':
            value = value.split('/')
        elif key == 'date':
            value = self._make_date_from_year(value)
        
        self._tag[self._get_mp4_key(key)] = value

    def __delitem__(self, key):
        del(self._tag[self._get_mp4_key(key)])

    def __contains__(self, key):
        return (self._get_mp4_key(item) in self._tag)

    def keys(self):
        keys = []
        for mp4_key in self._tag.keys():
            if mp4_key in mp4_frame_mapping:
                keys.append(mp4_frame_mapping[mp4_key])
            else:
                keys.append(mp4_key)
        return keys
