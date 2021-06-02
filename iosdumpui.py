#!/usr/bin/python

import sys
import shutil
import os
import os.path
from os.path import expanduser
import threading

from ios import ios
import iosdump

from kivy.config import Config
Config.set('graphics','resizable',0)

import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.logger import Logger

from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from kivy.effects.opacityscroll import OpacityScrollEffect

class ButtonListItem(Button):
	wid = StringProperty('')
	image = StringProperty('')
	title = StringProperty('')
	label = StringProperty('')
	pass

	def click(button):
		global app

		if button.wid != "details":
			app.clearSelection()

			app.screen_detail.label = button.label
			app.screen_detail.image = button.image

			iosBackup.select(int(button.wid))
			button.background_normal = 'atlas://data/images/defaulttheme/button_pressed'
			app.screen.transition.direction = 'left'
			app.screen.current = 'detail'

class DisplayListItem(Button):
	wid = StringProperty('')
	image = StringProperty('')
	title = StringProperty('')
	label = StringProperty('')
	pass

	def click(button):
		pass

class ButtonList(GridLayout):
	pass

class DisplayItem(Label):
	pass

class Detail(Screen):
	image = StringProperty('')
	label = StringProperty('')
	pass

class iOSDumpUI(App):
	icon = 'ico/extractor.png'
	title = 'iOSDump - Select iTunes Backup to Dump'

	def build(self):
		Window.size = 400, (5 * 90)

		# Setup Select Screen
		self.screen_select = Screen(name='select', direction='left')
		self.layout = ButtonList()
		self.layout.size = 400, (len(iosBackup.backups) * 78)

		self.select = ScrollView(
						size_hint=(None, None),
						size=Window.size,
						scroll_type=['bars', 'content'],
						effect_cls=OpacityScrollEffect
					)
		self.select.add_widget(self.layout)
		self.listBackups()
		self.screen_select.add_widget(self.select)

		# Setup Detail Screen
		self.screen_detail = Detail(
								name="detail",
								direction="right",
								image='ico/apple.png',
								label='testing'
							)

		# Setup Screen Manager
		self.screen = ScreenManager()
		self.screen.add_widget(self.screen_select)
		self.screen.add_widget(self.screen_detail)

		return self.screen

	def listBackups(self):
		'List all the iOS Backups and prompt for selection'
		for i in range(len(iosBackup.backups)):
			iosBackup.select(i)
			if ".DS_Store" not in iosBackup.path():
				label = "%s iOS v%s: %s\nDevice Name: %s\nLatest Backup: %s" % (iosBackup.deviceModel, iosBackup.productVersion, iosBackup.serialNumber, iosBackup.deviceName, iosBackup.lastBackupDate)

				ib = ButtonListItem(
					wid=str(i),
					image="ico/%s.png" % (iosBackup.productType),
					title=iosBackup.deviceType,
					label=label
				)
				self.buttons = {i:ib}
				self.layout.add_widget(ib)

	def clearSelection(self):
		for child in self.layout.children:
			#child.background_color = (1,1,1,1)
			child.background_normal = 'atlas://data/images/defaulttheme/button'

	def dumpData(self):
		i = iosBackup.index
		t = threading.Thread(target=iosdump.iosDumpData, args=(i,))
		t.start()
		print ( "Dumping " + str(iosBackup.index) )

	def logItem(self, message):
		print ( message )


# Initialize Objects, Output Folder and Clean Up Previous Dump
iosBackup = ios()
outputFolder = expanduser("~") + "/Desktop/iOSDump/"
if not os.path.exists(outputFolder):
	os.mkdir(outputFolder, 755)
else:
	iosdump.cleanFolder(outputFolder)

#if __name__ == "__main__":
app = iOSDumpUI()
app.run()
