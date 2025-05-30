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

### Method 1: From Repository (Recommended)

1. Make sure you have a running instance of Red-DiscordBot
2. Add the repository to your bot:
   ```
   [p]repo add email-cog https://github.com/mrdylanroberts/red-discordbot_email.forwarder
   ```
3. Install the cog:
   ```
   [p]cog install email-cog EmailCog
   ```
4. Load the cog:
   ```
   [p]load EmailCog
   ```

### Method 2: Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mrdylanroberts/red-discordbot_email.forwarder
   ```
2. Move the files to your Red-DiscordBot's cogs directory:
   ```bash
   # For Linux/Mac
   mkdir -p /path/to/your/redbot/cogs/EmailCog
   cp -r red-discordbot_email.forwarder/* /path/to/your/redbot/cogs/EmailCog/
   
   # For Windows
   mkdir "%USERPROFILE%\Red-DiscordBot\cogs\EmailCog"
   xcopy /E /I red-discordbot_email.forwarder\* "%USERPROFILE%\Red-DiscordBot\cogs\EmailCog\"
   ```
3. Install required dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
4. Load the cog in Discord:
   ```
   [p]load EmailCog
   ```

## Gmail API Setup

1. Create a new project in Google Cloud Console
2. Enable Gmail API for your project
3. Create OAuth 2.0 credentials
4. Download the credentials and save as `credentials.json` in your Red bot's data path
   - Usually in `~/.local/share/Red-DiscordBot/data/emailcog/`

## Usage

### Commands

All commands use the prefix configured for your bot (default is `!`). Examples below use `!` as the prefix.

- `!emailcog add <channel> <allowed_senders>`: Configure email forwarding for a channel
  - `channel`: The channel mention or ID
  - `allowed_senders`: Comma-separated list of allowed email senders
  - Example: `!emailcog add #announcements news@example.com,updates@example.com`

- `!emailcog list`: List all email forwarding configurations for the server

- `!emailcog remove <channel>`: Remove email forwarding configuration for a channel
  - `channel`: The channel mention or ID

- `!emailcog interval <minutes>`: Set the email checking interval
  - `minutes`: Number of minutes between email checks (minimum 1 minute)
  - Example: `!emailcog interval 10` to check emails every 10 minutes

### Permissions

- Commands require administrator permissions
- Bot needs permission to send messages and embeds in configured channels

## Notes

- The first time you run the bot, it will open a browser window for Gmail OAuth2 authentication
- Token is stored securely in your Red bot's data directory
- Emails are checked every 5 minutes by default (configurable with `!emailcog interval`)
- Only unread emails are forwarded
- Forwarded emails are marked as read automatically
- Configurations are stored per guild using Red's built-in Config system