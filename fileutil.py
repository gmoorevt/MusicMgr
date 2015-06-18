__author__ = 'gmoore'
import stat
from hashlib import md5
import os
import sys
import shutil


class DupinatorError(Exception):pass
class DoseNotExistError(DupinatorError):pass

class FileBySizer(object):

    def __init__(self,basePath = os.getcwd(),skipList=['Thumbs','.DS_Store'],minBytes = 100):
        if not os.path.isdir(basePath):
            raise DoseNotExistError, "basePath %s does NOT exist" % basePath
        else:
            self.basePath = os.path.abspath(basePath)
        self.skipList = skipList
        self.minBytes = minBytes
        self.filesBySize = self.getFilesBySize()

    def __str__(self):
        c = self.__class__.__name__
        s = '\n%s (%d files)' % (c, len(self.filesBySize))
        s += "\n ... basePath = '%s'" % self.basePath
        s += "\n ... skipList = ["
        for i in self.skipList:
            s += " '%s'," % i
        if s[-1] == ',':
            s = s[0:-1]
        s += ' ]'
        return s

    def walker(self,arg,dirname,fnames):
        d = os.getcwd()
        os.chdir(dirname)
        try:
            #todo for robust handling of skiplist imput arg
            fnames = [name for name in fnames if name!=".DS_Store" and name!="Thumbs"]
        except ValueError:
            pass
        for f in fnames:
            if not os.path.isfile(f) or os.path.islink(f):
                continue
            size = os.stat(f)[stat.ST_SIZE]
            if size < self.minBytes:
                continue
            if self.filesBySize.has_key(size):
                a = self.filesBySize[size]
            else:
                a = []
                self.filesBySize[size] = a
            a.append(os.path.join(dirname,f))
        os.chdir(d)

    def getFilesBySize(self):
        self.filesBySize = {}
        for x in sys.argv[1:]:
            d = os.path.normpath(x)
            print "Scanning directory '%s'...." % d
            os.path.walk(d,self.walker,self.filesBySize)
        return  self.filesBySize



class PotentialDupeFinder(object):
    """ A class for finding potential Dupes based on looking at the the first 128 bytes of a file"""

    def __init__(self,fbs, requireEqualNames=False,firstScanBytes=8192):
        self.filesBySize = fbs.filesBySize
        self.requireEqualNames = requireEqualNames
        self.firstScanBytes = firstScanBytes
        self.dupes, self.potentialDupes, self.potentialCount = self.findPotentialDupes()

    def __str__(self):
        c = self.__class__.__name__
        s = '\n%s (%d files)' % (c, len(self.filesBySize))
        s += "\n ... basePath = '%s'" % self.basePath
        s += "\n ... skipList = ["
        for i in self.skipList:
            s += " '%s'," % i
        if s[-1] == ',':
            s = s[0:-1]
        s += ' ]'
        return s
    def findPotentialDupes(self):
        print 'Finding potential dupes...'
        dupes = []
        potentialDupes = []
        potentialCount = 0
        sizes = self.filesBySize.keys()
        sizes.sort()
        for k in sizes:
            inFiles = self.filesBySize[k]
            hashes = {}
            if len(inFiles) is 1: continue
            print 'Testing %d files of size %d...' %(len(inFiles),k)
            if self.requireEqualNames:
                for fileName in inFiles:
                    hashes.setdefault(os.path.basename(fileName),[]).append(fileName)
                inFiles = []
                for nameGroup in hashes.values():
                    if len(nameGroup)>1:
                        inFiles.extend(nameGroup)
                hashes = {}
            for fileName in inFiles:
                if not os.path.isfile(fileName):
                    continue
                aFile = file(fileName, 'r')
                hasher = md5()
                hasher.update(aFile.read(self.firstScanBytes))
                hashValue = hasher.hexdigest()
                if hashes.has_key(hashValue):
                    hashes[hashValue].append(fileName)
                else:
                    hashes[hashValue] = [fileName]
                aFile.close()
            outFileGroups = [fileGroup for fileGroup in hashes.values()if len(fileGroup)>1]
            if k <= self.firstScanBytes:
                dupes.extend(outFileGroups)
            else:
                potentialDupes.extend(outFileGroups)
            potentialCount = potentialCount + len(outFileGroups)

        print 'Found %d sets of potential dupes...' % potentialCount
        return dupes, potentialDupes, potentialCount


class RealDupeFinder(object):
    def __init__(self,potDupeFinder):
        self.dupes = potDupeFinder.dupes
        self.potentialDupes = potDupeFinder.potentialDupes
        self.getRealDupes()

    def __str__(self):
        c = self.__class__.__name__
        s = '\n%s (%d files)' % (c, len(self.filesBySize))
        s += "\n ... basePath = '%s'" % self.basePath
        s += "\n ... skipList = ["
        for i in self.skipList:
            s += " '%s'," % i
        if s[-1] == ',':
            s = s[0:-1]
        s += ' ]'
        return s

    def getRealDupes(self):
        print 'Scanning for real dupes...'
        for aSet in self.potentialDupes:
            hashes = {}
            for fileName in aSet:
                print 'Scanning file "%s"...'  %fileName
                aFile = file(fileName,'r')
                hasher = md5()
                while True:
                    r = aFile.read()
                    if not len(r):
                        break
                    try:
                        hasher.update(r)
                    except Exception as e:
                        print e

                aFile.close()
                hashValue = hasher.hexdigest()
                if hashes.has_key(hashValue):
                    hashes[hashValue].append(fileName)
                else:
                    hashes[hashValue] = [fileName]
            outFileGroups = [fileGroup for fileGroup in hashes.values() if len(fileGroup)>1]
            self.dupes.extend(outFileGroups)

class DupeHandler(object):
    def __init__(self,dupes,result='list'):
        """
        This function accepts a list of files and moved
        :param dupes: A list of files that will be removed
        :param result: 'list' lists all files | 'move' Moves files to an output directory | 'delete' deletes files
        """
        self.dupes = dupes
        self.result = result
        self.handleDupes()

    def __str__(self):
        c = self.__class__.__name__
        s = '\n%s (%d files)' % (c, len(self.filesBySize))
        s += "\n ... basePath = '%s'" % self.basePath
        s += "\n ... skipList = ["
        for i in self.skipList:
            s += " '%s'," % i
        if s[-1] == ',':
            s = s[0:-1]
        s += ' ]'
        return s
    def handleDupes(self):
        #ToDo Give option to delete, move or list files
        i = 0
        bytesSaved = 0
        for d in self.dupes:
            print '## "%s"' % d
            for f in d[1:]:
                i = i +1
                bytesSaved += os.path.getsize(f)
                print "deleting %s" % f
                if self.result =='move':
                    dupedir = os.path.join(os.curdir,'dupes')
                    if not os.path.exists(dupedir):
                        os.makedirs(os.path.join(os.curdir,'dupes'))
                    fn = os.path.basename(f)
                    if os.path.exists(os.path.join(dupedir,fn)):
                        fi = 1
                        while os.path.exists(os.path.join(dupedir,fn)):
                            fi = fi +1
                            fn = "%s [%d]" % (fn,fi)
                            print fn

                    shutil.move(f,os.path.join(dupedir,fn) )

                if self.result == 'delete':
                    pass

                #os.remove(f)
            print
        print "We would have saved %.1fm: %d file(s) duplicated." % (bytesSaved/1024.0/1024.0,len(self.dupes))

class Dupinator(object):
    """Dupinator class to serve as base for file duplication utilities"""

    def __init__(self, basePath=os.getcwd(), skipList=['Thumbs','.DS_Store'],minbytes=100,reslut='list'):
        fileBySizeObj = FileBySizer(basePath = basePath,skipList=skipList,minBytes=minbytes)
        potentialDupeObj = PotentialDupeFinder(fileBySizeObj)
        realDupeObj = RealDupeFinder(potentialDupeObj)
        self.dupes = realDupeObj.dupes
        DupeHandler(self.dupes,reslut)

    def __str__(self):
        c = self.__class__.__name__
        s = '\n%s (%d files)' % (c, len())
        s += "\n ... basePath = '%s'" % self.basePath
        s += "\n ... skipList = ["
        for i in self.skipList:
            s += " '%s'," % i
        if s[-1] == ',':
            s = s[0:-1]
        s += ' ]'
        return s

if __name__ == '__main__':
    basePath = sys.argv[1]
    Dupinator(basePath=basePath)
    sys.exit(0)

    

