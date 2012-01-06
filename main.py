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

"""Main webapp driver for spojtweet."""

__author__ = 'ricbit@google.com (Ricardo Bittencourt)'

import datetime
import os
import urllib2

from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import admin
import crawler
import refresh_user
import settings
import user_page

class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.out.write('Under construction')

class NotFoundPage(webapp.RequestHandler):
  def get(self):
    self.error(404)
    self.response.out.write('404 Not Found')

app = webapp.WSGIApplication(
          [('/', MainPage),
           ('/user/([^/]+)', user_page.UserPage),
           ('/user/([^/]+)/(\d+)', user_page.UserEventPage),
           ('/refresh/([^/]+)', refresh_user.RefreshUserPage),
           ('/crawl', crawler.CrawlCountryPage),
           ('/crawl/users', crawler.CrawlRegisteredUsers),
           ('/admin', admin.AdminPage),
           ('/admin/keys/(.*?)/(.*?)/', admin.SetKeyPage),
           ('/settings/twitter', settings.TwitterLoginPage),
           ('/settings/auth/(.*?)/', settings.TwitterAuthPage),
           ('/settings', settings.SettingsPage),
           ('/settings/update', settings.SettingsUpdatePage),
           ('/.*', NotFoundPage)],
          debug=True)

def main():
  run_wsgi_app(app)

if __name__ == '__main__':
  main()
