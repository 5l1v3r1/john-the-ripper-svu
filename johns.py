#!/usr/bin/python

# TODO:
#   * allow the user to specify the location of john

import fileinput
import os
import subprocess
import time
import shlex
import signal


# Run john-the-ripper in child process, then terminate child
def thread(pw,user_count):
    john_path = '/home/jdellaire/john-the-ripper%d/run/john' %user_count
    file_name = '/tmp/pw%d' % user_count
    process_name = shlex.split(john_path + ' ' + file_name)
    new_file = open(file_name, 'w')
    new_file.write('user%d' % user_count + ":" + pw)
    new_file.close()
    proc = subprocess.Popen(process_name)
    tpid = os.fork()
    # Child process
    if tpid == 0:
        time = timer(proc.pid)
        print "Total time for %d is %d" %(proc.pid,time)
        os._exit(0)
    # Parent process
    else:
        # Use the following to terminate subprocess
        #print "proc.pid = %s" %proc.pid
        #os.kill(proc.pid,signal.SIGKILL)
        proc.wait()
        os.remove(file_name)
        os._exit(0)

# Test if child process is still active - pid array input
def check_multi_pid(pid_arr,thread_count):
    for pid in pid_arr:
        try:
            os.waitpid(int(pid),os.WNOHANG)
        except OSError:
            if thread_count > 0:
                thread_count -= 1
            pid_arr.remove(pid)
    return thread_count, pid_arr

# Test if child process is still active - single pid input
def check_single_pid(pid):
    try:
        os.kill(pid,0)
    except OSError:
        return False
    else:
        return True

# Timer function
def timer(pid):
    start_time = time.time()
    while check_single_pid(pid):
        pass
    end_time = time.time()

    return (end_time - start_time)


# Main function
def main():
    # Main variables
    data = {}
    max_thread = 8
    thread_count = 0
    user_count = 0
    pid_arr = []


    # Build dictionary of passwords and users
    for line in fileinput.input():
        line = line.rstrip(os.linesep)
        username, password = line.split(':')
        if password not in data.keys():
            data[password] = {'usernames': []}
        data[password]['usernames'].append(username)

    pw_count = len(data)

    # Create up to max_thread processes
    while (user_count < pw_count):
        if thread_count < max_thread:
            thread_count += 1
            user_count += 1
            pid = os.fork()
            if pid >= 0:
                # Child process
                if pid == 0:
                    thread(data.keys()[user_count-1],user_count)
                # Parent process
                else:
                    pid_arr.append(pid)
            else:
                thread_count -= 1
                user_count -= 1
        elif thread_count == max_thread:
            thread_count, pid_arr = check_multi_pid(pid_arr,thread_count)

    while pid_arr:
        thread_count, pid_arr = check_multi_pid(pid_arr,thread_count)


if __name__ == "__main__":
    main()

