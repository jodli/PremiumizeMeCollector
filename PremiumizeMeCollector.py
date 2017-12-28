# -*- coding: utf-8 -*-

from ..internal.Addon import Addon
from ..internal.misc import json

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
    self.log_debug('Activating with interval: {0} s'.format(self.config.get('interval')))
    self.periodical.start(self.config.get('interval'))

  def deactivate(self):
    self.info['activated'] = False
    self.log_debug('Deactivate')
    self.periodical.stop()

  def periodical_task(self):
    self.log_debug('Running periodically...')
    self.get_info(self.config.get('customerId'), self.config.get('pin'))
    self.get_folder_entries(self.config.get('customerId'), self.config.get('pin'), "")
    self.get_folder_entries(self.config.get('customerId'), self.config.get('pin'), "AMp43Zx6F1avhAyKJgyxlQ")

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

  def get_folder_entries(self, user, password, folder_id = None):
    self.log_debug("Calling folder/list")

    params = None
    if not folder_id is None:
      params = {'id': folder_id}

    result = self.api_respond("folder/list", user, password, params)

    if result['status'] != "success":
      self.log_error("Call failed: " + result['message'])
    else:
      self.log_debug("Result: " + str(result))



