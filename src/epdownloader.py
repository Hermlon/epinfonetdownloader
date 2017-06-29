import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import traceback

phpsessionid = ""
epinfocookie = ""
identity = ""

def savefile(name, text):
	myFile = open(name, "w")
	myFile.write(text)
	myFile.close()
	
def parseOverview(text):
	print(text)
	table = "<table class='fakturen'>" + text.split("<table class='fakturen'>")[2]
	table = table.split("<br/>")[0]
	soup = BeautifulSoup(table, 'html.parser')
	table = soup.prettify()
	savefile("overview.xml", table)
	root = ET.fromstring(table)
	result = {}
	for tr in root.findall("tr"):
		data = tr.findall("td")
		try:
			date = data[1].text.strip()
			number = data[2].find("a").text.strip()
			result[date] = number
		except:
			print("fhrh")
			pass
	return result

def getPdfFile(s, number):
	cookie = phpsessionid + "; " + epinfocookie + "; " + identity
	authheader = {"Cookie": cookie}
	pdf = requests.get("https://www.ep-infonet.de/apps/legacy/index/index?legacy_app_name=bestellbestand_index&layouttype=partial?id=0&re_nr=" + str(number) + "&phase=dokument_anfragen", headers=authheader)
	return pdf.text
	
def login(s, uname, pw):
	#get epinfocookie
	r = s.get("https://www.ep-infonet.de/")
	epinfocookie = r.headers["Set-Cookie"].split(";")[0]

	#get with it the sessionid
	header = {"Cookie": epinfocookie}
	r = s.get("https://www.ep-infonet.de/apps/", headers=header)
	
	phpsessionid = "PHPSESSID=" + s.cookies.get('PHPSESSID')
	
	#post login information
	login = {"login": uname, "password": pw}
	header = {"Cookie": phpsessionid + "; " + epinfocookie}
	r = s.post("https://www.ep-infonet.de/apps/cms/login", data=login, headers=header)
	
	#get identity
	header = {"Cookie": phpsessionid + "; " + epinfocookie}
	r = s.post("https://www.ep-infonet.de/apps/", headers=header)
	identity = r.headers["Set-Cookie"].split(";")[0]
	
def getOverview(s, startdate, enddate):
	#get overview
	url = "https://www.ep-infonet.de/apps/legacy/index/index?layouttype=partial&locale=de-DE&phase=fakturen&artikel_nr=&re_nr=&lief_nr=&re_datum_von=" + startdate + "&re_datum_bis=" + enddate + "&legacy_app_name=bestellbestand_index&layouttype=partial&locale=de-DE&frameLayout=v6&_=1498733538006"
	cookie = phpsessionid + "; " + epinfocookie + "; " + identity
	print("c:" + cookie)
	authheader = {"Cookie": cookie}
	overview = s.get(url, headers=authheader)
	return parseOverview(overview.text)
	
with requests.session() as s:
	print("Möchtest du dich zu ep-infonet.de verbinden? (J/n):")
	if input().lower() == "j":
		print("Login: ")
		user = input()
		print("Passwort: ")
		pw = input()
		try:
			login(s, user, pw)
			try:
				print("Startdatum: (tt.mm.jjjj)")
				startd = input()
				print("Enddatum: (tt.mm.jjjj)")
				endd = input()
				files = getOverview(s, startd, endd)
				print(files)
			except Exception as e:
				traceback.print_exc()
				print("Herunterladen der Übersicht fehlgeschlagen. Datum überprüfen!")
		except:
			print("Login fehlgeschlagen")
	

