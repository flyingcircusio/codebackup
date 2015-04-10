from os import path
import argparse
import json
import multiprocessing.pool
import os
import random
import requests
import subprocess
import sys
import urllib


class Repository(object):
    """A registered user at a code hosting site"""
    
    failed = None
    output = None

    def __init__(self, site, name):
        self.site = site
        self.name = name

    def backup(self, target):
        print 'Backing up {}/{}'.format(self.site.name, self.name)
        target = os.path.join(target, self.site.name, self.name)
        try:
            if not path.exists(target):
                self.clone_repository(target)
            else:
                self.update_repository(target)
        except Exception, e:
            print 'Failed to back up', self.name
            self.failed = e

    def clone_repository(self, target):
        assert not os.path.exists(target)
        url = self.CLONE_URL.format(**locals())
        os.makedirs(target)
        self.output = subprocess.check_output(
            self.CLONE_CMD.format(**locals()).split(),
            stderr=subprocess.STDOUT,
            cwd=target)
        
    def update_repository(self, target):
        url = self.CLONE_URL.format(**locals())
        self.output = subprocess.check_output(
            self.UPDATE_CMD.format(**locals()).split(),
            stderr=subprocess.STDOUT,
            cwd=target)


class Bitbucket(object):

    name = 'bitbucket'
    REPO_LIST_API = 'https://api.bitbucket.org/1.0/users/{self.username}/'

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_repositories(self):
        """Get all repositories for this site."""
        response = requests.get(self.REPO_LIST_API.format(**locals()),
                                auth=(self.username, self.password))
        j = json.loads(response.text)
        for repo in j['repositories']:
            if repo['scm'] == 'hg':
                yield HGRepository(self, repo['name'])
            elif repo['scm'] == 'git':
                yield GITRepository(self, repo['name'])


class HGRepository(Repository):

    CLONE_URL = 'ssh://hg@bitbucket.org/{self.site.username}/{self.name}/'
    CLONE_CMD = 'hg clone -U {url} .'
    UPDATE_CMD = 'hg pull {url}'


class GITRepository(Repository):

    CLONE_URL = 'git@bitbucket.org:{self.site.username}/{self.name}.git'
    CLONE_CMD = 'git clone --no-checkout {url} .'
    UPDATE_CMD = 'git pull'


def main():
    parser = argparse.ArgumentParser(
        description="A simple tool to backup your Bitbucket repositories",
    )
    
    parser.add_argument('username', type=str, help='Username')
    parser.add_argument('password', type=str, help='Password')
    parser.add_argument('backupdir', type=str, 
                        help='The target backup directory')
    
    args = parser.parse_args()
    
    bitbucket = Bitbucket(args.username, args.password)
    repos = list(bitbucket.get_repositories())
    random.shuffle(repos)

    pool = multiprocessing.pool.ThreadPool(20)
    pool.map(lambda x: x.backup(args.backupdir), repos)

    failed = 0
    for repo in repos:
        if repo.failed is None:
            continue
        failed += 1
        print 'WARNING: the following repositories failed to update:'
        print repo.name
        print repo.output
        print repo.failed
    if failed:
        sys.exit(2)
