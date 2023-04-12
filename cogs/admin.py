import discord
from discord.ext import commands

class admin(commands.Cog):
  def __init__(self,bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    print("Admin commands available")

  @commands.command()
  async def alive(self, ctx):
    bot_latency = round(self.bot.latency * 1000)
    await ctx.send(f"ping = {bot_latency} ms.")

  @commands.command()
  @commands.has_permissions(kick_members=True)
  async def kick(self, ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
            return await ctx.send("You can't kick yourself!")
    try:
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} has been kicked from the server.")
    except:
        await ctx.send("Failed to kick member.")

  @commands.command()
  @commands.has_permissions(ban_members=True)
  async def ban(self, ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
            return await ctx.send("You can't ban yourself!")
    try:
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} has been banned from the server.")
    except:
        await ctx.send("Failed to ban member.")
  
  @commands.command()
  @commands.has_permissions(manage_messages=True)
  async def purge(self, ctx, amount=10):
    await ctx.channel.purge(limit=amount+1)
    await ctx.send(f'{amount} messages successfully purged')
  
  @commands.Cog.listener()
  async def on_member_join(self, member):
    defaultrole = discord.utils.get(member.guild.roles, name="default")
    await member.add_roles(defaultrole)


  @commands.command()
  @commands.has_permissions(manage_roles=True)
  async def mute(self, ctx, member: discord.Member):  #checks for muted role and creates if doesn't exist
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
      role = await ctx.guild.create_role(name="Muted")
      for channel in ctx.guild.channels:
        await channel.set_permissions(role, send_messages=False)

    await member.add_roles(role)
    await ctx.send(f"{member} has been muted.")


async def setup(bot):
    await bot.add_cog(admin(bot))