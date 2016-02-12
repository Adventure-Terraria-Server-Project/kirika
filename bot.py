#! /usr/bin/env python
'''Yama's A.T.S.P.-Bot for IRC-Tasks'''

import re
import os
import csv
import msgs
import config
import random
import irc.bot
import requests
import irc.strings
from time import time, sleep, gmtime, strftime
from threading import Thread
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr

irc.client.ServerConnection.buffer_class.errors = 'ignore'
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
        #config.read('config.ini')
        c.mode(config.nick, '+B')
        c.privmsg('nickserv', 'identify ' + config.nickserv)
        c.join(self.channel)
        words = self.get_words(e)
        global slogans
        slogans = Thread(target=self.slogan, args=(e, words))
        slogans.start()

    def on_join(self, c, e):
        if 'kirika' != e.source.nick:
            nick = e.source.nick
            if e.target.lower() == '#terraria-support':
                for msg in msgs.support:
                    c.notice(nick, msg)

    def on_privmsg(self, c, e):
        cmd = e.arguments[0]
        nick = e.source.nick
        with open('logs/query.log', 'a') as query:
            print('<span style="color:green">%s</span> &#60;<span style="color:blue">%s</span>&#62; %s<br>' % (strftime('%Y.%m.%d - %H:%M:%S', gmtime()), nick, cmd), file=query)
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
        if re.match('^\!\w+', a):
            self.do_command(e, a[1:])
        elif ''.join(a).find('kirika') != -1 and e.target.lower() == '#terraria-support':
                c.privmsg(e.target, 'If you need help, type !help')
        elif e.target.lower() == '#terraria' and nick != 'ATSP':
            today = strftime('%y.%m.%d', gmtime())
            if not os.path.exists('logs/terraria-%s.log' % today):
                open('logs/terraria-%s.log' % today, 'x')
                os.remove('logs/terraria-%s.log' % strftime('%y.%m.%d', gmtime(time() - 259200)))
            with open('logs/terraria-%s.log' % today, 'a') as chan:
                print('<span style="color:green">%s</span> &#60;<span style="color:blue">%s</span>&#62; %s<br>' % strftime('%H:%M:%S', gmtime()), nick, a.replace('<', '&#60;').replace('>', '&#62;'), file=chan)

    def get_words(self, e):
        words = list()
        with open(config.itemlist) as itemsfile:
            itemsreader = csv.reader(itemsfile, delimiter=',', quotechar='"')
            for row in itemsreader:
                words.append(row[1])
        return words

    def slogan(self, e, words):
        c = self.connection
        while slogans.is_alive:
            sleep(10800)
            get = requests.get('http://www.sloganizer.net/en/outbound.php?slogan=%s' % random.choice(words))
            slog = str(get.text)
            slog = slog.replace("'", '"').replace('\\', '')
            slog = re.sub('<[^<]+?>', '', slog)
            slog = slog.replace('"', "'")
            c.privmsg('#Yamaria', slog)

    # Broadcasts ------>
    def bc_terraria(self, e):
        c = self.connection
        while t.is_alive:
            for msg in msgs.broadcasts.terraria:
                c.privmsg('#terraria', msg)
                sleep(10)

    def bc_yamaria(self, e):
        c = self.connection
        while y.is_alive:
            for msg in msgs.broadcasts.yamaria:
                c.privmsg('#Yamaria', msg)
                sleep(300)

    def bc_worldreset(self, e):
        c = self.connection
        while wr.is_alive:
            c.privmsg('#Yamaria', '#10We are preparing the new World. You will be informed, if the server is free to join.')
            sleep(120)

    # Commands ------>
    def do_command(self, e, cmd):
        nick = e.source.nick
        c = self.connection

        # Help commands ------>
        cmd = cmd.lower()
        if cmd in msgs.pubcmd.keys():
            c.privmsg(e.target, msgs.pubcmd[cmd])

        # Admin commands ------>
        elif e.target.lower() == '#terraria':
            if cmd == 'reload':
                reload(msgs)
                c.privmsg('#terraria', '4Broadcast Messages Reloaded')
            elif cmd == 'disconnect':
                self.disconnect()
            elif cmd == 'quit' and nick == 'Yama':
                self.die()
            elif cmd in msgs.admcmd.keys():
                c.privmsg('#Yamaria', msgs.admcmd[cmd])

            # Broadcasts ------>
            elif 'bc' == cmd.split(' ')[0]:
                if '#terraria' == cmd.split(' ')[1]:
                    global bc_t, t
                    if 'stop' in cmd:
                        if bc_t:
                            bc_t = False
                            t.terminate()
                            c.privmsg(e.target, '4#Terraria Broadcast halted')
                    elif not bc_t:
                        bc_t = True
                        t = Thread(target=self.bc_terraria, args=(e,))
                        t.start()
                    else:
                        c.privmsg(e.target, '4Broadcast is still running, dood')

                elif '#yamaria' == cmd.split(' ')[1]:
                    global bc_y, y
                    if 'stop' in cmd:
                        if bc_y:
                            bc_y = False
                            y.terminate()
                            c.privmsg(e.target, '4#Yamaria Broadcast halted')
                    elif not bc_y:
                        bc_y = True
                        y = Thread(target=self.bc_yamaria, args=(e,))
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
                    elif not bc_wr:
                        bc_wr = True
                        wr = Thread(target=self.bc_worldreset, args=(e,))
                        wr.start()
                    else:
                        c.privmsg(e.target, '4Broadcast is still running, dood')


def main():
    server = config.ip
    s = config.port
    channel = config.channels
    nickname = config.nick
    try:
        port = int(s)
    except ValueError:
        print("Error: Erroneous port, using 6667.")
        port = 6667

    bot = kirika(channel, nickname, server, port)
    bot.start()

if __name__ == "__main__":
    main()
