import os
import settings
import discord
import requests  #for requests.get
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
  async def scrape(ctx, *, site):
    print(site)
    page = urlopen(site)
    html = page.read().decode("utf-8", "ignore")
    pullData = BeautifulSoup(html, "html.parser")

    await ctx.send(f"**We are now scraping from:** {pullData.title.string}")

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

  bot.run(token, root_logger=True)


if __name__ == "__main__":
  run()
