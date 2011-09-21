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

"""Interafce with Twitter."""

__author__ = 'ricbit@google.com (Ricardo Bittencourt)'

import datetime
import logging
import re

from google.appengine.api import users
from google.appengine.ext import webapp
import oauthtwitter

import model

class TwitterPage(webapp.RequestHandler):
  def get(self):
    keys = model.OAuthData.get_by_key_name('oauth')
    twitter = oauthtwitter.OAuthApi(keys.consumer_key, keys.consumer_secret)
    temp_credentials = twitter.getRequestToken()
    logging.info(str(temp_credentials))
    self.response.out.write('see logs')


if __name__ == '__main__':
  Test()
