__author__ = 'gmoore'
import os
import shutil
import sys
import fnmatch

class FilesFinder(object):

    def __init__(self):
        self.musicfiles = ['*.mp3','*.3pq','*.act','*.aiff','*.aac','*.m4a','*.m4p','*.mmf','*.mpc','*.ogg','*.oga','*.ra',
                  '*.rm','*.raw','*.vox','*.wav','*.wma','*.wv','*.webm','*.ape']
        self.musiclist = []
        self.filecount = 0

    def walker(self,arg,dirname,fnames):
        d = os.getcwd()
        os.chdir(dirname)

        for ext in self.musicfiles:
            for fname in fnmatch.filter(fnames,ext):
                self.musicfiles.append(os.path.join(dirname,fname))
                self.filecount + 1
                print fname
        os.chdir(d)

    def findfiles(self,root):
        print "finding music"
        for dirName, subdirList, fileList in os.walk(root):
            for ext in self.musicfiles:
                for fname in fnmatch.filter(fileList,ext):
                    print fname
                    self.filecount = self.filecount +1
                    self.musiclist.append(os.path.join(dirName,fname))

        print "%i Music files found" % self.filecount
        print self.filecount
        return self.musiclist

