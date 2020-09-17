#!/usr/bin/env python3

from pmutils.repo_server import post_knowledge
from datetime import datetime
from datetime import date
from pathlib import Path
import subprocess
import argparse
import filecmp
import shutil
import os

parser = argparse.ArgumentParser()
parser.add_argument('--repo', default='/knowledge/sanctum-posts/knowledge_repo',
                    help='directory to populate notebooks')
args = parser.parse_args()
REPO = args.repo

# option -- have jenkins 
# 

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
    if project == 'stash':
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
        # with open(source_file, 'rb') as src:
        #    with open(mirror_file, 'wb+') as mir:
        #        mir.write(src.read())
        shutil.copy2(source_path, destination)
        return True

# comparable to update_repo()
def add_sanctum_post():
    # get files changed on last commit
    # only process files in the knowledge_repo directory that end with _kr.*
    commit_list = [c for c in subprocess.run('git diff-tree --no-commit-id --name-only -r head', capture_output=True
                                            ).stdout.decode('ascii').strip().split()
                            if c.startswith('knowledge_repo')
                            and '_kr.' in c]
   
    # end if list is empty
    if not commit_list:
        return

    for filename in commit_list:
        project = filename.split('/')[1]
        try:
            post_knowledge(filename=filename, project=project)
        except:
            #TODO: Exception handling
            print('Exception encountered while posting {filename} to repo/{project}'.format(filename=filename, project=project))
            continue


if __name__ == '__main__':
    add_sanctum_post()
