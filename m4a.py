# Copyright (c) 2008 Scott Paul Robertson (spr@scottr.org)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from tag_wrapper import dictionary_reverse, Tag, TagException
from mutagen.mp4 import MP4
import re

m4a_frame_mapping = {
        # Art
        'covr':     'album cover', 
        # Main information
        '\xa9nam':  'title',
        '\xa9ART':  'artist',
        'aART':     'album artist',
        '\xa9alb':  'album',
        '\xa9wrt':  'composer',
        '\xa9gen':  'genre',
        '\xa9day':  'date',
        'trkn':     'tracknumber',  # tuple (x, total)
        'disk':     'discnumber',   # tuple (x, total)
        'tmpo':     'bpm',
        # iTunes bonus stuff
        'cpil':     'compilation',  # boolean
        'pgap':     'gapless',      #  boolean
        '\xa9grp':  'grouping',
        # Sorting
        'soal':     'album sort order',
        'sonm':     'title sort order',
        'soaa':     'album artist sort order',
        'soar':     'artist sort order',
        'soco':     'composer sort order',
        # Miscellaneous
        '\xa9cmt':  'comment',
        'cprt':     'copyright',
        'tvsh':     'show',
        'purd':     'purchased',
        'apID':     'apple id',
}

norm_frame_mapping = dictionary_reverse(m4a_frame_mapping)

class M4ATag(Tag):
    """The Tag implementation for m4a (iTunes) tags"""

    def _get_real_key(self, key):
        if key in norm_frame_mapping:
            return norm_frame_mapping[key]
        else:
            return key

    def _make_date_from_year(self, year):
        return "%s-01-01T07:00:00Z" % year

    def _get_year_from_date(self, date):
        m = re.match(r'(\d{4})-', date)
        if m:
            return m.group(1)
        else:
            return date
    
    def __getitem__(self, key):
        """__getitem__: artist = tag['artist']
        Returns a list of values
        """
        value = self._tag[self._get_real_key(key)]
        if key == 'tracknumber' or key == 'discnumber':
            return [u'/'.join(map(unicode, v)) for v in value]
        elif key == 'date':
            return map(self._get_year_from_date, value)
        elif key == 'album cover':
            return value
        if type(value) != list:
            value = [value]
        return map(unicode, value)

    def __setitem__(self, key, value):
        if type(value) != list:
            value = [value]
        if key == 'tracknumber' or key == 'discnumber':
            value = [map(int, v.split('/')) for v in value]
            # TODO: I hate this.
            next = []
            for v in value:
                if len(v) == 1:
                    next.append((v[0],0))
                else:
                    next.append(v)
            value = next
        elif key == 'date':
            value = [self._make_date_from_year(v) for v in value]
        elif key == 'compilation' or key == 'gapless':
            value = bool(value[0])
        
        self._tag[self._get_real_key(key)] = value

    def __delitem__(self, key):
        del(self._tag[self._get_real_key(key)])

    def __contains__(self, key):
        return (self._get_real_key(key) in self._tag)

    def keys(self):
        keys = []
        for m4a_key in self._tag.keys():
            if m4a_key in m4a_frame_mapping:
                keys.append(m4a_frame_mapping[m4a_key])
            else:
                keys.append(m4a_key)
        return keys
