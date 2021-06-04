import base64
import json
import logging
import os
import socket
import threading
import time
import tkinter
from tkinter import Tk, Scrollbar, Label, END, Entry, Text, Button, filedialog, messagebox, \
    Toplevel, DISABLED, NORMAL

from chat import Chat

TARGET_IP = "127.0.0.1"
TARGET_PORT = 8889

# get user list and initialize thread trace
chat = Chat()
users = chat.getuser()
groups = chat.getgroup()


# members = ['messi', 'rimas', 'kinas']
# groups = chat.newgroup('group3', 'Group 3', members)

class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP, TARGET_PORT)
        self.sock.connect(self.server_address)
        self.initlocation = os.getcwd()
        self.isfile = False
        self.isgroup = False
        self.receiverid = ""
        # self.chatopen = False
        self.rcv = threading.Thread(target=self.getmessage)
        self.tokenid = ""
        self.initialize_login()

    def initialize_login(self):  # GUI initializer
        ## chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()

        # login window
        self.loginpage = Toplevel()
        # set the title
        self.loginpage.title("Login")
        self.loginpage.resizable(width=False,
                                 height=False)
        self.loginpage.configure(width=400,
                                 height=300)
        # create a Label
        self.pls = Label(self.loginpage,
                         text="Silahkan login dahulu",
                         font="Helvetica 14 bold")

        self.pls.place(relheight=0.15,
                       relx=0.2,
                       rely=0.07)
        # create a Label
        self.labelName = Label(self.loginpage,
                               text="Username: ",
                               font="Helvetica 12")

        self.labelName.place(relheight=0.2,
                             relx=0.1,
                             rely=0.27)

        # create a entry box for
        self.entryName = Entry(self.loginpage,
                               font="Helvetica 14")

        self.entryName.place(relwidth=0.5,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.3)

        # create a Label pass
        self.labelPass = Label(self.loginpage,
                               text="Password: ",
                               font="Helvetica 12")

        self.labelPass.place(relheight=0.2,
                             relx=0.1,
                             rely=0.47)

        # create a entry box for pass
        self.entryPass = Entry(self.loginpage,
                               font="Helvetica 14")

        self.entryPass.place(relwidth=0.5,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.5)

        # set the focus of the curser
        self.entryName.focus()

        # create a Continue Button
        # along with action
        self.go = Button(self.loginpage,
                         text="Login",
                         font="Helvetica 14 bold",
                         command=lambda: self.loginto(self.entryName.get(), self.entryPass.get()))

        self.go.place(relx=0.4,
                      rely=0.7)
        self.Window.mainloop()

    def loginto(self, username, password):
        self.loginpage.destroy()
        x = self.login(username, password).strip()
        # print(x)
        if (x == "Error, User Tidak Ada"):
            tkinter.messagebox.showinfo('Error', 'Nama tidak ada')
            self.loginpage.destroy()
            self.initialize_login()
        elif (x == "Error, Password Salah"):
            tkinter.messagebox.showinfo('Error', 'Password salah')
            self.loginpage.destroy()
            self.initialize_login()
        else:
            # start receiving msg
            # self.chatopen = True
            self.rcv.start()
            self.chatlist(username)
            # self.sendto(username);

    def chatlist(self, name):
        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("Menu Chat")
        self.Window.resizable(width=False,
                              height=False)
        self.Window.configure(width=470,
                              height=650,
                              bg="#17202A")
        self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text="login sebagai " + self.name,
                               font="Helvetica 13 bold",
                               pady=5)

        self.labelHead.place(relwidth=1)
        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")

        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=120.1)

        # label
        self.labellist = Label(self.line,
                               text="List Chat",
                               bg="#ABB2B9",
                               font="Helvetica 20")

        self.labellist.place(relheight=0.0005,
                             rely=0.0001,
                             relx=0.38)

        # loop name target list
        x = 0
        for k, v in users.items():
            # print(k, v)
            if (name == k):
                self.fullname = v["nama"]
                continue
            self.buttonperson = Button(self.line,
                                       text=v["nama"],
                                       font="Helvetica 10 bold",
                                       width=20,
                                       bg="#FFFFFF",
                                       command=lambda receiver=k, receivername=v["nama"]: self.sendto(name,
                                                                                                      receivername,
                                                                                                      receiver))

            self.buttonperson.place(relx=0.1,
                                    rely=0.0008 + x,
                                    relheight=0.0006,
                                    relwidth=0.8)
            x = x + 0.0008

        # loop group target list
        for k, v in groups.items():
            # print(k, v)
            for i in v['member']:
                if i == name:
                    self.buttongroup = Button(self.line,
                                              text=v["nama"],
                                              font="Helvetica 10 bold",
                                              width=20,
                                              bg="#FFFFFF",
                                              command=lambda group=k, groupname=v["nama"]: self.sendgroup(name,
                                                                                                          groupname,
                                                                                                          group))

                    self.buttongroup.place(relx=0.1,
                                           rely=0.0008 + x,
                                           relheight=0.0006,
                                           relwidth=0.8)
                    x = x + 0.0008

        # Bikin Grup Baru
        self.buttongrups = Button(self.line,
                                  text="Buat Grup",
                                  font="Helvetica 10 bold",
                                  width=20,
                                  bg="#FFFFFF",
                                  command=lambda: self.createegroup())

        self.buttongrups.place(relx=0.1,
                               rely=0.0008 + x,
                               relheight=0.0006,
                               relwidth=0.8)

        # # create a scroll bar
        # scrollbar = Scrollbar(self.line)
        #
        # # place the scroll bar
        # # into the gui window
        # scrollbar.place(relheight=1,
        #                 relx=0.974)
        #
        # scrollbar.config(command=self.line.yview)

        # self.textCons.config(state=DISABLED)

    def createegroup(self):
        self.Window.deiconify()
        self.Window.title("Menu Chat")
        self.Window.resizable(width=False,
                              height=False)
        self.Window.configure(width=400,
                              height=400,
                              bg="#17202A")
        self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text="login sebagai " + self.name,
                               font="Helvetica 13 bold",
                               pady=5)

        self.labelHead.place(relwidth=1)
        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")

        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=120.1)

        # label
        self.labelchat = Label(self.line,
                               text="Masukkan Informasi",
                               bg="#ABB2B9",
                               font="Helvetica 20")

        self.labelchat.place(relheight=0.0005,
                             rely=0.0001,
                             relx=0.18)
        # create a Label
        self.pls = Label(self.line,
                         text="Silahkan login dahulu",
                         font="Helvetica 14 bold")

        self.pls.place(relheight=0.15,
                       relx=0.2,
                       rely=0.07)

        # groupid name input
        self.entrygroupid = Entry(self.line,
                                  font="Helvetica 14", )

        self.entrygroupid.place(relx=0.4,
                                rely=0.0018,
                                relheight=0.0006,
                                relwidth=0.45)

        self.labelgroupid = Label(self.line,
                                  bg="#ABB2B9",
                                  text="Group Id : ",
                                  font="Helvetica 12")

        self.labelgroupid.place(relheight=0.0006,
                                relx=0.18,
                                rely=0.0018)

        # groupName name input
        self.entrygroupname = Entry(self.line,
                                    font="Helvetica 14", )

        self.entrygroupname.place(relx=0.4,
                                  rely=0.0028,
                                  relheight=0.0006,
                                  relwidth=0.45)

        self.labelgroupname = Label(self.line,
                                    bg="#ABB2B9",
                                    text="Nama Group : ",
                                    font="Helvetica 12")

        self.labelgroupname.place(relheight=0.0006,
                                  relx=0.10,
                                  rely=0.0028)

        # Member count name input
        self.entrymembercount = Entry(self.line,
                                      font="Helvetica 14", )

        self.entrymembercount.place(relx=0.4,
                                    rely=0.0038,
                                    relheight=0.0006,
                                    relwidth=0.45)

        self.labelmembercount = Label(self.line,
                                      bg="#ABB2B9",
                                      text="Jumlah Member : ",
                                      font="Helvetica 12")

        self.labelmembercount.place(relheight=0.0006,
                                    relx=0.05,
                                    rely=0.0038)

        # button submit
        self.buttonMsg = Button(self.line,
                                text="Buat",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.invitemember(self.entrygroupid.get(), self.entrygroupname.get(),
                                                                  self.entrymembercount.get()))

        self.buttonMsg.place(relx=0.1,
                             rely=0.0058,
                             relheight=0.0008,
                             relwidth=0.8)

    def invitemember(self, groupid, groupname, membercount):
        if not (groupid and groupid.strip()) or not (groupname and groupname.strip()) or not (
                membercount and membercount.strip()):
            return tkinter.messagebox.showinfo('Error', 'Input ada yang kosong')
        member = int(membercount)
        self.members = []
        self.Window.deiconify()
        self.Window.title("Pilih Anggota")
        self.Window.resizable(width=False,
                              height=False)
        self.Window.configure(width=400,
                              height=600,
                              bg="#17202A")
        self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text="login sebagai " + self.name,
                               font="Helvetica 13 bold",
                               pady=5)

        self.labelHead.place(relwidth=1)
        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")

        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=120.1)

        # label
        self.labelmember = Label(self.line,
                                 text="Isi Username Member",
                                 bg="#ABB2B9",
                                 font="Helvetica 20")

        self.labelmember.place(relheight=0.0005,
                               rely=0.0001,
                               relx=0.18)

        # Capture list user
        userlist = []
        for k, _ in users.items():
            userlist.append(k)

        usergang = ','.join(userlist)

        # Print list user
        self.labelmember = Label(self.line,
                                 text="user yang bisa diambil " + usergang,
                                 bg="#ABB2B9",
                                 font="Helvetica 10")

        self.labelmember.place(relheight=0.0005,
                               rely=0.0005,
                               relx=0.05)

        # loop Isi username
        self.entrymemberid = []
        y = 0
        for x in range(member):
            self.entrymemberid.append(Entry(self.line,
                                            font="Helvetica 14", ))

            self.entrymemberid[x].place(relx=0.4,
                                        rely=0.001 + y,
                                        relheight=0.0006,
                                        relwidth=0.45)

            self.labelmemberid = Label(self.line,
                                       bg="#ABB2B9",
                                       text="User Id : ",
                                       font="Helvetica 12")

            self.labelmemberid.place(relheight=0.0006,
                                     relx=0.18,
                                     rely=0.001 + y)
            y = y + 0.001
            # self.members[x] = self.entrymemberid[x].get()

        # button submit
        self.buttonMsg = Button(self.line,
                                text="Buat",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.grabmember(groupid, groupname, member))

        self.buttonMsg.place(relx=0.1,
                             rely=0.001 + y,
                             relheight=0.0008,
                             relwidth=0.8)

    def grabmember(self, groupids, groupnames, membercounts):
        for x in range(membercounts):
            input = self.entrymemberid[x].get()
            if input in users:
                self.members.append(self.entrymemberid[x].get())
            else:
                return tkinter.messagebox.showinfo('Error', 'Ada user id yang salah')
        uniques = []
        [uniques.append(num) for num in self.members if not num in uniques]
        groups = chat.newgroup(groupids, groupnames, uniques)
        self.backtochatlist(self.name)

    def sendto(self, username, receivername, receiver):
        self.isgroup = False
        self.receiverwho = receivername
        self.receiverid = receiver
        self.filename = ""
        # to show chat window
        self.Window.deiconify()
        self.Window.title("Ruangan Chat")
        self.Window.resizable(width=False,
                              height=False)
        self.Window.configure(width=470,
                              height=550,
                              bg="#17202A")
        self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text="Chat " + receivername + " sebagai " + self.name,
                               font="Helvetica 13 bold",
                               pady=5)

        self.labelHead.place(relwidth=1)

        # tombol kembali
        self.buttonBack = Button(self.Window,
                                 text="Bonjour",
                                 font="Helvetica 10 bold",
                                 width=20,
                                 bg="#ABB2B9",
                                 command=lambda: self.backtochatlist(username))

        self.buttonBack.place(relwidth=0.2, relx=0.8)

        # garis
        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")

        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=0.012)

        self.textCons = Text(self.Window,
                             width=20,
                             height=2,
                             bg="#17202A",
                             fg="#EAECEE",
                             font="Helvetica 14",
                             padx=5,
                             pady=5)

        self.textCons.place(relheight=0.585,
                            relwidth=1,
                            rely=0.08)

        self.labelBottom = Label(self.Window,
                                 bg="#ABB2B9",
                                 height=80)

        self.labelBottom.place(relwidth=1,
                               rely=0.66)

        # kolom pesan
        self.TextMsg = Text(self.labelBottom,
                            bg="#2C3E50",
                            fg="#EAECEE",
                            font="Helvetica 13")

        self.labelPassMsg = Label(self.labelBottom,
                                  text="Pesan: ",
                                  bg="#ABB2B9",
                                  font="Helvetica 10")

        self.labelPassMsg.place(relheight=0.02,
                                rely=0,
                                relx=0.011)

        self.TextMsg.place(relwidth=0.74,
                           relheight=0.088,
                           rely=0.02,
                           relx=0.011)

        # kolom receiver

        # self.entryRcv = Entry(self.labelBottom,
        #                       bg="#2C3E50",
        #                       fg="#EAECEE",
        #                       font="Helvetica 13",
        #                       text=receiver)
        # self.labelPassRcv = Label(self.labelBottom,
        #                        text="Penerima: ",
        #                        bg="#ABB2B9",
        #                        font="Helvetica 10")
        #
        # self.labelPassRcv.place(relheight=0.02,
        #                     rely=0,
        #                     relx=0.011)
        #
        # self.entryRcv.place(relwidth=0.74,
        #                     relheight=0.02,
        #                     rely=0.02,
        #                     relx=0.011)

        # nama file
        self.labelPassFile = Label(self.labelBottom,
                                   text="File: ",
                                   bg="#ABB2B9",
                                   font="Helvetica 10")

        self.labelPassFile.place(relheight=0.02,
                                 rely=0.107,
                                 relx=0.011)

        self.entryFile = Entry(self.labelBottom,
                               bg="#2C3E50",
                               fg="#EAECEE",
                               font="Helvetica 13")

        self.entryFile.place(relwidth=0.74,
                             relheight=0.02,
                             rely=0.1265,
                             relx=0.011)

        self.TextMsg.focus()

        # create a Send Button
        self.buttonMsg = Button(self.labelBottom,
                                text="Kirim",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.sendhandler(receiver, self.TextMsg.get("1.0", 'end-1c')))

        self.buttonMsg.place(relx=0.77,
                             rely=0.004,
                             relheight=0.05,
                             relwidth=0.22)

        # create a MyFile Button
        self.buttonMF = Button(self.labelBottom,
                               text="File Anda",
                               font="Helvetica 10 bold",
                               width=20,
                               bg="#ABB2B9",
                               command=lambda: self.myfilepage(receiver))

        self.buttonMF.place(relx=0.77,
                            rely=0.06,
                            relheight=0.035,
                            relwidth=0.22)

        # create a Send File Button
        self.buttonMsg2 = Button(self.labelBottom,
                                 text="Unggah File",
                                 font="Helvetica 10 bold",
                                 width=20,
                                 bg="#ABB2B9",
                                 command=self.browse_file)

        self.buttonMsg2.place(relx=0.77,
                              rely=0.1,
                              relheight=0.021,
                              relwidth=0.22)

        # create a Send File Button
        self.buttonMsg3 = Button(self.labelBottom,
                                 text="Kirim File",
                                 font="Helvetica 10 bold",
                                 width=20,
                                 bg="#ABB2B9",
                                 command=lambda: self.filehandler(receiver, self.filename))

        self.buttonMsg3.place(relx=0.77,
                              rely=0.126,
                              relheight=0.021,
                              relwidth=0.22)

        self.textCons.config(cursor="arrow")

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)

        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight=1,
                        relx=0.974)

        scrollbar.config(command=self.textCons.yview)

        self.textCons.config(state=DISABLED)

    def sendhandler(self, receiver, text):
        if not (self.TextMsg.get("1.0", 'end-1c') and self.TextMsg.get("1.0", 'end-1c').strip()):
            return tkinter.messagebox.showinfo('Error', 'Pesan tidak boleh kosong')
        self.sendmessage(receiver, text)

    def filehandler(self, receiver, filename):
        if not (self.filename and self.filename.strip()):
            return tkinter.messagebox.showinfo('Error', 'File tidak boleh kosong')
        self.sendfile(receiver, filename)

    def sendgroup(self, username, groupname, group):
        self.isgroup = True
        self.receiverid = group
        self.filename = ""
        # to show chat window
        self.Window.deiconify()
        self.Window.title("Ruangan Grup Chat")
        self.Window.resizable(width=False,
                              height=False)
        self.Window.configure(width=470,
                              height=550,
                              bg="#17202A")
        self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text="Grup Chat " + groupname + " sebagai " + self.name,
                               font="Helvetica 13 bold",
                               pady=5)

        self.labelHead.place(relwidth=1)

        # tombol kembali
        self.buttonBack = Button(self.Window,
                                 text="Bonjour",
                                 font="Helvetica 10 bold",
                                 width=20,
                                 bg="#ABB2B9",
                                 command=lambda: self.backtochatlist(username))

        self.buttonBack.place(relwidth=0.2, relx=0.8)

        # garis
        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")

        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=0.012)

        self.textCons = Text(self.Window,
                             width=20,
                             height=2,
                             bg="#17202A",
                             fg="#EAECEE",
                             font="Helvetica 14",
                             padx=5,
                             pady=5)

        self.textCons.place(relheight=0.585,
                            relwidth=1,
                            rely=0.08)

        self.labelBottom = Label(self.Window,
                                 bg="#ABB2B9",
                                 height=80)

        self.labelBottom.place(relwidth=1,
                               rely=0.66)

        # kolom pesan
        self.TextMsg = Text(self.labelBottom,
                            bg="#2C3E50",
                            fg="#EAECEE",
                            font="Helvetica 13")

        self.labelPassMsg = Label(self.labelBottom,
                                  text="Pesan: ",
                                  bg="#ABB2B9",
                                  font="Helvetica 10")

        self.labelPassMsg.place(relheight=0.02,
                                rely=0,
                                relx=0.011)

        self.TextMsg.place(relwidth=0.74,
                           relheight=0.088,
                           rely=0.02,
                           relx=0.011)

        # kolom receiver

        # self.entryRcv = Entry(self.labelBottom,
        #                       bg="#2C3E50",
        #                       fg="#EAECEE",
        #                       font="Helvetica 13",
        #                       text=receiver)
        # self.labelPassRcv = Label(self.labelBottom,
        #                        text="Penerima: ",
        #                        bg="#ABB2B9",
        #                        font="Helvetica 10")
        #
        # self.labelPassRcv.place(relheight=0.02,
        #                     rely=0,
        #                     relx=0.011)
        #
        # self.entryRcv.place(relwidth=0.74,
        #                     relheight=0.02,
        #                     rely=0.02,
        #                     relx=0.011)

        # nama file
        self.labelPassFile = Label(self.labelBottom,
                                   text="File: ",
                                   bg="#ABB2B9",
                                   font="Helvetica 10")

        self.labelPassFile.place(relheight=0.02,
                                 rely=0.107,
                                 relx=0.011)

        self.entryFile = Entry(self.labelBottom,
                               bg="#2C3E50",
                               fg="#EAECEE",
                               font="Helvetica 13")

        self.entryFile.place(relwidth=0.74,
                             relheight=0.02,
                             rely=0.1265,
                             relx=0.011)

        self.TextMsg.focus()

        # create a Send Button
        self.buttonMsg = Button(self.labelBottom,
                                text="Kirim",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.sendgrouphandler(group, self.TextMsg.get("1.0", 'end-1c')))

        self.buttonMsg.place(relx=0.77,
                             rely=0.004,
                             relheight=0.05,
                             relwidth=0.22)

        # create a MyFile Button
        self.buttonMF = Button(self.labelBottom,
                               text="File Anda",
                               font="Helvetica 10 bold",
                               width=20,
                               bg="#ABB2B9",
                               command=lambda: self.myfilepage(group))

        self.buttonMF.place(relx=0.77,
                            rely=0.06,
                            relheight=0.035,
                            relwidth=0.22)

        # create a Send File Button
        self.buttonMsg2 = Button(self.labelBottom,
                                 text="Unggah File",
                                 font="Helvetica 10 bold",
                                 width=20,
                                 bg="#ABB2B9",
                                 command=self.browse_file)

        self.buttonMsg2.place(relx=0.77,
                              rely=0.1,
                              relheight=0.021,
                              relwidth=0.22)

        # create a Send File Button
        self.buttonMsg3 = Button(self.labelBottom,
                                 text="Kirim File",
                                 font="Helvetica 10 bold",
                                 width=20,
                                 bg="#ABB2B9",
                                 command=lambda: self.filegrouphandler(group, self.filename))

        self.buttonMsg3.place(relx=0.77,
                              rely=0.126,
                              relheight=0.021,
                              relwidth=0.22)

        self.textCons.config(cursor="arrow")

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)

        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight=1,
                        relx=0.974)

        scrollbar.config(command=self.textCons.yview)

        # Capture list user
        userlist = []
        for k, v in users.items():
            for j, l in groups.items():
                if j == group:
                    for i in l['member']:
                        if i == k:
                            userlist.append(v['nama'])

        usergang = ', '.join(userlist)
        self.textCons.insert(END,
                             "Ada " + usergang + " dichat ini" + "\n")

        self.textCons.config(state=DISABLED)

    def sendgrouphandler(self, groupreceiver, text):
        if not (self.TextMsg.get("1.0", 'end-1c') and self.TextMsg.get("1.0", 'end-1c').strip()):
            return tkinter.messagebox.showinfo('Error', 'Pesan Grup tidak boleh kosong')
        self.sendgroupmessage(groupreceiver, text)

    def filegrouphandler(self, groupreceiver, filename):
        if not (self.filename and self.filename.strip()):
            return tkinter.messagebox.showinfo('Error', 'File tidak boleh kosong')
        self.sendgroupfile(groupreceiver, filename)

    def myfilepage(self, receiver):
        self.win = Toplevel()
        self.win.configure(width=400, height=550)
        self.win.configure(bg="#17202A")
        self.win.wm_title("File Anda")
        self.myfile()

        # for k, v in users.items():
        #     # print(k, v)
        #     if (name == k):
        #         self.fullname = v["nama"]
        #         continue
        #     self.buttonperson = Button(self.line,
        #                                text=v["nama"],
        #                                font="Helvetica 10 bold",
        #                                width=20,
        #                                bg="#FFFFFF",
        #                                command=lambda receiver=k, receivername=v["nama"]: self.sendto(name,
        #                                                                                               receivername,
        #                                                                                               receiver))
        #
        #     self.buttonperson.place(relx=0.1,
        #                             rely=0.0008 + x,
        #                             relheight=0.0006,
        #                             relwidth=0.8)
        #     x = x + 0.0008

    def backtochatlist(self, name):
        # self.chatopen = False
        self.receiverid = ""
        self.chatlist(name)

    def getmessage(self):
        while True:
            print(self.inbox().strip())
            time.sleep(1)
            # if self.chatopen == False :
            #     break
            # try:
            #
            #     print(self.inbox().strip())
            # except:
            #     # an error will be printed on the command line or console if there's an error
            #     break

    def browse_file(self):
        self.filelocation = filedialog.askopenfilename(initialdir="/", title="Pilih file",
                                                       filetypes=(("Text files", "*.txt*"), ("all files", "*.*")))
        s = self.filelocation
        self.filename = os.path.basename(s)
        os.chdir(os.path.dirname(s))
        self.entryFile.delete(0, END)
        self.entryFile.insert(0, self.filename)

    def proses(self, cmdline):
        j = cmdline.split(" ")
        try:
            command = j[0].strip()
            if (command == 'auth'):
                username = j[1].strip()
                password = j[2].strip()
                return self.login(username, password)
            elif (command == 'send'):
                usernameto = j[1].strip()
                message = ""
                for w in j[2:]:
                    message = "{} {}".format(message, w)
                return self.sendmessage(usernameto, message)
            elif (command == 'inbox'):
                return self.inbox()
            elif (command == 'send_file'):
                usernameto = j[1].strip()
                filename = j[2].strip()
                return self.sendfile(usernameto, filename)
            elif (command == 'my_file'):
                return self.myfile()
            elif (command == 'download_file'):
                username = j[1].strip()
                filename = j[2].strip()
                return self.downloadfile(username, filename)
                logging.warning("DOWNLOAD: session {} file {}".format(sessionid, filename))
                username = self.sessions[sessionid]['username']
                return self.download_file(sessionid, username, usernameto, filename)
            elif (command == 'send_group'):
                groupto = j[1].strip()
                message = ""
                for w in j[2:]:
                    message = "{} {}".format(message, w)
                return self.sendgroupmessage(groupto, message)
            elif (command == 'send_group_file'):
                groupto = j[1].strip()
                filename = j[2].strip()
                return self.sendgroupfile(groupto, filename)
            else:
                return "*Maaf, command tidak benar"
        except IndexError:
            return "-Maaf, command tidak benar"

    def sendstring(self, string):
        try:
            self.sock.sendall(string.encode())
            receivemsg = ""
            while True:
                data = self.sock.recv(64)
                print("diterima dari server", data)
                if (data):
                    receivemsg = "{}{}".format(receivemsg,
                                               data.decode())  # data harus didecode agar dapat di operasikan dalam bentuk string
                    if receivemsg[-4:] == '\r\n\r\n':
                        print("end of string")
                        return json.loads(receivemsg)
        except:
            self.sock.close()
            return {'status': 'ERROR', 'message': 'Gagal'}

    def login(self, username, password):
        string = "auth {} {} \r\n".format(username, password)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            self.tokenid = result['tokenid']
            return "username {} logged in, token {} ".format(username, self.tokenid)
        else:
            return "Error, {}".format(result['message'])

    def sendmessage(self, usernameto="xxx", message="xxx"):
        if (self.tokenid == ""):
            return "Error, not authorized"
        string = "send {} {} {} \r\n".format(self.tokenid, usernameto, message)
        print(string)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            # insert a new text
            self.textCons.config(state=NORMAL)
            if self.isfile == True:
                self.textCons.insert(END,
                                     self.fullname + " : " + message + "\n")
            else:
                self.textCons.insert(END,
                                     self.fullname + " : " + self.TextMsg.get("1.0", 'end-1c') + "\n")
                self.isfile = False
            self.textCons.config(state=DISABLED)
            self.textCons.see(END)
            # clear msgtext
            self.TextMsg.delete('1.0', END)
            return "message sent to {}".format(usernameto)
        else:
            tkinter.messagebox.showinfo('Error', 'Pesan gagal Dikirim')
            return "Error, {}".format(result['message'])

    def inbox(self):
        if (self.tokenid == ""):
            return "Error, not authorized"
        string = "inbox {} \r\n".format(self.tokenid)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            for k, v in result['messages'].items():
                if v:
                    # if self.isgroup:
                    #     return "PROOO"
                    if k == self.receiverid:
                        self.textCons.config(state=NORMAL)
                        # print(self.isgroup)
                        if self.isgroup:
                            self.textCons.insert(END,
                                                 v[0].get('msg_from') + " :" + v[0].get('msg'))
                        else:
                            self.textCons.insert(END,
                                                 self.receiverwho + " :" + v[0])
                        self.textCons.config(state=DISABLED)
                        self.textCons.see(END)
            return "{}".format(json.dumps(result['messages']))
        else:
            tkinter.messagebox.showinfo('Error', 'Inbox Gagal Dibuka')
            return "Error, {}".format(result['message'])

    def sendfile(self, usernameto, filename):
        if (self.tokenid == ""):
            return "Error, not authorized"
        try:
            file = open(filename, "rb")
        except FileNotFoundError:
            return "Error, {} file not found".format(filename)

        buffer = file.read()
        convertedstring = base64.b64encode(buffer).decode('utf-8')
        message = "send_file {} {} {} {} \r\n".format(self.tokenid, usernameto, filename, convertedstring)
        result = self.sendstring(message)
        if result['status'] == 'OK':
            # check if file + reset location back
            self.isfile = True
            self.sendmessage(usernameto, "Mengirim File " + filename + " ke File Anda")
            self.entryFile.delete(0, END)
            self.filename = ""
            os.chdir(self.initlocation)
            return "file {} sent to {}".format(filename, usernameto)
        else:
            return "Error, {}".format(result['message'])

    def download_file(self, username, filename):
        if (self.tokenid == ""):
            return "Error, not authorized"
        string = "download_file {} {} {} \r\n".format(self.tokenid, username, filename)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            output_file = open(result['filename'], 'wb')
            output_file.write(base64.b64decode(result['data']))
            output_file.close()
            return "{}".format(json.dumps(result['messages']))
        else:
            return "Error, {}".format(result['message'])

    def myfile(self):
        if (self.tokenid == ""):
            return "Error, not authorized"
        string = "my_file {} \r\n".format(self.tokenid)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            for k, v in result['messages'].items():
                if k == self.receiverid:
                    y = 0
                    for ngok in v:
                        ngoks = os.path.basename(ngok)
                        self.buttonperson = Button(self.win,
                                                   text=ngoks,
                                                   font="Helvetica 10 bold",
                                                   width=20,
                                                   bg="#FFFFFF",
                                                   command=lambda receiver=k, filename=ngok: self.downloadd(
                                                       receiver, filename))

                        self.buttonperson.place(relx=0.1,
                                                rely=0.01 + y,
                                                relheight=0.1,
                                                relwidth=0.8)

                        y = y + 0.12
            return "{}".format(json.dumps(result['messages']))
        else:
            return "Error, {}".format(result['message'])

    def downloadd(self, receiverd, filenamed):
        self.win.destroy()
        self.download_file(receiverd, filenamed)
        tkinter.messagebox.showinfo('Error', 'File berhasil diunduh')

    def sendgroupmessage(self, groupto="xxx", message="xxx"):
        if (self.tokenid == ""):
            return "Error, not authorized"
        string = "send_group {} {} {} \r\n".format(self.tokenid, groupto, message)
        print(string)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            # clear msgtext
            self.TextMsg.delete('1.0', END)
            return "message sent to {}".format(groupto)
        else:
            return "Error, {}".format(result['message'])

    def sendgroupfile(self, groupto, filename):
        if (self.tokenid == ""):
            return "Error, not authorized"
        try:
            file = open(filename, "rb")
        except FileNotFoundError:
            return "Error, {} file not found".format(filename)

        buffer = file.read()
        convertedstring = base64.b64encode(buffer).decode('utf-8')
        message = "send_group_file {} {} {} {} \r\n".format(self.tokenid, groupto, filename, convertedstring)
        result = self.sendstring(message)
        if result['status'] == 'OK':
            # check if file + reset location back
            self.isfile = True
            self.sendgroupmessage(self.receiverid, "Mengirim File " + filename + " ke File Anda")
            self.entryFile.delete(0, END)
            self.filename = ""
            os.chdir(self.initlocation)
            return "file {} sent to {}".format(filename, groupto)
        else:
            return "Error, {}".format(result['message'])


if __name__ == "__main__":
    cc = ChatClient()
    while True:
        cmdline = input("Command {}:".format(cc.tokenid))
        print(cc.proses(cmdline))
