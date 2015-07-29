# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from . import Tinify
from .result import Result

class Source(object):
    @classmethod
    def from_file(cls, path):
        if hasattr(path, 'read'):
            return cls._shrink(path)
        else:
            with open(path, 'rb') as f:
                return cls._shrink(f.read())

    @classmethod
    def from_buffer(cls, string):
        return cls._shrink(string)

    @classmethod
    def _shrink(cls, obj):
        response = Tinify.client.request('POST', '/shrink', obj)
        return cls(response.headers.get('location'))

    def __init__(self, url, **commands):
        self.url = url
        self.commands = commands

    def resize(self, **options):
        return type(self)(self.url, **self._merge_commands(resize=options))

    def store(self, **options):
        response = Tinify.client.request('POST', self.url, self._merge_commands(store=options))
        return Result(response.headers, response.content)

    def result(self):
        response = Tinify.client.request('GET', self.url, self.commands)
        return Result(response.headers, response.content)

    def to_file(self, path):
        return self.result().to_file(path)

    def to_buffer(self):
        return self.result().to_buffer()

    def _merge_commands(self, **options):
        commands = type(self.commands)(self.commands)
        commands.update(options)
        return commands
