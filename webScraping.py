import requests
import wikipedia
from bs4 import BeautifulSoup


class Scrape:

  def __init__(self, site):  #grabs site information once when class is created
    self.header = {
      'User-Agent':
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.3'
    }
    self.url = site
    self.page = requests.get(self.url, headers=self.header)
    self.site = BeautifulSoup(self.page.content, "html.parser")

  def headerCheck(self):  #verifies site header in case page doesnt exist or any other server error
    page = requests.get(self.url, headers=self.header)
    return page.status_code


class Wiki(Scrape):

  def scrapeFromWiki(self, term):
    print(term)
    try:
      wikipedia.page(term)  #checks if the page is a disambiguation page or redirects to one

      pageStat = self.headerCheck()

      if pageStat == 200:
        for div in self.site.find_all('div', class_='mw-parser-output'):
          return (self.site.find_all('p')[1].text)
      elif pageStat == 404:
        return "Sorry, this page does not exist! Please check the term for any spelling mistakes or add _ instead"
      else:
        return "Something went wrong! Please try again later."

    except wikipedia.exceptions.DisambiguationError:  #the wikipedia package gives a handy error if it is a disambiguation page
      return (
        "We just hit a disambiguation page! Please try to specify what term you want to search for. Unfortunately due to how Wikipedia sometimes redirects from disambiguation pages, we cannot grab the other related terms."
      )

    except wikipedia.exceptions.PageError:
      return (
        "It looks like you hit one of the bugged words. Unfortunately, one of our libraries did not parse your input properly and threw an error."
      )

  def wikiSearch(self, searchTerm):
    results = []
    prefilter = self.site.findAll('p')
    for p in prefilter:
      if searchTerm in p.getText():
        results.append(p.getText())
    formatted = []
    for x in results:
      format = x.replace(searchTerm, f"__***{searchTerm}***__")
      formatted.append(format)

    return formatted


class Steam(Scrape):

  def initialCheck(self):
    headerCheck = self.headerCheck()
    if headerCheck == 200:
      try:
        return (self.SteamAnalyze())
      except AttributeError:
        return (
          "Unfortunately, due to an interaction between BeautifulSoup and the registered trademark unicode, we are unable to analyze this game."
        )
    elif headerCheck == 404:
      return ("Game not found! Please check your link again.")
    else:
      return (
        "Something happened that wasn't supposed to! Please try again later.")

  def SteamAnalyze(self):

    if self.SaleCheck():
      gameName = self.site.find('div', class_="apphub_AppName").get_text()
      discountedPrice = self.site.find('div', class_="discount_final_price").string
      discountedPrice = discountedPrice.strip().replace('\t', '').replace('\n', '')
      origPrice = self.site.find('div', class_="discount_original_price").string
      discPercent = self.site.find('div', class_="discount_pct").string + " off"
      onSale = self.SaleCheck()
      gameRating = self.site.find('span', class_="game_review_summary").string
      gameRatingNumber = self.site.find('span', class_="responsive_hidden").string
      gameRatingNumber = gameRatingNumber.strip().replace('\t', '').replace('\n', '')
      gameRating = gameRating + f" based off of {gameRatingNumber} ratings"
      thumbnail = self.site.find('img', class_="game_header_image_full")

      results = [
        onSale, thumbnail['src'], gameName, origPrice, discPercent,
        discountedPrice, gameRating
      ]
      return results
    else:

      gameName = self.site.find('div', class_="apphub_AppName").get_text()
      gamePrice = self.site.find('div',
                                 class_="game_purchase_price price").string
      gamePrice = gamePrice.strip().replace('\t', '').replace('\n', '')
      onSale = self.SaleCheck()
      gameRating = self.site.find('span', class_="game_review_summary").string
      gameRatingNumber = self.site.find('span',
                                        class_="responsive_hidden").string
      gameRatingNumber = gameRatingNumber.strip().replace('\t', '').replace(
        '\n', '')
      gameRating = gameRating + f" based off of {gameRatingNumber} ratings"
      thumbnail = self.site.find('img', class_="game_header_image_full")

      results = [onSale, thumbnail['src'], gameName, gamePrice, gameRating]

      return results

  def SaleCheck(self):
    for div in self.site.find_all('div', class_='discount_prices'):
      parent_classes = [c.get('class') for c in div.find_parents('div')]
      if 'game_area_purchase_game_wrapper' in [c for classes in parent_classes for c in classes] and \
         ['game_area_purchase_game_wrapper', 'dynamic_bundle_description', 'ds_no_flags'] not in parent_classes:
        return True
    return False

class Custom(Scrape):
  def customSearch(self,tag):
    tags = ["a","abbr","acronym","address","area","b","base","bdo","big","blockquote","body","br","button","caption","cite","code","col","colgroup","dd","del","dfn","div","dl","DOCTYPE","dt","em","fieldset","form","h1","h2","h3","h4","h5","h6","head","html","hr","i","img","input","ins","kbd","label","legend","li","link","map","meta","noscript","object","ol","optgroup","option","p","param","pre","q","samp","script","select","small","span","strong","style","sub","sup","table","tbody","td","textarea","tfoot","th","thead","title","tr","tt","ul","var"]
    status = self.headerCheck()
    if status == 200:
        if tag in tags:
            if tag == "a": #grabs only the links since the default behavour would grab the link text rather than the link
                results = self.site.find_all(tag)
                formattedResult = []
                for unclean in results:
                    formattedResult.append(unclean['href'])

                formattedResult = [link for link in formattedResult if link.startswith("http://") or link.startswith("https://")] #removes any internal links for the site
                return formattedResult
            else:
                results = self.site.find_all(tag)
                del results[10:] #limit results to 10 to prevent spamming.
                formattedResult = []
                for unclean in results:
                    formattedResult.append(unclean.text.strip().replace('\t', '').replace('\n', ''))
                return formattedResult
        else:
            return "Sorry, it seems like you have inserted an invalid tag"
    elif status == 404:
      return "Page not found! Please try again."
    else:
      return "Something went wrong! Please try again later."