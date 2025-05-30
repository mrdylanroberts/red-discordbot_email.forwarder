# Discord Email Cog for Red-DiscordBot

A Red-DiscordBot cog that forwards unread Gmail messages to configured Discord channels. The cog uses Gmail API to check for new emails and forwards them to specified Discord channels based on sender configurations.

## Features

- OAuth2 authentication with Gmail API
- Configurable email forwarding per Discord channel
- Automatic email checking every 5 minutes
- Rich Discord embeds for email content
- Mark forwarded emails as read
- Per-guild configuration storage
- Secure credential storage with optional encryption

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

### Option 1: Using Environment Variables (Most Secure)

1. Create a new project in Google Cloud Console
2. Enable Gmail API for your project
3. Create OAuth 2.0 credentials
4. Download the credentials JSON file
5. Set the environment variable `GMAIL_CREDENTIALS` with the contents of the JSON file:

   ```bash
   # Linux/Mac
   export GMAIL_CREDENTIALS=$(cat /path/to/credentials.json)
   
   # Windows PowerShell
   $env:GMAIL_CREDENTIALS = Get-Content -Raw -Path "C:\path\to\credentials.json"
   ```

   For permanent storage, add this to your startup script or environment configuration.

### Option 2: Using Credentials File

1. Create a new project in Google Cloud Console
2. Enable Gmail API for your project
3. Create OAuth 2.0 credentials
4. Download the credentials and save as `credentials.json` in your Red bot's data path for this cog
   - Usually in `~/.local/share/Red-DiscordBot/data/EmailCog/`
   - On Windows: `%APPDATA%\Red-DiscordBot\data\EmailCog\`

## Security Features

### Token Encryption

The cog now supports encrypting the OAuth token file for additional security. This requires the `cryptography` package, which is included in the requirements.txt file.

When the cog loads, it will:
1. Automatically generate an encryption key if one doesn't exist
2. Store the key securely with restricted permissions
3. Use the key to encrypt/decrypt the OAuth token

### File Permissions

All sensitive files (credentials, tokens, encryption keys) are stored with restricted permissions (600) to ensure only the owner can read or write them.

## Usage

### Commands

All commands use the prefix configured for your bot (default is `[p]`). Examples below use `[p]` as the prefix.

- `[p]emailcog add <channel> <allowed_senders>`: Configure email forwarding for a channel
  - `channel`: The channel mention or ID
  - `allowed_senders`: Comma-separated list of allowed email senders
  - Example: `[p]emailcog add #announcements news@example.com,updates@example.com`

- `[p]emailcog list`: List all email forwarding configurations for the server

- `[p]emailcog remove <channel>`: Remove email forwarding configuration for a channel
  - `channel`: The channel mention or ID

- `[p]emailcog interval <minutes>`: Set the email checking interval
  - `minutes`: Number of minutes between email checks (minimum 1 minute)
  - Example: `[p]emailcog interval 10` to check emails every 10 minutes

### Permissions

- Commands require administrator permissions
- Bot needs permission to send messages and embeds in configured channels

## Notes

- The first time you run the bot, it will open a browser window for Gmail OAuth2 authentication
- Token is stored securely (encrypted if cryptography is available) in your Red bot's data directory
- Emails are checked every 5 minutes by default (configurable with `[p]emailcog interval`)
- Only unread emails are forwarded
- Forwarded emails are marked as read automatically
- Configurations are stored per guild using Red's built-in Config system