# vim: set fileencoding=utf-8:

import os
import time
import megaplan

import puppeteer.util

class MegaplanClient:
    def __init__(self, settings):
        self.settings = settings

    def get_project_issues(self):
        issues = {}
        c = megaplan.Client(self.settings['host'], self.settings['access_id'], self.settings['secret_key'])
        for task in c.get_tasks_by_status(status = 'status' in self.settings and self.settings['status'] or 'inprocess'):
            issue = {
                'id': task['Id'],
                'url': 'https://%s/task/%s/card/' % (c.hostname, task['Id']),
                'subject': task['Name'],
                'description': c.get_task_details(task['Id'])['task']['Statement'].replace('<br/>', ''),
                'time': int(time.mktime(time.strptime(task['TimeCreated'], '%Y-%m-%d %H:%M:%S'))),
                'project': self.settings['name'],
                'comments': [],
            }

            comments = c.get_task_comments(task['Id'])
            if 'comments' in comments:
                for comment in comments['comments'].values():
                    issue['comments'].append({
                        'time': comment['TimeCreated'],
                        'user': comment['Author']['Name'],
                        'body': comment['Text'].replace('<br/>', ''),
                    })
            issues[task['Id']] = issue
        return issues

class GitHubClient:
    def __init__(self, settings):
        self.settings = settings

    def fetch_project_issues(self):
        "Returns raw issue descriptions."
        return puppeteer.util.fetch_json('http://github.com/api/v2/json/issues/list/%s/open' % self.settings['name'])

    def fetch_issue_comments(self, issue_id):
        "Return raw issue comments."
        return puppeteer.util.fetch_json('http://github.com/api/v2/json/issues/comments/%s/%u' % (self.settings['name'], issue_id))
        
    def get_project_issues(self, for_user=None):
        "Returns issues with comments."
        issues = {}
        for issue in self.fetch_project_issues()['issues']:
            if for_user is not None and for_user != issue['user']:
                continue
            issues[issue['number']] = {
                'subject': issue['title'],
                'description': issue['body'],
                'url': 'https://github.com/%s/issues/%u' % (self.settings['name'], issue['number']),
                'time': int(time.mktime(time.strptime(issue['updated_at'][:19], '%Y/%m/%d %H:%M:%S'))),
                'project': 'github/' + self.settings['name'],
            }
            if issue['comments']:
                issues[issue['number']]['comments'] = self.fetch_issue_comments(issue['number'])['comments']
        return issues

def get_data():
    cache_fn = os.path.expanduser('~/.puppeteer-cache.json')
    if os.path.exists(cache_fn):
        result = puppeteer.util.load_json(cache_fn)
    else:
        result = {}
        for tracker in puppeteer.util.load_yaml(os.path.expanduser('~/.config/tremor.yaml'))['trackers']:
            cls = None
            if tracker['type'].lower() == 'github':
                cls = GitHubClient
            elif tracker['type'].lower() == 'megaplan':
                cls = MegaplanClient
            if cls is not None:
                result[tracker['name']] = cls(tracker).get_project_issues()
        puppeteer.util.save_json(cache_fn, result)
    return result
