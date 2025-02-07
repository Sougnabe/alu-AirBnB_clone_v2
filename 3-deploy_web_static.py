#!/usr/bin/python3
"""Fabric script to create and distribute an archive to web servers"""
from fabric.api import env, put, run, local
from datetime import datetime
from os.path import exists

# Define server details
env.hosts = ['54.242.200.31', '98.80.12.8']
env.user = "ubuntu"
env.key_filename = "~/.ssh/id_rsa"

def do_pack():
    """Generates a .tgz archive from the contents of the web_static folder."""
    try:
        local("mkdir -p versions")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        archive_path = "versions/web_static_{}.tgz".format(timestamp)
        local("tar -cvzf {} web_static".format(archive_path))
        return archive_path
    except Exception as e:
        return None

def do_deploy(archive_path):
    """Distributes an archive to the web servers."""
    if not exists(archive_path):
        return False
    try:
        file_name = archive_path.split("/")[-1]
        name = file_name.split(".")[0]
        path_name = "/data/web_static/releases/" + name
        put(archive_path, "/tmp/")
        run("mkdir -p {}/".format(path_name))
        run("tar -xzf /tmp/{} -C {}/".format(file_name, path_name))
        run("rm /tmp/{}".format(file_name))
        run("mv {}/web_static/* {}".format(path_name, path_name))
        run("rm -rf {}/web_static".format(path_name))
        run("rm -rf /data/web_static/current")
        run("ln -s {}/ /data/web_static/current".format(path_name))
        print("New version deployed!")
        return True
    except Exception:
        return False

def deploy():
    """Creates and distributes an archive to web servers."""
    archive_path = do_pack()
    if not archive_path:
        return False
    return do_deploy(archive_path)
