import time, os, re
import marshal


from generate_graph import generate

vmsize_regex = re.compile('VmSize:\s+(\d+)')
def get_mem_size(pid):
    out = open('/proc/%s/status' % pid).read()
    return vmsize_regex.findall(out)[0]

url_regex = re.compile(r'"(GET|POST) (.*?) HTTP', re.DOTALL)
def get_url(logline):
    try:
        return url_regex.findall(logline)[0]
    except IndexError:
        return repr(logline)

#Set the filename and open the file

#Find the size of the file and move to the end
def get_readings(filename, pid, long_term=False):
    """
    return a generator of tuples that look like this:
    (('GET','/some/url'), 10000, 112356792.23656)
    
    If @long_term only yield readings of the memory changes
    """
    file = open(filename,'r')
    st_results = os.stat(filename)
    st_size = st_results[6]
    file.seek(st_size)
    
    prev_timestamp = 0
    prev_memory = 0
    
    while 1:
        where = file.tell()
        line = file.readline()
        if not line:
            time.sleep(1)
            file.seek(where)
        else:
            timestamp = round(time.time(), 2)
            if timestamp > prev_timestamp:
                prev_timestamp = timestamp
                mem = int(get_mem_size(pid))
                if mem != prev_memory:
                    prev_memory = mem
                    yield get_url(line), mem, timestamp
                
    

def start(zope_home, long_term=False, quiet=False):
    
    filename = os.path.join(zope_home, 'log/Z2.log')
    pid_filename = os.path.join(zope_home, 'var/Z2.pid')
    dump_file = '/tmp/zope-memory-readings.dat'


    pid = open(pid_filename).read()
    pid = int(pid)
    if not quiet:
        print "PID", pid
        if long_term:
            print "Running long term"

        print "Hit Ctrl-C when you want to stop recording"
        print "Recording..."
    
    readings = []
    prev = None
    try:
        for reading in get_readings(filename, pid, long_term=long_term):
            if not quiet:
                print reading[1],
                if prev is not None:
                    if reading[1] > prev:
                        print "+%d" % (reading[1]-prev)
                    elif reading[1] < prev:
                        print "%d" % (reading[1]-prev)
                    else:
                        print 
                    
            readings.append(reading)
            prev = reading[1]
    except KeyboardInterrupt:
        marshal.dump(readings, open(dump_file, 'wb'))
        if not quiet:
            print "Generating graphs..."
        generate(dump_file)
        
#        
#def run(*args):
#    if not args:
#        print "Usage: python %s /directory/of/zope" % __file__
#        return 1
#    zope_home = args[0]
#    if not os.path.isdir(zope_home):
#        print "%s not a directory" % zope_home
#        print "Usage: python %s /directory/of/zope" % __file__
#        return 2
#    
#    if not os.path.isfile(os.path.join(zope_home, 'log/Z2.log')):
#        print "%s does not have a 'log/Z2.log' file" % zope_home
#        print "Usage: python %s /directory/of/zope" % __file__
#        return 3
#    
#    if not os.path.isfile(os.path.join(zope_home, 'var/Z2.pid')):
#        print "%s does not have a 'var/Z2.pid' file" % zope_home
#        print "Is the Zope running?"
#        print "Usage: python %s /directory/of/zope" % __file__
#        return 4
#    
#    start(zope_home)
#    return 0
#
#if __name__=='__main__':
#    import sys
#    sys.exit(run(*sys.argv[1:]))



#### The command line handler ##################################################

import CommandLineApp

class get_readings_app(CommandLineApp.CommandLineApp):
    """ measure the memory of a Zope and record what URLs each memory change
    corresponds to.
    """
    
    def showVerboseHelp(self):
        CommandLineApp.CommandLineApp.showVerboseHelp(self)

    long_term = False
    def optionHandler_long_term(self):
        """ only record times when the memory usage changes """
        self.long_term = True
        return
    optionHandler_L = optionHandler_long_term

    def main(self, zope_home):
        """ Start! """
        if not os.path.isdir(zope_home):
            print "%s not a directory" % zope_home
            print "Usage: python %s /directory/of/zope" % __file__
            return 2
    
        if not os.path.isfile(os.path.join(zope_home, 'log/Z2.log')):
            print "%s does not have a 'log/Z2.log' file" % zope_home
            print "Usage: python %s /directory/of/zope" % __file__
            return 3
        
        if not os.path.isfile(os.path.join(zope_home, 'var/Z2.pid')):
            print "%s does not have a 'var/Z2.pid' file" % zope_home
            print "Is the Zope running?"
            print "Usage: python %s /directory/of/zope" % __file__
            return 4
        
        start(zope_home, long_term=self.long_term, quiet=self.verbose_level==0)
        
        
if __name__=='__main__':
    get_readings_app().run()
        
    

