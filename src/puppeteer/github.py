# vim: set fileencoding=utf-8:

import time

import puppeteer.util

def fetch_project_issues(project_name):
    "Returns raw issue descriptions."
    return puppeteer.util.fetch_json('http://github.com/api/v2/json/issues/list/%s/open' % project_name)

def fetch_issue_comments(project_name, issue_id):
    "Return raw issue comments."
    return puppeteer.util.fetch_json('http://github.com/api/v2/json/issues/comments/%s/%u' % (project_name, issue_id))
    
def get_project_issues(project_name, for_user=None):
    "Returns issues with comments."
    issues = {}
    for issue in fetch_project_issues(project_name)['issues']:
        if for_user is not None and for_user != issue['user']:
            continue
        issues[issue['number']] = {
            'subject': issue['title'],
            'description': issue['body'],
            'url': 'https://github.com/%s/issues/%u' % (project_name, issue['number']),
            'time': int(time.mktime(time.strptime(issue['updated_at'][:19], '%Y/%m/%d %H:%M:%S'))),
            'project': 'github/' + project_name,
        }
        if issue['comments']:
            issues[issue['number']]['comments'] = fetch_issue_comments(project_name, issue['number'])['comments']
    return issues

if __name__ == '__main__':
    import sys
    import json
    if len(sys.argv) < 2:
        print 'Usage: %s project_name' % sys.argv[0]
        sys.exit(1)
    issues = get_project_issues(sys.argv[1])
    print json.dumps(issues, ensure_ascii=False, indent=True)
