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
    command = command.split()

    # Check if command[0] is itself a path
    if os.path.exists(command[0]):
        os.execve(command[0], command, os.environ.copy())
    else:
        for directory in path:
            executable = directory + '/' + command[0]
            if os.path.exists(executable):
                pid = os.fork()
                if pid == 0:
                    os.execve(executable, command, os.environ.copy())
                else:
                    os.wait()


