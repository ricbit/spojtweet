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

if __name__ == '__main__':
  unittest.main()
