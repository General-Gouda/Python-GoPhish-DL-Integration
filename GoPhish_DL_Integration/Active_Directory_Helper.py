import gophish
import json
import os.path
import smtplib
import logging

import multiprocessing

from queue import Queue
from threading import Thread

from concurrent.futures import ThreadPoolExecutor
from functools import partial

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders

from ldap3 import Server, Connection
from GoPhish_DL_Integration.Configuration_Helper import Configuration

class GroupsWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            entry, connection, search_base = self.queue.get()

            try:
                get_group_members(entry, connection, search_base)
            finally:
                self.queue.task_done()

class AD_User_Class:
    def __init__(self, first_name=None, last_name=None, email=None, position=None):
        self.First_Name = first_name
        self.Last_Name = last_name
        self.Email = email
        self.Position = position

class AD_Group_Class:
    def __init__(self, group_name=None, display_name=None, distinguished_name=None, email=None, member=[]):
        self.Group_Name = ""

class AD_Helper:
    def __init__(self, servername, search_base):
        self._config = Configuration()
        if self._config.Testing:
            self._username = self._config.Testing_ADQueryAsUser
            self._email_server = self._config.Testing_Email_Server
        else:
            self._username = self._config.ADQueryAsUser
            self._email_server = self._config.Email_Server

        self.exclusion_search_filters = self._config.Exclude_Groups

        with open(r"./app_pass") as ap:
            _app_pass = ap.read().replace("\n","").replace("\r","")

        self.Server_Name = servername
        self.Server = Server(self.Server_Name)
        self.Connection = Connection(
            server = self.Server,
            user = self._username,
            password = _app_pass,
            auto_bind = True
        )
        self.Search_Base = search_base

    def send_email(self, send_from, send_to, subject, text, files=[]):
        try:
            msg = MIMEMultipart()
            msg['From'] = send_from
            msg['To'] = COMMASPACE.join(send_to)
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = subject

            msg.attach(MIMEText(text))

            for f in files:
                part = MIMEBase('application', "octet-stream")
                part.set_payload(open(f, "rb").read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(f)}"')
                msg.attach(part)

            smtp = smtplib.SMTP(self._email_server, 25)
            smtp.connect(self._email_server, 25)
            smtp.starttls()
            smtp.sendmail(send_from, send_to, msg.as_string())
            smtp.quit()
        except Exception as ex:
            logging.error(f"Exception while sending email:{ex}")

    def close_connection(self):
        self.Connection.unbind()
        self.Connection = None

def get_ad_distribution_group_list(exclusion_search_filters, connection, search_base):
    group_list = []

    exclusion_search_filters = ""

    for exclusion in exclusion_search_filters:
        exclusion_search_filters = exclusion_search_filters + f"(!(name={exclusion}))"

    group_search_filters = f"(&(objectClass=group){exclusion_search_filters})"

    try:
        entries = connection.extend.standard.paged_search(
            search_base = search_base,
            search_filter = group_search_filters,
            attributes = [
                'name',
                'displayName',
                'distinguishedName',
                'mail',
                'member'
            ],
            paged_size = 5000
        )

        for group in entries:
            if group['attributes']['member']:
                group_list.append(group['attributes'])

        return group_list

    except Exception as ex:
        logging.error(f"Exception retrieving distribution groups: {ex}")

def get_group_members(member, connection, search_base):
    member_list = []

    member = member.replace("(","\\28").replace(")","\\29")
    connection.search(
        search_base=search_base,
        search_filter=f'(distinguishedName={member})',
        attributes=[
            'name',
            'givenName',
            'sn',
            'mail',
            'description',
            'objectClass'
        ]
    )

    if len(connection.response) > 0:
        member_entry = connection.response[0]['attributes']

        if "group" in member_entry['objectClass']:
            nested_group_list = get_ad_group_member_list(
                connection=connection,
                group_name=member_entry['name'],
                search_base=search_base
            )
            member_list = member_list + nested_group_list
        else:
            for key in member_entry.keys():
                if type(member_entry[key]) is list:
                    if member_entry[key] == []:
                        member_entry[key] = "None"
                    else:
                        member_entry[key] = ", ".join(member_entry[key])

            if member_entry['mail'] is not "None":
                member_info = AD_User_Class(
                    first_name=member_entry['givenName'].upper(),
                    last_name=member_entry['sn'].upper(),
                    email=member_entry['mail'].lower(),
                    position=member_entry['description']
                )

                member_list.append(member_info)

    return member_list

def get_ad_group_member_list(group_name, connection, search_base):
    member_list = []

    try:
        connection.search(
            search_base = search_base,
            search_filter = f'(&(objectClass=group)(name={group_name}))',
            attributes = ['member']
        )

        entries = connection.entries

        if entries:
            with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
                for member in [entry.member.values for entry in entries][0]:
                    future = executor.submit(get_group_members, member, connection, search_base)
                    member_list = member_list + future.result()

        return member_list
    except Exception as ex:
        logging.error(ex)