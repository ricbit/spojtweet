import model

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

class UserMetadata(object):
  def __init__(self):
    self.problems = None
    self.language_count = None
    self.country_position = None
    self.country = None

def ProgressiveBadge(count, titles, requirements, descriptions):
  badge = None
  for title, req, desc in zip(titles, requirements, descriptions):
    if count >= req:
      badge = (title, desc)
  return [model.Badge(*badge)] if badge is not None else []

def CountryBadge(metadata):
  country = metadata.country.title()
  titles = ['Citizen', 'VIP', 'Leader']
  badge_titles = ['%s %s' % (country, title) for title in titles]
  requirements = [-100, -10, -1]
  descriptions = ['Top 100 problem solvers from ' + country,
                  'Top 10 problem solvers from ' + country,
		  'Best problem solver from ' + country]
  return ProgressiveBadge(
      -metadata.country_position, badge_titles, requirements, descriptions)

def LanguageBadge(metadata):
  badges = []
  for language, count in metadata.language_count.iteritems():
    language_name = LANGUAGE_CODES.get(language, language)
    titles = ['Novice', 'User', 'Master', 'Guru']
    badge_titles = ["%s %s" % (language_name, title) for title in titles]
    requirements = [3, 10, 100, 500]
    descriptions = ["Solved %d problems in %s" % (x, language_name)
                    for x in requirements]
    badges.extend(ProgressiveBadge(
        count, badge_titles, requirements, descriptions))
  return badges    

def SolvedProblemsBadge(metadata):
  titles = ['Apprentice', 'Mage', 'Warlock']
  requirements = [10, 100, 1000]
  descriptions = ["Solved %d problems" % x for x in requirements]
  return ProgressiveBadge(
      len(metadata.problems), titles, requirements, descriptions)

def SharpshooterBadge(metadata):
  count = 0
  for problem in metadata.problems:
    if problem.tries_before_ac == 0:
      count += 1
  badge = model.Badge('Sharpshooter', 'Solved 25 problems on the first try')
  return [badge] if count >= 25 else []

def StubbornBadge(metadata):
  stubborn = any(problem.tries_before_ac >= 50 and problem.solved
                 for problem in metadata.problems)
  badge = model.Badge('Stubborn', 'Solved a problem after 50 attempts')
  return [badge] if stubborn else []

BADGES = [LanguageBadge, SolvedProblemsBadge, SharpshooterBadge, StubbornBadge,
          CountryBadge]

def EvalLanguageCount(problems):
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
