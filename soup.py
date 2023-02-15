print("Boiling the Soup")

from bs4 import BeautifulSoup
from urllib.request import urlopen

print("please enter in a website")

url = input("site:")
#url="https://www.reddit.com
page = urlopen(url)
html = page.read().decode("utf-8", "ignore")
pullData = BeautifulSoup(html, "html.parser")

print("Site Title is:  " + pullData.title.string)

for pullPara in pullData.find_all("p"):
  print(pullPara.get_text())
