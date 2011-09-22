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

"""Interface with Twitter."""

__author__ = 'ricbit@google.com (Ricardo Bittencourt)'

import datetime
import logging
import re
import cgi
import urllib

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from pythontwitter import twitter as pythontwitter
import oauth2 as oauth

import model

APP_KEYS = None
def GetAppKeys():
  global APP_KEYS
  if APP_KEYS is None:
    APP_KEYS = model.OAuthData.get_by_key_name('#app')
  return APP_KEYS

APP_CONSUMER = None
def GetAppConsumer():
  global APP_CONSUMER
  if APP_CONSUMER is None:
    app_keys = GetAppKeys()
    APP_CONSUMER = oauth.Consumer(
        key=app_keys.oauth_key, secret=app_keys.oauth_secret)
  return APP_CONSUMER

class TwitterPage(webapp.RequestHandler):
  def get(self):
    consumer = GetAppConsumer()
    client = oauth.Client(consumer)
    temp_key = model.OAuthData().put()
    body = urllib.urlencode(
        {'oauth_callback': 'http://spojtweet.appspot.com/twitter/auth/%s/' %
	                   str(temp_key.id())})
    response, content = client.request(
        pythontwitter.REQUEST_TOKEN_URL, 'POST', body=body)
    request_token = dict(cgi.parse_qsl(content))
    temp_data = model.OAuthData(
        key=temp_key,
        oauth_key=request_token['oauth_token'],
        oauth_secret=request_token['oauth_token_secret'])
    temp_data.put()
    self.redirect('%s?oauth_token=%s' %
        (pythontwitter.SIGNIN_URL, temp_data.oauth_key))

class TwitterAuthPage(webapp.RequestHandler):
  def get(self, temp_id):
    temp_data = model.OAuthData.get_by_id(int(temp_id))
    if temp_data.oauth_key != self.request.get('oauth_token'):
      self.response.out.write('Not authorized.')
      self.error(401)
      return
    token = oauth.Token(temp_data.oauth_key, temp_data.oauth_secret)
    token.set_verifier(self.request.get('oauth_verifier'))
    consumer = GetAppConsumer()
    client = oauth.Client(consumer, token)
    response, content = client.request(pythontwitter.ACCESS_TOKEN_URL, 'POST')
    access_token = dict(cgi.parse_qsl(content))
    user_keys = model.OAuthData(key_name=access_token['user_id'],
        oauth_key=access_token['oauth_token'],
	oauth_secret=access_token['oauth_token_secret'])
    user_keys.put()
    temp_data.delete()
    self.response.out.write('Welcome ' + access_token['screen_name'])

class SendTweetPage(webapp.RequestHandler):
  def get(self, username):
    if not users.is_current_user_admin():
      self.response.out.write('Not authorized.')
      self.error(401)
      return
    app_keys = GetAppKeys()
    self.response.out.write(str(app_keys) + '<p>')
    user_keys = model.OAuthData.get_by_key_name(username)
    api = pythontwitter.Api(
        consumer_key=app_keys.oauth_key,
	consumer_secret=app_keys.oauth_secret,
	access_token_key=user_keys.oauth_key,
	access_token_secret=user_keys.oauth_secret,
	cache=None)
    api.PostUpdate(
        'Se você consegue ler isso, minha implementação de oauth funciona.')
    self.response.out.write('posted')

if __name__ == '__main__':
  Test()
