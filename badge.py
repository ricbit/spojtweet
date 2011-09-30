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

"""Grants badges to users."""

__author__ = [
  'ricbit@google.com (Ricardo Bittencourt)'
  'leandro@tia.mat.br (Leandro Pereira)'
]

import datetime
from country_demonyms import COUNTRY_DEMONYMS
from language_codes import LANGUAGE_CODES

LANGUAGE_CONVERT = {
  'C99' : 'C'
}

class Badge(object):
  BRONZE = 3
  SILVER = 2
  GOLD = 1

  def __init__(self, name, description, value):
    self.name = name
    self.description = description
    self.value = value

  def __str__(self):
    return "(%s, %s)" % (self.name, self.description)

class UserMetadata(object):
  def __init__(self):
    self.problems = None
    self.language_count = None
    self.country_position = None
    self.country = None
    self.first_place = None
    self.first_place_permanent = None
    self.max_attempts_day = None
    self.granted_badges = None
    self.skipped_badges = None

NO_BADGES = ([], [])

def Solved(problem_list):
  return (problem for problem in problem_list if problem.solved)

def ProgressiveBadge(count, titles, requirements, descriptions, values):
  granted = []
  skipped = []
  badges = zip(titles, requirements, descriptions, values)
  for title, req, desc, value in badges:
    if count >= req:
      skipped.extend(granted)
      granted = [Badge(title, desc, value)]
    else:
      break
  return granted, skipped

def CountryBadge(metadata):
  if metadata.country_position is None:
    return NO_BADGES
  country = metadata.country.title()
  titles = ['Citizen', 'VIP', 'Leader']
  demonym = COUNTRY_DEMONYMS.get(country.upper(), country)
  badge_titles = ['%s %s' % (demonym, title) for title in titles]
  requirements = [-100, -10, -1]
  descriptions = ['Top 100 problem solvers from ' + country,
                  'Top 10 problem solvers from ' + country,
		  'Best problem solver from ' + country]
  values = [Badge.BRONZE, Badge.SILVER, Badge.GOLD]
  return ProgressiveBadge(
      -metadata.country_position,
      badge_titles, requirements, descriptions, values)

def LanguageBadge(metadata):
  granted_badges = []
  skipped_badges = []
  for language, count in metadata.language_count.iteritems():
    language_name = LANGUAGE_CODES.get(language, language)
    titles = ['Novice', 'User', 'Master', 'Guru']
    badge_titles = ["%s %s" % (language_name, title) for title in titles]
    requirements = [3, 10, 100, 500]
    descriptions = ["Solved %d problems in %s" % (x, language_name)
                    for x in requirements]    		    
    values = [Badge.BRONZE, Badge.BRONZE, Badge.SILVER, Badge.GOLD]
    granted, skipped = ProgressiveBadge(
        count, badge_titles, requirements, descriptions, values)
    granted_badges.extend(granted)
    skipped_badges.extend(skipped)
  return granted_badges, skipped_badges

def SolvedProblemsBadge(metadata):
  if metadata.problems is None:
    return NO_BADGES
  titles = ['Apprentice', 'Mage', 'Warlock']
  requirements = [10, 100, 1000]
  descriptions = ['Solved %d problems' % x for x in requirements]
  values = [Badge.BRONZE, Badge.SILVER, Badge.GOLD]
  return ProgressiveBadge(
      len(metadata.problems), titles, requirements, descriptions, values)

def FirstPlaceBadge(metadata):
  titles = ['Roadrunner', 'The Flash']
  requirements = [1, 10]
  description = ['Wrote the fastest solution for a problem',
                 'Wrote the fastest solution for 10 problems']
  values = [Badge.SILVER, Badge.GOLD]
  return ProgressiveBadge(
      metadata.first_place, titles, requirements, description, values)

def Forever(metadata):
  if metadata.first_place_permanent is None:
    return NO_BADGES
  badge = Badge(
      'Forever', 'First place on a problem with a time of 0.00s', Badge.GOLD)
  return ([badge], []) if metadata.first_place_permanent else (NO_BADGES)

def VeteranBadge(metadata):
  if metadata.problems is None:
    return NO_BADGES
  titles = ['Recruit', 'Soldier', 'Veteran']
  requirements = [datetime.timedelta(30),
                  datetime.timedelta(365),
                  datetime.timedelta(5*365)]
  description = ['Solving problems on SPOJ for %s' % time
                 for time in ['one month', 'one year', 'five years']]
  problem_dates = [problem.first_ac_date
                   for problem in Solved(metadata.problems)]
  values = [Badge.BRONZE, Badge.SILVER, Badge.GOLD]
  if not problem_dates:
    return NO_BADGES
  min_date = min(problem_dates)
  max_date = max(problem_dates)
  return ProgressiveBadge(
      max_date - min_date, titles, requirements, description, values)

def SharpshooterBadge(metadata):
  if metadata.problems is None:
    return NO_BADGES
  count = sum(1 for problem in Solved(metadata.problems)
              if problem.tries_before_ac == 0)
  badge = Badge(
      'Sharpshooter', 'Solved 25 problems on the first try', Badge.SILVER)
  return ([badge], []) if count >= 25 else(NO_BADGES)

def StubbornBadge(metadata):
  if metadata.problems is None:
    return NO_BADGES
  stubborn = any(problem.tries_before_ac >= 50
                 for problem in Solved(metadata.problems))
  badge = Badge('Stubborn', 'Solved a problem after 50 attempts', Badge.BRONZE)
  return ([badge], []) if stubborn else (NO_BADGES)

def Overthinker(metadata):
  if metadata.problems is None:
    return NO_BADGES
  year = datetime.timedelta(365)
  overthinker = any(problem.first_ac_date - problem.first_attempt_date >= year
                    for problem in Solved(metadata.problems))
  badge = Badge(
      'Overthinker', 'More than a year to solve a problem', Badge.BRONZE)
  return ([badge], []) if overthinker else (NO_BADGES)

def Addicted(metadata):
  if metadata.max_attempts_day is None:
    return NO_BADGES
  badge = Badge(
      'Addicted', 'Submitted 50 attempts on the same day', Badge.BRONZE)
  return ([badge], []) if metadata.max_attempts_day >= 50 else (NO_BADGES)

def Inactive(metadata):
  if metadata.problems is None:
    return NO_BADGES
  badge = Badge(
      'Inactive', 'More than a year without solving a problem', Badge.BRONZE)
  problem_dates = [problem.first_ac_date
                   for problem in Solved(metadata.problems)]
  if not problem_dates:
    return NO_BADGES
  max_date = max(problem_dates)
  inactive = datetime.datetime.now() - max_date > datetime.timedelta(365)
  return ([badge], []) if inactive else (NO_BADGES)

def Blink(metadata):
  if metadata.problems is None:
    return NO_BADGES
  badge = Badge('Blink', 'Solved a problem with a time of 0.00s', Badge.BRONZE)
  blink = any(problem.best_time == 0
              for problem in Solved(metadata.problems))
  return ([badge], []) if blink else (NO_BADGES)

BADGES = [LanguageBadge, SolvedProblemsBadge, SharpshooterBadge, StubbornBadge,
          CountryBadge, FirstPlaceBadge, VeteranBadge, Overthinker, Addicted,  
	  Inactive, Blink, Forever]

def EvalLanguageCount(problems):
  if problems is None:
    return {}
  language_count = {}
  for problem in problems:
    for language in problem.languages:
      language = LANGUAGE_CONVERT.get(language, language)
      language_count[language] = 1 + language_count.get(language, 0)
  return language_count

def GrantBadges(metadata):
  metadata.language_count = EvalLanguageCount(metadata.problems)
  granted_badges = []
  skipped_badges = []
  for badge in BADGES:
    granted, skipped = badge(metadata)
    granted_badges.extend(granted)
    skipped_badges.extend(skipped)
  return granted_badges, skipped_badges
