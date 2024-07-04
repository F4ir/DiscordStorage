# Discord Storage
Utilize Discord servers as cloud storage!



## Tutorial
#### Setting up the bot/server

##### 1) Creating the bot
In order for this program to work, you're going to need to create a discord bot so we can connect to the discord API. Go to [this](https://discordapp.com/developers/applications/me) link to create a bot. Make sure to create a user bot and ensure the bot is private. [Here's](http://i.imgur.com/QIWBksk.png) a picture to the configuration. **Keep note of the token and the client ID.**
##### 2) Setting up the server
The bot will need a place to upload files. Create a new discord server, make sure no one else is on it unless you want them to access your files.

##### 3) Adding your bot to the server
To add the bot to the server (assuming your bot isn't public), go to the following link: https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&permissions=8&scope=bot
Replace {CLIENT_ID} with the client ID you copied earlier. Then, select the server you just made and authorize. Your server should now show your bot like [this](http://i.imgur.com/NnqQAv7.png).



#### Setting up the program
##### 1) Dependecies
Clone the repository and run ```pip install -r requirements.txt``` or run ```requirements installation.bat``` to install the dependencies for the program.

##### 2) Configuration
Run ```python ds.py``` in commandprompt or run ```start.bat``` to begin configuration of the bot. When prompted, copy and paste your **token** from when you created your bot. For the channel ID, copy the channel ID with right click on the channel (developer mode must be enabled under appearance on Discord settings to have the option for Copy ID). Your configuration should look like [this](http://i.imgur.com/g72BDoG.png)


*You can delete ```config.discord``` to reconfigure the program.*
#### Commands
Usage: ```python ds.py [flag] {args}```

```-upload /full_path/file.exe``` The -upload or -u flag and the full file path uploads a file.

```-download {FILE_CODE}``` The -download or -d flag and the file code will download a file from the discord server. Refer to the ```-list``` command to see uploaded file codes.

```-delete {FILE_CODE}``` The -delete or -del flag and the file code will delete the file of your selected code that you chose from the ```-list``` command from the discord server and the config file.

```-list``` The -list or -l flag will list all the file names/codes/sizes uploaded to the discord server.

```-help``` The -help or -h flag will display the help message (these commands listed here).



#### Disclaimer
You shouldn't be using this as your main source of file storage. Program was inspired by [nigel-DiscordStorage](https://github.com/nigel/DiscordStorage). 

It is his Original code but i added some extra futures.
