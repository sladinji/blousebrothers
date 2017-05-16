# -*- encoding: utf-8 -*-

from __future__ import with_statement
from fabric.api import *
import requests
import re
import fabric
from raven import Client

sentry = Client('https://770aeeaa5cc24a3e8b16a10c328c28c5:1aca22596ba1421198ff5269032f0ffd@sentry.io/104798')

env.hosts = ['admin@blousebrothers.fr']
code_dir = 'projets/blousebrothers/blousebrothers'


def send_simple_message(msg):
    return requests.post(
                "https://api.mailgun.net/v3/blousebrothers.fr/messages",
                auth=("api", "key-0cb37ccb0c2de16fc921df70228346bc"),
                data={"from": "Futur Bot <noreply@blousebrothers.fr>",
                      "to": ["julien.almarcha@gmail.com", "guillaume@blousebrothers.fr"],
                      "subject": "https://labresult.fr updated",
                      "text": msg})


def deploy():
    if not fabric.contrib.console.confirm("Deploy to production ?"):
        return
    if not fabric.contrib.console.confirm("Sérieux ?"):
        return
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            run("git clone git@github.com:sladinji/blousebrothers.git %s" % code_dir)
    with cd(code_dir):
        run("git pull origin master")
        put(".env", ".env")
        run("docker-compose build")
        run("docker-compose up -d")
        run("docker-compose run django ./manage.py migrate")
        run("docker-compose run django ./manage.py cgu_sync")
        run("docker-compose run django ./manage.py rebuild_index --noinput")


@hosts('ubuntu@labresult.fr')
def futur(branch='master',reset='no'):
    """
    Deploy on futur
    """
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            run("git clone git@github.com:sladinji/blousebrothers.git %s" % code_dir)
    with cd(code_dir):
        run("git fetch")
        run("git checkout {}".format(branch))
        logs = run("git log --pretty=oneline --abbrev-commit ..origin/{}".format(branch))
        logs = ["* {}".format(x) for x in re.findall(r'\[m (.*)\x1b', logs)]
        send_simple_message("\n".join(logs))
        run("git merge origin/{}".format(branch))
        with prefix("source blouserc"):
            run("docker-compose build")
            run("docker-compose up -d")
            run("docker-compose run django ./manage.py migrate")
            if reset == 'yes':
                run("fab proddb")
            run("docker-compose run django ./manage.py cgu_sync")
            run("docker-compose run django ./manage.py rebuild_index --noinput")


def proddb(pre=False):
    """
    Dump prod db and load it load loacally.
    """
    with cd(code_dir):
        run("docker-compose run postgres backup")
        backups = run("docker-compose run postgres list-backups").replace("\r\n", '\t').split('\t')[3:]
        last = sorted(backups)[-1]
        run(r"docker run --rm --volumes-from blousebrothers_postgres_1 "
            r"-v $(pwd):/backup ubuntu tar cvzf /backup/backup.tgz /backups/%s" % last)

    get("%s/backup.tgz" % code_dir)
    if not pre:
        load_last_dump(last)
    return last


class FabricException(Exception):
    pass

@hosts('ubuntu@labresult.fr')
def backup():
    with settings(abort_exception = FabricException):
        try:
            local("docker-compose run postgres backup")
            backups = local("docker-compose run postgres list-backups", capture=True).replace("\r\n", '\t').split('\t')[3:]
            last = sorted(backups)[-1]
            local(r"docker run --rm --volumes-from blousebrothers_postgres_1 "
                r"-v $(pwd):/backup ubuntu tar cvzf /backup/backup.tgz /backups/%s" % last)
            put("backup.tgz")
        except Exception:
            print("AHAAH")
    	    sentry.captureException()

@hosts('ubuntu@labresult.fr')
def preproddb():
    """
    Dump prrprod and loat it locallly.
    """
    with prefix("source blouserc"):
        last = proddb(pre=True)
    load_last_dump(last, pre=True)


def load_last_dump(last=None, pre=False, mangoreset='yes'):
    if not last:
        backups = local("docker-compose run postgres list-backups", capture=True).replace("\r\n", '\t').split('\t')[3:]
        last = sorted(backups)[-1]
    if pre:
        local("cd ubuntu@labresult.fr && tar xzf backup.tgz")
        local("docker run --rm "
              "--volumes-from blousebrothers_postgres_1 "
              "-v $(pwd)/ubuntu@labresult.fr/backups:/backup "
              "blousebrothers_postgres cp /backup/%s /backups" % last)
    else:
        local("cd admin@blousebrothers.fr && tar xzf backup.tgz")
        local("docker run --rm "
              "--volumes-from blousebrothers_postgres_1 "
              "-v $(pwd)/admin@blousebrothers.fr/backups:/backup "
              "blousebrothers_postgres cp /backup/%s /backups" % last)
    local("docker-compose stop django")
    local("docker exec blousebrothers_postgres_1 restore %s" % last)
    local("docker-compose start django")
    local("docker-compose run django ./manage.py migrate")
    if mangoreset=='yes':
        local("docker-compose run django ./manage.py mango_reset")


def get_migrations():
    """
    Remove local migration files et grab them from prod, nice to get a clean migration set.
    """
    local("sudo rm -rf blousebrothers/users/migrations/*")
    local("sudo rm -rf blousebrothers/confs/migrations/*")
    get("%s/blousebrothers/users/migrations/*.py" % code_dir, "blousebrothers/users/migrations/")
    get("%s/blousebrothers/confs/migrations/*.py" % code_dir, "blousebrothers/confs/migrations/")


@hosts('ubuntu@labresult.fr')
def futur_publish_confs():
    """
    Publish_confs on futur.
    """
    with cd(code_dir):
        with prefix("source blouserc"):
            run("docker-compose run django ./manage.py publish_confs")


@hosts('ubuntu@labresult.fr')
def futur_gen_code():
    with cd(code_dir):
        with prefix("source blouserc"):
            run('./manage.py gen_code "https://s3.amazonaws.com/blousebrothers/imgemail/members.csv"')


@hosts('ubuntu@labresult.fr')
def futur_syncdb():
    with cd(code_dir):
        with prefix("source blouserc"):
            run('fab proddb')
    futur_publish_confs()
