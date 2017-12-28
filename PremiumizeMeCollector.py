# -*- coding: utf-8 -*-

from ..internal.Addon import Addon

class PremiumizeMeCollector(Addon):
  __name__ = "PremiumizeMeCollector"
  __type__ = "hook"
  __version__ = "0.1"
  __status__ = "testing"

  __config__ = [("activated", "bool", "Activated", False),
                ("interval", "int", "Collection interval in seconds", 15)]

  __description__ = """Automagically checks the premiumize.me cloud storage and adds the files to the Collector."""
  __license__ = "GPLv3"
  __authors__ = [("Jan-Olaf Becker", "job87@web.de")]

  def activated(self):
    self.log_debug('Activating with interval: %s' % interval)
    self.periodical.start(self.config.get('interval'))

  def deactivated(self):
    self.log_debug('Deactivating')

  def periodical_task(self):
    self.log_debug('Running periodically...')
