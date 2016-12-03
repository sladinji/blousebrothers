from __future__ import with_statement
import re
from fabric.api import *
import requests

env.hosts = ['dowst@blousebrothers.fr']
code_dir = 'projets/blousebrothers/blousebrothers'


def send_simple_message(msg):
    return requests.post(
                "https://api.mailgun.net/v3/blousebrothers.fr/messages",
                auth=("api", "key-0cb37ccb0c2de16fc921df70228346bc"),
                data={"from": "Futur Bot <noreply@blousebrothers.fr>",
                                    "to": ["julien.almarcha@gmail.com", "guillaume@blousebrothers.fr"],
                      "subject": "http://futur.blousebrothers.fr:8000 updated",
                                    "text": msg})

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
    """
    Deploy on futur
    """
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            run("git clone git@github.com:sladinji/blousebrothers.git %s" % code_dir)
    with cd(code_dir):
        run("git fetch origin master")
        logs = run("git log --pretty=oneline --abbrev-commit ..origin/master")
        logs =[ "* {}".format(x) for x in  re.findall(r'\[m (.*)\x1b', logs)]
        send_simple_message("\n".join(logs))
        run("git merge")
        with prefix("source blouserc"):
            run("docker-compose build")
            run("docker-compose up -d")
            run("docker-compose run django ./manage.py migrate")

def proddb():
    """
    Dump prod db and load it load loacally.
    """
    with cd(code_dir):
        run("docker-compose run postgres backup")
        backups = run("docker-compose run postgres list-backups").replace("\r\n",'\t').split('\t')[3:]
        last = sorted(backups)[-1]
        run(r"docker run --rm --volumes-from blousebrothers_postgres_1 "
            r"-v $(pwd):/backup ubuntu tar cvzf /backup/backup.tgz /backups/%s" % last)

    get("%s/backup.tgz" % code_dir)
    local("cd dowst@blousebrothers.fr && tar xzf backup.tgz")
    local("docker run --rm "
          "--volumes-from blousebrothers_postgres_1 "
          "-v $(pwd)/dowst@blousebrothers.fr/backups:/backup "
          "blousebrothers_postgres cp /backup/%s /backups" % last)
    local("docker-compose stop django")
    local("docker exec blousebrothers_postgres_1 restore %s" % last)
    local("docker-compose start django")

def get_migrations():
    """
    Remove local migration files et grab them from prod, nice to get a clean migration set.
    """
    local("sudo rm -rf blousebrothers/users/migrations/*")
    local("sudo rm -rf blousebrothers/confs/migrations/*")
    get("%s/blousebrothers/users/migrations/*.py" % code_dir, "blousebrothers/users/migrations/")
    get("%s/blousebrothers/confs/migrations/*.py" % code_dir, "blousebrothers/confs/migrations/")

@hosts('admin@futur.blousebrothers.fr')
def futur_publish_confs():
    """
    Publish_confs on futur.
    """
    with cd(code_dir):
        with prefix("source blouserc"):
            run("docker-compose run django ./manage.py publish_confs")
