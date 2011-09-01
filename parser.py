import datetime
import re

import spojuser

class ParseError(Exception):
  pass

def ParseStatusPage(text):
  name_re = '(?i)<h3>(.+?)\'s user data </h3>'
  match = re.search(name_re, text)
  if match == None:
    raise ParseError()
  name = match.group(1).strip()

  country_re = '(?i)Country:.*?<td>([^>]+?)</td>'
  match = re.search(country_re, text.replace('\n',''))
  if match == None:
    raise ParseError()
  country = match.group(1).strip()


  return name, country

def ParseDetailsPage(usertext):
  problem_map = {}
  for line in usertext.split('\n'):
    fields = [field.strip() for field in line.split('|')]
    if len(fields) != 9 or not fields[1].isdigit() or fields[4] != 'AC':
      continue
    date = datetime.datetime.strptime(fields[2], "%Y-%m-%d %H:%M:%S")
    code = fields[3]
    language = fields[7]
    problem_map.setdefault((code, language), []).append(date)
  problems = []
  for (code, language), date_list in problem_map.iteritems():
    problems.append(spojuser.SpojProblem(
        code=code, date=min(date_list), language=language))
  return problems

def Test():
  page = open('ricbit.html').read()
  print ParseStatusPage(page)

if __name__ == '__main__':
  Test()
