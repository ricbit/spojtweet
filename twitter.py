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
import urllib

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from pythontwitter import twitter as pythontwitter
import oauth2 as oauth

import model

class TwitterPage(webapp.RequestHandler):
  def get(self):
    app_keys = model.OAuthData.get_by_key_name('oauth')
    consumer = oauth.Consumer(
        key=app_keys.consumer_key, secret=app_keys.consumer_secret)
    client = oauth.Client(consumer)
    temp_data = model.OAuthData()
    temp_key = temp_data.put()
    body = urllib.urlencode(
        {'oauth_callback': 'http://spojtweet.appspot.com/twitter/auth/%s/' %
	                   str(temp_key.id())})
    response, content = client.request(
        pythontwitter.REQUEST_TOKEN_URL, 'POST', body=body)
    request_token = dict(cgi.parse_qsl(content))
    temp_data.key = temp_key
    temp_data.consumer_key = request_token['oauth_token']
    temp_data.consumer_secret = request_token['oauth_token_secret']
    temp_data.put()
    self.redirect('%s?oauth_token=%s' % 
        (pythontwitter.AUTHORIZATION_URL, request_token['oauth_token']))

class TwitterAuthPage(webapp.RequestHandler):
  def get(self, temp_id):
    temp_data = model.OAuthData.get_by_id(int(temp_id))
    assert temp_data.consumer_key == self.request.get('oauth_token')
    token = oauth.Token(temp_data.consumer_key, temp_data.consumer_secret)
    token.set_verifier(self.request.get('oauth_verifier'))
    app_keys = model.OAuthData.get_by_key_name('oauth')
    consumer = oauth.Consumer(
        key=app_keys.consumer_key, secret=app_keys.consumer_secret)
    client = oauth.Client(consumer, token)
    response, content = client.request(pythontwitter.ACCESS_TOKEN_URL, 'POST')
    access_token = dict(cgi.parse_qsl(content))
    final = model.OAuthData(key_name='ricbit',
        consumer_key=access_token['oauth_token'],
	consumer_secret=access_token['oauth_token_secret']).put()
    temp_data.delete()
    self.response.out.write('done')

class SendTweetPage(webapp.RequestHandler):
  def get(self, username):
    if not users.is_current_user_admin():
      return
    app_keys = model.OAuthData.get_by_key_name('oauth')
    user_keys = model.OAuthData.get_by_key_name(username)
    api = pythontwitter.Api(
        consumer_key=app_keys.consumer_key,
	consumer_secret=app_keys.consumer_secret,
	access_token_key=user_keys.consumer_key,
	access_token_secret=user_keys.consumer_secret,
	cache=None)
    api.PostUpdate(
        'Se você consegue ler isso, minha implementação de oauth funciona.')
    self.response.out.write('posted')

if __name__ == '__main__':
  Test()
