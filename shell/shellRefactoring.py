#!/usr/bin/python3

import os
import sys
import re


def execute(command):
    print('Command in execute before split ', command)
    command1 = command.split()
    print('Executed command ', command1)
    # Check if command[0] is itself a path
    if os.path.exists(command1[0]):
            os.execve(command1[0], command1, os.environ.copy())
    else:
        for directory in path:
            executable = directory + '/' + command1[0]
            if os.path.exists(executable):
                    os.execve(executable, command1, os.environ.copy())


def redirect(command):
    command1, output = command.split('>')
    output = output.strip()
    os.close(1)
    os.open(output, os.O_CREAT | os.O_WRONLY)
    os.set_inheritable(1, True)

    print('Command passed to execute. ', command1, file=sys.stderr)
    execute(command1)


def split(command, option=None):
    pid = os.fork()
    if pid == 0:
        if option is None:
            execute(command)
        if option == 'redirect':
            print('redirect')
            redirect(command)
    else:
        os.wait()


def initialize():
    try:
        sys.ps1
    except AttributeError:
        sys.ps1 = '$ '
    global path
    path = os.environ['PATH']
    path = path.split(':')


def shell():
    initialize()
    while True:
        command = input(sys.ps1)
        if command == '':
            continue
        if command == 'exit':
            sys.exit(1)
        if 'cd' in command:
            os.chdir(command.split()[1])
        if '>' in command:
            print('Redirection')
            split(command, option='redirect')
        split(command)

shell()
