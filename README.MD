Telethon app allows to get chats and messages from those chats via API requests for easier integration with other services

original telethon library is here - https://github.com/LonamiWebs/Telethon

telethon-app contains session generator for 'session_name.session' for usage of telethon as telegram client instead of bot

sessionGenerator has run.sh file for easier running python script. in the file run.sh should be replaced TELEGRAM_API_ID and TELEGRAM_API_HASH  
session_name.session file should be in the folder app inside telethon-app folder<br/>
.env file should be in telethon-app folder<br/>
example of .env:
 - TELEGRAM_API_ID=12345
 - TELEGRAM_API_HASH=0123456789abcdef0123456789abcdef

telethon-app starts from the telethon-app directory by command
- docker compose up -d --build

it will listen to 5000 port and use .env file