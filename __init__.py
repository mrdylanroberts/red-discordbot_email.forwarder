from .email_cog import EmailCog

async def setup(bot):
    cog = EmailCog(bot)
    await bot.add_cog(cog)

__red_end_user_data_statement__ = "This cog stores email sender configurations for Discord channels and Gmail API credentials locally."