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

"""Render user page."""

__author__ = 'ricbit@google.com (Ricardo Bittencourt)'

import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db

import model
import parser

class UserPage(webapp.RequestHandler):
  def RenderPage(self, user):
    spojuser = model.SpojUser.get_by_key_name(user)
    if (spojuser is None or
        spojuser.version is None or
	spojuser.version < model.VERSION):
      self.response.out.write(
          'Please <a href="/refresh/%s">refresh user %s</a>' % (user, user))
      return
    path = os.path.join(os.path.dirname(__file__), 'user.html')
    badge_value_names = {
      1: 'gold',
      2: 'silver',
      3: 'bronze'
    }
    badges = spojuser.badges[:]
    badges.sort(key=lambda x: (x.value, x.name))
    for badge in badges:
      badge.value = badge_value_names[badge.value]
    values = {
      'name': spojuser.name,
      'country': spojuser.country.title(),
      'badges': badges
    }
    return template.render(path, values)

  def get(self, user):
    self.response.out.write(self.RenderPage(user))


if __name__ == '__main__':
  main()
