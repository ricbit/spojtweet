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

def LanguageBadge(metadata):
  badges = []
  for language, count in metadata.language_count.iteritems():
    language_name = LANGUAGE_CODES.get(language, language)
    if count >= 500:
      badges.append(language_name + ' Guru')
      continue
    if count >= 100:
      badges.append(language_name + ' Master')
      continue
    if count >= 10:
      badges.append(language_name + ' User')
      continue
    if count >= 3:
      badges.append(language_name + ' Novice')
      continue
  return badges    

BADGES = [LanguageBadge]

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
