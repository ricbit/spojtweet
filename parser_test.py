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

"""Tests for parser.py."""

__author__ = 'ricbit@google.com (Ricardo Bittencourt)'

import unittest

import parser

class ParserTest(unittest.TestCase):

  def testParseUserPage(self):
    text = open('testdata/ricbit.html').read()
    name, country = parser.ParseStatusPage(text)
    self.assertEquals('Ricardo Bittencourt', name)
    self.assertEquals('BRAZIL', country)
    self.assertTrue(name, unicode)
    self.assertTrue(country, unicode)

  def testParseUserPageFailsToParse(self):
    text = 'nothing to see here, move along'
    try:
      name, country = parser.ParseStatusPage(text)
      self.fail()
    except parser.ParseError:
      pass

  def testParseProblemDetails(self):
    text = open('testdata/problems_best.html').read()
    details = parser.ParseProblemDetails(text)
    self.assertEquals('Hotline', details['name'])
    self.assertEquals(111, details['users_accepted'])
    self.assertEquals(295, details['submissions'])
    self.assertEquals(118, details['accepted'])
    self.assertEquals(127, details['wrong_answer'])
    self.assertEquals(25, details['compile_error'])
    self.assertEquals(22, details['runtime_error'])
    self.assertEquals(3, details['time_limit_exceeded'])
    self.assertEquals('adrian', details['first_place'])
    self.assertEquals('adrian', details['first_place_permanent'])

  def testParseProblemDetailsUnsolved(self):
    text = open('testdata/problems_best_unsolved.html').read()
    details = parser.ParseProblemDetails(text)
    self.assertEquals('Department', details['name'])
    self.assertTrue('first_place' not in details)
    self.assertTrue('first_place_time' not in details)

  def testParseProblemDetailsFailsToParse(self):
    text = 'nothing to see here, move along'
    try:
      details = parser.ParseProblemDetails(text)
      self.fail()
    except parser.ParseError:
      pass

  def testParseCountryList(self):
    text = open('testdata/country.html').read()
    countries = parser.ParseCountryList(text)
    for country in countries:
      self.assertEquals(2, len(country))
      self.assertEquals(2, len(country[0]))
      self.assertTrue(isinstance(country[1], unicode))
    

if __name__ == '__main__':
  unittest.main()
