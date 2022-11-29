import os
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.command()
async def test(ctx): #trigger word here
  await ctx.send("I am alive!") #sending a message back here


token = os.environ['TOKEN']
bot.run(token)
