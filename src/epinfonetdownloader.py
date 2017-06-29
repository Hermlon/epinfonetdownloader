import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import traceback
import os

class EPInfonet(object):
	
	def __init__(self):
		with requests.session() as s:
			self.session = s
			
	def login(self, username, password):
		 #get epinfocookie
		r = self.session.get("https://www.ep-infonet.de/")
		self.epinfocookie = r.headers["Set-Cookie"].split(";")[0]
		
		#get with it the sessionid
		header = {"Cookie": self.epinfocookie}
		r = self.session.get("https://www.ep-infonet.de/apps/", headers=header)
		
		self.phpsessionid = "PHPSESSID=" + self.session.cookies.get('PHPSESSID')
		
		#post login information
		login = {"login": username, "password": password}
		header = {"Cookie": self.phpsessionid + "; " + self.epinfocookie}
		r = self.session.post("https://www.ep-infonet.de/apps/cms/login", data=login, headers=header)
		
		#get identity
		header = {"Cookie": self.phpsessionid + "; " + self.epinfocookie}
		r = self.session.post("https://www.ep-infonet.de/apps/", headers=header)
		self.identity = r.headers["Set-Cookie"].split(";")[0]
		
	def getPdfFile(self, number):
		cookie = self.phpsessionid + "; " + self.epinfocookie + "; " + self.identity
		authheader = {"Cookie": cookie}
		pdf = self.session.get("https://www.ep-infonet.de/apps/legacy/index/index?legacy_app_name=bestellbestand_index&layouttype=partial?id=0&re_nr=" + str(number) + "&phase=dokument_anfragen", headers=authheader)
		return pdf.content

	def getOverview(self, startdate, enddate):
		#get overview
		url = "https://www.ep-infonet.de/apps/legacy/index/index?layouttype=partial&locale=de-DE&phase=fakturen&artikel_nr=&re_nr=&lief_nr=&re_datum_von=" + startdate + "&re_datum_bis=" + enddate + "&legacy_app_name=bestellbestand_index&layouttype=partial&locale=de-DE&frameLayout=v6&_=1498733538006"
		cookie = self.phpsessionid + "; " + self.epinfocookie + "; " + self.identity
		authheader = {"Cookie": cookie}
		overview = self.session.get(url, headers=authheader)
		return self.parseOverview(overview.text)
		
	def parseOverview(self, text):
		table = "<table class='fakturen'>" + text.split("<table class='fakturen'>")[2]
		table = table.split("<br/>")[0]
		soup = BeautifulSoup(table, 'html.parser')
		table = soup.prettify()
		root = ET.fromstring(table)
		result = {}
		for tr in root.findall("tr"):
			data = tr.findall("td")
			try:
				date = data[1].text.strip()
				number = data[2].find("a").text.strip()
				result[date] = number
			except:
				pass
		return result
		
def savefile(path, name, text):
	if not os.path.exists(path):
		os.makedirs(path)
	print("Schreibe Datei " + name)
	myFile = open(path + "/" + name, "wb")
	myFile.write(text)
	myFile.close()

print("Möchtest du dich zu ep-infonet.de verbinden? (J/n):")
if input().lower() == "j":
	ep = EPInfonet()
	print("Login: ")
	user = input()
	print("Passwort: ")
	pw = input()
	try:
		print("Logge ein...")
		ep.login(user, pw)
		print("Erfolgreich eingeloggt!")
		try:
			print("Startdatum: (tt.mm.jjjj)")
			startd = input()
			print("Enddatum: (tt.mm.jjjj)")
			endd = input()
			files = ep.getOverview(startd, endd)
			print(str(len(files)) + " Dateien gefunden!")
			print("Herunterladen? (J/n)")
			if input().lower() == "j":
				try:
					for date in files:
						savefile(date.split("-")[0], date + ".pdf", ep.getPdfFile(files[date]))
				except:
					traceback.print_exc()
					print("Herunterladen Dateien fehlgeschlagen!")		
		except:
			traceback.print_exc()
			print("Herunterladen der Übersicht fehlgeschlagen. Datum überprüfen!")
	except:
		traceback.print_exc()
		print("Login fehlgeschlagen")
