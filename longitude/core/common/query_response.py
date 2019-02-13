class LongitudeQueryResponse:
    def __init__(self, rows=None, fields=None, profiling=None):
        self.rows = rows or []
        self.fields = fields or {}
        self.profiling = profiling or {}
        self._from_cache = False

    @property
    def from_cache(self):
        return self._from_cache

    def mark_as_cached(self):
        self._from_cache = True
