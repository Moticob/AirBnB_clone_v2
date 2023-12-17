#!/usr/bin/python3
"""
Generate .tgz files
"""
from os import path
from datetime import datetime as dt
from fabric.api import local, put, run, env
from fabric.context_managers import lcd


env.user = "ubuntu"
env.hosts = ["18.210.28.31", "3.236.121.230"]


def do_pack():
    """ generate .tgz file"""
    archived = dt.utcnow()
    if not path.isdir("versions"):
        if local("mkdir -p versions").failed:
            return None
    p = "versions/web_static_{}{}{}{}{}{}.tgz".format(
        archived.year, archived.month, archived.day,
        archived.hour, archived.minute, archived.second)
    if local("tar -cvzf {} web_static/".format(p)).failed:
        return None
    return p


def do_deploy(archive_path):
    """ Deploy files to servers"""
    print(archive_path)
    if not path.isfile(archive_path):
        return False
    result = put(archive_path, "/tmp/{}".format(archive_path.split("/")[1]))
    if result.failed:
        return False
    extract_path = archive_path.split("/")[1].split(".")[0]
    if run("rm -rf /data/web_static/releases/{}/".format(extract_path)).failed:
        return False
    if run("mkdir -p /data/web_static/releases/{}".format(extract_path)).failed:
        return False
    if run("tar -xzf /tmp/{} -C /data/web_static/releases/{}".format(
            archive_path.split("/")[1], extract_path)).failed:
        return False
    if run("rm -rf /tmp/{}".format(archive_path.split("/")[1])).failed:
        return False
    part1 = "mv /data/web_static/releases/{}/web_static/*".format(extract_path)
    part2 = "/data/web_static/releases/{}/".format(extract_path)
    mv = "{} {}".format(part1, part2)
    if run(mv).failed:
        return False
    if run("rm -rf /data/web_static/current").failed:
        return False
    if run("ln -sf /data/web_static/releases/{}/ /data/web_static/current".format(extract_path)).failed:
        return False
    
    # Additional step to check if the HTML file is available
    check_html = run("curl -s -o /dev/null -w \"%{{http_code}}\" http://{}{}".format(env.hosts[0], '/hbnb_static/0-index.html'))
    return check_html == "200"

