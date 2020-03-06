#!/usr/bin/env python3

from pmutils.repo_server import post_knowledge
from pmutils import git
from datetime import datetime
from datetime import date
from pathlib import Path
import subprocess
import filecmp
import shutil
import time
import os



NOW = datetime.now()
WEEKDAY = date(NOW.year, NOW.month, NOW.day).weekday()
REPO = '/Users/posh/knowledge_repo/analytics/knowledge_repo'
BASE_DIR = '/Users/posh/knowledge_repo'
#TODO change above directory to whatever is needed for production



def sleep(t=5, simple=True):

    if simple:
        time.sleep(t)
        return

    # check for weekend
    if WEEKDAY < 5:
        if NOW.hour < 6 or NOW.hour > 22:
            time.sleep(3600)
        else:
            time.sleep(30)

    else:
        if NOW.hour < 6 or NOW.hour > 22:
            time.sleep(7200)
        else:
            time.sleep(1800)



# makes a directory and waits up to 10 seconds for it to exists
def create_project(path=None, wait=10):
    os.makedirs(path, exist_ok=True)
    loops = int(wait/0.1)
    for i in range(loops):
        time.sleep(0.1)
        if os.path.exists(path):
            break



# TODO: add option for reference path outside of cwd
# checks if files exist in mirror, if they do compares file for any differences in source
# returns true if missing or different, returns false if files are identical
def is_updated(project=None, filename=None, repo=None, ref='mirror', ref_path=None):
    if project=='stash':
        source_path = '/'.join([repo, filename])
    else:
        source_path = '/'.join([repo, project, filename])
    mirror_path = '/'.join([os.getcwd(), ref, project, filename])
    source_file, mirror_file = Path(source_path), Path(mirror_path)

    # copy file to the mirror if it doesn't exist.
    if mirror_file.exists() and mirror_file.is_file():
        return not filecmp.cmp(source_file, mirror_file, shallow=False)
    else:
        destination = '/'.join([os.getcwd(), ref, project])
        create_project(path=destination)
        #with open(source_file, 'rb') as src:
        #    with open(mirror_file, 'wb+') as mir:
        #        mir.write(src.read())
        shutil.copy2(source_path, destination)
        return True




def update_repo():

    # pull the latest commits. 
    previous_head = subprocess.run("git rev-parse head".split(),
                                  capture_output=True
                                 ).stdout.decode('ascii').strip()
    commits = git.pull()
    current_head = subprocess.run("git rev-parse head".split(),
                              capture_output=True
                             ).stdout.decode('ascii').strip()
    # get a list of all commits since last pull
    commit_list = subprocess.run(f'git rev-list --no-walk {current_head} ^{previous_head}'.split()
                                 ,capture_output=True
                                ).stdout.decode('ascii').strip().split()
    
    # Return if there are no new commits
    # can be changed to check if current_head = previous_head
    if commits.stdout.decode('ascii').startswith('Already up to date.'):
        return 
    

    # get files from all commits between previous head and current head
    cmds = [f'git show --commit_list-only --oneline HEAD~{commit}'.split()
            for commit in commit_list]

    os.chdir(BASE_DIR)
    CWD = os.getcwd()
    os.chdir(f'{CWD}/analytics')
    commits = [subprocess.run(cmd,
                                capture_output=True
                               ).stdout.decode('ascii')
                         for cmd in cmds]
    commits = '\n'.join(commits).split('\n')
    knowledge_posts = [c for c in commits
                       if c.startswith('knowledge_repo/')
                       and '_kr.' in c]
    os.chdir(CWD)

    if not knowledge_posts:
        print('Already up to date.')
        return

    # loop through knowledge_posts add them to the knowledge_repo
    # only add items that contain '_kr. in the filename'
    for notebook in knowledge_posts:
        project = notebook.split('/')[1]
        filename = CWD + '/analytics/' + notebook
        try:
            post_knowledge(filename=filename, project=project)
        except:
            #TODO: Exception handling
            print(f'Exception encountered while posting {filename} to repo/{project}')


if __name__ == '__main__':
    update_repo()