# Discord Email Cog for Red-DiscordBot

A Red-DiscordBot cog that forwards unread Gmail messages to configured Discord channels. The cog uses Gmail API to check for new emails and forwards them to specified Discord channels based on sender configurations.

## Features

- OAuth2 authentication with Gmail API
- Configurable email forwarding per Discord channel
- Automatic email checking every 5 minutes
- Rich Discord embeds for email content
- Mark forwarded emails as read
- Per-guild configuration storage

## Installation

1. Make sure you have a running instance of Red-DiscordBot
2. Add the repository to your bot:
   ```
   [p]repo add email-cog https://github.com/mrdyl/red-emailcog
   ```
3. Install the cog:
   ```
   [p]cog install email-cog emailcog
   ```
4. Load the cog:
   ```
   [p]load emailcog
   ```

## Gmail API Setup

1. Create a new project in Google Cloud Console
2. Enable Gmail API for your project
3. Create OAuth 2.0 credentials
4. Download the credentials and save as `credentials.json` in your Red bot's data path
   - Usually in `~/.local/share/Red-DiscordBot/data/emailcog/`

## Usage

### Commands

- `[p]emailcog add <channel> <allowed_senders>`: Configure email forwarding for a channel
  - `channel`: The channel mention or ID
  - `allowed_senders`: Comma-separated list of allowed email senders
  - Example: `[p]emailcog add #announcements news@example.com,updates@example.com`

- `[p]emailcog list`: List all email forwarding configurations for the server

- `[p]emailcog remove <channel>`: Remove email forwarding configuration for a channel
  - `channel`: The channel mention or ID

### Permissions

- Commands require administrator permissions
- Bot needs permission to send messages and embeds in configured channels

## Notes

- The first time you run the bot, it will open a browser window for Gmail OAuth2 authentication
- Token is stored securely in your Red bot's data directory
- Emails are checked every 5 minutes to avoid API rate limits
- Only unread emails are forwarded
- Forwarded emails are marked as read automatically
- Configurations are stored per guild using Red's built-in Config system