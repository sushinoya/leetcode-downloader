import os
import sys
import requests
import getpass
import time
import random

LOGIN_URL = 'https://leetcode.com/accounts/login/'
SUBMISSIONS_URL = 'https://leetcode.com/api/submissions/'
PROBLEMS_URL = 'https://leetcode.com/api/problems/all/'
CLIENT = requests.Session()
DIRECTORY = 'solutions'
FILE_EXTENSIONS = {
    'mysql': 'sql',
    'bash': 'sh',
    'python3': 'py',
    'php': 'php',
    'rust': 'rs',
    'kotlin': 'kt',
    'scala': 'scala',
    'golang': 'go',
    'swift': 'swift',
    'ruby': 'rb',
    'javascript': 'py',
    'csharp': 'cs',
    'c': 'c',
    'python': 'py',
    'java': 'java',
    'cpp': 'cpp'
}


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


def get_file_extension(file_type):
  if file_type in FILE_EXTENSIONS:
    return FILE_EXTENSIONS[file_type]
  return 'txt'


def get_comment_symbol(file_type):
  if file_type in ['sql']:
    return '--'
  if file_type in ['python3', 'python', 'php', 'ruby', 'bash']:
    return '#'
  if file_type in ['csharp', 'rust', 'kotlin', 'scala', 'golang', 'swift',
                   'javascript', 'c', 'java', 'cpp']:
    return '//'
  return ''


def successfully_login(username, password):
  # Important step to get csrftoken
  CLIENT.get(LOGIN_URL)

  csrftoken = CLIENT.cookies['csrftoken'] if 'csrftoken' in CLIENT.cookies else CLIENT.cookies['csrf']

  payload = {
      'csrfmiddlewaretoken': csrftoken,
      'login': username,
      'password': password,
      'next': '/'
  }

  response = CLIENT.post(LOGIN_URL, data=payload, headers=dict(Referer=LOGIN_URL))
  # The status code and reasons fields for response object return same
  # values for successful and unsuccessful logins, hence the url field is used
  return response.url != "https://leetcode.com/accounts/login/"


def fetch_all_attempted_problem_slugs():
  problems = CLIENT.get(PROBLEMS_URL).json()['stat_status_pairs']
  accepted_problems = [problem['stat']
                       for problem in problems if problem['status'] == 'ac']
  return [problem['question__title_slug'] for problem in accepted_problems]


def fetch_best_submission_for_problem(problem_slug):
  submissions = CLIENT.get(
      f'https://leetcode.com/api/submissions/{problem_slug}').json()
  if 'submissions_dump' not in submissions:
    raise Exception('Accessing submissions for {problem_slug} denied.')

  submissions = submissions['submissions_dump']
  filtered_submissions = filter(
      lambda sub: sub['status_display'] == 'Accepted', submissions)
  return min(filtered_submissions, key=lambda x: int(x['runtime'].strip('ms')))


# Returns the fastest submission for each problem
def fetch_best_submissions():
  problem_slugs = set(fetch_all_attempted_problem_slugs())
  num_attempted_problems = len(problem_slugs)
  submissions = []

  while problem_slugs:
    current_iteration_slugs = problem_slugs.copy()
    for slug in current_iteration_slugs:
      try:
        submission = fetch_best_submission_for_problem(slug)
        submissions.append(submission)
        problem_slugs.discard(slug)
        progress(num_attempted_problems - len(problem_slugs),
                 num_attempted_problems, f'fetched {slug}')
      except:
        time.sleep(random.uniform(0.5, 1.5))
  return submissions


# Keeps the first occurrence of a problem's submission and discard
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
    is_logged_in = False
    for i in range(5):
      username = input('Username: ')
      password = getpass.getpass()
      if successfully_login(username, password):
        is_logged_in = True
        break
      print("The username and/or password you specified are not correct.", file=sys.stderr)

    if not is_logged_in:
      print(f"You have exceeded the maximum number of login attempts allowed.")
    else:
      submissions = fetch_best_submissions()
      for submission in submissions:
        save_submission_as_file(submission)
