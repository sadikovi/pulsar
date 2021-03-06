#!/usr/bin/env python

'''
Copyright 2015 Ivan Sadikov

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''


# import libs
import json
from types import StringType, UnicodeType
# import classes
import analytics.utils.misc as misc
from analytics.loading.loader import Loader


class JsonLoader(Loader):
    """
        JsonLoader class is a subclass of Loader that provides actual interface
        to load data from json file. It overrides methods @prepareDataFrom and
        @processData and takes attribute for file path.

        Example of json file:
            [
                {"id": "1", "name": "1", "desc": "1", "parent": null},
                {"id": "2", "name": "2", "desc": "2", "parent": "1"},
                {"id": "3", "name": "3", "desc": "3", "parent": "1"},
                {"id": "4", "name": "4", "desc": "4", "parent": "2"},
                {"id": "5", "name": "5", "desc": "5", "parent": "2"}
            ]

        Attributes:
            _filepath (str): json file path
    """

    def __init__(self, filepath):
        self._filepath = filepath

    @classmethod
    def prepareDataFrom(cls, filepath):
        """
            Class method to instantiate JsonLoader instance. Takes file path
            as an argument and checks against StringType.

            Args:
                filepath (str): json file path
        """
        misc.checkTypeAgainst(type(filepath), StringType, __file__)
        return cls(filepath)

    # [Public]
    def processData(self, filepath=None):
        """
            Process data from the file specified as _filepath attribute.
            Returns standard dictionary / list as json object, or raises
            exception, if file does not exist or json is invalid. If filepath
            is not specified then instance uses _filepath property.

            Args:
                filepath (str): file path

            Returns:
                dict<str, object> / list<object>: json object from the file
        """
        fpath = filepath if filepath is not None else self._filepath
        with open(fpath) as file:
            jsonObject = json.load(file, object_hook=self._decode_dict)
        return jsonObject

    # [Private]
    def _decode_dict(self, data):
        """
            Hook to convert any unicode string to StringType.

            Args:
                data (dict<str, obj>): data item

            Returns:
                dict<str, obj>: updated data item with StringType
        """
        for key in data.keys():
            key_upd = key; data_upd = data[key]
            if type(key_upd) is UnicodeType:
                key_upd = str(key_upd)
            if type(data_upd) is UnicodeType:
                data_upd = str(data_upd)
            del data[key]
            data[key_upd] = data_upd
        return data
