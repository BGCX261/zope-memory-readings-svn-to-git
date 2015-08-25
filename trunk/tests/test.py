import marshal
import os
from random import randint
from nose.tools import raises, with_setup

import sys
sys.path.insert(0, '..')
from generate_graph import _generate_title, _title2foldername, generate


def test_generate_title():
    timestamp1 = 1212143496
    timestamp2 = timestamp1 + 5000
    result = _generate_title(timestamp1, timestamp2)
    assert result == '2008/05/30 11:31:36 (1.4 hours)'
    
    timestamp2 = timestamp1 + 10
    result = _generate_title(timestamp1, timestamp2)
    assert result == '2008/05/30 11:31:36 (10 seconds)'
    
    timestamp2 = timestamp1 + 60 * 2
    result = _generate_title(timestamp1, timestamp2)
    assert result == '2008/05/30 11:31:36 (2.0 minutes)'
    
    timestamp2 = timestamp1 + 60 * 2 + 30
    result = _generate_title(timestamp1, timestamp2)
    assert result == '2008/05/30 11:31:36 (2.5 minutes)'
    
    timestamp2 = timestamp1 + 3600 * 26
    result = _generate_title(timestamp1, timestamp2)
    assert result == '2008/05/30 11:31:36 (1.1 days)', result
    
    
def test_title2foldername():
    title = '2008/05/30 11:31:36 (1.4 hours)'
    result = _title2foldername(title)
    assert result == '2008-05-30_11.31.36__1.4_hours', result
    
    title = '2008/05/30 11:31:36 (10 seconds)'
    result = _title2foldername(title)
    assert result == '2008-05-30_11.31.36__10_seconds', result
    
    title = '2008/05/30 11:31:36 (2.0 minutes)'
    result = _title2foldername(title)
    assert result == '2008-05-30_11.31.36__2.0_minutes', result
    
    
    
def _before_generate():
    data = []
    t0 = 1212143496
    for i in range(11):
        t = t0 + i
        url = '/some/url/%s' % i
        method = 'GET'
        memory = 10000 + randint(1, 1000) - randint(1, 100)
        data.append(((method, url), memory, t))
        
    marshal.dump(data, open('fake.marshal','w'))
        
    
def _after_generate():
    if os.path.isfile('fake.marshal'):
        os.remove('fake.marshal')
        
    if os.path.isdir('2008-05-30_11.31.36__10_seconds'):
        os.remove(os.path.join('2008-05-30_11.31.36__10_seconds','index.html'))
        os.rmdir('2008-05-30_11.31.36__10_seconds')
        
    
@with_setup(_before_generate, _after_generate)
def test_generate():
    generate('fake.marshal')
    # this should have created a directory called '2008-05-30_11.31.36__9_seconds'
    # because the _before_generate() starts on 1212143496 and does a loop for 11
    # revs which would mean the test lasts for 10 seconds.
    expect_title = _generate_title(1212143496, 1212143496+ 10)
    #print expect_title
    
    expect_foldername = _title2foldername(expect_title)
    
    assert expect_foldername in os.listdir('.'), "didn't create folder %r"% expect_foldername
    
    assert os.path.isfile(os.path.join(expect_foldername, 'index.html'))
    report = open(os.path.join(expect_foldername, 'index.html')).read()
    
    assert expect_title in report, "couldn't find expected title"
    
    
    