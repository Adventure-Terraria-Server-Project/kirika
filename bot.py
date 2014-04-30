#! /usr/bin/env python
'''Yama's A.T.S.P.-Bot for IRC-Tasks'''

import irc.bot
import irc.strings
import re
import logging
import configparser
from time import sleep, gmtime, strftime
from multiprocessing import Process
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr

irc.client.ServerConnection.buffer_class.errors = 'ignore'
#logging.basicConfig(level=logging.DEBUG)
config = configparser.ConfigParser()
config.read('msg.ini')
wr = 0
bc_t = False
bc_y = False
bc_wr = False
bc_st = False
bc_st2 = False

class kirika(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        config.read('config.ini')
        c.mode(c.nick, '+B')
        c.privmsg('nickserv', 'identify ' + config.get('server', 'nickserv'))
        c.join(self.channel)

    def on_part(self, c, e):
        if 'kirika' != e.source.nick.lower() and e.target.lower() == '#terraria':
            nick = e.source.nick
            with open('join.log', 'a') as join:
                print(strftime('%Y.%m.%d - %H:%M:%S', gmtime()) + ' ' + nick + ' has left<br>', file=join)
            with open('terraria.log', 'a') as chan:
                print(strftime('%Y.%m.%d - %H:%M:%S', gmtime()) + ' ' + nick + ' has left<br>', file=chan)

    def on_join(self, c, e):
        if 'kirika' != e.source.nick:
            nick = e.source.nick
            if e.target.lower() == '#terraria-support':
                for msg in config.options('support'):
                    c.notice(nick, config.get('support', msg))
            elif e.target.lower() == '#terraria':
                with open('join.log', 'a') as join:
                    print(strftime('%Y.%m.%d - %H:%M:%S', gmtime()) + ' ' + nick + ' has joined<br>', file=join)
                with open('terraria.log', 'a') as chan:
                    print(strftime('%Y.%m.%d - %H:%M:%S', gmtime()) + ' ' + nick + ' has joined<br>', file=chan)

    def on_privmsg(self, c, e):
        cmd = e.arguments[0]
        nick = e.source.nick
        with open('query.log', 'a') as query:
            print(strftime('%Y.%m.%d - %H:%M:%S', gmtime()) + ' &#60' + nick + '&#62 ' + cmd + '<br>', file=query)
        for chname, chobj in self.channels.items():
            users = ','.join(chobj.halfops())
            users += ','.join(chobj.opers())
            users += ','.join(chobj.owners())
            if chname == '#terraria':
                if nick in users:
                    if cmd.split()[0] == 'say':
                        say = ' '.join(cmd.split()[2:])
                        c.privmsg(cmd.split()[1], say)
                    elif cmd.split()[0] == 'cmd':
                        c.send_raw(cmd[4:])
                    return
        c.privmsg(nick, config.get('rest', 'privmsg'))

    def on_pubmsg(self, c, e):
        a = e.arguments[0]
        nick = e.source.nick
        try:
            if re.match('^\!\w+', a):
                self.do_command(e, a[1:])
            elif ''.join(a).find('kirika') != -1 and e.target.lower() == '#terraria-support':
                    c.privmsg(e.target, 'If you need help, type !help')
            elif e.target.lower() == '#terraria' and nick != 'ATSP':
                with open('terraria.log', 'a') as chan:
                    print(strftime('%Y.%m.%d - %H:%M:%S', gmtime()) + ' &#60' + nick + '&#62 ' + a + '<br>', file=chan)
        except TypeError:
            pass

    #Broadcasts ------>
    def bc_terraria(self, e):
        c = self.connection
        #config.read('broadcasts.ini')
        while t.is_alive:
            for i in config.options('#terraria'):
                c.privmsg('#terraria', config.get('#terraria', i))
                sleep(10)

    def bc_yamaria(self, e):
        c = self.connection
        #config.read('broadcasts.ini')
        while y.is_alive:
            for m in config.options('#Yamaria'):
                c.privmsg('#Yamaria', config.get('#Yamaria', m))
                sleep(900)

    def bc_worldreset(self, e):
        c = self.connection
        while wr.is_alive:
            c.privmsg('#Yamaria', '#10We are preparing the new World. You will be informed, if the server is free to join.')
            sleep(120)

    def bc_stream(self, e, game):
        c = self.connection
        while st.is_alive:
            c.privmsg('#Yamaria', '10Yama will stream4 %s 10in a few minutes!' %game)
            sleep()

    def bc_stream2(self, e, game):
        c = self.connection
        while st2.is_alive:
            c.privmsg('#Yamaria', '10Yama is streaming4 %s 10now: 4http://www.twitch.tv/Yamahi' %game)
            sleep(3)

    #Commands ------>
    def do_command(self, e, cmd):
        nick = e.source.nick
        c = self.connection

        #Help commands ------>
        if cmd.lower() in config.options('pubcmd'):
            c.privmsg(e.target, config.get('pubcmd', cmd))

        #Admin commands ------>
        elif e.target.lower() == '#terraria':
            if cmd == 'disconnect':
                self.disconnect()
            elif cmd == 'quit' and nick == 'Yama':
                self.die()
            elif cmd in config.options('admcmd'):
                c.privmsg('#Yamaria', config.get('admcmd', cmd))

            #Broadcasts ------>
            elif 'bc' == cmd.split(' ')[0]:
                if '#terraria' == cmd.split(' ')[1]:
                    global bc_t, t
                    if 'stop' in cmd:
                        if bc_t:
                            bc_t = False
                            t.terminate()
                            c.privmsg(e.target, '4#Terraria Broadcast halted')
                    elif bc_t == False:
                        bc_t = True
                        t = Process(target=self.bc_terraria, args=(e,))
                        t.start()
                    else:
                        c.privmsg(e.target, '4Broadcast is still running, dood')

                elif '#Yamaria' == cmd.split(' ')[1]:
                    global bc_y, y
                    if 'stop' in cmd:
                        if bc_y:
                            bc_y = False
                            y.terminate()
                            c.privmsg(e.target, '4#Yamaria Broadcast halted')
                    elif bc_y == False:
                        bc_y = True
                        y = Process(target=self.bc_yamaria, args=(e,))
                        y.start()
                    else:
                        c.privmsg(e.target, '4Broadcast is still running, dood')

                elif 'world reset' in cmd:
                    global bc_wr, wr
                    if 'stop' in cmd:
                        if bc_wr:
                            bc_wr = False
                            wr.terminate()
                            c.privmsg('#Yamaria', '#4You can join the server now!')
                    elif bc_wr == False:
                        bc_wr = True
                        wr = Process(target=self.bc_worldreset, args=(e,))
                        wr.start()
                    else:
                        c.privmsg(e.target, '4Broadcast is still running, dood')

                elif 'stream' == cmd.split(' ')[1]:
                    global bc_st, st
                    if 'stop' in cmd:
                        if bc_st:
                            bc_st = False
                            st.terminate()
                            c.privmsg(e.target, '4Stream-Broadcast halted')
                    elif bc_st == False:
                        bc_st = True
                        game = ' '.join(cmd.split(' ')[2:])
                        st = Process(target=self.bc_stream, args=(e, game))
                        st.start()
                    else:
                        c.privmsg(e.target, '4Broadcast is still running, dood')

                elif 'stream2' == cmd.split(' ')[1]:
                    global bc_st2, st2
                    if 'stop' in cmd:
                        if bc_st2:
                            bc_st2 = False
                            st2.terminate()
                            c.privmsg(e.target, '4Stream2-Broadcast halted')
                    elif bc_st2 == False:
                        bc_st2 = True
                        game = ' '.join(cmd.split(' ')[2:])
                        st2 = Process(target=self.bc_stream2, args=(e, game))
                        st2.start()
                    else:
                        c.privmsg(e.target, '4Broadcast is still running, dood')

def main():
    config.read('config.ini')
    server = config.get('server', 'ip')
    s = config.get('server', 'port')
    channel = config.get('server', 'channels')
    nickname = config.get('server', 'nick')
    try:
        port = int(s)
    except ValueError:
        print("Error: Erroneous port, using 6667.")
        port = 6667

    bot = kirika(channel, nickname, server, port)
    bot.start()

if __name__ == "__main__":
    main()
