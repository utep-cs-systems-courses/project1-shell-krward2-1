#!/usr/bin/python3

import os
import sys
import re


def execute(command):
    cmd = command.split()
    #print('PID: ', os.getpid(), 'about to execute: ', cmd)
    # Check if command[0] is itself a path
    if os.path.exists(cmd[0]):
        os.execve(cmd[0], cmd, os.environ.copy())
    else:
        for directory in path:
            executable = directory + '/' + cmd[0]
            if os.path.exists(executable):
                os.execve(executable, cmd, os.environ.copy())


def redirect(input):
    cmd, output = input.split('>')
    output = output.strip()
    os.close(1)
    os.open(output, os.O_CREAT | os.O_WRONLY)
    os.set_inheritable(1, True)

    #print('')
    execute(cmd)

#TODO: There might be some unnecessary inheritances being made. Try to clean up.
def pipe(command_set, type='write', file_descriptor=None):
    if type == 'write':
        #print('Child 1: Creating read and write ends')
        cmd, cmd2 = command_set.split('|')
        read_pipe, write_pipe = os.pipe()
        for fd in (read_pipe, write_pipe):
            os.set_inheritable(fd, True)
        #print('Child 1: Pipes created. Forking new process to run second process connected to read end.')
        fork_new_process(cmd2, option='pipe_complete', file_descriptors=read_pipe)

        #print('Child 1: Setting stdout to write_pipe')
        os.close(1)
        os.dup(write_pipe)
        os.set_inheritable(1, True)

        #print('Child 1: Executing command', file=sys.stderr)
        execute(cmd)
    if type == 'read' and file_descriptor:

        #print('Child 2: Set stdin to read_pipe (file_descriptor)', file=sys.stderr)
        os.set_inheritable(file_descriptor, True)
        os.close(0)
        os.dup(file_descriptor)
        os.set_inheritable(0, True)
        #print('Child 2: Executing command', file=sys.stderr)
        execute(command_set)


def fork_new_process(input, option=None, file_descriptors=None):
    pid = os.fork()
    if pid == 0:
        if option is None or option == 'run_in_background':
            #print('PID: ', os.getpid(), ' option=none')
            execute(input.strip('&').strip())
        if option == 'redirect':
            #print('PID: ', os.getpid(), ' option=redirect')
            redirect(input)
        if option == 'pipe_begin':
            #print('PID: ', os.getpid(), ' option=pipe_begin')
            pipe(input)
        if option == 'pipe_complete' and file_descriptors:
            #print('PID: ', os.getpid(), ' option=pipe_complete')
            pipe(input, type='read', file_descriptor=file_descriptors)
    if pid != 0 and option != 'pipe_complete' and option != 'run_in_background':
        #print('PID: ', os.getpid(), ' Parent waiting.')
        os.wait()


def initialize():
    try:
        sys.ps1
    except AttributeError:
        sys.ps1 = '$ '
    global path
    path = os.environ['PATH'].split(':')


def getLine():
    input = os.read(0, 1024)
    if input == b'':
        sys.exit(1)
    else:
        return input.decode().strip()


def shell():
    initialize()
    count = 0
    while True:
        if os.isatty(0):
            os.write(1, sys.ps1.encode())
        count += 1
        #print('PID: ', os.getpid(), ' shell cycle ', count)
        user_input = getLine()
        #print(user_input)
        if user_input == '':
            continue
        elif user_input == 'exit':
            sys.exit(1)
        elif 'cd' in user_input:
            os.chdir(user_input.split()[1])
        elif '>' in user_input:
            #print('Redirection')
            fork_new_process(user_input, option='redirect')
        elif '|' in user_input:
            fork_new_process(user_input, option='pipe_begin')
        elif '&' in user_input:
            fork_new_process(user_input, option='run_in_background')
        else:
            fork_new_process(user_input)


shell()
