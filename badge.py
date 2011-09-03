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

def GrantBadges(problems):
  language_set = {}
  for problem in problems:
    for language in problem.languages:
      if language in LANGUAGE_CONVERT:
        language = LANGUAGE_CONVERT[language]
      language_set[language] = 1 + language_set.get(language, 0)
  badges = []
  for language, count in language_set.iteritems():
    if count < 3:
      continue
    if language in LANGUAGE_CODES:
      badges.append(LANGUAGE_CODES[language] + ' user')
    else:
      badges.append(language + ' user')
  return badges
