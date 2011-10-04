# Copyright (C) 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utils for common tasks using webapp."""

__author__ = 'ricbit@google.com (Ricardo Bittencourt)'

import os

from google.appengine.ext import db
from google.appengine.api import urlfetch


def LoadTemplate(name):
  return os.path.join(os.path.dirname(__file__), name)

class FetchUrl(object):
  def __init__(self, url):
    self.url = url

  def run(self):
    self.rpc = urlfetch.create_rpc()
    urlfetch.make_fetch_call(self.rpc, self.url)

  def get(self):
    return self.rpc.get_result().content

class GetModel(object):
  def __init__(self, model, key_name):
    self.model = model
    self.key_name = key_name

  def run(self):
    key = db.Key.from_path(self.model, self.key_name)
    self.rpc = db.get_async(key)

  def get(self):
    return self.rpc.get_result()

class QueryCount(object):
  def __init__(self, model, model_property, user):
    self.model = model
    self.model_property = model_property
    self.user = user

  def run(self):
    self.query = self.model.all(keys_only=True)

  def get(self):
    return self.query.filter(self.model_property, self.user).count()

class ParallelFetch(object):
  def __init__(self, **queries):
    self.queries = queries

  def run(self):
    results = {}
    for query in self.queries.itervalues():
      query.run()
    for name, query in self.queries.iteritems():
      results[name] = query.get()
    return results
