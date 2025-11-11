#!/usr/bin/python3

import os

class File():
    def __init__(self, storage: LocalStorage, path: str): # pylint: disable=used-before-assignment
        self.path = path
        self.storage = storage

    def open(self, *args, **kwargs):
        ''' Open the file using the relevant storage '''
        return(self.storage.open(self.path, *args, **kwargs))

class LocalStorage():
    ''' Class to represent a location on a local file system '''
    def __init__(self, uri: str):
        self.uri = uri

    def ls(self, path: str = '') -> list[File]:
        ''' Return a listing of a directory '''
        if path.startswith('/'):
            path = path[1:]
        fullpath = os.path.join(self.uri, path)
        return [File(self, os.path.join(fullpath, x)) for x in os.listdir(fullpath)]

    def open(self, path: str, *args, **kwargs):
        ''' Open a file '''
        return open(os.path.join(self.uri, path), *args, **kwargs, encoding='utf8')
