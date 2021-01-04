

class SplitMergeAble:
    """ Mixin for something that that we can split and merge."""

    def split(self):
        """Split a duplicate."""
        key = '/library/metadata/%s/split' % self.ratingKey
        return self._server.query(key, method=self._server._session.put)

    def merge(self, ratingKeys):
        """Merge duplicate items."""
        if not isinstance(ratingKeys, list):
            ratingKeys = str(ratingKeys).split(",")

        key = '%s/merge?ids=%s' % (self.key, ','.join(ratingKeys))
        return self._server.query(key, method=self._server._session.put)
