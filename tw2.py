#!/usr/bin/env python
# coding:utf-8

import sys, urllib2, urllib, twitter as tw, readline, simplejson, os
from pit import Pit
import logging

try:
  import Growl
  g = Growl.GrowlNotifier(
    applicationName='Pytter', notifications=['SyntaxError', 'PytterNotify'])
  g.register()
except:
  pass

def _T(text):
  if 'nt' == os.name:
    return text.encode('mbcs', 'ignore')
  else:
    return text

# KeyConfig
getFriendsTimeLineKey = ['friends', 'f']
getRepliesKey = ['res', 'r', '']
sendPostKey = ['post', 'p']
exitKey = ['x', 'ZZ', 'exit', 'bye']

# Log file Name
#logFileName = './wtLog.log'
#logging.basicConfig(filename=logFileName, level=logging.INFO, format='%(message)s',)

class Wassr:
  def __init__(self, user, passwd):
    self.user = user
    self.passwd = passwd
  def post(self, text):
    text = text.encode('utf-8')
   #text = text.encode('utf-7')
    self.getOpener().open('http://api.wassr.jp/statuses/update.json', urllib.urlencode({'status':text}))
  def getTimeline(self):
    url = 'http://api.wassr.jp/statuses/friends_timeline.json'
    r = self.getOpener().open(url)
    data = simplejson.loads(r.read())
    return data
  def getReplies(self):
    url = 'http://api.wassr.jp/statuses/replies.json'
    r = self.getOpener().open(url)
    data = simplejson.loads(r.read())
    return data
  def getOpener(self):
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, 'api.wassr.jp', self.user, self.passwd)
    authhandler = urllib2.HTTPBasicAuthHandler(passman)
    opener = urllib2.build_opener(authhandler)
    opener.addheaders = [('User-agent', 'WassrClient(http://d.hatena.ne.jp/jYoshiori/)')]
    return opener


if __name__ == "__main__":
  import os 
  readline.parse_and_bind("tab: complete")
  # auth setting
  wassr_config = Pit.get('wassr.jp',{'require' : {'user':'Your wassr name','password':'Your wassr password'}})
  wassr = Wassr(wassr_config['user'],wassr_config['password'])
  twitter_config = Pit.get('twitter.com',{'require' : {'user':'Your twitter name','password':'Your twitter password'}})
  twitter = tw.Api(twitter_config['user'], twitter_config['password'])

  friends = set()
  friendsTimeLine = []

  def complete(text, status):
    results = [x for x in friends if x.startswith(text)] + [None]
    return results[status]
  
  def twitPost(input):
    # post twitter and wassr
    twit = ''.join(input[1:])
    wassr.post(input)
    twitter.PostUpdate(input)
    print 'update : ' + input

  def getReplies(wassr, twitter):
    # get twitter friends Replies
    print '\twassr replies\t'
    for data in reversed(wassr.getReplies()):
      #print '%-12s : %s' % (data['user_login_id'] ,data['text'])
      print _T('%-12s : %s' % (data['user_login_id'] ,data['text']))
      friends.add(data['user_login_id'])
  
    # get twitter friends Replies        
    print '\n\ttwitter replies\t'
    for data in reversed(twitter.GetReplies()):
      #print '%-12s : %s' % (data.GetUser().GetScreenName() ,data.GetText())
      print _T('%-12s : %s' % (data.GetUser().GetScreenName() ,data.GetText()))
      friends.add(data.GetUser().GetScreenName())
    return 0


  def getFriensTimeLine(wassr, twitter):
    # Get FriendsTimeLine
    print ' -----  wassr Friends Time Line  -----'
    for data in reversed(wassr. getTimeline()):
      #print "%-12s: %s" % (data['user_login_id'] ,data['text'])
      print _T("%-12s: %s" % (data['user_login_id'] ,data['text']))
      twit = "wr[]%-12s: %s" % (data['user_login_id'] ,data['text'])
      if twit in friendsTimeLine:
        pass
      else:
        logging.info(twit)
        friendsTimeLine.append(twit)
    print '\n  -----  twitter Friends Time Line  -----'
    for data in reversed(twitter.GetFriendsTimeline()):
      #print '%-12s : %s' % (data.GetUser().GetScreenName() ,data.GetText())
      print _T('%-12s : %s' % (data.GetUser().GetScreenName() ,data.GetText()))
      # append log
      twit  = "tw[%s]%-12s: %s" % (data.GetCreatedAt(), data.GetUser().GetScreenName(), data.GetText())
      if twit in friendsTimeLine:
        pass
      else:
        logging.info(twit)
        
        '''
        g.notify(
          noteType='PytterNotify', 
          title='%s'%(data.GetUser().GetScreenName()), 
          description='%s'%(data.GetText()), 
          sticky=False)
        '''

        friendsTimeLine.append(twit)
 
  readline.set_completer(complete)

  prompt = '\n cmd: Friendstimeline[f] eXit[x] \n> '
  
  while True:
    if os.name == 'nt':
      print prompt,
      input = sys.stdin.readline().decode('mbcs').encode('utf-8').strip().split(" ")
    else:
      all_input = raw_input(prompt)
      input = all_input.split(" ")
    if input[0] != '':
      if input[0] in getFriendsTimeLineKey: 
        getFriensTimeLine(wassr, twitter)
        continue
      elif input[0] in sendPostKey:
        twitPost(unicode(' '.join(input[1:]), 'utf-8'))
        continue
      elif input[0] in getRepliesKey:
        getReplies(wassr, twitter)
        continue
      elif input[0] in exitKey:
        print 'bye ;-)'
        break
      else:
        twitPost(unicode('%s'%(all_input), 'utf-8'))
        continue
    else: 
      getReplies(wassr, twitter)
