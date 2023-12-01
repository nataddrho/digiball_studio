from tkinter import *
from tkinter.ttk import *
from datetime import datetime

class AlignmentDialog:

    def __init__(self, window, tags, video_time, dataLog):
        self.dataLog = dataLog
        self.dialog = Toplevel(window)
        self.dialog.resizable(False, False)
        self.dialog.title("Align data to video time %.3fs"%video_time)
        self.date_format = "%H:%M:%S %m/%d/%Y"
        self.video_time = video_time

        frame1 = Frame(self.dialog, borderwidth=2, relief=GROOVE)
        frame1.pack(padx = 10, pady = 10)

        label = Label(frame1, text="Select Tag")
        label.pack()

        scroll_tags = Scrollbar(frame1)
        scroll_tags.pack(side=RIGHT, fill=Y)

        self.list_tags = Listbox(frame1, width=50, yscrollcommand = scroll_tags.set)
        i = 1
        for j in range(0,len(tags)):
            N = len(tags)-j-1
            tag = tags[N]
            epoch = tag['epoch']
            tagname = tag['tag']
            dt = datetime.fromtimestamp(epoch/1000).strftime(self.date_format)
            liststr = "%s - %s"%(dt,tagname)
            self.list_tags.insert(i,liststr)
            i += 1



        self.list_tags.pack(side=LEFT, fill=BOTH)
        scroll_tags.config(command=self.list_tags.yview)

        frame1a = Frame(self.dialog)
        frame1a.pack()

        self.btn_tags = Button(frame1a, text='Align', command=self.button_tags)
        self.btn_tags.pack()

        frame2 = Frame(self.dialog)
        frame2.pack(padx = 10, pady = 10)

        label = Label(frame2, text="H:M:S M/D/YY")
        label.grid(row = 0, column = 0)

        self.entry_datetime = Entry(frame2, width=30)
        self.entry_datetime.grid(row = 0, column = 1, padx = 3, pady = 3)

        btn_datetime = Button(frame2, text='Align', command=self.button_datetime)
        btn_datetime.grid(row=0, column=2, padx=3, pady=3)

        label = Label(frame2, text="Epoch (ms)")
        label.grid(row = 1, column = 0)

        self.entry_epoch = Entry(frame2, width=30)
        self.entry_epoch.grid(row = 1, column = 1, padx = 3, pady = 3)

        btn_epoch = Button(frame2, text='Align', command=self.button_epoch)
        btn_epoch.grid(row = 1, column = 2, padx = 3, pady = 3)

        btn_close = Button(frame2, text='Close', command=self.dialog.destroy)
        btn_close.grid(row=2, column=2, padx=3, pady=3)

        frame3 = Frame(self.dialog)
        frame3.pack(padx=10, pady=10)

        self.message = Label(frame3, text="Click Align or Close.")
        self.message.pack()

    def button_tags(self):
        selection = self.list_tags.curselection()
        if len(selection)>0:
            value = self.list_tags.get(selection[0])
            date_str = value.split('-')[0].strip(' ')
            dtr = datetime.strptime(date_str, self.date_format)
            starting_epoch = int((dtr.timestamp() - self.video_time) * 1000)
            print(starting_epoch)
            self.dataLog.align_to_starting_epoch(starting_epoch)
            self.message.config(text="Successfully aligned to %s. Click Close." % date_str)
        else:
            self.message.config(text="No tag selected.")
            return

    def button_epoch(self):

        epoch_text = self.entry_epoch.get()
        try:
            epoch = int(epoch_text)
        except:
            self.message.config(text = "Invalid epoch (timestamp) format.")
            return

        starting_epoch = epoch - int(self.video_time*1000)
        print(starting_epoch)
        self.dataLog.align_to_starting_epoch(starting_epoch)
        self.message.config(text="Successfully aligned to %s. Click Close."%epoch)


    def button_datetime(self):

        date_str = self.entry_datetime.get()
        try:
            dtr = datetime.strptime(date_str, self.date_format)
        except:
            self.message.config(text = "Invalid date format.")
            return

        starting_epoch = int((dtr.timestamp() - self.video_time) * 1000)
        print(starting_epoch)
        self.dataLog.align_to_starting_epoch(starting_epoch)
        self.message.config(text="Successfully aligned to %s. Click Close."%date_str)







