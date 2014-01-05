kirika
======

IRC-Bot with broadcast and triggers.  
Designed to run with **Python 3**.  
Coded with Python 3.3.

Using [Jaraco IRC Module](https://bitbucket.org/jaraco/irc).  
Based on [this example-script](https://bitbucket.org/jaraco/irc/src/5fb84776e69a3a5fe4f3e34f27571d3b575f2fab/scripts/testbot.py).

**Run**  
`./bot.py yamahi.eu:6667 #Yamaria botnick`

I did a lot for myself but it should be easy to modify it.

**e.arguments** has the whole message that was posted.  
**e.target** is the channel where the message was posted.

**on_welcome** is triggered on connecting to a server.  
Commands here are executed before joining channels.

**on_join** is triggered if someone joins a channel or the bot itself.

**on_privmsg** is triggered if the bot gets private messages (query).

**on_pubmsg** is triggered on messages on channels.

*More events are possible.* Just **uncomment the 13th line** and check the output.

The standard 'help'-triggers are not really hardcoded.  
Every message with the beginning '!' will trigger the **on_pubmsg**.  
Second word is **here** ignored. If the first word appears in the file *cmds.ini* under *[pubcmd]*, it goes to the **do_command** function.

The messages in *cmds.ini* under *[support]* are sent to a user only via **notice** if he joins the desired channel (#terraria-support).  
Messages under the section *[rest]* are sent on private messages and if the nick of the bot is mentioned in a message.  
Nickserv is to identify on nickserv.

I made a extra file for broadcasts and seperated the broadcasts for each channel in sections.  
All the broadcasts are posted in the desired channel in the order in a loop.  
To change the intervall, just edit the integer in the sleep() function.

**Example**  
!bc #Yamaria  
*Starts the broadcasts fpr the channek #Yamaria*

!bc #Yamaria stop  
*Stops the running broadcast for #Yamaria*

**These commands are only executable in #terraria (just change it).