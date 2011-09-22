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
import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from pythontwitter import twitter as pythontwitter
import oauth2 as oauth

import model

class TwitterPage(webapp.RequestHandler):
  def get(self):
    keys = model.OAuthData.get_by_key_name('oauth')
    oauth.SignatureMethod_HMAC_SHA1()
    consumer = oauth.Consumer(
        key=keys.consumer_key, secret=keys.consumer_secret)
    client = oauth.Client(consumer)
    response, content = client.request(pythontwitter.REQUEST_TOKEN_URL)
    request_token = dict(cgi.parse_qsl(content))
    self.redirect('%s?oauth_token=%s' % 
        (pythontwitter.AUTHORIZATION_URL, request_token['oauth_token']))


if __name__ == '__main__':
  Test()
