#!/usr/bin/python

import sys
import shutil
import os
import os.path
from os.path import expanduser

import glob
import json
import sqlite3
import tempfile
import datetime
from ios import ios

# Global Variables
selected = -1

# List iTunes Backups
def selectBackup():
	'List all the iOS Backups and prompt for selection'
	global selected

	for i in range(len(iosBackup.backups)):
		iosBackup.select(i)
		print ( str(i) + ":\t" + iosBackup.deviceName + " (" + str(iosBackup.lastBackupDate) + ")" )

	print
	selected = input("Select Backup to Dump: ")
	if len(selected) > 0:
		selected = int(selected)
	else:
		selected = 0
		
	if selected < 0 or selected > len(iosBackup.backups) - 1:
		print ( "Invalid Selection!" )
	else:
		iosBackup.select(selected)
		print ( "You selected: " + str(selected) + " - " + iosBackup.deviceName + " (" + str(iosBackup.lastBackupDate) + ")" )
		iosDumpData(selected)

def cleanFolder(folder):
	for the_file in os.listdir(folder):
		file_path = os.path.join(folder, the_file)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
			else:
				shutil.rmtree(file_path)
		except Exception as e:
			print ( e )

def iosDumpData(selection):
	iosBackup.index = selection

	# Clean Up Previous Dump
	if not os.path.exists(outputFolder):
		os.mkdir(outputFolder, 755)
	else:
		cleanFolder(outputFolder)

		os.mkdir(outputFolder + "contacts", 755)
		os.mkdir(outputFolder + "db", 755)
		os.mkdir(outputFolder + "roll", 755)
		os.mkdir(outputFolder + "rec", 755)
		os.mkdir(outputFolder + "sms", 755)
		os.mkdir(outputFolder + "vm", 755)


	#print ( ios.dbRecordings
	#print ( iosBackup.deviceName(0) + " (" + iosBackup.backups[0] + ")"
	print ( outputFolder )
	print ( iosBackup.path() )

	# Copy Database Files to Output Folder
	if os.path.exists(iosBackup.path() + ios.dbAddressBook):
		shutil.copyfile(iosBackup.path() + ios.dbAddressBook, outputFolder + "db/AddressBook.sqlite")
	if os.path.exists(iosBackup.path() + ios.dbAddressBookImages):
		shutil.copyfile(iosBackup.path() + ios.dbAddressBookImages, outputFolder + "db/AddressBookImages.sqlite")
	if os.path.exists(iosBackup.path() + ios.dbCalendar):
		shutil.copyfile(iosBackup.path() + ios.dbCalendar, outputFolder + "db/Calendar.sqlite")
	if os.path.exists(iosBackup.path() + ios.dbCallHistory):
		shutil.copyfile(iosBackup.path() + ios.dbCallHistory, outputFolder + "db/call_history.sqlite")
	if os.path.exists(iosBackup.path() + ios.dbNotes):
		shutil.copyfile(iosBackup.path() + ios.dbNotes, outputFolder + "db/notes.sqlite")
	if os.path.exists(iosBackup.path() + ios.dbPhotos):
		shutil.copyfile(iosBackup.path() + ios.dbPhotos, outputFolder + "db/Photos.sqlite")
	if os.path.exists(iosBackup.path() + ios.dbRecordings):
		shutil.copyfile(iosBackup.path() + ios.dbRecordings, outputFolder + "db/Recordings.sqlite")
	if os.path.exists(iosBackup.path() + ios.dbSMS):
		shutil.copyfile(iosBackup.path() + ios.dbSMS, outputFolder + "db/sms.sqlite")
	if os.path.exists(iosBackup.path() + ios.dbVoicemail):
		shutil.copyfile(iosBackup.path() + ios.dbVoicemail, outputFolder + "db/voicemail.sqlite")

	print ( "Dumping SMS Messages" )
	iosBackup.dumpSMS(outputFolder, "sms.json")

	print ( "Dumping Call History" )
	iosBackup.dumpCallHistory(outputFolder + "callhistory.json")

	print ( "Dumping Address Book" )
	iosBackup.dumpAddressBook(outputFolder)

	print ( "Dumping Voicemail" )
	iosBackup.dumpVoicemail(outputFolder, "voicemail.json")

	print ( "Dumping Voice Memos" )
	iosBackup.dumpMemos(outputFolder, "recordings.json")

	print ( "Dumping Camera Roll" )
	iosBackup.dumpCameraRoll(outputFolder, "cameraroll.json")

	print ( "Dumping Notes" )
	iosBackup.dumpNotes(outputFolder + "notes.json")

	print ( "Dump Complete!" )

	os.system("open " + outputFolder)




iosBackup = ios()
#outputFolder = expanduser("~") + "/Desktop/iOSDump/"
outputFolder = expanduser(".") + "/dump/"
if __name__ == "__main__":
	# Initialize Objects & Set Output Folder
	if not os.path.exists(outputFolder):
		os.mkdir(outputFolder, 755)
	else:
		cleanFolder(outputFolder)


	print ( "\nWhich iTunes Backup would you like to dump?\n" )
	selectBackup()
