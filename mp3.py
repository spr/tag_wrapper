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
from mutagen.id3 import ID3
from mutagen import id3

encodings = {
        'iso-8859-1':   0,
        'utf-16':       1,
        'utf-16be':     2,
        'utf-8':        3,
}

id3_frame_mapping = {
        # Art
        'APIC:': 'album cover',
        # Main information
        'TIT2': 'title',
        'TPE1': 'artist',
        'TPE2': 'album artist',
        'TALB': 'album',
        'TCOM': 'composer',
        'TCON': 'genre',
        'TDRC': 'date',
        'TRCK': 'tracknumber',  # x/total
        'TPOS': 'discnumber',   # x/total
        'TBPM': 'bpm',
        # iTunes bonus stuff
        'TCMP': 'compilation',
        # Gapless support via comments
        'TIT1': 'grouping',
        # Sorting
        'TSOA': 'album sort order',
        'TSOT': 'title sort order',
        'TSOP': 'artist sort order',
        # Miscellaneous
        'TCOP': 'copyright',
        'TPE3': 'conductor',
        'TLEN': 'length',
        'TEXT': 'lyricist',
        'TENC': 'encoder',
        'TSSE': 'encoder settings',
}

norm_frame_mapping = dictionary_reverse(id3_frame_mapping)

class ID3Tag(Tag):
    """The Tag implementation for ID3 tags"""

    def __init__(self, tag, lang='eng', encoding=encodings['utf-8']):
        super(ID3Tag, self).__init__(tag)
        self.lang = lang
        if encoding in encodings:
            self.encoding = encodings[encoding]
        elif encoding <= 3 and encoding >= 0:
            self.encoding = encoding
        else:
            raise TagException('Encoding %s not supported by ID3' % encoding)

    def _build_comm_key(self, key, lang='eng'):
        """Builds key for a COMM tag as found in mutagen.id3.ID3"""
        return unicode(''.join(('COMM:', key, ":'", lang, "'")))

    def _get_real_key(self, key):
        """This returns the key that mutagen.id3.ID3 uses given a "normal"
        value.
        """
        new_key = ''
        if key in norm_frame_mapping:
            new_key = norm_frame_mapping[key]
        elif key == 'comment':
            new_key = self._build_comm_key('', self.lang)
        elif key == 'gapless':
            new_key = self._build_comm_key('iTunPGAP', self.lang)
        else:
            new_key = self._build_comm_key(key, self.lang)
        return new_key

    def __getitem__(self, key):
        """ __getitem__: artist = tag['artist']
        Returns a list of values
        """
        rkey = self._get_real_key(key)
        if key == 'album cover':
            return [self._tag[rkey].data]
        value = self._tag[rkey].text
        if type(value) != list:
            value = [value]
        return map(unicode, value)

    def __setitem__(self, key, value):
        """__setitem__: tag['artist'] = "Guster"
        If a tag supports multiple values, the user must put vales into
        a list themselves. If the tag already exists we overwrite the data.
        Mutagen will make a list out of Null separated values.
        """
        rkey = self._get_real_key(key)
        # Tag is a supported frame
        if type(value) != list:
            value = [value]
        if key in norm_frame_mapping:
            if key == 'album cover':
                tag_class = getattr(id3, rkey[:-1])
                self._tag[rkey] = tag_class(encoding=self.encoding,
                        desc='', type=3, mime='image/png', data=value[0])
            else:
                tag_class = getattr(id3, rkey)
                self._tag[rkey] = tag_class(encoding=self.encoding, text=value) 
        # Tag is a comment
        else:
            desc = key
            if key == 'comment':
                desc = ''
            elif key == 'gapless':
                desc = 'iTunPGAP'
            self._tag[rkey] = id3.COMM(encoding=self.encoding, lang=self.lang,
                        desc=desc, text=value)

    def __delitem__(self, key):
        del(self._tag[self._get_real_key(key)])

    def __contains__(self, item):
        return (self._get_real_key(item) in self._tag)

    def keys(self):
        keys = []
        for id3_key in self._tag:
            if id3_key in id3_frame_mapping:
                keys.append(id3_frame_mapping[id3_key])
            elif id3_key.startswith('COMM:'):
                s = id3_key.split(':')[1]
                if s == '':
                    keys.append('comment')
                elif s == 'gapless':
                    keys.append('gapless')
                else:
                    keys.append(s)
        return keys

    def save(self):
        """Saves tag (ID3v2.4 and ID3v1.1) to disk."""
        self._tag.save(v1=2)
