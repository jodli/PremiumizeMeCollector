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

    collector = self.pyload.api.getCollector()
    self.log_debug("Initializing existing collector packages.")
    #self.log_debug(str(collector))
    for package in collector:
      self.packages.append(package.name)

    self.log_debug('Activating with interval: {0} s'.format(self.config.get('interval')))
    self.periodical.start(self.config.get('interval'))

  def deactivate(self):
    self.info['activated'] = False
    self.log_debug('Deactivate')
    self.periodical.stop()

  def periodical_task(self):
    #self.log_debug('Running periodically...')
    files = self.get_files_in_folder(self.config.get('customerId'), self.config.get('pin'))
    #self.log_debug("files: " + str(files))
    new_files = self.remove_duplicates(files)
    #self.log_debug("new_files: " + str(new_files))
    
    for file in new_files:
      self.add_package(file['name'], file['link'])

  def api_respond(self, method, user, password, params = None):
    if params is None:
      params = {}

    params['customer_id'] = user
    params['pin'] = password

    html = self.load(self.API_URL + method, get=params)
    return json.loads(html)

  def get_files_in_folder(self, user, password, folder_id = None):
    self.log_debug("Calling folder/list for id " + str(folder_id))

    params = None
    if not folder_id is None:
      params = {'id': folder_id}

    result = self.api_respond("folder/list", user, password, params)

    files = []
    if result['status'] != "success":
      self.log_error("Call to folder/list failed: " + result['message'])
    else:
      self.log_debug("Result: " + str(result))
      for entry in result['content']:
        #self.log_debug(str(entry))
        if entry['type'] != "file":
          self.log_debug(entry['name'] + " is not a file. Skipping.")
        else:
          self.log_debug("Found a file: " + entry['name'])
          self.log_debug("with link: " + entry['link'])
          files.append({'name': entry['name'], 'link': entry['link']})
    return files

  def remove_duplicates(self, files):
    new_files = copy.deepcopy(files)
    #self.log_debug(str(new_files))

    for f in files:
      self.log_debug("Checking: " + str(f['name']))

      if f['name'] in self.packages:
        self.log_debug(str(f['name']) + " already added. Removing.")
        new_files.remove(f)
    return new_files

  def add_package(self, name, link):
    self.log_info("Adding package with name: " + name)
    self.log_info("and link: " + link)

    pid = self.pyload.api.addPackage(name, [link], 0)
    if pid > 0:
      self.packages.append(name)
      #self.log_debug(str(self.packages))

    self.log_info("to collector. pid: " + str(pid))
