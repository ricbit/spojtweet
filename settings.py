# coding: utf-8
#
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

"""Settings page."""

__author__ = 'ricbit@google.com (Ricardo Bittencourt)'

import os

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import model
import twitter

class TwitterLoginPage(webapp.RequestHandler):
  def get(self):
    redirect_url = twitter.TwitterLogin()
    self.redirect(redirect_url)

class TwitterAuthPage(webapp.RequestHandler):
  def get(self, temp_id):
    twitter_username, session_id = twitter.TwitterAuth(
        temp_id, self.request.get('oauth_token'),
        self.request.get('oauth_verifier'))
    twitter.SetCookie(self.response.headers,
        'uid', twitter_username, secure=True)
    twitter.SetCookie(self.response.headers,
        'sid', session_id, secure=True)
    self.response.out.write('Welcome ' + twitter_username)

class SettingsPage(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'settings.html')
    values = {
        'twitter_username': self.request.get('sid')
    }
    self.response.out.write(template.render(path, values))

class SettingsUpdatePage(webapp.RequestHandler):
  def post(self):
    self.response.out.write('posted')
