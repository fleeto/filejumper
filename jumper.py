#!/usr/bin/python
import sys
import os
import jumper.host
import jumper.task
import time


def check_dir(working_directory):
    if not os.path.exists(working_directory):
        os.makedirs(working_directory)
    if (os.path.exists(working_directory)) and (os.path.isdir(working_directory)):
        path_list = ['data', 'task', 'result']
        for element in path_list:
            current_path = os.path.join(working_directory, element)
            if not os.path.exists(current_path):
                os.makedirs(os.path.join(working_directory, element))
        return True
    return False

if len(sys.argv) != 3:
    print "Usage: %s [machine id] [jumper dir]" % sys.argv[0]
    exit(1)

host = sys.argv[1]
path = sys.argv[2]
sleep_interval = 10


if check_dir(path):
    print "Entering working directory"
else:
    print "Can't access working directory."
    exit(1)


while True:
    task_util = jumper.task.Task(path, host)
    new_task = task_util.find_task_by_status("new")

    for task in new_task:
        task.execute()

    # update task remote status

    running_task = task_util.find_task_by_status("running")

    for task in running_task:
        print "Updating task status %s" % task.file
        task.update_task()

    time.sleep(sleep_interval)