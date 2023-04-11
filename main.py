import os
import random
import settings
import discord
import requests  #for requests.get
import wikipediaapi  # for wiki
import asyncio
# googlesearch also requires an additional module; pip install googlesearch-python (already installed)
from googlesearch import search # for google

from PyDictionary import PyDictionary
from discord.ext import commands

from webScraping import *
import yfinance as yf



weatherkey = os.environ['weather']  #weather API Key

rapidAPIkey = os.environ['rapidAPIkey'] # API key for currency / translation

logger = settings.logging.getLogger("bot")

def run():
  intents = discord.Intents.all()
  token = os.environ['TOKEN']  #discord bot token
  bot = commands.Bot(command_prefix="#", intents=intents)

  async def load(): #cog load
    for filename in os.listdir("./cogs"):
      if filename.endswith(".py"):
        await bot.load_extension(f"cogs.{filename[:-3]}")

  async def main():
    await load()
    await bot.start(token)
  
  @bot.event
  async def on_ready():
    logger.info(f"User:{bot.user} (ID:{bot.user.id})")

  @bot.command(alias=['p'],
               description="checks for a pulse",
               enable=True,
               hidden=True)
  async def ping(ctx):
    await ctx.send("I am Alive")

  @bot.command(
    brief="Returns the first paragraph from a Wikipedia page",
    description=
    "This command searches Wikipedia and returns the first paragragh as a summary to the user.",
    help=
    "Please use this command with the following format. #wikiscrape [Word to Search]"
  )
  async def wikiscrape(ctx, *, query="wikipedia"):
    userInput = f"https://en.wikipedia.org/wiki/{query}"
    input = Wiki(userInput)
    result = input.scrapeFromWiki(query)

    await ctx.send(result)

  @bot.command(
    brief="Returns paragraphs from a Wikipedia page containing a given term.",
    description=
    "This command searches Wikipedia and returns back all the paragraphs that contain your given term.",
    help=
    "Please use this command with the following format. #wikisearch [Word to Search],[Term]"
  )
  async def wikisearch(ctx, *, input):
    async with ctx.typing():
      if ',' in input:
        argList = input.split(",")
        wikiInput = argList[0]
        searchTerm = argList[1]
        if len(argList) == 2:
          if (wikiInput == searchTerm):
    
            await ctx.send(
              "Nice try. Please search for another word other than the article.")
    
          else:
            userInput = f"https://en.wikipedia.org/wiki/{wikiInput}"
            input = Wiki(userInput)
            result = input.wikiSearch(searchTerm)
    
            if result:
              for x in result:
                await ctx.send(x)
            else:
              await ctx.send("No Results Found")
    
        else:
          await ctx.send("Please only enter 2 arguments")
      else:
        await ctx.send("Please insert a comma between your search query and the word you want to search.")
  @bot.command(
    brief="Scrapes a Steam store page",
    description=
    "This command grabs the price and reviews from a Steam store page and checks if there's a sale going on. A little less advanced than the inbuilt Discord imbeds.",
    help="Please use this command with the following format. #steam [URL]")
  async def steam(ctx, input):

    if input.startswith("https://store.steampowered.com/app/"):

      userInput = Steam(input)
      results = userInput.initialCheck()

      if isinstance(results, list):
        saleStatus = results[0]
        thumbnail = results[1]
        results.pop(0)
        results.pop(0)
        async with ctx.typing():
          if saleStatus:  #formatted results for games on sale
            categories = [
              'Title: ', 'Price: ', 'Discounted Price: ', 'Discount Percent: ',
              'Recent Reviews: '
            ]
            steamEmbed = discord.Embed(title="Steam Game Analysis",
                                       color=discord.Color.from_rgb(
                                         50, 238, 58))
            steamEmbed.set_thumbnail(url=thumbnail)
            for i in range(len(results)):
              steamEmbed.add_field(name=categories[i],
                                   value=results[i],
                                   inline=False)
            await ctx.send(embed=steamEmbed)

          else:
            categories = ['Title: ', 'Price: ', 'Recent Reviews: ']
            steamEmbed = discord.Embed(title="Steam Game Analysis", color=discord.Color.from_rgb(65, 95, 117))
            steamEmbed.set_thumbnail(url=thumbnail)
            for i in range(len(results)):
              steamEmbed.add_field(name=categories[i],
                                   value=results[i],
                                   inline=False)

            await ctx.send(embed=steamEmbed)

      else:
        await ctx.send(results)

    else:
      await ctx.send(
        "Invalid URL! Please input a game URL. Bundles are currently not supported!"
      )
  @bot.command(
    brief="Grabs all text from a specified tag from a site",
    description=
    "This command will grab all the text from a tag and site you choose. Please make sure the tag you are specifying is a valid html tag ",
    help="Please use this command with the following format. #tagsearch [URL], [TAG]")
  async def tagsearch(ctx,*,input):
    if ',' in input:
      argList = input.split(",")
      urlInput = argList[0]
      searchTag = argList[1]
      searchTag = searchTag.replace(" ","")
      async with ctx.typing():
        try: 
          input = Custom(urlInput)
          results = input.customSearch(searchTag)
          for i in results:
            await ctx.send(i)
        except discord.errors.HTTPException:
          
          await ctx.send("Discord.py just ran into an error! Most likely we have exceeded the character limit.")
      
    else:
      await ctx.send("Please insert a comma between your URL and the tag you want to search.")
  @bot.command(
    brief="Grabs stock information from Yahoo Finance",
    description=
    "This command will grab price information on a given company's stock ticker symbol with data sourced from Yahoo! Finance",
    help="Please use this command with the following format. #ticker [SYMBOL]"
  )
  async def ticker(ctx,*,input):

    try:
      ticker = yf.Ticker(input).info
    except AttributeError:
      await ctx.send("The symbol you searched is invalid! Please check your symbol and try again. ")

    stockPrice = ticker['regularMarketPrice']
    pastPrice = ticker['regularMarketPreviousClose']
    priceChange = stockPrice - pastPrice
    changePercent = round((priceChange/pastPrice)*100,2)
    
    if changePercent >= 0:
      change = True
    else:  
        change = False
    changePercent = f"{changePercent}%"

    if change:
      tickerEmbed = discord.Embed(title=ticker['shortName'],color=discord.Color.from_rgb(50, 238, 58)) 
    else:
      tickerEmbed = discord.Embed(title=ticker['shortName'],color=discord.Color.from_rgb(238, 63, 63 ))
      
    tickerEmbed.add_field(name="Ticker Symbol:",value=ticker['symbol'],inline=False)
    tickerEmbed.add_field(name="Current Price:",value=stockPrice,inline=True)
    tickerEmbed.add_field(name="Yesterday's Price:",value=pastPrice,inline=True)
    tickerEmbed.add_field(name="Today's Change:",value=changePercent,inline=True)
    tickerEmbed.set_footer(text="Data sourced from Yahoo Finance. This information is provided as is.")
    await ctx.send(embed=tickerEmbed)
  @bot.command()
  async def dog(ctx):
    r = requests.get(" https://dog.ceo/api/breeds/image/random")
    res = r.json()
    em = discord.Embed()
    em.set_image(url=res['message'])
    await ctx.send(embed=em)

  @bot.command(alias=['w'], description="Shows the weather from a location")
  async def weather(ctx, *, place: str):
    r = requests.get(
      f"http://api.weatherapi.com/v1/forecast.json?key={weatherkey}&q={place}&days=1&aqi=no&alerts=no"
    )
    res = r.json()
    Temp = f"It is currently {res['current']['temp_c']} degrees right now and {res['current']['condition']['text']} in {place}."
    await ctx.send(Temp)

  @bot.command()
  async def wiki(ctx, *, arg):
    print(arg)
    wiki = wikipediaapi.Wikipedia('en')
    result = wiki.page(arg)
    await ctx.send("Searched Term: %s" % result.title)
    await ctx.send("Summary: %s" % result.summary)
    await ctx.send("Link to Page: %s" % result.fullurl)

  @bot.command()
  async def google(ctx, *, arg):
    await ctx.send(f"Searched Term: {arg}")
    for url in search(f'{arg}', stop=5):
      await ctx.send(url)

  @bot.command()
  async def define(ctx, *, arg):
    dictionary = PyDictionary()
    result = dictionary.meaning(arg)
    temp = discord.Embed(title = "Definition", description = result, colour = 0x5865F2)
    await ctx.send(embed = temp)

  @bot.command()
  async def poll(ctx, *, arg):
    temp = discord.Embed(title = "Voting Poll", description = arg, colour = 0x5865F2)
    sendresult = await ctx.send(embed = temp)
    await sendresult.add_reaction("✅")
    await sendresult.add_reaction("❌")

  @bot.command()
  async def translate(ctx, *, arg):
  
    url = "https://text-translator2.p.rapidapi.com/translate"
    payload = f"source_language=auto&target_language=en&text={arg}"
    headers = {
	   "content-type": "application/x-www-form-urlencoded",
	   "X-RapidAPI-Key": f"{rapidAPIkey}",
	   "X-RapidAPI-Host": "text-translator2.p.rapidapi.com"
}
    response = requests.request("POST", url, data=str(payload).encode('utf-8'), headers=headers)
    data = response.json()

    temp = discord.Embed(title = "Autodetect Language Translation", description = data['data']['translatedText'], colour = 0x5865F2)
    await ctx.send(embed = temp)

  @bot.command()
  async def currency(ctx, arg1, arg2, arg3):
    url = "https://currency-converter-by-api-ninjas.p.rapidapi.com/v1/convertcurrency"

    querystring = {"amount":{arg1},"have":{arg2},"want":{arg3}}

    headers = {
	   "X-RapidAPI-Key": f"{rapidAPIkey}",
	   "X-RapidAPI-Host": "currency-converter-by-api-ninjas.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    oldAmount = (data['old_amount'])
    newAmount = (data['new_amount'])
    oldCurrency = (data['old_currency'])
    newCurrency = (data['new_currency'])
    temp = discord.Embed(title = "Currency Conversion", description = f"Original Currency: {oldCurrency}\nOriginal Value: {oldAmount}\nNew Currency: {newCurrency}\nConverted Value: {newAmount}\n", colour = 0x5865F2)
    await ctx.send(embed = temp)

  @bot.command()
  async def randomfact(ctx):
    fact = requests.get(f'https://uselessfacts.jsph.pl/api/v2/facts/random').json()
    result = fact['text']
    temp = discord.Embed(title = "Random Fact", description = result, colour = 0x5865F2)
    await ctx.send(embed = temp)

  @bot.command()
  async def coinflip(ctx):
    coin = random.randint(0, 1)
    if coin == 0:
      result = "Tails!"
    if coin == 1:
      result = "Heads!"
    temp = discord.Embed(title = "Coin Flip", description = result, colour = 0x5865F2)
    await ctx.send(embed = temp)

  @bot.command()
  async def roll(ctx, arg1: int):
    roll = random.randint(1, arg1)
    temp = discord.Embed(title = "Dice Roll", description = f"You roll a dice with {arg1} sides. The dice lands on {roll}.", colour = 0x5865F2)
    await ctx.send(embed = temp)
  
  asyncio.run(main())

if __name__ == "__main__":
  run()

