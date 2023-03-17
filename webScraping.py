import requests
import wikipedia
from bs4 import BeautifulSoup

class Scrape:

  def __init__(self,site): #grabs site information once when class is created
    self.header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.3'}
    self.url = site
    self.page = requests.get(self.url,headers=self.header)
    self.site = BeautifulSoup(self.page.content, "html.parser")
    
  def headerCheck(self): #verifies site header in case page doesnt exist or any other server error
    page = requests.get(self.url,headers=self.header)
    print (page.status_code)
    return page.status_code
    

class Wiki(Scrape):
  def scrapeFromWiki(self,term):
    print(term)
    try:
      wikipedia.page(term)#checks if the page is a disambiguation page or redirects to one

      pageStat = self.headerCheck()
      
      if pageStat == 200:
        print("Site Title is:  " + self.site.title.string)
        for div in self.site.find_all('div', class_='mw-parser-output'):
          print(self.site.find_all('p')[1].text)
          return (self.site.find_all('p')[1].text)
      elif pageStat == 404:
        return "Sorry, this page does not exist! Please check the term for any spelling mistakes or add _ instead"
      else:
        return "Something went wrong! Please try again later."
        
    except wikipedia.exceptions.DisambiguationError: #the wikipedia package gives a handy error if it is a disambiguation page
      return("We just hit a disambiguation page! Please try to specify what term you want to search for. Unfortunately due to how Wikipedia sometimes redirects from disambiguation pages, we cannot grab the other related terms.")

    except wikipedia.exceptions.PageError:
       return("It looks like you hit one of the bugged words. Unfortunately, one of our libraries did not parse your input properly and threw an error.")
    
  def wikiSearch(self,searchTerm):
    results = []
    prefilter = self.site.findAll('p')
    for p in prefilter:
        if searchTerm in p.getText():
            results.append(p.getText())
    formatted = []
    for x in results:
        format = x.replace(searchTerm,f"__***{searchTerm}***__")
        formatted.append(format)

    return formatted
    

    