from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm

env.hosts = ['blousebrothers.fr']

def deploy():
    code_dir = 'projets/blousebrothers/blousebrothers'
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            run("git clone git@github.com:sladinji/blousebrothers.git %s" % code_dir)
    with cd(code_dir):
        run("git pull origin master")
        run("docker-compose build")
        run("docker-compose up -d")
