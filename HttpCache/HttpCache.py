__author__ = 'PsCool'


class HttpCache(object):
    def __init__(self):
        self.cache_dir = {}

    def get_entry(self, host, path):
        if self.cache_dir.has_key(host) and self.cache_dir[host].has_key(path):
            return self.cache_dir[host][path]

    def add_entry(self, cache_entry):
        if not self.cache_dir.has_key(cache_entry.host):
            self.cache_dir[cache_entry.host] = {}

        self.cache_dir[cache_entry.host][cache_entry.path] = cache_entry


