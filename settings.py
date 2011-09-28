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

import datetime
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
    twitter_id, session_id = twitter.TwitterAuth(
        temp_id, self.request.get('oauth_token'),
        self.request.get('oauth_verifier'))
    twitter.SetCookie(self.response.headers,
        'uid', twitter_id, secure=True)
    twitter.SetCookie(self.response.headers,
        'sid', session_id, secure=True)
    self.redirect('/settings')

class SettingsPage(webapp.RequestHandler):
  def get(self):
    if 'sid' not in self.request.cookies:
      self.redirect('/settings/login')
      return
    session_id = self.request.cookies['sid']
    twitter_id = self.request.cookies['uid']
    preferences = model.UserPreferences.get_by_key_name(twitter_id)
    if preferences is None:
      self.redirect('/settings/login')
      return
    session_expires = datetime.timedelta(0, 10*60)
    if datetime.datetime.now() - preferences.session_start > session_expires:
      self.redirect('/settings/login')
      return
    path = os.path.join(os.path.dirname(__file__), 'settings.html')
    values = {
        'twitter_username': preferences.twitter_screen_name
    }
    self.response.out.write(template.render(path, values))

class SettingsUpdatePage(webapp.RequestHandler):
  def post(self):
    self.response.out.write('posted')
