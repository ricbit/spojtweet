import unittest

import parser

class ParserTest(unittest.TestCase):

  def testParseUserPage(self):
    text = open('testdata/ricbit.html').read()
    name, country = parser.ParseStatusPage(text)
    self.assertEquals('Ricardo Bittencourt', name)
    self.assertEquals('BRAZIL', country)

  def testParseUserPageFailsToParse(self):
    text = 'nothing to see here, move along'
    try:
      name, country = parser.ParseStatusPage(text)
      self.fail()
    except parser.ParseError:
      pass

if __name__ == '__main__':
  unittest.main()
