__author__ = 'gmoore'
import os
import sys
import fileutil






#for x in sys.argv[1:]:
#  print 'Scanning directory "%s"...' % x

#fileutil.dirwalker(x)

#os.path.walk(x, fileutil.walker, filesBySize)

print 'Finding potential dupes...'

#print fileutil.dupfinder(filesBySize)

fileutil.Dupinator('/Users/gmoore/test',reslut='move')