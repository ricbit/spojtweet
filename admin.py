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

"""Administration page."""

__author__ = 'ricbit@google.com (Ricardo Bittencourt)'

import datetime
import re

from google.appengine.api import users
from google.appengine.ext import webapp

import model

class AdminPage(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user is None:
      login_url = users.create_login_url('/admin')
      self.response.out.write('<a href="%s">Login</a>' % login_url)
    else:
      self.response.out.write('Welcome %s<br>' % user.nickname()) 
      logout_url = users.create_logout_url('/admin')
      self.response.out.write('<a href="/crawl">Launch crawler</a> | ')
      self.response.out.write('<a href="%s">Logout</a>' % logout_url)

class SetKeyPage(webapp.RequestHandler):
  def get(self, consumer_key, consumer_secret):
    if not users.is_current_user_admin():
      return
    data = model.OAuthData(
        key_name='oauth',
	consumer_key=consumer_key,
	consumer_secret=consumer_secret).put()
    self.response.out.write('Updated keys.')

if __name__ == '__main__':
  Test()
