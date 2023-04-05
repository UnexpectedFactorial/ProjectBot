import discord
from discord.ext import commands


class AdminCommands(commands.Cog):
  def __init__(self,bot):
    self.bot = bot

def perms(**perms):
  async def predicate(ctx):
    #checks admin role
    if ctx.author.guild_permissions.administrator:
      return True
    #checks  other role perms
    for role in ctx.author.roles:
      if role.permissions_in(ctx.channel).manage_channels:
        return True
    #role has no perms
    raise commands.MissingPermissions(perms)
  return commands.check(predicate)
  
  @commands.Cog.listener()
  async def on_member_join(self, member):
    defaultrole = discord.utils.get(member.guild.roles, name="default")
    await member.add_roles(defaultrole)

  @commands.command()
  async def purge(self, ctx, amount=10):
    await ctx.channel.purge(limit=amount+1)
    await ctx.send(f'{amount} messages successfully purged')

  @commands.command()
  @perms(kick_members=True)
  async def kick(self, ctx, member: discord.Member):
    await member.kick()
    await ctx.send(f"{member} has been kicked.")

  @commands.command()
  @perms(ban_members=True)
  async def ban(self, ctx, member: discord.Member):
    await member.ban()
    await ctx.send(f"{member} has been banned.")

  @commands.command()
  @perms(add_roles=True)
  async def mute(self, ctx, member: discord.Member):  #checks for muted role and creates if doesn't exist
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
      role = await ctx.guild.create_role(name="Muted")
      for channel in ctx.guild.channels:
        await channel.set_permissions(role, send_messages=False)

    await member.add_roles(role)
    await ctx.send(f"{member} has been muted.")


async def setup(bot):
    await bot.add_cog(AdminCommands(bot))