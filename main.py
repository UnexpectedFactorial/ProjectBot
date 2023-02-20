import os
import settings
import discord
import requests  #for requests.get
from PyDictionary import PyDictionary
from discord.ext import commands

from bs4 import BeautifulSoup
from urllib.request import urlopen

token = os.environ['TOKEN']  #discord bot token

weatherkey = os.environ['weather']  #weather API Key

logger = settings.logging.getLogger("bot")


def run():
  intents = discord.Intents.default()
  intents.message_content = True

  bot = commands.Bot(command_prefix="#", intents=intents)

  @bot.event
  async def on_ready():
    logger.info(f"User:{bot.user} (ID:{bot.user.id})")

  @bot.command(alias=['p'],
               description="checks for a pulse",
               enable=True,
               hidden=True)
  async def ping(ctx):
    await ctx.send("I am Alive")

  @bot.command()
  async def repeat(ctx, *, word):
    print(word)
    await ctx.send(word)

  @bot.command()
  async def wikiscrape(ctx, *, query):
    print(query)
    page = urlopen(f"https://en.wikipedia.org/wiki/{query}")
    print(page)
    html = page.read().decode("utf-8", "ignore")
    site = BeautifulSoup(html, "html.parser")

    await ctx.send(f"**We are now scraping from:** {site.title.string}")

    for div in site.find_all('div', class_='mw-body-content mw-content-ltr'):
      await ctx.send(site.find_all('p')[1].text)

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
    arg = arg.replace(' ', '_').replace('  ', '_')
    print(arg)
    await ctx.send(f'https://en.wikipedia.org/wiki/{arg}')

  @bot.command()
  async def google(ctx, *, arg):
    arg = arg.replace(' ', '_').replace('  ', '_')
    await ctx.send(f"https://www.google.com/search?q={arg}")
  
  @bot.command()
  async def define(ctx, *, arg):
    dictionary = PyDictionary()
    result = dictionary.meaning(arg)
    await ctx.send(f"{result}")
  
  bot.run(token, root_logger=True)

if __name__ == "__main__":
  run()
