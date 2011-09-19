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

"""Parse html from the spoj website."""

__author__ = 'ricbit@google.com (Ricardo Bittencourt)'

import datetime
import re

class ParseError(Exception):
  pass

def ParseStatusPage(text):
  name_re = '(?i)<h3>(.+?)\'s user data </h3>'
  match = re.search(name_re, text)
  if match == None:
    raise ParseError()
  name = match.group(1).strip()

  country_re = '(?is)Country:.*?<td>([^>]+?)</td>'
  match = re.search(country_re, text)
  if match == None:
    raise ParseError()
  country = match.group(1).strip()

  return name.decode('iso-8859-1'), country.decode('iso-8859-1')

def ParseDetailsPage(usertext):
  problems = {}
  for line in usertext.split('\n'):
    fields = [field.strip() for field in line.split('|')]
    if len(fields) != 9 or not fields[1].isdigit():
      continue
    date = datetime.datetime.strptime(fields[2], "%Y-%m-%d %H:%M:%S")
    code = fields[3]
    status = fields[4]
    time = int(fields[5].replace('.', ''))
    language = fields[7]
    problems.setdefault(code, []).append((date, status, language, time))
  return problems

def ParseCountryList(text):
  country_list = re.findall('(?i)users/(..)/\">(.*?)</a>', text)
  return [(code, name.decode('iso-8859-1')) for code, name in country_list]

def ParseCountryPage(text):
  user_list = re.findall(
      '(?i)<td>(\d+)</td>.*?<td><a href=\".*?/users/(.+?)\"',
      text.replace('\n', ''))
  return [(int(pos), userid) for pos, userid in user_list]

def ParseProblemList(text):
  match = re.search('href=\"(.*?)\".*?>Next</a>', text)
  if match is not None:
    next_link = 'http://www.spoj.pl' + match.group(1)
  else:
    next_link = None
  problem_list = re.findall(
      'problemrow.*?/problems/(\w+)/\"', text.replace('\n', ''))
  return next_link, problem_list

def ParseProblemDetails(text):
  match = re.search('/problems/.*?\">(.*?)</a> statistics', text)
  if match is None:
    raise ParseError()
  details = {'name': match.group(1).decode('iso-8859-1')}
  stats = ['users_accepted', 'submissions', 'accepted', 'wrong_answer',
           'compile_error', 'runtime_error', 'time_limit_exceeded']
  regexp = '(?s)lightrow\">' + ''.join('.*?(?P<%s>\d+)' % s for s in stats)
  match = re.search(regexp, text)
  if match is None:
    raise ParseError()
  for key, value in match.groupdict().iteritems():
    details[key] = int(value)
  regexp = '(?s)status_sm.*?/users/(.*?)/\".*?statustime_.*?\".*?([0-9.]+)'
  match = re.search(regexp, text)
  if match is not None:
    details['first_place'] = match.group(1)
    if match.group(2) == '0.00':
      details['first_place_permanent'] = match.group(1)
  return details

def Test():
  page = open('testdata/problems_last.html').read()
  print ParseProblemList(page)

if __name__ == '__main__':
  Test()
