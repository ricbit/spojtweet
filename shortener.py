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

"""Interface to the goo.gl shortener service."""

__author__ =  'ricbit@google.com (Ricardo Bittencourt)'

from django.utils import simplejson as json
from google.appengine.api import urlfetch

def Shorten(url):
  service = 'https://www.googleapis.com/urlshortener/v1/url'
  headers = {'Content-Type': 'application/json'}
  request = {'longUrl': url}
  response = urlfetch.fetch(service,
                            payload=json.dumps(request),
                            method=urlfetch.POST,
                            headers=headers).content
  decoded_response = json.loads(response)
  return decoded_response['id']
