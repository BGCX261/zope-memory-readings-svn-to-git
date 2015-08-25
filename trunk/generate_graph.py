import os
import datetime
import marshal



def generate(marshal_file):
    readings = marshal.load(open(marshal_file, 'rb'))
    
    html = open(os.path.join(os.path.dirname(__file__), 'template.html')).read()
    
    
    d = []
    first_timestamp = readings[0][2]
    last_timestamp = readings[-1][2]
    min_memory = None
    max_memory = 0
    
    for (method, uri), memory, timestamp in readings:
        timestamp = round(timestamp, 2)
        #timestamp = int(timestamp)
        d.append("[%s,%s,'%s']" % (timestamp, memory, uri))
        if min_memory is None:
            min_memory = memory
        elif memory < min_memory:
            min_memory = memory
            
        if memory > max_memory:
            max_memory = memory
    
    html = html.replace('{{max_value}}', str(max_memory))
    html = html.replace('{{min_value}}', str(min_memory))
    html = html.replace('{{data_array}}', '[%s]' % ', '.join([str(x) for x in d]))
    
    title = _generate_title(first_timestamp, last_timestamp)
    html = html.replace('{{title}}', title)
    
    save_dir = _title2foldername(title)
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)
    open(os.path.join(save_dir, 'index.html'),'w').write(html)
    
    report_file = os.path.join(save_dir, 'index.html')
    print report_file
    return report_file


def _generate_title(first_timestamp, last_timestamp):
    date = datetime.datetime.fromtimestamp(first_timestamp)
    title = date.strftime('%Y/%m/%d %H:%M:%S')
    seconds = last_timestamp - first_timestamp
    if seconds < 60:
        title += ' (%d seconds)' % seconds
    elif seconds < 60*60:
        title += ' (%.1f minutes)' % (seconds/60.0)
    elif seconds < 60*60*24:
        title += ' (%.1f hours)' % (seconds/60.0/60.0)
    else:
        title += ' (%.1f days)' % (seconds/60.0/60/24)
    
    return title
    
def _title2foldername(title):
    title = title.replace(':','.')
    title = title.replace('(',' ').replace(')','')
    title = title.replace(' ','_')
    title = title.replace('/','-')
    return title


if __name__=='__main__':
    import sys
    sys.exit(generate(sys.argv[1]))