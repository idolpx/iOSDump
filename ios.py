#!/usr/bin/python

# http://www.imactools.com/iphonebackupviewer/
# http://www.securitylearn.net/2012/05/05/iphone-backup-mbdb-file-structure/
# http://www.securitylearn.net/tag/iphone-backups-decrypting-the-keychain/
# https://theiphonewiki.com/wiki/ITunes_Backup
# http://www.mobile60s.com/iphone/jailbreaks-and-ios-hacks/list-of-files-and-their-roles-in-itunes-backups-and-how-to-use-them-54158.html
# http://codepen.io/samuelkraft/pen/Farhl
# http://stackoverflow.com/questions/3085153/how-to-parse-the-manifest-mbdb-file-in-an-ios-4-0-itunes-backup
# http://linuxsleuthing.blogspot.com/2012/10/whos-texting-ios6-smsdb.html
# http://www.securitylearn.net/2012/10/27/cookies-binarycookies-reader/
# http://www.slideshare.net/ohprecio/iphone-forensics-without-iphone-using-itunes-backup


import shutil
import os
import os.path
from os.path import expanduser

import re
import base64
import hashlib
import json
import sqlite3
import tempfile
from biplist import *

# Setup Global Vars
path = expanduser("~") + "/Library/Application Support/MobileSync/Backup/"



# iOS Specific Filenames
plistKeyChain = 'KeychainDomain-keychain-backup.plist'								# 51a4616e576dd33cd2abadfea874eb8ff246bf0e
plistHistory = 'HomeDomain-Library/Safari/History.plist'
plistRestrictions = 'HomeDomain-Library/Preferences/com.apple.springboard.plist'

dbSMS = 'HomeDomain-Library/SMS/sms.db'												# 3d0d7e5fb2ce288813306e4d4636395e047a3d28
dbAddressBook = 'HomeDomain-Library/AddressBook/AddressBook.sqlitedb'				# 31bb7ba8914766d4ba40d6dfb6113c8b614be442
dbAddressBookImages = 'HomeDomain-Library/AddressBook/AddressBookImages.sqlitedb' 	# cd6702cea29fe89cf280a76794405adb17f9a0ee
dbCallHistory = 'WirelessDomain-Library/CallHistory/call_history.db'				# 2b2b0084a1bc3a5ac8c27afdf14afb42c61a19ca
dbNotes = 'HomeDomain-Library/Notes/notes.sqlite'									# ca3bc056d4da0bbf88b5fb3be254f3b7147e639c
dbCalendar = 'HomeDomain-Library/Calendar/Calendar.sqlitedb'						# 2041457d5fe04d39d0ab481178355df6781e6858
dbVoicemail = 'HomeDomain-Library/Voicemail/voicemail.db'							# 992df473bbb9e132f4b3b6e4d33f72171e97bc7a
dbPhotos = 'CameraRollDomain-Media/PhotoData/Photos.sqlite'							# 12b144c0bd44f2b3dffd9186d3f9c05b917cee25
dbRecordings = 'MediaDomain-Media/Recordings/Recordings.db'							# 303e04f2a5b473c5ca2127d65365db4c3e055c05
dbBookmarks = 'HomeDomain-Library/Safari/Bookmarks.db'
dbLocations = ''

class ios:
	'Base class for all iOS backup file functions'

	# Device Model Strings
	devices = {
				"iPhone1,1": "iPhone",
				"iPhone1,2": "iPhone 3",
				"iPhone2,1": "iPhone 3GS",
				"iPhone3,1": "iPhone 4",
				"iPhone3,2": "iPhone 4",
				"iPhone3,3": "iPhone 4",
				"iPhone4,1": "iPhone 4S",
				"iPhone5,1": "iPhone 5",
				"iPhone5,2": "iPhone 5",
				"iPhone5,3": "iPhone 5C",
				"iPhone5,4": "iPhone 5C",
				"iPhone6,1": "iPhone 5S",
				"iPhone6,2": "iPhone 5S",
				"iPhone7,2": "iPhone 6",
				"iPhone7,1": "iPhone 6 Plus",
				"iPhone8,1": "iPhone 6S"
				"iPhone8,2": "iPhone 6S Plus"
				"iPhone8,4": "iPhone SE"
				"iPhone9,1": "iPhone 7"
				"iPhone9,3": "iPhone 7"
				"iPhone9,2": "iPhone 7 Plus"
				"iPhone9,4": "iPhone 7 Plus"
				"iPod1,1": "iPod Touch 1G",
				"iPod2,1": "iPod Touch 2G",
				"iPod3,1": "iPod Touch 3G",
				"iPod4,1": "iPod Touch 4G",
				"iPod5,1": "iPod Touch 5G",
				"iPod7,1": "iPod Touch 6G",
				"iPad1,1": "iPad",
				"iPad2,1": "iPad 2",
				"iPad2,2": "iPad 2",
				"iPad2,3": "iPad 2",
				"iPad2,4": "iPad 2",
				"iPad3,1": "iPad 3",
				"iPad3,2": "iPad 3",
				"iPad3,3": "iPad 3",
				"iPad3,4": "iPad 4",
				"iPad3,5": "iPad 4",
				"iPad3,6": "iPad 4",
				"iPad4,1": "iPad Air",
				"iPad4,2": "iPad Air",
				"iPad4,3": "iPad Air",
				"iPad5,3": "iPad Air 2",
				"iPad5,4": "iPad Air 2",
				"iPad6,11": "iPad (2017)",
				"iPad6,12": "iPad (2017)",
				"iPad2,5": "iPad Mini",
				"iPad2,6": "iPad Mini",
				"iPad2,7": "iPad Mini",
				"iPad4,4": "iPad Mini 2",
				"iPad4,5": "iPad Mini 2",
				"iPad4,6": "iPad Mini 2",
				"iPad4,7": "iPad Mini 3",
				"iPad4,8": "iPad Mini 3",
				"iPad4,9": "iPad Mini 3",
				"iPad5,1": "iPad Mini 4",
				"iPad5,2": "iPad Mini 4",
				"iPad6,7": "iPad Pro (12.9in)",
				"iPad6,8": "iPad Pro (12.9in)",
				"iPad6,3": "iPad Pro (9.7in)",
				"iPad6,4": "iPad Pro (9.7in)"
			}

	deviceType = ''
	deviceModel = ''
	productType = ''
	productVersion = ''
	serialNumber = ''
	deviceName = ''
	lastBackupDate = ''
	targetIdentifier = ''

	# Hash iOS Filenames
	plistKeyChain = hashlib.sha1(plistKeyChain).hexdigest()
	plistHistory = hashlib.sha1(plistHistory).hexdigest()
	plistRestrictions = hashlib.sha1(plistRestrictions).hexdigest()

	dbSMS = hashlib.sha1(dbSMS).hexdigest()
	dbAddressBook = hashlib.sha1(dbAddressBook).hexdigest()
	dbAddressBookImages = hashlib.sha1(dbAddressBookImages).hexdigest()
	dbCallHistory = hashlib.sha1(dbCallHistory).hexdigest()
	dbNotes = hashlib.sha1(dbNotes).hexdigest()
	dbCalendar = hashlib.sha1(dbCalendar).hexdigest()
	dbVoicemail = hashlib.sha1(dbVoicemail).hexdigest()
	dbPhotos = hashlib.sha1(dbPhotos).hexdigest()
	dbRecordings = hashlib.sha1(dbRecordings).hexdigest()

	def __init__(self):
		self.index = 0
		self.backups = os.listdir(path)

	def select(self, index):
		self.index = index
		plistInfo = path + self.backups[index] + "/Info.plist"
		if os.path.exists(plistInfo):
			try:
				info = readPlist(plistInfo)
				m = re.match("(.*?)\d", info['Product Type'])
				self.deviceType = m.group(1)
				self.deviceModel = self.devices[info['Product Type']]
				self.productType = info['Product Type'].replace(',', '').lower()
				self.productVersion = info['Product Version']
				self.serialNumber = info['Serial Number']
				self.deviceName = info['Device Name']
				self.lastBackupDate = info['Last Backup Date']
				self.targetIdentifier = info['Target Identifier']
			except Exception, e:
				print e

		#self.dumpRestrictionPasscode(index)

	# Return Backup Path
	def path(self, index=-1):
		if index == -1:
			backup = path + self.backups[self.index] + "/"
		else:
			backup = path + self.backups[index] + "/"

		return backup


# Dump Restriction Passcode

	def dumpRestrictionPasscode(self, index):
		plistRestrictions = path + self.backups[index] + "/" + self.plistRestrictions
		#print "Restriction Passcode: " + plistRestrictions
		if os.path.exists(plistRestrictions):
			try:
				info = readPlist(plistRestrictions)
				self.restrictionPasscode = info['SBParentalControlsPIN']
				self.restrictionFailedAttempts = info['SBParentalControlsFailedAttempts']
				#print "Restriction Passcode: " + info['SBParentalControlsPIN']
				#print "Restriction Passcode: " + info['SBParentalControlsFailedAttempts']
			except Exception, e:
				print e

# SMS, MMS, iMessages, and iMessage/FaceTime settings
# HomeDomain
# Library/Preferences/com.apple.imservice*
# Library/Preferences/com.apple.madrid.plist
# Library/Preferences/com.apple.MobileSMS.plist
# Library/SMS/*
# Library/SMS/Attachments/[random string associated with an MMS]/[MMS file name].[extension] - An MMS file
# Library/SMS/Attachments/[random string associated with an MMS]/[MMS file name]-preview-left.jpg - A preview/thumbnail of an MMS file

	def dumpSMS(self, path, filename):

		# iOS < v7 - Database Extraction
		try:
			print "SMS Database: " + self.path() + self.dbSMS
			db = sqlite3.connect(self.path() + self.dbSMS)
			cursor = db.cursor()

			try:
				sql = '''SELECT message.ROWID,
							message.flags,
							ifnull(message.address,'') || ifnull(madrid_handle,'') as address,
							message.subject,
							message.text,
							message.group_id,
							message.recipients,
							message.read,
							message.association_id,
							message.UIFlags,
							datetime(message.date+978307200, 'unixepoch', 'localtime') as 'date'
						FROM message
						WHERE message.text is not NULL
						ORDER BY message.date'''

				cursor.execute(sql)

				with open(path + filename, 'w') as outfile:
					json.dump(cursor.fetchall(), outfile, default=base64.b64encode)

			except Exception as e:
				print e

			try:
				# No 'madrid_handle' field in message table
				sql = '''SELECT message.ROWID,
							message.flags,
							message.address as address,
							message.subject,
							message.text,
							message.group_id,
							message.recipients,
							message.read,
							message.association_id,
							message.UIFlags,
							datetime(message.date+978307200, 'unixepoch', 'localtime') as 'date'
						FROM message
						WHERE message.text is not NULL
						ORDER BY message.date'''

				cursor.execute(sql)

				with open(path + filename, 'w') as outfile:
					json.dump(cursor.fetchall(), outfile, default=base64.b64encode)

			except Exception as e:
				print e


			try:
				# Dump SMS Message Group Data
				sql = "SELECT * FROM msg_group"
				cursor.execute(sql)
				print "msg_group: " + path + "sms_group.json"
				with open(path + "sms_group.json", 'w') as outfile:
					json.dump(cursor.fetchall(), outfile, default=base64.b64encode)
			except Exception as e:
				print e

			try:
				# Dump SMS Attachment Data
				sql = "SELECT * FROM msg_pieces"
				cursor.execute(sql)
				print "msg_pieces: " + path + "sms_pieces.json"
				with open(path + "sms_pieces.json", 'w') as outfile:
					json.dump(cursor.fetchall(), outfile, default=base64.b64encode)
			except Exception as e:
				print e

			db.close()

			try:
				# Save all SMS Attachments iOS < 6.0
				sql = "SELECT * FROM msg_pieces"
				db = sqlite3.connect(self.path() + self.dbSMS)
				db.row_factory = sqlite3.Row
				cursor = db.cursor()
				cursor.execute(sql)
				for row in cursor:
					if row['content_loc'] is not None:
						# Write each attachment out to the sms folder
						f = "MediaDomain-Library/SMS/Attachments/" + row['content_loc']
						print f
						f = self.path() + hashlib.sha1(f).hexdigest()
						print f
						if os.path.exists(f):
							shutil.copyfile(f, path + "sms/" + row['content_loc'])

				db.close()
			except Exception as e:
				print e

		except Exception as e:
			print e



		# iOS >= v6 - Database Extraction
		try:
			print "SMS Database: " + self.path() + self.dbSMS
			db = sqlite3.connect(self.path() + self.dbSMS)
			cursor = db.cursor()

			sql = '''SELECT chat_message_join.chat_id as id,
						handle.id as contact_id,
						message.is_from_me,
						message.text,
						chat.state,
						message.is_read,
						message.is_sent,
						datetime(message.date+978307200, 'unixepoch', 'localtime') as 'date',
						datetime(message.date_read+978307200, 'unixepoch', 'localtime') as 'date_read',
						datetime(message.date_delivered+978307200, 'unixepoch', 'localtime') as 'date_delivered'
					FROM chat INNER JOIN chat_message_join ON chat.ROWID = chat_message_join.chat_id
						 INNER JOIN message ON chat_message_join.message_id = message.ROWID
						 INNER JOIN chat_handle_join ON chat.ROWID = chat_handle_join.chat_id AND chat_handle_join.handle_id = handle.ROWID,
						handle
					ORDER BY chat_message_join.chat_id, message.date'''

			cursor.execute(sql)

			with open(path + filename, 'w') as outfile:
				json.dump(cursor.fetchall(), outfile, default=base64.b64encode)

			try:
				# Dump SMS Message Group Data
				sql = "SELECT * FROM chat"
				cursor.execute(sql)
				print "chat: " + path + "sms_chat.json"
				with open(path + "sms_chat.json", 'w') as outfile:
					json.dump(cursor.fetchall(), outfile, default=base64.b64encode)
			except Exception as e:
				print e

			try:
				# Dump SMS Attachment Data
				sql = "SELECT * FROM attachment"
				cursor.execute(sql)
				print "attachment: " + path + "sms_attachment.json"
				with open(path + "sms_attachment.json", 'w') as outfile:
					json.dump(cursor.fetchall(), outfile, default=base64.b64encode)
			except Exception as e:
				print e

			db.close()

			try:
				# Save all SMS Attachments
				sql = "SELECT * FROM attachment"
				db = sqlite3.connect(self.path() + self.dbSMS)
				db.row_factory = sqlite3.Row
				cursor = db.cursor()
				cursor.execute(sql)
				for row in cursor:
					if row['filename'] is not None:
						# Write each attachment out to the sms folder
						f = row['filename']
						f = f.replace("/var/mobile/", "MediaDomain-")
						f = f.replace("~/", "MediaDomain-")
						#print f
						f = self.path() + hashlib.sha1(f).hexdigest()
						#print f
						if os.path.exists(f):
							head, tail = os.path.split(row['filename'])
							shutil.copyfile(f, path + "sms/" + tail)

				db.close()
			except Exception as e:
				print e

		except Exception as e:
			print e



# Contacts
# HomeDomain
# Library/AddressBook/*

	def dumpAddressBook(self, path):
		try:
			print "Address Book Database: " + self.path() + self.dbAddressBook
			dbAB = sqlite3.connect(self.path() + self.dbAddressBook)
			cursorAB = dbAB.cursor()

			sql = '''SELECT ABPerson.ROWID as id,
								ABPerson.DisplayName,
								ABPerson.First,
								ABPerson.Middle,
								ABPerson.Last,
								ABPerson.Nickname,
								ABPerson.Organization,
								ABPerson.Department,
								ABPerson.JobTitle,
								ABPerson.Note,
								ABPerson.Birthday,
								ABPersonFullTextSearch_content.c15Phone,
								ABPersonFullTextSearch_content.c16Email,
								ABPersonFullTextSearch_content.c18SocialProfile,
								ABPersonFullTextSearch_content.c19URL,
								datetime(ABPerson.CreationDate+978307200, 'unixepoch', 'localtime') AS creation_date,
								datetime(ABPerson.ModificationDate+978307200, 'unixepoch', 'localtime') AS modified_date
							FROM ABPerson INNER JOIN ABPersonFullTextSearch_content ON ABPerson.ROWID = ABPersonFullTextSearch_content.docid
							ORDER BY ABPerson.ROWID'''

			cursorAB.execute(sql)
			with open(path + "contacts.json", 'w') as outfile:
				json.dump(cursorAB.fetchall(), outfile, default=base64.b64encode)


			try:
				sql = "SELECT * FROM ABMultiValueEntry" # WHERE parent_id = 1 Order By 'key'"
				cursorAB.execute(sql)
				with open(path + "contact_address.json", 'w') as outfile:
					json.dump(cursorAB.fetchall(), outfile, default=base64.b64encode)
			except Exception as e:
				print e

			try:
				sql = "SELECT * FROM ABMultiValue" # WHERE record_id = 1 Order By label"
				cursorAB.execute(sql)
				with open(path + "contact_phone_email.json", 'w') as outfile:
					json.dump(cursorAB.fetchall(), outfile, default=base64.b64encode)
			except Exception as e:
				print e

			dbAB.close()
		except Exception as e:
			print e


		# Dump Address Book Images
		try:
			dbABI = sqlite3.connect(self.path() + self.dbAddressBookImages)
			dbABI.row_factory = sqlite3.Row
			cursorABI = dbABI.cursor()


			sql = "SELECT * FROM ABFullSizeImage" # WHERE record_id = 1"
			cursorABI.execute(sql)
			for row in cursorABI:
				# Write each image out to the contacts folder
				print path + "contacts/%s.jpg" % row['record_id']
				f = open(path + "contacts/" + str(row['record_id']) + ".jpg", "w")
				f.write(row['data'])
				f.close()

			dbABI.close()
		except Exception as e:
			print e



# Call History
# WirelessDomain
# Library/CallHistory/*

	def dumpCallHistory(self, filename):
		try:
			print "Call History Database: " + self.path() + self.dbCallHistory
			db = sqlite3.connect(self.path() + self.dbCallHistory)
			cursor = db.cursor()

			sql = '''SELECT  call.ROWID as id,
						call.id as contact_id,
						call.address,
						call.duration,
						call.flags,
						datetime(call.date+978307200, 'unixepoch', 'localtime') as 'date'
					FROM call
					ORDER BY call.date'''

			cursor.execute(sql)

			with open(filename, 'w') as outfile:
				json.dump(cursor.fetchall(), outfile, default=base64.b64encode)

			db.close()
		except Exception as e:
			print e

# Calendar
# HomeDomain
# Library/Calendar/* <-The asterisk (*) means all files inside that folder
# Library/Preferences/com.apple.mobilecal*

	def dumpCalendar(self, filename):
		try:
			print "Calendar Database: " + self.path() + self.dbCalendar
			db = sqlite3.connect(self.path() + self.dbCalendar)
			cursor = db.cursor()

			sql = '''SELECT ZNOTE.ZBODY as id,
						ZNOTE.ZTITLE as title,
						ZNOTE.ZSUMMARY as summary,
						ZNOTEBODY.ZCONTENT as content,
						ZNOTE.ZDELETEDFLAG as deleted,
						datetime(ZNOTE.ZCREATIONDATE+978307200, 'unixepoch', 'localtime') as 'creation_date',
						datetime(ZNOTE.ZMODIFICATIONDATE+978307200, 'unixepoch', 'localtime') as 'modified_date'
					FROM ZNOTE INNER JOIN ZNOTEBODY ON ZNOTE.Z_PK = ZNOTEBODY.ZOWNER
					ORDER BY ZNOTE.ZCREATIONDATE'''

			cursor.execute(sql)

			with open(filename, 'w') as outfile:
				json.dump(cursor.fetchall(), outfile, default=base64.b64encode)

			db.close()
		except Exception as e:
			print e


# Camera Roll - When replacing, you should delete all files in the respected folders first
# CameraRollDomain
# Media/DCIM/*
# Media/PhotoData/*
# Library/Preferences/com.apple.mobileslideshow.plist
# Media/DCIM/[number1]APPLE/IMG_[number2].[extension]
# Media file in the Camera Roll, be it photo, screenshot, video, or saved from elsewhere.
# Number1 is the number of the Camera Roll, which depends on how many Camera Rolls you've had and ranges from 100-999.
# Number2 is the chronological number of the file in the Camera Roll, which ranges from 0001-9999.
# Media/PhotoData/Metadata/DCIM/[number >= 100]APPLE/IMG_[number of video in Camera Roll].JPG - Preview image of a video in the Camera Roll before you press the play button
# Media/PhotoData/Metadata/DCIM/[number >= 100]APPLE/IMG_[number of video in Camera Roll].THM - Thumbnail of a video in the Camera Roll
# Media/PhotoData/Metadata/PhotoData/Sync/[number >= 100]SYNCD/IMG_[number of video in Camera Roll].JPG - Corresponds to its parallel in Media/PhotoData/Metadata/DCIM/[number >= 100]APPLE/IMG_number of video in Camera Roll].JPG
# Media/PhotoData/Metadata/PhotoData/Sync/[number >= 100]SYNCD/IMG_[number of video in Camera Roll].THM - Corresponds to its parallel in Media/PhotoData/Metadata/DCIM/[number >= 100]APPLE/IMG_number of video in Camera Roll].THM

	def dumpCameraRoll(self, path, filename):
		try:
			print "Photo Database: " + self.path() + self.dbPhotos
			db = sqlite3.connect(self.path() + self.dbPhotos)
			cursor = db.cursor()

			sql = '''SELECT ZGENERICASSET.Z_PK AS id,
						ZGENERICASSET.ZKIND AS kind,
						ZGENERICASSET.ZWIDTH AS width,
						ZGENERICASSET.ZHEIGHT AS height,
						ZGENERICASSET.ZORIENTATION AS orientation,
						ZADDITIONALASSETATTRIBUTES.ZDURATION as duration,
						ZADDITIONALASSETATTRIBUTES.ZORIGINALFILESIZE as filesize,
						ZGENERICASSET.ZDIRECTORY AS directory,
						ZGENERICASSET.ZFILENAME AS filename,
						ZGENERICASSET.ZUNIFORMTYPEIDENTIFIER AS type,
						ZGENERICASSET.ZTHUMBNAILINDEX AS thumbnail_index,
						ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILWIDTH,
						ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILHEIGHT,
						ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILLENGTH,
						ZADDITIONALASSETATTRIBUTES.ZEMBEDDEDTHUMBNAILOFFSET,
						datetime(ZGENERICASSET.ZDATECREATED+978307200, 'unixepoch', 'localtime') AS creation_date,
						datetime(ZGENERICASSET.ZMODIFICATIONDATE+978307200, 'unixepoch', 'localtime') AS modified_date
					FROM ZGENERICASSET INNER JOIN ZADDITIONALASSETATTRIBUTES ON ZGENERICASSET.ZADDITIONALATTRIBUTES = ZADDITIONALASSETATTRIBUTES.Z_PK
					WHERE ZGENERICASSET.ZDATECREATED is not NULL
					ORDER BY ZGENERICASSET.ZDATECREATED ASC'''

			cursor.execute(sql)

			with open(path + filename, 'w') as outfile:
				json.dump(cursor.fetchall(), outfile, default=base64.b64encode)

			db.close()
		except Exception as e:
			print e


		try:
			db = sqlite3.connect(self.path() + self.dbPhotos)
			db.row_factory = sqlite3.Row
			cursor = db.cursor()
			cursor.execute(sql)
			for row in cursor:
				# Copy each image to the roll folder
				f = "CameraRollDomain-Media/" + row['directory'] + "/" + row['filename']
				f = self.path() + hashlib.sha1(f).hexdigest()
				if os.path.exists(f):
					print f
					shutil.copyfile(f, path + "roll/" + row['filename'])

				# Copy video thumbnails to roll folder
				if row['kind'] == 1:
					f = "CameraRollDomain-Media/PhotoData/Metadata/" + row['directory'] + "/" + row['title'] + ".THM"
					f = self.path() + hashlib.sha1(f).hexdigest()
					if os.path.exists(f):
						print f
						shutil.copyfile(f, path + "roll/" + row['title'] + ".JPG")
					else:
						f = "CameraRollDomain-Media/PhotoData/Metadata/" + row['directory'] + "/" + row['title'] + ".JPG"
						f = self.path() + hashlib.sha1(f).hexdigest()
						if os.path.exists(f):
							print f
							shutil.copyfile(f, path + "roll/" + row['title'] + ".JPG")

			db.close()
		except Exception as e:
			print e


# Voicemail
# HomeDomain
# Library/Voicemail/*

	def dumpVoicemail(self, path, filename):
		try:
			print "Voicemail Database: " + self.path() + self.dbVoicemail
			db = sqlite3.connect(self.path() + self.dbVoicemail)
			cursor = db.cursor()

			sql = '''SELECT voicemail.ROWID as id,
						voicemail.remote_uid,
						voicemail.sender,
						voicemail.duration,
						voicemail.flags,
						datetime(voicemail.date+978307200, 'unixepoch', 'localtime') as 'date',
						datetime(voicemail.trashed_date+978307200, 'unixepoch', 'localtime') as 'trashed_date'
					FROM voicemail
					ORDER BY voicemail.date'''

			cursor.execute(sql)

			with open(path + filename, 'w') as outfile:
				json.dump(cursor.fetchall(), outfile, default=base64.b64encode)

			db.close()
		except Exception as e:
			print e


		try:
			db = sqlite3.connect(self.path() + self.dbVoicemail)
			db.row_factory = sqlite3.Row
			cursor = db.cursor()
			cursor.execute(sql)
			for row in cursor:
				# Write each image out to the contacts folder
				vm = "HomeDomain-Library/Voicemail/" + str(row['id']) + ".amr"
				vm = self.path() + hashlib.sha1(vm).hexdigest()
				print vm
				if os.path.exists(vm):
					shutil.copyfile(vm, path + "vm/" + str(row['id']) + ".amr")

			db.close()
		except Exception as e:
			print e



# Voice Memos
# MediaDomain
# Media/Recordings/*
# Media/Recordings/[date] [time].m4a - Voice Memo, named YYYYMMDD HHMMSS.m4a

	def dumpMemos(self, path, filename):
		try:
			print "Voice Memo Database: " + self.path() + self.dbRecordings
			db = sqlite3.connect(self.path() + self.dbRecordings)
			cursor = db.cursor()

			sql = '''SELECT ZRECORDING.Z_PK as id,
						ZRECORDING.ZCUSTOMLABEL as label,
						ZRECORDING.ZDURATION as duration,
						ZRECORDING.ZPATH as path,
						datetime(ZRECORDING.ZDATE+978307200, 'unixepoch', 'localtime') as 'date'
					FROM ZRECORDING
					ORDER BY ZDATE'''

			cursor.execute(sql)

			with open(path + filename, 'w') as outfile:
				json.dump(cursor.fetchall(), outfile, default=base64.b64encode)

			db.close()
		except Exception as e:
			print e


		try:
			db = sqlite3.connect(self.path() + self.dbRecordings)
			db.row_factory = sqlite3.Row
			cursor = db.cursor()
			cursor.execute(sql)
			for row in cursor:
				# Write each image out to the contacts folder
				vm = row['path']
				vm = vm.replace("/var/mobile/", "MediaDomain-")
				vm = self.path() + hashlib.sha1(vm).hexdigest()
				print vm
				if os.path.exists(vm):
					shutil.copyfile(vm, path + "rec/" + str(row['id']) + ".m4a")

			db.close()
		except Exception as e:
			print e


# Notes
# HomeDomain
# Library/Notes/*
# Library/Preferences/com.apple.mobilenotes.plist

	def dumpNotes(self, filename):
		try:
			print "Notes Database: " + self.path() + self.dbNotes
			db = sqlite3.connect(self.path() + self.dbNotes)
			cursor = db.cursor()

			sql = '''SELECT ZNOTE.ZBODY as id,
						ZNOTE.ZTITLE as title,
						ZNOTE.ZSUMMARY as summary,
						ZNOTEBODY.ZCONTENT as content,
						ZNOTE.ZDELETEDFLAG as deleted,
						datetime(ZNOTE.ZCREATIONDATE+978307200, 'unixepoch', 'localtime') as 'creation_date',
						datetime(ZNOTE.ZMODIFICATIONDATE+978307200, 'unixepoch', 'localtime') as 'modified_date'
					FROM ZNOTE INNER JOIN ZNOTEBODY ON ZNOTE.Z_PK = ZNOTEBODY.ZOWNER
					ORDER BY ZNOTE.ZCREATIONDATE'''

			cursor.execute(sql)

			with open(filename, 'w') as outfile:
				json.dump(cursor.fetchall(), outfile, default=base64.b64encode)

			db.close()
		except Exception as e:
			print e
