# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 09:29:09 2017

@author: yiyuezhuo
"""

import difflib
import json
import random
import time
import argparse

def test(s1,s2):
    # https://pymotw.com/3/difflib/index.html
    
    s1 = s1.copy()
    s2 = s2.copy()

    print('Initial data:')
    print('s1 =', s1)
    print('s2 =', s2)
    print('s1 == s2:', s1==s2)
    print('\n')
    
    matcher = difflib.SequenceMatcher(None, s1, s2)
    for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
    
        if tag == 'delete':
            print('Remove %s from positions [%d:%d]' % (s1[i1:i2], i1, i2))
            del s1[i1:i2]
    
        elif tag == 'equal':
            print('The sections [%d:%d] of s1 and [%d:%d] of s2 are the same' % \
                (i1, i2, j1, j2))
    
        elif tag == 'insert':
            print('Insert %s from [%d:%d] of s2 into s1 at %d' % \
                (s2[j1:j2], j1, j2, i1))
            s1[i1:i2] = s2[j1:j2]
    
        elif tag == 'replace':
            print('Replace %s from [%d:%d] of s1 with %s from [%d:%d] of s2' % (
                s1[i1:i2], i1, i2, s2[j1:j2], j1, j2))
            s1[i1:i2] = s2[j1:j2]
    
        print('s1 =', s1)
        print('s2 =', s2)
        print('\n')
    
    print('s1 == s2:', s1==s2)


def diff(A, B, raw = False):
    d = difflib.Differ()
    r = d.compare([A], [B]) # d.compare receive string list. In this, A,B are strings.
    if raw:
        return list(r)
    return '\n'.join(r)
    
def diff2(s1, s2):
    # It include inplace modify.
    
    #s1 = [w.strip() for w in A.split(' ') if len(w.strip())>0]
    #s2 = [w.strip() for w in B.split(' ') if len(w.strip())>0]
    
    matcher = difflib.SequenceMatcher(None, s1, s2)
    #ratio = matcher.ratio()
    
    rl = []
    for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
        #print(tag, i1, i2, j1, j2)
        if tag == 'delete':
            rl = ['[-'] + s1[i1:i2] + ['-]'] + rl
            del s1[i1:i2]
        elif tag == 'equal':
            rl = s1[i1:i2] + rl
        elif tag == 'insert':
            rl =  ['[+'] + s2[j1:j2] + ['+]'] + rl
            s1[i1:i2] = s2[j1:j2]
        elif tag == 'replace':
            rl = ['['] + s1[i1:i2] + ['->'] + s2[j1:j2] + [']'] + rl
            s1[i1:i2] = s2[j1:j2]
    return rl
    
def diff3(s1, s2):
    # s1, s2 are string.
    # return opt string such that s1 like s2
    # diff3('I am man, you idiot.','I am woman, you fool.')
    # ->
    # 'I am [ man, -> woman, ] you [ idiot. -> fool. ]'
    s1 = [w.strip() for w in s1.split(' ') if len(w.strip())>0]
    s2 = [w.strip() for w in s2.split(' ') if len(w.strip())>0]
    
    return ' '.join(diff2(s1,s2))

    
    
    
    
class DataBase(object):
    def __init__(self, bind_path = 'db.json'):
        self.bind_path = bind_path
        self.data = {'learner':'yiyuezhuo',
                     'time':time.ctime(),
                     'content':[]}
        self.point = None
    def load(self):
        with open(self.bind_path, encoding='utf8') as f:
            self.data = json.load(f)
    def dump(self):
        self.data['time'] = time.ctime()
        with open(self.bind_path, 'w', encoding='utf8') as f:
            json.dump(self.data, f)
    def sample(self):
        self.point = random.choice(range(len(self.data['content'])))
        return self.data['content'][self.point]
    def write(self, english, chinese):
        self.data['content'].append([english, chinese])
        self.point = len(self.data['content']) - 1
    def move(self, point):
        self.point = point
    def remove(self, point = None):
        point = point if point is not None else self.point
        del self.data['content'][point]
        self.point = None
    def get_name(self):
        return self.data['learner']
    def get_time(self):
        return self.data['time']
        
class Interface(object):
    def __init__(self, db):
        self.db = db
        self.command_stack = []
    def start(self):
        name = self.db.get_name()
        last_time = self.db.get_time()
        print('Hello {name}, welcome start a new course.'.format(name = name))
        print('Now is {now_time}, last course is in {last_time}'.format(now_time = time.ctime(),
                                                                   last_time = last_time))
        self.event_loop()
    def get_command(self):
        inp = input(':')
        self.command_stack.append(inp)
    def run_command(self, command):
        if command in ('e', 'exit'):
            self.db.dump()
            exit()
        elif command in ('c', 'commit'):
            self.db.dump()
        elif command in ('w', 'write'):
            self.write_sentence()
        elif command in ('s', 'sample', ''):
            self.examination()
        elif command in ('r', 'remove'):
            self.remove()
        else:
            raise Exception("Unknow command : {}".format(command))
    def event_loop(self):
        while True:
            if len(self.command_stack) == 0:
                self.get_command()
            else:
                command = self.command_stack.pop()
                self.run_command(command)
    def write_sentence(self):
        english = input("input english:")
        chinese = input("input chinese:")
        self.db.write(english, chinese)
    def examination(self):
        english, chinese = self.db.sample()
        print(chinese)
        print("please give english")
        inp_english = input("english:")
        print('\n')
        res = diff3(inp_english, english)
        print(res)
    def remove(self):
        self.db.remove()
            
A='The book is intended to serve as a text for the course in analysis that is usually taken by advanced undergraduates or by first-year student who study mathematics.'
B='The book is intented to serve as textbook for course in analysis that is taken by advanced undergraduates or by first-year student who study mathematics.'

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--run', action = 'store_true')
parser.add_argument('-i', '--init', action = 'store_true')
parser.add_argument('-p', '--path', default = 'db.json')
args = parser.parse_args()

if args.run:
    db = DataBase(args.path)
    if not args.init:
        db.load()
    interface = Interface(db)
    interface.start()
    