import datetime
import re

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
  problems = {}
  for line in usertext.split('\n'):
    fields = [field.strip() for field in line.split('|')]
    if len(fields) != 9 or not fields[1].isdigit():
      continue
    date = datetime.datetime.strptime(fields[2], "%Y-%m-%d %H:%M:%S")
    code = fields[3]
    status = fields[4]
    time = int(fields[5].replace('.', ''))
    language = fields[7]
    problems.setdefault(code, []).append((date, status, language, time))
  return problems

def ParseCountryList(text):
  return re.findall('(?i)users/(..)/\">(.*?)</a>', text)

def Test():
  page = open('country.html').read()
  print ParseCountryList(page)

if __name__ == '__main__':
  Test()
