# ticket2rtm.py
#   hook Trac to sync with RTM.
#
# License: revised BSD
# Motohiro Takayama <mootoh@gmail.com>
#
import re
from genshi.builder import tag
from trac.core import *
from trac.ticket.api import ITicketChangeListener
import rtm

class Ticket2RTMPlugin(Component):
  implements(ITicketChangeListener)

  def __init__(self):
    self.env.log.debug('--------------- Ticket2RTMPlugin init')
    self.rtm_instance = rtm.Task(
      rtm.API(
        self.config.get('ticket2rtm', 'rtm_api_key', ''),
        self.config.get('ticket2rtm', 'rtm_api_secret', ''),
        self.config.get('ticket2rtm', 'rtm_api_token', '')),
      self.config.get('ticket2rtm', 'rtm_tag', 'trac'),
      self.config.get('ticket2rtm', 'rtm_list', ''))

  def create_task(self, ticket):
    self.env.log.debug('--------------- create_task')
    self.env.log.debug(ticket['priority'])

    self.rtm_instance.add_task(
      ticket['summary'],
      self.env.project_url + 'ticket/' + `ticket.id`,
      ticket.id,
      ticket['description'],
      ticket['priority'])

  def change_task(self, ticket, comment, author, old_values):
    self.env.log.debug('--------------- change_task')

  def complete_task(self, ticket):
    self.env.log.debug('--------------- complete_task')
    self.rtm_instance.complete_task(ticket)

  # ITicketChangeListener
  def ticket_created(self, ticket):
    self.create_task(ticket)

  def ticket_changed(self, ticket, comment, author, old_values):
    self.env.log.debug('################ ticket_changed')
    self.env.log.debug(ticket['summary'])
    self.env.log.debug(ticket['status'])
    self.env.log.debug(old_values)

    if ticket['status'] == 'closed' and old_values['status'] != 'closed':
      self.complete_task(ticket)
    else:
      self.change_task(ticket, comment, author, old_values)

  def ticket_deleted(self, ticket):
    self.complete_task(ticket)
