from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.ext import webapp
from google.appengine.api import urlfetch

import model
import parser
import logging

def CrawlCountry(country_list):
  if not country_list:
    return
  code, name = country_list[0]
  url = 'http://www.spoj.pl/ranks/users/%s' % code
  logging.info('parsing %s', name)
  text = urlfetch.fetch(url).content
  user_list = parser.ParseCountryPage(text)
  users = []
  for position, username in user_list:
    users.append(model.UserPosition(username, position))
  model.CountryInfo(key_name=name, users=users).put()
  deferred.defer(CrawlCountry, country_list[1:])

def StartCountryCrawl():
  country_url = 'http://www.spoj.pl/ranks/countries/'
  country_page = urlfetch.fetch(country_url).content
  country_list = parser.ParseCountryList(country_page)
  deferred.defer(CrawlCountry, country_list)

def CrawlProblems(problem_list):
  if not problem_list:
    return
  code = problem_list[0]
  logging.info('crawling problem %s', code)
  problem_url = 'http://www.spoj.pl/ranks/' + code
  problem_page = urlfetch.fetch(problem_url).content
  details = parser.ParseProblemDetails(problem_page)
  problem = model.ProblemDetails(key_name=code, **details)
  problem.put()
  deferred.defer(CrawlProblems, problem_list[1:])


def SaveProblemList(problem_list):
  problems = model.ProblemList(key_name='classical', problems=problem_list)
  problems.put()
  deferred.defer(CrawlProblems, problem_list)

def ProblemCrawl(url, problem_list):
  logging.info('crawling %s', url)
  problem_page = urlfetch.fetch(url).content
  next_link, problems = parser.ParseProblemList(problem_page)
  problem_list.extend(problems)
  if next_link is None:
    deferred.defer(SaveProblemList, problem_list)
  else:
    deferred.defer(ProblemCrawl, next_link, problem_list)

class CrawlCountryPage(webapp.RequestHandler):
  def get(self):
    deferred.defer(ProblemCrawl, 'http://www.spoj.pl/problems/classical/', [])
    self.response.out.write('launched')
