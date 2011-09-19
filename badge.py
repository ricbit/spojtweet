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

LANGUAGE_CODES = {
  'HAS' : 'Haskell',
  'TEX' : 'Text',
  'C'   : 'C',
  'C++' : 'C++',
  'PYT' : 'Python',
  'ASM' : 'Assembly',
  'JAV' : 'Java',
  'PER' : 'Perl',
  'SCM' : 'Scheme',
  'RUB' : 'Ruby',
  'PAS' : 'Pascal',
  'BF'  : 'Brainfuck'
}

LANGUAGE_CONVERT = {
  'C99' : 'C'
}

class Badge(object):
  BRONZE = 'bronze'
  SILVER = 'silver'
  GOLD = 'gold'
  PLATINUM = 'platinum'

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
    self.max_attempts_day = None

def ProgressiveBadge(count, titles, requirements, descriptions, values):
  badge = None
  for title, req, desc, value in zip(titles, requirements, descriptions, values):
    if count >= req:
      badge = (title, desc, value)
  return [Badge(*badge)] if badge is not None else []

def CountryBadge(metadata):
  if metadata.country_position is None:
    return []
  country = metadata.country.title()
  titles = ['Citizen', 'VIP', 'Leader']
  badge_titles = ['%s %s' % (country, title) for title in titles]
  requirements = [-100, -10, -1]
  descriptions = ['Top 100 problem solvers from ' + country,
                  'Top 10 problem solvers from ' + country,
		  'Best problem solver from ' + country]
  values = [Badge.BRONZE, Badge.SILVER, Badge.GOLD]
  return ProgressiveBadge(
      -metadata.country_position, badge_titles, requirements, descriptions, values)

def LanguageBadge(metadata):
  badges = []
  for language, count in metadata.language_count.iteritems():
    language_name = LANGUAGE_CODES.get(language, language)
    titles = ['Novice', 'User', 'Master', 'Guru']
    badge_titles = ["%s %s" % (language_name, title) for title in titles]
    requirements = [3, 10, 100, 500]
    descriptions = ["Solved %d problems in %s" % (x, language_name)
                    for x in requirements]
    values = [Badge.BRONZE, Badge.SILVER, Badge.GOLD, Badge.PLATINUM]
    badges.extend(ProgressiveBadge(
        count, badge_titles, requirements, descriptions, values))
  return badges    

def SolvedProblemsBadge(metadata):
  if metadata.problems is None:
    return []
  titles = ['Apprentice', 'Mage', 'Warlock']
  requirements = [10, 100, 1000]
  descriptions = ["Solved %d problems" % x for x in requirements]
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
    return []
  badge = Badge('Forever', 'First place on a problem with a time of 0.00s', Badge.GOLD)
  return [badge] if metadata.first_place_permanent else []

def VeteranBadge(metadata):
  if metadata.problems is None:
    return []
  titles = ['Recruit', 'Soldier', 'Veteran']
  requirements = [datetime.timedelta(30),
                  datetime.timedelta(365),
                  datetime.timedelta(5*365)]
  description = ['Solving problems on SPOJ for %s' % time
                 for time in ['one month', 'one year', 'five years']]
  problem_dates = [problem.first_ac_date
                   for problem in metadata.problems if problem.solved]
  values = [Badge.BRONZE, Badge.SILVER, Badge.GOLD]
  if not problem_dates:
    return []
  min_date = min(problem_dates)
  max_date = max(problem_dates)
  return ProgressiveBadge(
      max_date - min_date, titles, requirements, description, values)

def SharpshooterBadge(metadata):
  if metadata.problems is None:
    return []
  count = sum(1 for problem in metadata.problems
              if problem.solved and problem.tries_before_ac == 0)
  badge = Badge('Sharpshooter', 'Solved 25 problems on the first try', Badge.GOLD)
  return [badge] if count >= 25 else []

def StubbornBadge(metadata):
  if metadata.problems is None:
    return []
  stubborn = any(problem.tries_before_ac >= 50 and problem.solved
                 for problem in metadata.problems)
  badge = Badge('Stubborn', 'Solved a problem after 50 attempts', Badge.BRONZE)
  return [badge] if stubborn else []

def Overthinker(metadata):
  if metadata.problems is None:
    return []
  year = datetime.timedelta(365)
  overthinker = any(problem.first_ac_date - problem.first_attempt_date >= year
                    for problem in metadata.problems if problem.solved)
  badge = Badge(
      'Overthinker', 'More than a year to solve a problem', Badge.BRONZE)
  return [badge] if overthinker else []

def Addicted(metadata):
  if metadata.max_attempts_day is None:
    return []
  badge = Badge('Addicted', 'Submitted 50 solutions on the same day', Badge.PLATINUM)
  return [badge] if metadata.max_attempts_day >= 50 else []

def Inactive(metadata):
  if metadata.problems is None:
    return []
  badge = Badge('Inactive', 'More than a year without solving a problem', Badge.BRONZE)
  problem_dates = [problem.first_ac_date
                   for problem in metadata.problems if problem.solved]
  if not problem_dates:
    return []
  max_date = max(problem_dates)
  inactive = datetime.datetime.now() - max_date > datetime.timedelta(365)
  return [badge] if inactive else []

def Blink(metadata):
  if metadata.problems is None:
    return []
  badge = Badge('Blink', 'Solved a problem with a time of 0.00s', Badge.GOLD)
  blink = any(problem.best_time == 0
              for problem in metadata.problems if problem.solved)
  return [badge] if blink else []

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
  for badge in BADGES:
    granted_badges.extend(badge(metadata))
  return granted_badges
