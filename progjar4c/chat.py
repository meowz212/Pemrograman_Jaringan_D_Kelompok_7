import sys
import os
import json
import uuid
import logging
from queue import Queue


class Chat:
    def __init__(self):
        self.sessions = {}
        self.users = {}
        self.groups = {}
        self.users['messi'] = {'nama': 'Lionel Messi', 'negara': 'Argentina', 'password': 'surabaya', 'incoming': {},
                               'outgoing': {}, 'files': {}}
        self.users['henderson'] = {'nama': 'Jordan Henderson', 'negara': 'Inggris', 'password': 'surabaya',
                                   'incoming': {}, 'outgoing': {}, 'files': {}}
        self.users['lineker'] = {'nama': 'Gary Lineker', 'negara': 'Inggris', 'password': 'surabaya', 'incoming': {},
                                 'outgoing': {}, 'files': {}}
        self.users['aul'] = {'nama': 'Aul Ronaldo', 'negara': 'Inggris', 'password': 'sby', 'incoming': {},
                             'outgoing': {}, 'files': {}}
        self.users['kinas'] = {'nama': 'Kinas turu', 'negara': 'Inggris', 'password': 'sby', 'incoming': {},
                               'outgoing': {}, 'files': {}}
        self.users['rimas'] = {'nama': 'Rimas Lineker', 'negara': 'Inggris', 'password': 'sby', 'incoming': {},
                               'outgoing': {}, 'files': {}}
        self.groups['group1'] = {'nama': 'Group 1', 'member': ['messi', 'henderson', 'lineker']}
        self.groups['group2'] = {'nama': 'Group 2', 'member': ['messi', 'aul', 'rimas', 'kinas']}

    def getuser(self):
        return self.users

    def newgroup(self, groupid, groupname, members):
        self.groups[groupid] = {'nama': groupname, 'member': members}
        return self.groups

    def getgroup(self):
        return self.groups

    def proses(self, data):
        j = data.split(" ")
        try:
            command = j[0].strip()
            if (command == 'auth'):
                username = j[1].strip()
                password = j[2].strip()
                logging.warning("AUTH: auth {} {}".format(username, password))
                return self.autentikasi_user(username, password)
            elif (command == 'send'):
                sessionid = j[1].strip()
                usernameto = j[2].strip()
                message = ""
                for w in j[3:]:
                    message = "{} {}".format(message, w)
                usernamefrom = self.sessions[sessionid]['username']
                logging.warning(
                    "SEND: session {} send message from {} to {}".format(sessionid, usernamefrom, usernameto))
                return self.send_message(sessionid, usernamefrom, usernameto, message)
            elif (command == 'inbox'):
                sessionid = j[1].strip()
                username = self.sessions[sessionid]['username']
                logging.warning("INBOX: {}".format(sessionid))
                return self.get_inbox(username)
            elif (command == 'send_file'):
                sessionid = j[1].strip()
                usernameto = j[2].strip()
                filename = j[3].strip()
                message = ""

                for w in j[4:-1]:
                    message = "{} {}".format(message, w)
                username_from = self.sessions[sessionid]['username']
                logging.warning("SEND: session {} send message from {} to {}".format(sessionid, username_from, usernameto))
                return self.send_file(sessionid, username_from, usernameto, filename, message)
            elif (command == 'download_file'):
                sessionid = j[1].strip()
                usernameto = j[2].strip()
                filename = j[3].strip()

                username_from = self.sessions[sessionid]['username']
                logging.warning("DOWNLOAD: session {} file {} ".format(sessionid, filename))
                return self.download_file(sessionid, username_from, usernameto, filename)
            elif (command == 'my_file'):
                sessionid = j[1].strip()
                logging.warning("FILES: session {}".format(sessionid))
                username = self.sessions[sessionid]['username']
                return self.my_file(sessionid, username)
            elif (command == 'send_group'):
                sessionid = j[1].strip()
                groupto = j[2].strip()
                usernamefrom = self.sessions[sessionid]['username']
                message = ""
                for w in j[3:]:
                    message = "{} {}".format(message, w)
                logging.warning(
                    "SEND: session {} send message from {} to group {}".format(sessionid, usernamefrom, groupto))
                return self.send_groupmessage(sessionid, usernamefrom, groupto, message)
            elif (command == 'send_group_file'):
                sessionid = j[1].strip()
                groupto = j[2].strip()
                filename = j[3].strip()
                message = ""

                for w in j[4:-1]:
                    message = "{} {}".format(message, w)
                username_from = self.sessions[sessionid]['username']
                logging.warning("SEND: session {} send message from {} to {} with data {}".format(sessionid, username_from, groupto, message))
                return self.send_groupfile(sessionid, username_from, groupto, filename, message)
            else:
                return {'status': 'ERROR', 'message': '**Protocol Tidak Benar'}
        except KeyError:
            return {'status': 'ERROR', 'message': 'Informasi tidak ditemukan'}
        except IndexError:
            return {'status': 'ERROR', 'message': '--Protocol Tidak Benar'}

    def autentikasi_user(self, username, password):
        if (username not in self.users):
            return {'status': 'ERROR', 'message': 'User Tidak Ada'}
        if (self.users[username]['password'] != password):
            return {'status': 'ERROR', 'message': 'Password Salah'}
        tokenid = str(uuid.uuid4())
        self.sessions[tokenid] = {'username': username, 'userdetail': self.users[username]}
        return {'status': 'OK', 'tokenid': tokenid}

    def get_user(self, username):
        if (username not in self.users):
            return False
        return self.users[username]

    def get_group(self, group):
        if (group not in self.groups):
            return False
        return self.groups[group]

    def send_message(self, sessionid, username_from, username_dest, message):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        s_fr = self.get_user(username_from)
        s_to = self.get_user(username_dest)

        if (s_fr == False or s_to == False):
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

        outqueue_sender = s_fr['outgoing']
        inqueue_receiver = s_to['incoming']
        try:
            outqueue_sender[username_from].put(message)
        except KeyError:
            outqueue_sender[username_from] = Queue()
            outqueue_sender[username_from].put(message)
        try:
            inqueue_receiver[username_from].put(message)
        except KeyError:
            inqueue_receiver[username_from] = Queue()
            inqueue_receiver[username_from].put(message)
        return {'status': 'OK', 'message': 'Message Sent'}

    def send_groupmessage(self, sessionid, username_from, group_to, message):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        s_fr = self.get_user(username_from)
        s_gr = self.get_group(group_to)

        if (s_fr == False):
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

        if (s_gr == False):
            return {'status': 'ERROR', 'message': 'Group Tidak Ditemukan'}

        outqueue_sender = s_fr['outgoing']
        message_out = {'msg_from': s_fr['nama'], 'msg_to': s_gr['nama'], 'msg': message}
        try:
            outqueue_sender[username_from].put(message_out)
        except KeyError:
            outqueue_sender[username_from] = Queue()
            outqueue_sender[username_from].put(message_out)

        for member in s_gr['member']:
            s_to = self.get_user(member)
            if (s_to == False):
                continue
            message_in = {'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': message}
            inqueue_receiver = s_to['incoming']
            try:
                inqueue_receiver[group_to].put(message_in)
            except KeyError:
                inqueue_receiver[group_to] = Queue()
                inqueue_receiver[group_to].put(message_in)

        return {'status': 'OK', 'message': 'Message Sent'}

    def send_groupfile(self, sessionid, username_from, group_to, filename, message):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        s_fr = self.get_user(username_from)
        s_gr = self.get_group(group_to)

        if (s_fr == False ):
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

        if (s_gr == False):
            return {'status': 'ERROR', 'message': 'Group Tidak Ditemukan'}

        try:
            s_fr['files'][username_from][filename] = message
        except KeyError:
            s_fr['files'][username_from] = {}
            s_fr['files'][username_from][filename] = message

        for member in s_gr['member']:
            s_to = self.get_user(member)
            if (s_to == False):
                continue
            try:
                s_to['files'][group_to][filename] = message
            except KeyError:
                s_to['files'][group_to] = {}
                s_to['files'][group_to][filename] = message

        return {'status': 'OK', 'message': 'File Sent'}

    def get_inbox(self, username):
        s_fr = self.get_user(username)
        incoming = s_fr['incoming']
        msgs = {}
        for users in incoming:
            msgs[users] = []
            while not incoming[users].empty():
                msgs[users].append(s_fr['incoming'][users].get_nowait())

        return {'status': 'OK', 'messages': msgs}

    def send_file(self, sessionid, username_from, username_dest, filename, message):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        s_fr = self.get_user(username_from)
        s_to = self.get_user(username_dest)

        if (s_fr == False or s_to == False):
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

        try:
            s_to['files'][username_from][filename] = message
        except KeyError:
            s_to['files'][username_from] = {}
            s_to['files'][username_from][filename]= message
        try:
            s_fr['files'][username_dest][filename]= message
        except KeyError:
            s_fr['files'][username_dest] = {}
            s_fr['files'][username_dest][filename]= message
        return {'status': 'OK', 'message': 'File Sent'}

    def download_file(self, sessionid, username_from, username_to, filename):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        s_usr = self.get_user(username_from)
        if (username_to not in s_usr['files']):
            return {'status': 'ERROR', 'message': 'File Tidak Ditemukan'}
        if filename not in s_usr['files'][username_to]:
            return {'status': 'ERROR', 'message': 'File Tidak Ditemukan'}
        data = s_usr['files'][username_to][filename]
        return {'status': 'OK', 'messages': f'Downloaded {filename}', 'filename': f'{filename}', 'data': f'{data}'}
    def my_file(self, sessionid, username):
            if (sessionid not in self.sessions):
                return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
            s_usr = self.get_user(username)
            files = s_usr['files']
            msgs = {}
            for user in files:
                msgs[user] = []
                for file in files[user] :
                    msgs[user].append(file)
            return {'status': 'OK', 'messages': msgs}

if __name__ == "__main__":
    j = Chat()
    sesi = j.proses("auth messi surabaya")
    print(sesi)
    # sesi = j.autentikasi_user('messi','surabaya')
    # print sesi
    tokenid = sesi['tokenid']
    print(j.proses("send {} henderson hello gimana kabarnya son ".format(tokenid)))
    print(j.proses("send {} messi hello gimana kabarnya mess ".format(tokenid)))

    # print j.send_message(tokenid,'messi','henderson','hello son')
    # print j.send_message(tokenid,'henderson','messi','hello si')
    # print j.send_message(tokenid,'lineker','messi','hello si dari lineker')

    print("isi mailbox dari messi")
    print(j.get_inbox('messi'))
    print("isi mailbox dari henderson")
    print(j.get_inbox('henderson'))
















