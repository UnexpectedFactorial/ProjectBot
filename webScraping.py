import requests
from bs4 import BeautifulSoup
class Scrape:

    def __init__(self,site):
        self.header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.3'}
        self.url = site
    def headerCheck(self):
        page = requests.get(self.url,headers=self.header)
        if page.status_code == 200:
            return True
        elif page.status_code == 404:
            return 404
        else:
            return False

class Wiki(Scrape):

    def scrapeFromWiki(self):
        if self.headerCheck():
          page = requests.get(self.url,headers=self.header)
          site = BeautifulSoup(page.content, "html.parser")
          print("Site Title is:  " + site.title.string)
          for div in site.find_all('div', class_='mw-body-content mw-content-ltr'):
            await ctx.send(site.find_all('p')[1].text)  
        elif self.headerCheck() == 404:
          await ctx.send("Sorry, this page does not exist! Please check the term for any spelling mistakes!")
        else:
          await ctx.send("Something went wrong! Please try again later.")

    def wikiSearch(self):
      