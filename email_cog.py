import asyncio
import os
import pickle
from datetime import datetime, timezone
from typing import Dict, List

import discord
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.config import Group
from redbot.core.utils.chat_formatting import box, pagify

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class EmailCog(commands.Cog):
    """Forward Gmail messages to Discord channels."""

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(
            self,
            identifier=987654321,
            force_registration=True,
        )
        default_guild = {
            "channel_configs": {},  # channel_id -> list of allowed senders
            "last_check_time": None,
            "check_interval": 5,  # Default check interval in minutes
        }
        self.config.register_guild(**default_guild)
        
        # Gmail API settings
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        self.TOKEN_FILE = 'token.pickle'
        self.CREDENTIALS_FILE = 'credentials.json'
        self.service = None

        # Start background task
        self.bg_task = self.bot.loop.create_task(self.check_emails_loop())

    def cog_unload(self):
        if self.bg_task:
            self.bg_task.cancel()

    async def authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        creds = None

        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.CREDENTIALS_FILE):
                    raise FileNotFoundError(f'Missing {self.CREDENTIALS_FILE}. Please download it from Google Cloud Console.')

                flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS_FILE, self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open(self.TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)

    @commands.group(name="emailcog")
    @commands.guild_only()
    @commands.admin_or_permissions(administrator=True)
    async def emailcog(self, ctx: commands.Context):
        """Email forwarding settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @emailcog.command(name="interval")
    async def set_interval(self, ctx: commands.Context, minutes: int):
        """Set the email checking interval in minutes (minimum 1 minute).

        Args:
            minutes: The interval in minutes between email checks
        """
        if minutes < 1:
            await ctx.send("The check interval must be at least 1 minute.")
            return

        await self.config.guild(ctx.guild).check_interval.set(minutes)
        await ctx.send(f"Email check interval set to {minutes} minutes.")
        
        # Restart the background task with new interval
        if self.bg_task:
            self.bg_task.cancel()
        self.bg_task = self.bot.loop.create_task(self.check_emails_loop())

    @emailcog.command(name="add")
    async def add_sender(self, ctx: commands.Context, channel: str, *, allowed_senders: str):
        """Configure email forwarding for a channel.

        Args:
            channel: The channel mention or ID
            allowed_senders: Comma-separated list of allowed email senders
        """
        try:
            channel_id = int(channel.strip('<#>'))
            channel_obj = ctx.guild.get_channel(channel_id)
            if not channel_obj:
                await ctx.send("Invalid channel. Please mention a valid channel or use its ID.")
                return

            async with self.config.guild(ctx.guild).channel_configs() as configs:
                configs[str(channel_id)] = [s.strip() for s in allowed_senders.split(',')]

            await ctx.send(f"Email forwarding configured for {channel_obj.mention}")

        except ValueError:
            await ctx.send("Invalid channel format. Please mention the channel or use its ID.")

    @emailcog.command(name="list")
    async def list_config(self, ctx: commands.Context):
        """List email forwarding configuration for this server."""
        configs = await self.config.guild(ctx.guild).channel_configs()
        
        if not configs:
            await ctx.send("No email forwarding configurations found.")
            return

        msg = ["Email forwarding configurations:"]
        for channel_id, senders in configs.items():
            channel = ctx.guild.get_channel(int(channel_id))
            if channel:
                msg.append(f"\n{channel.mention}:")
                msg.append(box('\n'.join(senders)))

        for page in pagify('\n'.join(msg)):
            await ctx.send(page)

    @emailcog.command(name="remove")
    async def remove_config(self, ctx: commands.Context, channel: str):
        """Remove email forwarding configuration for a channel.

        Args:
            channel: The channel mention or ID
        """
        try:
            channel_id = int(channel.strip('<#>'))
            async with self.config.guild(ctx.guild).channel_configs() as configs:
                if str(channel_id) in configs:
                    del configs[str(channel_id)]
                    await ctx.send(f"Removed email forwarding configuration for <#{channel_id}>")
                else:
                    await ctx.send("No configuration found for this channel.")

        except ValueError:
            await ctx.send("Invalid channel format. Please mention the channel or use its ID.")

    async def create_message_embed(self, message_data: dict) -> discord.Embed:
        """Create a Discord embed from an email message."""
        headers = {header['name']: header['value'] 
                  for header in message_data['payload']['headers']}
        
        embed = discord.Embed(
            title=headers.get('Subject', 'No Subject'),
            color=await self.bot.get_embed_color(None),
            timestamp=datetime.fromtimestamp(int(message_data['internalDate']) / 1000)
        )

        embed.add_field(name='From', value=headers.get('From', 'Unknown'), inline=False)
        
        # Extract plain text content
        parts = message_data['payload'].get('parts', [])
        content = ''
        for part in parts:
            if part['mimeType'] == 'text/plain':
                content = part.get('body', {}).get('data', '')
                break

        if content:
            if len(content) > 1024:
                content = content[:1021] + '...'
            embed.add_field(name='Content', value=content, inline=False)

        return embed

    async def check_emails_loop(self):
        """Background task to check for new emails."""
        await self.bot.wait_until_ready()
        
        while True:
            try:
                if not self.service:
                    await self.authenticate()

                for guild in self.bot.guilds:
                    last_check = await self.config.guild(guild).last_check_time()
                    if not last_check:
                        last_check = datetime.now(timezone.utc).timestamp()
                        await self.config.guild(guild).last_check_time(last_check)
                        continue

                    configs = await self.config.guild(guild).channel_configs()
                    if not configs:
                        continue

                    query = f'is:unread after:{int(last_check)}'
                    results = self.service.users().messages().list(
                        userId='me', q=query
                    ).execute()
                    messages = results.get('messages', [])

                    for message in messages:
                        msg_data = self.service.users().messages().get(
                            userId='me', id=message['id'], format='full'
                        ).execute()

                        headers = {h['name']: h['value'] 
                                 for h in msg_data['payload']['headers']}
                        sender = headers.get('From', '')

                        # Check each channel's allowed senders
                        for channel_id, allowed_senders in configs.items():
                            if any(allowed in sender for allowed in allowed_senders):
                                try:
                                    channel = guild.get_channel(int(channel_id))
                                    if channel:
                                        embed = await self.create_message_embed(msg_data)
                                        await channel.send(embed=embed)

                                        # Mark message as read
                                        self.service.users().messages().modify(
                                            userId='me',
                                            id=message['id'],
                                            body={'removeLabelIds': ['UNREAD']}
                                        ).execute()
                                except discord.errors.Forbidden:
                                    continue
                                except Exception as e:
                                    continue

                    # Update last check time
                    await self.config.guild(guild).last_check_time(
                        datetime.now(timezone.utc).timestamp()
                    )

            except Exception as e:
                pass

            check_interval = await self.config.guild(guild).check_interval()
            await asyncio.sleep(check_interval * 60)  # Convert minutes to seconds