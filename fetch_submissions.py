import os
import sys
import requests
import getpass
from operator import itemgetter

LOGIN_URL = 'https://leetcode.com/accounts/login/'
SUBMISSIONS_URL = 'https://leetcode.com/api/submissions/'
CLIENT = requests.Session()
DIRECTORY = 'solutions'


# UTIL METHODS
def get_file_extension(file_type):
  if file_type == 'python3':
    return 'py'
  if file_type == 'php':
    return 'php'
  if file_type == 'rust':
    return 'rs'
  if file_type == 'kotlin':
    return 'kt'
  if file_type == 'scala':
    return 'scala'
  if file_type == 'golang':
    return 'go'
  if file_type == 'swift':
    return 'swift'
  if file_type == 'ruby':
    return 'rb'
  if file_type == 'javascript':
    return 'py'
  if file_type == 'csharp':
    return 'cs'
  if file_type == 'c':
    return 'c'
  if file_type == 'python':
    return 'py'
  if file_type == 'java':
    return 'java'
  if file_type == 'cpp':
    return 'cpp'
  return 'txt'


def get_comment_symbol(file_type):
  if file_type in ['python3', 'python', 'php', 'ruby']:
    return '#'
  if file_type in ['csharp', 'rust', 'kotlin', 'scala', 'golang', 'swift',
                   'javascript', 'c', 'java', 'cpp']:
    return '//'
  return ''


def login(username, password):
  # Important step to get csrftoken
  CLIENT.get(LOGIN_URL)

  csrftoken = CLIENT.cookies['csrftoken'] if 'csrftoken' in CLIENT.cookies else CLIENT.cookies['csrf']

  payload = {
      'csrfmiddlewaretoken': csrftoken,
      'login': username,
      'password': password,
      'next': '/'
  }

  CLIENT.post(LOGIN_URL, data=payload, headers=dict(Referer=LOGIN_URL))


# Returns the fastest submission for each problem
def fetch_best_submissions():
  response = CLIENT.get(SUBMISSIONS_URL).json()
  submissions = response['submissions_dump']
  filtered_submissions = filter(
      lambda sub: sub['status_display'] == 'Accepted', submissions)
  sorted_submissions = sorted(
      submissions, key=itemgetter('title', 'runtime'))
  best_submissions = drop_duplicate_submissions(sorted_submissions)

  return best_submissions


# Keeps the first occurnece of a problem's submission and discard
# any following submissions to the same problem
def drop_duplicate_submissions(submissions):
  seen_problems = set()
  submissions_without_duplicates = []

  for submission in submissions:
    if submission['title'] in seen_problems:
      continue

    submissions_without_duplicates.append(submission)
    seen_problems.add(submission['title'])

  return submissions_without_duplicates


def save_submission_as_file(submission):
  print(f'Saving solution for {submission["title"]}')

  if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)

  name = f'{DIRECTORY}/{submission["title"]}.{get_file_extension(submission["lang"])}'
  comment_symbol = get_comment_symbol(submission["lang"])
  with open(name, 'w') as outfile:
    outfile.write(f'{comment_symbol} Title: {submission["title"]}\n')
    outfile.write(f'{comment_symbol} Runtime: {submission["runtime"]}\n')
    outfile.write(f'{comment_symbol} Memory: {submission["memory"]}\n\n')
    outfile.write(submission['code'])

if __name__ == '__main__':
    if (len(sys.argv) != 2):
        print('Usage: python3 fetch_submissions.py <username>')
    else:
        username = sys.argv[1]
        password = getpass.getpass()
        login(username, password)
        submissions = fetch_best_submissions()

        for submission in submissions:
          save_submission_as_file(submission)
