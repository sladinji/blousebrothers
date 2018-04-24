# -*- encoding: utf-8 -*-

from __future__ import with_statement
from fabric.api import *
import requests
import re
import fabric
from raven import Client

sentry = Client('https://770aeeaa5cc24a3e8b16a10c328c28c5:1aca22596ba1421198ff5269032f0ffd@sentry.io/104798')

env.hosts = ['admin@blousebrothers.fr']
code_dir = 'projets/blousebrothers'


def send_simple_message(msg):
    return requests.post(
                "https://api.mailgun.net/v3/blousebrothers.fr/messages",
                auth=("api", "key-0cb37ccb0c2de16fc921df70228346bc"),
                data={"from": "Futur Bot <noreply@blousebrothers.fr>",
                      "to": ["julien.almarcha@gmail.com", "guillaume@blousebrothers.fr"],
                      "subject": "https://137.74.25.128 updated",
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


@hosts('ubuntu@137.74.25.128')
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


def proddb(pre=False, mangoreset='yes'):
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
    local("cd admin@blousebrothers.fr && tar xzf backup.tgz")
    if not pre:
        load_last_dump(last, mangoreset)
    return last


class FabricException(Exception):
    pass

@hosts('ubuntu@137.74.25.128')
def backup():
    with settings(abort_exception = FabricException):
        try:
            local("/usr/local/bin/docker-compose run postgres backup")
            local(r"/usr/bin/docker run --rm --volumes-from blousebrothers_postgres_1 "
                r"-v $(pwd):/backup ubuntu tar cvzf /backup/backup.tgz /backups/last_dump.sql")
            put("backup.tgz")
        except Exception:
    	    sentry.captureException()

@hosts('ubuntu@137.74.25.128')
def preproddb():
    """
    Dump prrprod and loat it locallly.
    """
    with prefix("source blouserc"):
        last = proddb(pre=True)
    load_last_dump(last, pre=True)


def load_last_dump(last="last_dump.sql", pre=False, mangoreset='yes'):
    if not last:
        backups = local("docker-compose run postgres list-backups", capture=True).replace("\r\n", '\t').split('\t')[3:]
        last = sorted(backups)[-1]
    if pre:
        local("docker run --rm "
              "--volumes-from blousebrothers_postgres_1 "
              "-v $(pwd)/admin@blousebrothers.fr/backups:/backup "
              "blousebrothers_postgres cp /backup/%s /backups" % last)
    else:
        local("docker run --rm "
              "--volumes-from blousebrothers_postgres_1 "
              "-v $(pwd)/admin@blousebrothers.fr/backups:/backup "
              "blousebrothers_postgres cp /backup/%s /backups" % last)
    try:
        local("docker-compose stop django")
    except:
        print("No django docker running, continue")
    try:
        local("docker-compose start postgres")
    except:
        print("Postgres docker's already running, continue")
    local("docker exec blousebrothers_postgres_1 restore %s" % last)
    try:
        local("docker-compose start django")
    except:
        print("Can't start django docker, continue")
    local("docker-compose run django ./manage.py migrate")
    if mangoreset=='yes':
        local("docker-compose run django ./manage.py mango_reset")


def get_migrations():
    """
    Remove local migration files et grab them from prod, nice to get a clean migration set.
    """
    for app in ['users', 'confs', 'cards']:
        local("sudo rm -rf blousebrothers/%s/migrations/*" % app)
        get("%s/blousebrothers/%s/migrations/*.py" % (code_dir, app), "blousebrothers/%s/migrations/" % app)


@hosts('ubuntu@137.74.25.128')
def futur_publish_confs():
    """
    Publish_confs on futur.
    """
    with cd(code_dir):
        with prefix("source blouserc"):
            run("docker-compose run django ./manage.py publish_confs")


@hosts('ubuntu@137.74.25.128')
def futur_gen_code():
    with cd(code_dir):
        with prefix("source blouserc"):
            run('./manage.py gen_code "https://s3.amazonaws.com/blousebrothers/imgemail/members.csv"')


@hosts('ubuntu@137.74.25.128')
def futur_syncdb():
    with cd(code_dir):
        with prefix("source blouserc"):
            run('fab proddb')
    futur_publish_confs()
