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

import logging
import os
import utils

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import model
import parser
import refresh_user

def RenderPage(user, eventid):
  spojuser = model.SpojUser.get_by_key_name(user)
  if eventid is not None:
    events = model.Event.get_by_id(int(eventid))
    if user != events.user:
      raise Exception()
    event_list = events.event_list
  else:
    event_list = []
  event_list.sort(key=lambda event: event.code)
  if (spojuser is None or
      spojuser.version is None or
      spojuser.version < model.VERSION):
    spojuser, refresh_info = refresh_user.RefreshUser().refresh(user)
    logging.info(refresh_info)

  path = utils.LoadTemplate('user.html')
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
    'badges': badges,
    'events': event_list
  }
  return template.render(path, values)

class UserPage(webapp.RequestHandler):
  def get(self, user):
    key = '#'.join([str(model.VERSION), user])
    page = memcache.get(key)
    if page is not None:
      self.response.out.write(page)
    else:
      page = RenderPage(user, None)
      expires = 30 * 60
      memcache.add(key, page, expires)
      self.response.out.write(page)

class UserEventPage(webapp.RequestHandler):
  def get(self, user, eventid):
    key = '#'.join([str(model.VERSION), user])
    page = memcache.get(key)
    if page is not None:
      self.response.out.write(page)
    else:
      page = RenderPage(user, eventid)
      expires = 30 * 60
      memcache.add(key, page, expires)
      self.response.out.write(page)


if __name__ == '__main__':
  main()
