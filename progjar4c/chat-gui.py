import socket
import os
import json
import tkinter
from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, filedialog, messagebox, \
    Toplevel


TARGET_IP = "127.0.0.1"
TARGET_PORT = 8889


class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP, TARGET_PORT)
        self.sock.connect(self.server_address)
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
                         command=lambda: self.goAhead(self.entryName.get(), self.entryPass.get()))

        self.go.place(relx=0.4,
                      rely=0.7)
        self.Window.mainloop()

    def goAhead(self, username, password):
        self.loginpage.destroy()
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
            self.sendto(username);

    def sendto(self, name):
        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=False,
                              height=False)
        self.Window.configure(width=470,
                              height=550,
                              bg="#17202A")
        self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text=self.name,
                               font="Helvetica 13 bold",
                               pady=5)

        self.labelHead.place(relwidth=1)
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

        self.textCons.place(relheight=0.745,
                            relwidth=1,
                            rely=0.08)

        self.labelBottom = Label(self.Window,
                                 bg="#ABB2B9",
                                 height=80)

        self.labelBottom.place(relwidth=1,
                               rely=0.66)

        self.entryMsg = Entry(self.labelBottom,
                              bg="#2C3E50",
                              fg="#EAECEE",
                              font="Helvetica 13")

        # kolom pesan
        self.labelPassMsg = Label(self.labelBottom,
                               text="Pesan: ",
                               bg="#ABB2B9",
                               font="Helvetica 10")

        self.labelPassMsg.place(relheight=0.02,
                            rely=0.038,
                            relx=0.011)

        self.entryMsg.place(relwidth=0.74,
                            relheight=0.05,
                            rely=0.058,
                            relx=0.011)

        self.entryRcv = Entry(self.labelBottom,
                              bg="#2C3E50",
                              fg="#EAECEE",
                              font="Helvetica 13")

        # kolom receiver
        self.labelPassRcv = Label(self.labelBottom,
                               text="Penerima: ",
                               bg="#ABB2B9",
                               font="Helvetica 10")

        self.labelPassRcv.place(relheight=0.02,
                            rely=0,
                            relx=0.011)

        self.entryRcv.place(relwidth=0.74,
                            relheight=0.02,
                            rely=0.02,
                            relx=0.011)

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

        self.entryMsg.focus()

        # create a Send Button
        self.buttonMsg = Button(self.labelBottom,
                                text="Send",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.sendmessage(self.entryRcv.get(), self.entryMsg.get()))

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
                                command= self.browse_file)

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
            return "message sent to {}".format(usernameto)
        else:
            tkinter.messagebox.showinfo('Error', 'Username tidak ditemukan')
            return "Error, {}".format(result['message'])

    def inbox(self):
        if (self.tokenid == ""):
            return "Error, not authorized"
        string = "inbox {} \r\n".format(self.tokenid)
        result = self.sendstring(string)
        if result['status'] == 'OK':
            return "{}".format(json.dumps(result['messages']))
        else:
            return "Error, {}".format(result['message'])


if __name__ == "__main__":
    cc = ChatClient()
    while True:
        cmdline = input("Command {}:".format(cc.tokenid))
        print(cc.proses(cmdline))
