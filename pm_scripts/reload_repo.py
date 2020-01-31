from pmutils.repo_server import post_knowledge
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



def sleep(t=None):
    if t:
        sleep(t)
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
    for item in os.walk(REPO):
        if item[0].endswith('.ipynb_checkpoints')\
        or len(item[2]) < 1:
            continue

        for notebook in item[2]:
            if  '_kr.' not in notebook:
                continue

            if item[0] == REPO:
                project = 'stash'
            else:
                project = item[0].split('/')[-1]

            filename = item[0] + '/' + notebook

            post_knowledge(filename=filename, project=project)


while True:
    update_repo()
    break#sleep(t=1800)
