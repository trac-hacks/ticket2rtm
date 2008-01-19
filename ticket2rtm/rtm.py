# rtm.py
#   a tiny RTM wrapper by Python.
#
# License: revised BSD
# Motohiro Takayama <mootoh@gmail.com>
#
import re
import md5
import urllib
from xml.dom.minidom import parseString

class API:
  def __init__(self, key, secret, token=None):
    self.api_key = key
    self.secret  = secret
    self.token   = token

  def sign(self, args):
    str = ''
    for k in sorted(set(args)):
      str += ''.join([k,args[k]])
    str = self.secret + str
    return md5.new(str).hexdigest()

  def make_req_url(self, method, args={}):
    args['method']  = method
    args['api_key'] = self.api_key
    args['api_sig'] = self.sign(args)

    url = 'http://api.rememberthemilk.com/services/rest/?'
    for k,v in args.iteritems():
      url += k + '=' + urllib.quote(v.encode('utf-8')) + '&'
    return url

  def make_auth_url(self, perms, frob=None):
    args = {'api_key':self.api_key, 'perms':perms}

    if frob:
      args['frob'] = frob

    args['api_sig'] = self.sign(args)

    url = 'http://www.rememberthemilk.com/services/auth/?'
    for k,v in args.iteritems():
      url += k + '=' + v + '&'

    return url

  def request(self, url):
    ret = urllib.urlopen(url).read()
    return ''.join(ret.split('\n'))

  def get_frob(self):
    url = self.make_req_url('rtm.auth.getFrob')
    ret = self.request(url)
    regexp = re.compile('.*<frob>(.+)</frob>.*')
    o = regexp.match(ret)
    if o != None:
      return o.group(1)
    return ''

  def get_token(self, frob):
    url = self.make_req_url('rtm.auth.getToken', {'frob':frob})
    ret = self.request(url)
    regexp = re.compile('.*<token>(.+)</token>.*')
    o = regexp.match(ret)
    if o != None:
      return o.group(1)
    return ''

class Task:
  def __init__(self, api, tag, list):
    self.api  = api
    self.tag  = tag
    self.list = list

    self.priority_map = {
      'blocker':'1',
      'critical':'1',
      'major':'2',
      'minor':'3',
      'trivial':'3'
    }

    self.task_cache = {}
    self.parse_taskList(self.get_list())

  def create_timeline(self):
    # 1. create timeline
    url = self.api.make_req_url('rtm.timelines.create',
      {'auth_token':self.api.token})
    ret = self.api.request(url)
    regexp = re.compile('.*<timeline>(.*)</timeline>.*')
    o = regexp.match(ret)
    return o.group(1)

  def add_task(self, name, ticket_url, ticket_id, note, priority, list=None):
    # 1. create timeline
    url = self.api.make_req_url('rtm.timelines.create',
      {'auth_token':self.api.token})
    ret = self.api.request(url)
    regexp = re.compile('.*<timeline>(.*)</timeline>.*')
    o = regexp.match(ret)
    timeline = o.group(1)
    
    # 2. add a task
    params = {'auth_token':self.api.token,
              'timeline':timeline,
              'name':name}
    if list:
      params['list_id'] = list

    url = self.api.make_req_url('rtm.tasks.add', params)
    ret = self.api.request(url)
    # XXX: order of elements are not fixed...
    #      should use XML parser instead.
    regexp = re.compile('.*<list id="(\d+)"><taskseries id="(\d+)".*<task id="(\d+)"')
    o = regexp.match(ret)
    list_id = o.group(1)
    taskseries_id = o.group(2)
    task_id = o.group(3)

    self.task_cache[ticket_id] = {
      'list_id':list_id,
      'taskseries_id':taskseries_id,
      'task_id':task_id}

    # 3. set priority
    params = {'auth_token':self.api.token,
              'timeline':timeline,
              'list_id':list_id,
              'taskseries_id':taskseries_id,
              'task_id':task_id,
              'priority':self.priority_map[priority]}
    url = self.api.make_req_url('rtm.tasks.setPriority', params)
    ret = self.api.request(url)

    # 4. set tags
    params = {'auth_token':self.api.token,
              'timeline':timeline,
              'list_id':list_id,
              'taskseries_id':taskseries_id,
              'task_id':task_id,
              'tags':self.tag}
    url = self.api.make_req_url('rtm.tasks.addTags', params)
    ret = self.api.request(url)

    # 5. set URL
    params = {'auth_token':self.api.token,
              'timeline':timeline,
              'list_id':list_id,
              'taskseries_id':taskseries_id,
              'task_id':task_id,
              'url':ticket_url}
    url = self.api.make_req_url('rtm.tasks.setURL', params)
    ret = self.api.request(url)

    # 6. add a note
    if note:
      params = {'auth_token':self.api.token,
                'timeline':timeline,
                'list_id':list_id,
                'taskseries_id':taskseries_id,
                'task_id':task_id,
                'note_title':'',
                'note_text':note}
      url = self.api.make_req_url('rtm.tasks.notes.add', params)
      ret = self.api.request(url)

  def complete_task(self, ticket):
    params = {'auth_token':self.api.token,
              'timeline':self.create_timeline(),
              'list_id':self.task_cache[ticket.id]['list_id'],
              'taskseries_id':self.task_cache[ticket.id]['taskseries_id'],
              'task_id':self.task_cache[ticket.id]['task_id']}
    print params
    url = self.api.make_req_url('rtm.tasks.complete', params)
    ret = self.api.request(url)

  def get_list(self):
    params = {'auth_token':self.api.token,
              'filter':'tag:'+self.tag}
    url = self.api.make_req_url('rtm.tasks.getList', params)
    ret = self.api.request(url)
    return ret

  def parse_taskList(self, task_list_xml):
    document = parseString(task_list_xml)
    tasks = document.getElementsByTagName('task')
    if not tasks:
      return {}
    list_id = tasks[0].parentNode.parentNode.getAttribute('id')
    for task in tasks:
      if u'' != task.getAttribute('completed'):
        continue
      parent = task.parentNode
      url = parent.getAttribute('url')
      if not url:
        continue
      regexp = re.compile('.*/ticket/(.+)$')
      o = regexp.match(url)
      if o == None:
        continue
      ticket_id = int(o.group(1))
      values = {'task_id':task.getAttribute('id'),
                'taskseries_id':parent.getAttribute('id'),
                'list_id':list_id}
      self.task_cache[ticket_id] = values
