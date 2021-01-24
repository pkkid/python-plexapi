# -*- coding: utf-8 -*-


class SplitMerge(object):
    """ Mixin for Plex objects that can be split and merged."""

    def split(self):
        """ Split duplicated Plex object into separate objects. """
        key = '/library/metadata/%s/split' % self.ratingKey
        return self._server.query(key, method=self._server._session.put)

    def merge(self, ratingKeys):
        """ Merge other Plex objects into the current object.
        
            Parameters:
                ratingKeys (list): A list of rating keys to merge.
        """
        if not isinstance(ratingKeys, list):
            ratingKeys = str(ratingKeys).split(',')

        key = '%s/merge?ids=%s' % (self.key, ','.join([str(r) for r in ratingKeys]))
        return self._server.query(key, method=self._server._session.put)
