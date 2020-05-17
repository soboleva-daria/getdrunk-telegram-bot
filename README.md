**getdrunk is a telegram bot that recommends you an alcohol drink in return to the list of ingredients you have.**

**Description** 

getdrunk bot supports the next scenarios of communication:
-  ask and receive the recipe of the cocktail in return to ingredients provided
-  ask and receive all the recipes of the cocktails that are similar to the given one
-  ask and receive current intoxication level (in stages: Sobriety, Euphoria, Excitement, Confusion, ..., Coma, Death)
-  ask and receive the image of the cocktail
-  ask and receive any useful information about the cocktail
-  ask and receive the recipe of the day
-  ask and recieve the menu information
-  ask to start the session
-  ask to end the session

**Examples of the dialogs supported**
<img src="get_drunk_telegram_bot/images/examples.png" width="1000" height="350" />

**The Authors**
- Daria Soboleva, 517 group (@soboleva-daria)
- Nikolay Skachkov, 517 group (@Seriont)
- Alexey Pismenny, 517 group (@alexey-pismenny)
- Mariia Yavorskaia, 517 group (@IavorskaiaMariia)


**How to start using**

If you want to try using our bot you can write a message to @get_drunk_bot in Telegram.

If you want to run your own bot follow the instructions below. 
    
**How to install and run**

After clonning, you may use two different ways to run the bot:  

(1) Install the package (Recommended)
```python
pip install <path-to-root>
```
(2) Preparing to run your own bot
- Write a message to @BotFather in Telegram. It will give you your own ```<token>``` if you want to run your own GetDrunkBot
- Bind your port with external url. For example you may run ngrok. After installing ngrok you should run:
```
./ngrok http <port>
```
```<your server url>``` is the one returned by this command. Note: it should start with ```https:```.

(3) Run the command (Please verify you have Python >=3.6.0) 
```python
   python -m get_drunk_telegram_bot --token <token> --port <port> ----web-hook-url <your server url>
```
Your bot is ready. You may write it a message!

<img src="get_drunk_telegram_bot/images/readme-img.png" width="400" height="350" />


