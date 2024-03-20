# dsmusic

## Description

This is a very simple discord bot using slash commands to play music using lavalink on your guild channels.

## Setup

### Docker

The preferred method to run this is with a docker container. To launch it, run the following command:

```bash
docker run -d \
   -e DS_TOKEN="DISCORD_TOKEN" \
   -e DS_GUILD_ID="YOUR_GUILD_ID" \ 
   -e CF_TOKEN="CLOUDFLARE_TOKEN" \
   -e CF_ACCOUNT_ID="CLOUDFLARE_ACCOUNT_ID" \
   -v $(pwd)/lavalink.json:/bot/config/lavalink.json \
   ghcr.io/jotonedev/dsmusic:latest
```

The file lavalink.json must be created using the [template](config/lavalink.example.json) in the repository.
If you haven't already set up a lavalink node, you can check the lavalink
repository [here](https://github.com/lavalink-devs/Lavalink) on how to set up one.
After that you need to add its ip address, port and password in the lavalink.json file. You can add how many nodes you
want, but only one is required.

### Console

You can also launch the bot manually using the following commands (just remember to edit the lavalink.json
appropriately):

```bash
# Add environment variables
export DS_TOKEN="DISCORD_TOKEN"
export DS_GUILD_ID="YOUR_GUILD_ID"
export CF_TOKEN="CLOUDFLARE_TOKEN"
export CF_ACCOUNT_ID="CLOUDFLARE_ACCOUNT_ID"

# Minimum requirements
pip install --upgrade discord.py mafic

# Run the bot
python -m dsmusic
```

If you want to install the bot with the optional requirements, you can use [poetry](https://python-poetry.org/)

### Notes

If you don't want to use the Cloudflare integration, just don't declare the environment variables `CF_TOKEN` and `CF_ACCOUNT_ID`.
