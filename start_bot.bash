#!/bin/bash

echo "Starting bot at $(date +%F_%T)..."
# Wait for network
TRIES=1
while true; do
    ping -c1 www.discord.com &> /dev/null && break;
    let TRIES++
    sleep 0.1;
done
echo "Network ready after $TRIES tries."

# Activate virtual environment and run
cd /home/goss/GossDiscordBot
source .venv/bin/activate
echo "Current Python is $(which python)"
python -m goss_bot