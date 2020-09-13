#!/usr/bin/python3

import os
import sys
import re


try:
    sys.ps1
except AttributeError:
    sys.ps1 = '$ '
path = os.environ['PATH']
path = path.split(':')

while True:
    command = input(sys.ps1)
    if command == '':
        continue
    if command == 'exit':
        sys.exit()
    if '>' in command:
        command, output = command.split('>')
        command = command.split()
        output = output.strip()
        pid = os.fork()

        if pid == 0:
            os.close(1)
            os.open(output, os.O_CREAT | os.O_WRONLY)
            os.set_inheritable(1, True)
            if os.path.exists(command[0]):
                os.execve(command[0], command, os.environ.copy())
            else:
                for directory in path:
                    executable = directory + '/' + command[0]
                    if os.path.exists(executable):
                        os.execve(executable, command, os.environ.copy())
                sys.exit()
        else:
            os.wait()

        continue

    if '|' in command:
        command, command2 = command.split('|')
        command = command.split()
        command2 = command2.split()

        r, w = os.pipe()
        for f in (r, w):
            os.set_inheritable(f, True)

        pid = os.fork()
        if pid == 0:
            os.close(1)
            os.dup(w)
            for fd in (w, r):
               os.close(fd)
            if os.path.exists(command[0]):
                print('About to run cat ', os.fstat(1), file=sys.stderr) ######
                os.execve(command[0], command, os.environ)
            else:
                for directory in path:
                    executable = directory + '/' + command[0]
                    if os.path.exists(executable):
                        print('About to run cat ', os.fstat(1), file=sys.stderr) #####
                        os.execve(executable, command, os.environ)
                print('Command not found')
                sys.exit()
        else:
            print('forking 2nd process')
            pid = os.fork()
            if pid == 0:
                os.close(0)
                os.dup(r)
                for fd in (w, r):
                    os.close(fd)
                if os.path.exists(command2[0]):
                    print('About to run grep ', os.fstat(0)) #######
                    os.execve(command2[0], command2, os.environ)
                else:
                    for directory in path:
                        executable = directory + '/' + command2[0]
                        if os.path.exists(executable):
                            print('About to run grep ', os.fstat(0)) ######
                            os.execve(executable, command2, os.environ)
                    print('Command not found')
                    sys.exit()
            else:
                print('Shell waiting')
                os.wait()
        continue

    command = command.split()
    if command[0] == 'cd':
        os.chdir(command[1])
        continue

    # Check if command[0] is itself a path
    if os.path.exists(command[0]):
        pid = os.fork()
        if pid == 0:
            os.execve(command[0], command, os.environ.copy())
        else:
            os.wait()
    else:
        for directory in path:
            executable = directory + '/' + command[0]
            if os.path.exists(executable):
                pid = os.fork()
                if pid == 0:
                    os.execve(executable, command, os.environ.copy())
                else:
                    os.wait()


