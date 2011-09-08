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
  def __init__(self, problems, language_count):
    self.problems = problems
    self.language_count = language_count

def ProgressiveBadge(count, titles, requirements):
  badge = None
  for title, requirement in zip(titles, requirements):
    if count >= requirement:
      badge = title
  return badge if badge is not None else []

def LanguageBadge(metadata):
  badges = []
  for language, count in metadata.language_count.iteritems():
    language_name = LANGUAGE_CODES.get(language, language)
    titles = ['Novice', 'User', 'Master', 'Guru']
    badge_titles = ["%s %s" % (language_name, title) for title in titles]
    requirements = [3, 10, 100, 500]
    badges.append(ProgressiveBadge(count, badge_titles, requirements))
  return badges    

def SolvedProblemsBadge(metadata):
  titles = ['Apprentice', 'Mage', 'Warlock']
  requirements = [10, 100, 1000]
  return [ProgressiveBadge(len(metadata.problems), titles, requirements)]

BADGES = [LanguageBadge, SolvedProblemsBadge]

def EvalLanguageCount(problems):
  language_count = {}
  for problem in problems:
    for language in problem.languages:
      if language in LANGUAGE_CONVERT:
        language = LANGUAGE_CONVERT[language]
      language_count[language] = 1 + language_count.get(language, 0)
  return language_count

def GrantBadges(problems):
  metadata = UserMetadata(problems, EvalLanguageCount(problems))
  granted_badges = []
  for badge in BADGES:
    granted_badges.extend(badge(metadata))
  return granted_badges
