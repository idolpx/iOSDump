# iOSDump
Dump contents of an iOS device iTunes backup

![Screen Shot 2017-06-13 at 1.06.17 AM.png](https://s20.postimg.org/v59ebrrh9/Screen_Shot_2017-06-13_at_1.06.17_AM.png) ![Screen Shot 2017-06-13 at 1.08.20 AM.png](https://s20.postimg.org/k4e96qz8d/Screen_Shot_2017-06-13_at_1.08.20_AM.png)

This project was intended to get me familiar with programming in Python & [Kivy](https://kivy.org) and also to help me learn how data is stored in an iTunes backup.

The goal was to dump all of the data from a backup of an iOS device along with an HTML/CSS user interface to simulate the device in a browser to be able to access all of the extracted data.

First make sure you have [Kivy](https://kivy.org) installed.

Then to launch the program with the Kivy UI run the following command.
```
$ python iosdumpui.py
```

To launch the program with a text interface use this command instead.
```
$ python iosdump.py
```

## Currently Extracts the following
* Call History
* Calendar
* Camera Roll Images & Video files
* Contacts
* Notes
* SMS & iMessage Messages (Including Attachments)
* Voice Memos
* Voicemail Messages

## To-Do
* Recover Restriction Passcode
* Extract Browser History & Bookmarks
* Build HTML/CSS device simulators
* Build HTML/CSS app simulators for displaying specific data
* Automatically launch browser with index.html after dump is complete
* Support encrypted & icloud backups
* Show progress in UI during dumping process
* Add option to specify where to dump the data
* Add option to select where backup is stored
  (For selecting backups on a removable/network drive)
* Support plugins for extracting App Specific data
  (Facebook, Messenger, WhatsApp, Kik, Tinder, etc.)
  
I wrote this code a few years ago and I'm still no expert python coder.  If you see a better way to do something I have in here, please let me know.  Anyway, I haven't touched this in a while except to add a few more devices to the list.  I figured I would share it before it got lost forever.  Maybe there are some others out there that want to help complete this project.  I'd like to find some time to work on it some more myself.  Some company and fresh eyes would be nice too though.
