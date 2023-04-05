import os
import settings
import discord
import requests  #for requests.get
import wikipediaapi  # for wiki

from PyDictionary import PyDictionary
from discord.ext import commands

from admin import AdminCommands
from webScraping import Wiki
from webScraping import Steam
from webScraping import Custom

token = os.environ['TOKEN']  #discord bot token

weatherkey = os.environ['weather']  #weather API Key

logger = settings.logging.getLogger("bot")

def run():
  intents = discord.Intents.all()

  bot = commands.Bot(command_prefix="#", intents=intents)
  bot.add_cog(AdminCommands(bot))
  
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
  
  # @bot.event
  # async def on_member_join(member):
  #   defaultrole = discord.utils.get(member.guild.roles, name="default")
  #   await member.add_roles(defaultrole)

  # @bot.command()
  # async def purge(ctx, amount=10):
  #   await ctx.channel.purge(limit=amount + 1)
  #   await ctx.send(f'{amount} messages successfully purged')

  # def perms(**perms):

  #   async def predicate(ctx):

  #     #checks admin role
  #     if ctx.author.guild_permissions.administrator:
  #       return True

  #     #checks  other role perms
  #     for role in ctx.author.roles:
  #       if role.permissions_in(ctx.channel).manage_channels:
  #         return True

  #     #role has no perms
  #     raise commands.Missing.Permissions(perms)

  #   return commands.check(predicate)

  # @bot.command()
  # @perms(kick_members=True)
  # async def kick(ctx, member: discord.Member):
  #   await member.kick()
  #   await ctx.send(f"{member} has been kicked.")

  # @bot.command()
  # @perms(ban_members=True)
  # async def ban(ctx, member: discord.Member):
  #   await member.ban()
  #   await ctx.send(f"{member} has been banned.")

  # @bot.command()
  # @perms(add_roles=True)
  # async def mute(ctx, member: discord.Member
  #                ):  #checks for muted role and creates if doesn't exist
  #   role = discord.utils.get(ctx.guild.roles, name="Muted")
  #   if not role:
  #     role = await ctx.guild.create_role(name="Muted")
  #     for channel in ctx.guild.channels:
  #       await channel.set_permissions(role, send_messages=False)

  #   await member.add_roles(role)
  #   await ctx.send(f"{member} has been muted.")


  @bot.command()
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
  @bot.command()
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
