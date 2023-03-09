import os
import settings
import discord
import requests  #for requests.get
import wikipediaapi # for wiki

from PyDictionary import PyDictionary
from discord.ext import commands
from bs4 import BeautifulSoup

from webScraping import Wiki

token = os.environ['TOKEN']  #discord bot token

weatherkey = os.environ['weather']  #weather API Key

logger = settings.logging.getLogger("bot")


def run():
  intents = discord.Intents.all()
  
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

#administrative commands

  @bot.event
  async def on_member_join(member):
    defaultrole = discord.utils.get(member.guild.roles, name="default")
    await member.add_roles(defaultrole)

  @bot.event  #self-assign reaction
  async def on_reaction_add(reaction, user):
    message = reaction.message
    if message.id == 1079854132816519189:
      guild = message.guild
      roles_dict = { #"Emotename": "Rolename"
        ":red_square:": "red",
        ":green_square:": "green",
        ":blue_square:": "blue"
      }
      role_name = roles_dict.get(str(reaction.emoji))
      if role_name is not None:
        role = discord.utils.get(guild.roles, name=role_name)
        await user.add_roles(role)

  @bot.command()
  async def purge(ctx, amount= 10):
    await ctx.channel.purge(limit=amount+1)
    await ctx.send(f'{amount} messages successfully purged')

  def perms(**perms):
    async def predicate(ctx):

      #checks admin role
      if ctx.author.guild_permissions.administrator:
        return True
        
      #checks  other role perms
      for role in ctx.author.roles:
        if role.permissions_in(ctx.channel).**perms:
          return True
          
      #role has no perms
      raise commands.Missing.Permissions(perms):
    return commands.check(predicate)
    

  @bot.command()
  @perms(kick_members=True)
  async def kick(ctx, member: discord.Member):
    await member.kick()
    await ctx.send(f"{member} has been kicked.")

  @bot.command()
  @perms(ban_members=True)
  async def ban(ctx, member: discord.Member):
    await member.ban()
    await ctx.send(f"{member} has been banned.")

  @bot.command()
  @perms(add_roles=True)
    async def mute(ctx, member: discord.Member): #checks for muted role and creates if doesn't exist
      role = discord.utils.get(ctx.guild.roles, name="Muted") 
      if not role: 
          role = await ctx.guild.create_role(name="Muted") 
          for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False)

      await member.add_roles(role)
      await ctx.send(f"{member} has been muted.")

  @bot.command()
  async def repeat(ctx, *, word):
    print(word)
    await ctx.send(word)

  @bot.command()
  async def wikiscrape(ctx, *, query):
    userInput = f"https://en.wikipedia.org/wiki/{query}"
    input = Wiki(userInput)
    input.scrapeFromWiki()

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
