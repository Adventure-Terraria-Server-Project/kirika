#! /usr/bin/env python
'''Yama's A.T.S.P.-Bot for IRC-Tasks'''

import irc.bot
import irc.strings
import re
import logging
import configparser
from time import sleep
from multiprocessing import Process
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
irc.client.ServerConnection.buffer_class.errors = 'ignore'
#logging.basicConfig(level=logging.DEBUG)
config = configparser.ConfigParser()
config.read('cmds.ini')
bc = 0
t = None
y = None
wr = None

class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.privmsg('nickserv', 'identify ' + config.get('rest', 'nickserv'))
        c.join(self.channel)

    def on_join(self, c, e):
        if 'kirika' != e.source.nick.lower() and e.target == '#terraria-support':
            nick = e.source.nick
            for msg in config.options('support'):
                c.notice(nick, config.get('support', msg))

    def on_privmsg(self, c, e):
        nick = e.source.nick
        c.privmsg(nick, config.get('rest', 'privmsg'))

    def on_pubmsg(self, c, e):
        a = e.arguments[0]
        try:
            if re.match('^\!\w+', a):
                self.do_command(e, a[1:], bc)
            elif ''.join(a).find('kirika') != -1:
                if e.target.lower() == '#terraria-support':
                    c.privmsg(e.target, 'If you need help, type !help')
                else:
                    c.privmsg(e.target, config.get('rest', 'contact'))
        except TypeError:
            pass

    #Broadcasts ------>
    def bc_terraria(self, e, bcterraria):
        c = self.connection
        config.read('broadcasts.ini')
        while t.is_alive:
            for i in config.options('#terraria'):
                c.privmsg('#terraria', config.get('#terraria', i))
                sleep(10)

    def bc_yamaria(self, e, bcyamaria):
        c = self.connection
        config.read('broadcasts.ini')
        while y.is_alive:
            for m in config.options('#Yamaria'):
                c.privmsg('#Yamaria', config.get('#Yamaria', m))
                sleep(900)

    def bc_worldreset(self, e, bc):
        c = self.connection
        while wr.is_alive:
            c.privmsg('#Yamaria', '#10We are preparing the new World. You will be informed, if the server is free to join.' )
            sleep(120)

    #Commands ------>
    def do_command(self, e, cmd, bc):
        nick = e.source.nick
        c = self.connection

        #Help commands ------>
        if e.target.lower() != '#yamaria':
            if cmd.lower() in config.options('pubcmd'):
                c.privmsg(e.target, config.get('pubcmd', cmd))
        elif e.target.lower() == '#yamaria' and cmd in ['help', 'trigger']:
            c.privmsg(e.target, config.get('rest', 'support'))

        #Admin commands ------>
        if e.target.lower() == '#terraria':
            if cmd == 'disconnect':
                self.disconnect()
            elif cmd == 'exit' and nick == 'Yama':
                self.die()
            elif 'bc' == cmd.split(' ')[0]:
                if '#terraria' in cmd:
                    if 'stop' in cmd:
                        if t != None and t.is_alive:
                            t.terminate()
                            c.privmsg(e.target, '4#Terraria Broadcast halted')
                    else:
                        global t
                        t = Process(target=self.bc_terraria, args=(e, bc))
                        t.start()

                elif '#Yamaria' in cmd:
                    if 'stop' in cmd:
                        if y != None and y.is_alive:
                            y.terminate()
                            c.privmsg(e.target, '4#Yamaria Broadcast halted')
                    else:
                        global y
                        y = Process(target=self.bc_yamaria, args=(e, bc))
                        y.start()

                elif 'world reset' in cmd:
                    if 'stop' in cmd:
                        if wr != None and wr.is_alive:
                            wr.terminate()
                            c.privmsg('#Yamaria', '#4You can join the server now!')
                    else:
                        global wr
                        wr = Process(target=self.bc_worldreset, args=(e, bc))
                        wr.start()

def main():
    import sys
    if len(sys.argv) != 4:
        print("Usage: testbot <server[:port]> <channel> <nickname>")
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print("Error: Erroneous port.")
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]

    bot = TestBot(channel, nickname, server, port)
    bot.start()

if __name__ == "__main__":
    main()
