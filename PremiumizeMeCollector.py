# -*- coding: utf-8 -*-

from ..internal.Addon import Addon
from ..internal.misc import json

import copy

class PremiumizeMeCollector(Addon):
  __name__ = "PremiumizeMeCollector"
  __type__ = "hook"
  __version__ = "0.11"
  __status__ = "testing"

  __config__ = [("activated", "bool", "Activated", False),
                ("interval", "int", "Collection interval in seconds", 15),
                ("customerId", "string", "Customer ID", ""),
                ("pin", "string", "PIN", "")]

  __description__ = """Automagically checks the premiumize.me cloud storage and adds the files to the Collector."""
  __license__ = "GPLv3"
  __authors__ = [("Jan-Olaf Becker", "job87@web.de")]

  API_URL = "https://www.premiumize.me/api/"

  def activate(self):
    self.info['activated'] = True
    self.packages = []

    queue = self.pyload.api.getQueue()
    self.log_debug(str(queue))
    for package in queue:
      self.packages.append(package.name)

    collector = self.pyload.api.getCollector()
    self.log_debug(str(collector))
    for package in collector:
      self.packages.append(package.name)

    self.log_debug('Activating with interval: {0} s'.format(self.config.get('interval')))
    self.periodical.start(self.config.get('interval'))

  def deactivate(self):
    self.info['activated'] = False
    self.log_debug('Deactivate')
    self.periodical.stop()

  def periodical_task(self):
    self.log_debug('Running periodically...')
    #self.get_info(self.config.get('customerId'), self.config.get('pin'))
    files = self.get_files_in_folder(self.config.get('customerId'), self.config.get('pin'), "")
    self.log_debug("files: " + str(files))
    new_files = self.remove_duplicates(files)
    self.log_debug("new_files: " + str(new_files))
    
    for file in new_files:
      self.add_package(file['name'], file['link'])
    
    #self.get_folder_entries(self.config.get('customerId'), self.config.get('pin'), "AMp43Zx6F1avhAyKJgyxlQ")
    #self.add_package("name123", "link123")

  def api_respond(self, method, user, password, params = None):
    if params is None:
      params = {}

    params['customer_id'] = user
    params['pin'] = password

    html = self.load(self.API_URL + method, get=params)
    return json.loads(html)

  def get_info(self, user, password):
    self.log_debug("Calling account/info")
    
    result = self.api_respond("account/info", user, password)

    if result['status'] != "success":
      self.log_error("Call failed: " + result['message'])
    else:
      self.log_debug("Result: " + str(result))

  def get_files_in_folder(self, user, password, folder_id = None):
    self.log_debug("Calling folder/list for id " + str(folder_id))

    params = None
    if not folder_id is None:
      params = {'id': folder_id}

    result = self.api_respond("folder/list", user, password, params)

    files = []
    if result['status'] != "success":
      self.log_error("Call failed: " + result['message'])
    else:
      self.log_debug("Result: " + str(result))
      for entry in result['content']:
        self.log_debug(str(entry))
        if entry['type'] != "file":
          self.log_debug("not a file.")
        else:
          self.log_info("Found a file: " + entry['name'])
          self.log_info("with link: " + entry['link'])
          files.append({'name': entry['name'], 'link': entry['link']})
    return files

  def remove_duplicates(self, files):
    new_files = copy.deepcopy(files)
    self.log_debug(str(new_files))

    for f in files:
      self.log_debug("Checking: " + str(f['name']))

      if f['name'] in self.packages:
        self.log_debug(str(f['name']) + " already added. Removing")
        new_files.pop(f['name'])
    return new_files

  def add_package(self, name, link):
    self.log_debug("Adding package with name: " + name)
    self.log_debug("and link: " + link)

    pid = self.pyload.api.addPackage(name, [link], 0)
    if pid > 0:
      self.packages.append(name)
      self.log_debug(str(self.packages))

    self.log_debug("to collector. pid: " + str(pid))
