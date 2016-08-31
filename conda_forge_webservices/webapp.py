import os
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.web

import requests
import os
from glob import glob
import tempfile
from git import Repo
import textwrap
import github
import conda_smithy.lint_recipe
import shutil
from contextlib import contextmanager


import conda_forge_webservices.linting as linting
import conda_forge_webservices.status as status


class RegisterHandler(tornado.web.RequestHandler):
    def get(self):
        token = os.environ.get('GH_TOKEN')
        headers = {'Authorization': 'token {}'.format(token)}

        url = 'https://api.github.com/repos/conda-forge/staged-recipes/hooks'

        payload = {
              "name": "web",
              "active": True,
              "events": [
                "pull_request"
              ],
              "config": {
                "url": "http://conda-linter.herokuapp.com/hook",
                "content_type": "json"
              }
            }

        r1 = requests.post(url, json=payload, headers=headers)

        url = 'https://api.github.com/repos/conda-forge/status/hooks'

        payload = {
              "name": "web",
              "active": True,
              "events": [
                "issues"
              ],
              "config": {
                "url": "http://conda-forge-status.herokuapp.com/hook",
                "content_type": "json"
              }
            }

        r2 = requests.post(url, json=payload, headers=headers)


class LintingHookHandler(tornado.web.RequestHandler):
    def post(self):
        headers = self.request.headers
        event = headers.get('X-GitHub-Event', None)

        if event == 'ping':
            self.write('pong')
        elif event == 'pull_request':
            body = tornado.escape.json_decode(self.request.body)
            repo_name = body['repository']['name']
            repo_url = body['repository']['clone_url']
            owner = body['repository']['owner']['login']
            pr_id = int(body['pull_request']['number'])
            is_open = body['pull_request']['state'] == 'open'

            # Only do anything if we are working with conda-forge, and an open PR.
            if is_open and owner == 'conda-forge':
                lint_info = linting.compute_lint_message(owner, repo_name, pr_id,
                                                         repo_name == 'staged-recipes')
                msg = linting.comment_on_pr(owner, repo_name, pr_id, lint_info['message'])
                linting.set_pr_status(owner, repo_name, lint_info, target_url=msg.html_url)
        else:
            print('Unhandled event "{}".'.format(event))
            self.set_status(404)
            self.write_error(404)


class StatusHookHandler(tornado.web.RequestHandler):
    def post(self):
        headers = self.request.headers
        event = headers.get('X-GitHub-Event', None)

        if event == 'ping':
            self.write('pong')
        elif event == 'issues' or event == 'issue_comment' or event == 'push':
            body = tornado.escape.json_decode(self.request.body)
            repo_full_name = body['repository']['full_name']

            # Only do something if it involves the status page
            if repo_full_name == 'conda-forge/status':
                status.update()
        else:
            print('Unhandled event "{}".'.format(event))
            self.set_status(404)
            self.write_error(404)


def create_webapp():
    application = tornado.web.Application([
        (r"/conda-linting/hook", LintingHookHandler),
        (r"/conda-forge-status/hook", StatusHookHandler),
    ])
    return application


def main():
    application = create_webapp()
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    port = int(os.environ.get("PORT", 5000))
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
