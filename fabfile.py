from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.context_managers import prefix
from fabric.decorators import hosts

env.hosts = ['blousebrothers.fr']
code_dir = 'projets/blousebrothers/blousebrothers'

def deploy():
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            run("git clone git@github.com:sladinji/blousebrothers.git %s" % code_dir)
    with cd(code_dir):
        run("git pull origin master")
        run("docker-compose build")
        run("docker-compose up -d")
        run("docker-compose run django ./manage.py migrate")

@hosts('admin@futur.blousebrothers.fr')
def futur():
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            run("git clone git@github.com:sladinji/blousebrothers.git %s" % code_dir)
    with cd(code_dir):
        run("git pull origin master")
        with prefix("source preprodrc"):
            run("docker-compose build")
            run("docker-compose up -d")
            run("docker-compose run django ./manage.py migrate")

def proddb():
    """
    Dump prod db and load it load loacally.
    """
    with cd(code_dir):
        run("docker-compose run postgres backup")
        backups = run("docker-compose run postgres list-backups").replace("\r\n",'\t').split('\t')[4:]
        last = sorted(backups)[-1]
        run(r"docker run --rm --volumes-from blousebrothers_postgres_1 "
            r"-v $(pwd):/backup ubuntu tar cvzf /backup/backup.tgz /backups/%s" % last)

    get("%s/backup.tgz" % code_dir)
    local("cd blousebrothers.fr && tar xzf backup.tgz")
    local("docker run --rm "
          "--volumes-from blousebrothers_postgres_1 "
          "-v $(pwd)/blousebrothers.fr/backups:/backup "
          "blousebrothers_postgres cp /backup/%s /backups" % last)
    local("docker-compose stop django")
    local("docker exec blousebrothers_postgres_1 restore %s" % last)
    local("docker-compose start django")
