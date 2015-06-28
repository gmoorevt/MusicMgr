__author__ = 'gmoore'
import os
import sys
import fileutil
import cmd
from getfiles import FilesFinder



class FileMgr(cmd.Cmd):



    def do_greet(self,line):
        print "hello"

    def do_msg(self,line):
        print 'hello'

    def do_finddupes(self,line):
        print "path: %s" %path

    def do_findmusic(self,line):

        ff = FilesFinder()
        ff.findfiles(line)

       # FilesFinder.findfiles('/User/gmoore/')

    def do_EOF(self,line):
        return True



if __name__ == '__main__':

    FileMgr().cmdloop("Welcome to FileManager. Let's get started.")












#for x in sys.argv[1:]:
#  print 'Scanning directory "%s"...' % x

#fileutil.dirwalker(x)

#os.path.walk(x, fileutil.walker, filesBySize)

#print 'Finding potential dupes...'

#print fileutil.dupfinder(filesBySize)
