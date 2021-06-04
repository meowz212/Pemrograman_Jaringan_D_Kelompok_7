import json
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
users = {}
users = chat.getuser()


class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP, TARGET_PORT)
        self.sock.connect(self.server_address)
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
                         text="Please login to continue",
                         font="Helvetica 14 bold")

        self.pls.place(relheight=0.15,
                       relx=0.2,
                       rely=0.07)
        # create a Label
        self.labelName = Label(self.loginpage,
                               text="Name: ",
                               font="Helvetica 12")

        self.labelName.place(relheight=0.2,
                             relx=0.1,
                             rely=0.2)

        # create a entry box for
        self.entryName = Entry(self.loginpage,
                               font="Helvetica 14")

        self.entryName.place(relwidth=0.4,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.2)

        # create a Label pass
        self.labelPass = Label(self.loginpage,
                               text="Pass: ",
                               font="Helvetica 12")

        self.labelPass.place(relheight=0.2,
                             relx=0.1,
                             rely=0.4)

        # create a entry box for pass
        self.entryPass = Entry(self.loginpage,
                               font="Helvetica 14")

        self.entryPass.place(relwidth=0.4,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.4)

        # set the focus of the curser
        self.entryName.focus()

        # create a Continue Button
        # along with action
        self.go = Button(self.loginpage,
                         text="CONTINUE",
                         font="Helvetica 14 bold",
                         command=lambda: self.loginto(self.entryName.get(), self.entryPass.get()))

        self.go.place(relx=0.4,
                      rely=0.7)
        self.Window.mainloop()

    def loginto(self, username, password):
        self.loginpage.destroy()

        # start receiving msg
        # self.chatopen = True
        self.rcv.start()

        x = self.login(username, password).strip();
        print(x)
        if (x == "Error, User Tidak Ada"):
            tkinter.messagebox.showinfo('Error', 'Nama tidak ada')
            self.loginpage.destroy()
            self.initialize_login()
        elif (x == "Error, Password Salah"):
            tkinter.messagebox.showinfo('Error', 'Password salah')
            self.loginpage.destroy()
            self.initialize_login()
        else:
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
                              height=550,
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
                               text="List Chat",
                               bg="#ABB2B9",
                               font="Helvetica 20")

        self.labelchat.place(relheight=0.0005,
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

        self.buttonperson = Button(self.line,
                                   text="Buat atau Join Grup",
                                   font="Helvetica 10 bold",
                                   width=20,
                                   bg="#FFFFFF",
                                   command=lambda receiver=k, receivername=v["nama"]: self.sendto(name, receivername,
                                                                                                  receiver))

        self.buttonperson.place(relx=0.1,
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

    def sendto(self, username, receivername, receiver):
        self.receiverwho = receivername
        self.receiverid = receiver
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
                               text="Chat " + receivername,
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

        self.textCons.place(relheight=0.545,
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
                                text="Send",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.sendmessage(receiver, self.TextMsg.get("1.0", 'end-1c')))

        self.buttonMsg.place(relx=0.77,
                             rely=0.008,
                             relheight=0.06,
                             relwidth=0.22)

        # create a Send File Button
        self.buttonMsg2 = Button(self.labelBottom,
                                 text="Attach File",
                                 font="Helvetica 10 bold",
                                 width=20,
                                 bg="#ABB2B9",
                                 command=self.browse_file)

        self.buttonMsg2.place(relx=0.77,
                              rely=0.077,
                              relheight=0.03,
                              relwidth=0.22)

        # create a Send File Button
        self.buttonMsg3 = Button(self.labelBottom,
                                 text="Send File",
                                 font="Helvetica 10 bold",
                                 width=20,
                                 bg="#ABB2B9",
                                 command=lambda: self.sendmessage(self.entryRcv.get(), self.entryFile.get()))

        self.buttonMsg3.place(relx=0.77,
                              rely=0.118,
                              relheight=0.03,
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

    def backtochatlist(self, name):
        # self.chatopen = False
        self.receiverid = ""
        self.chatlist(name)

    def getmessage(self):
        while True:
            print(self.inbox().strip())
            time.sleep(3)
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
        self.entryFile.delete(0, END)
        self.entryFile.insert(0, self.filename)
        # self.entryFile.configure(text="File : " + self.filename)

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
            self.textCons.insert(END,
                                 self.fullname + " : " + self.TextMsg.get("1.0", 'end-1c') + "\n")

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
                    if k == self.receiverid:
                        # print(" ".format(json.dumps(v[0])))
                        self.textCons.config(state=NORMAL)
                        self.textCons.insert(END,
                                             self.receiverwho + " :" + v[0].get('msg'))

                        self.textCons.config(state=DISABLED)
                        self.textCons.see(END)
            return "{}".format(json.dumps(result['messages']))
        else:
            tkinter.messagebox.showinfo('Error', 'Inbox Gagal Dibuka')
            return "Error, {}".format(result['message'])


if __name__ == "__main__":
    cc = ChatClient()
    while True:
        cmdline = input("Command {}:".format(cc.tokenid))
        print(cc.proses(cmdline))
