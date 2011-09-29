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

def ValidSession(request):
  if 'sid' not in request.cookies:
    return None
  session_id = request.cookies['sid']
  twitter_id = request.cookies['uid']
  preferences = model.UserPreferences.get_by_key_name(twitter_id)
  if preferences is None or preferences.session_id != session_id:
    return None
  session_expires = datetime.timedelta(0, 10*60)
  if datetime.datetime.now() - preferences.session_start > session_expires:
    return None
  return preferences

class SettingsPage(webapp.RequestHandler):
  def get(self):
    preferences = ValidSession(self.request)
    if preferences is None:
      self.redirect('/settings/login')
      return      
    spoj_user = preferences.spoj_user
    if spoj_user is None:
      spoj_user = ''
    path = os.path.join(os.path.dirname(__file__), 'settings.html')
    values = {
        'twitter_username': preferences.twitter_screen_name,
 	'spoj_username': spoj_user,
	'send_badge': 'checked' if preferences.send_badge else '',
	'send_solution': 'checked' if preferences.send_solution else ''
    }
    self.response.out.write(template.render(path, values))

class SettingsUpdatePage(webapp.RequestHandler):
  def post(self):
    preferences = ValidSession(self.request)
    if preferences is None:
      self.redirect('/settings/login')
      return      
    preferences.spoj_user = self.request.get('spoj_user')
    preferences.send_solution = self.request.get('send_solution') == 'on'
    preferences.send_badge = self.request.get('send_badge') == 'on'
    preferences.put()
    self.redirect('/settings')
