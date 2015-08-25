#!/usr/bin/python

import os, sys
from path import path

WHERE_IS = os.path.dirname(__file__)
                                     


def rmEmptyFolders(home):
    dels = []
    for d in path.walkdirs(path(home)):
        ending = d.split()[-1]
        if not d.listdir():
            print " * rmdir %s *"%d
            dels.append(d)#d.rmdir()
            
    for e in dels:
        e.rmdir()
            

here_is = os.path.abspath('.')

WHERE_IS = os.path.abspath(os.path.expanduser(WHERE_IS))
#foldername = WHERE_IS.split(os.sep)[-1]
foldername = os.path.basename(WHERE_IS)

# 1. Prepare a destination
if sys.argv[1:]:
    if sys.argv[1]=='.':
        raise "InvalidDestination", "Can't deploy right here"
    destin = os.path.abspath(sys.argv[1])
else:
    print "Put result into ~/tmp"
    destin = os.path.join('~', 'tmp')
    destin = os.path.expanduser(destin)
if not os.path.isdir(destin):
    os.mkdir(destin); print
        
# 2. Make a copy of the CVS one
cmd = 'cp -R %s %s/'%(WHERE_IS, destin)
os.popen4(cmd)[1].read(); print cmd

# 3. Enter it
folderpath = os.path.join(destin, foldername)
os.chdir(folderpath); print "Move to %s"%folderpath

# 4. Remove junk
_home = path(folderpath)
for each in ('*~','*.pyc','*.old','*.bak','.#*','Smurler*.tgz', os.path.basename(__file__)):
    for f in _home.walkfiles(each):
        print " * delete %s *"%f
        
        f.remove()

        
for d in list(_home.walkdirs('.svn')):
    os.system("rm -fr %s" % d)
#

    

# 5. Remove empty folders
rmEmptyFolders(folderpath)

# 5. Find out the version number
version = ''
if os.path.isfile('version.txt'):
    version = open('version.txt').read().strip()
if not version:
    version = raw_input('Version: ')

# 6. Move up one step
os.chdir('../'); print 'cd ../' # we're now in ~/tmp

# 7. Zip it
zipname = '%s-%s.tgz'%(foldername, version)
cmd = 'tar zcf %s %s'%(zipname, foldername); print cmd
os.popen4(cmd)[1].read()

# 8. Move it back to where we start from
#cmd = 'mv %s %s'%(zipname, here_is); print cmd
#os.popen4(cmd)[1].read()

# 9. Move README.txt and CHANGES.txt to destin
#cmds = []
#doc_moves = []
#for each in ('README.txt','CHANGES.txt'):
#    if each in os.listdir(foldername):
#        doc_moves.append('Copied %s to %s'%(each, os.path.abspath('.')))
#        cmds.append('mv %s %s'%(os.path.join(foldername, each), destin)); 
#        print cmd
#cmd = ';'.join(cmds)
#if cmd:
#    os.popen4(cmd)[1].read()

    
# 10. Remove the folder in ~/tmp
cmd = 'rm -fr %s'%foldername
os.popen4(cmd)[1].read(); print cmd

# 11. Move the zipped file to the destin
cmd = 'mv %s %s'%(zipname, destin)
print os.popen4(cmd)[1].read(); print cmd

print
#if doc_moves:
#    print "\n".join(doc_moves)
print "Generated %s in %s"%(zipname, destin)