from discordstorage import core
import threading, json, asyncio, random, sys, argparse, os, time

TOKEN_SECRET = ""  # bot's secret token
ROOM_ID = ""  # channel text ID
BOT_INFO = None
FILES = None

# Generates a file code from 0-4097
def genCode():
    code = str(random.randint(0, 4098))
    if FILES is None:
        return code
    while code in FILES.keys():
        code = str(random.randint(0, 4098))
    return code

# Returns if the config file is configured or not.
def isConfigured():
    return os.path.isfile('config.discord')

# Invokes file uploading, to be used on a thread that's not in main thread.
# Writes to config file accordingly.
def tellupload(line1, line2, cmd, code, client):
    while not client.isready():
        time.sleep(0.5)
    if not os.path.isfile(cmd):
        print('[ERROR] File does not exist.')
        client.logout()
        return
    flcode = client.upload(cmd, code)
    if flcode == -1:
        print('[ERROR] File upload fail')
    else:
        jobject = json.loads(line2)
        jobject[code] = flcode
        with open('config.discord', 'w') as f:
            f.write(line1)
            f.write(json.dumps(jobject))
        print('[DONE] File upload complete')
    client.logout()

def GetHumanReadable(size, precision=2):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1  # increment the index of the suffix
        size = size / 1024.0  # apply the division
    return "%.*f%s" % (precision, size, suffixes[suffixIndex])

# Invokes file downloading, to be used on a thread that's not in main thread
def telldownload(client, inp):
    while not client.isready():
        time.sleep(0.5)
    client.download(inp)
    client.logout()

# Invokes file deleting, to be used on a thread that's not in main thread
def telldelete(client, code):
    while not client.isready():
        time.sleep(0.5)
    client.delete(code)
    client.logout()

# Parses cmd line arguments
def parseArgs(inp):
    commands = ['-h', '-help', '-l', '-list', '-d', '-download', '-u', '-upload', '-delete', '-del']
    if len(inp) == 1:
        print('----------------------\n|DiscordStorage v0.2 |')
        print('|github.com/F4ir     |\n----------------------')
        print('\nUsage: python ds.py [command] (target)\n')
        print('COMMANDS:')
        print('[-h, -help]: Show the current message')
        print('[-l, -list]: Lists all the file informations that has been uploaded to the server')
        print('[-d, -download] (FILE CODE): Downloads a file from the server. A filecode is taken in as the file identifier')
        print('[-u, -upload] (FILE PATH/DRAG FILE): Uploads a file to the server. The full file directory is taken in for the argument')
        print('[-del, -delete] (FILE CODE): Deletes a file from the server and the configuration\n')
    elif isConfigured():
        with open('config.discord', 'r') as f:
            first = f.readline()
            second = f.readline()
        global TOKEN_SECRET, FILES
        TOKEN_SECRET = json.loads(first.replace("\\n", ""))['TOKEN']
        FILES = json.loads(second)

        for el in inp:
            if '-d' == el or '-download' == el:
                if not (FILES and inp[inp.index(el) + 1] in FILES.keys()):
                    print('\n[ERROR] File code not found\n')
                else:
                    obj = json.loads(second)[inp[inp.index(el) + 1]]
                    print('DOWNLOADING: ' + obj[0])
                    print('SIZE: ' + GetHumanReadable(obj[1]))
                    client = core.Core(os.getcwd() + "/", TOKEN_SECRET, ROOM_ID)
                    threading.Thread(target=telldownload, args=(client, obj,)).start()
                    client.start()
                    break
            elif '-u' == el or '-upload' == el:
                print('UPLOADING: ' + inp[inp.index(el) + 1])
                client = core.Core(os.getcwd() + "/", TOKEN_SECRET, ROOM_ID)
                threading.Thread(target=tellupload, args=(first, second, inp[inp.index(el) + 1], genCode(), client,)).start()
                client.start()
                break
            elif '-list' == el or '-l' == el:
                if FILES:
                    print('\nFILES UPLOADED TO DISCORD:\n')
                    for key in FILES.keys():
                        if FILES[key] is None:
                            # correct nullified attribute
                            print(' [CONSOLE] Removed incorrect file with filecode ' + str(key))
                            with open('config.discord', 'w') as f:
                                f.write(first)
                                jobject = json.loads(second)
                                del jobject[key]
                                f.write(json.dumps(jobject))
                        else:
                            print('name: ' + str(FILES[key][0]) + ' | code: ' + str(key) + ' | size: ' + GetHumanReadable(FILES[key][1]))
                    print('\n')
                break
            elif '-delete' == el or '-del' == el:
                if not (FILES and inp[inp.index(el) + 1] in FILES.keys()):
                    print('\n[ERROR] File code not found\n')
                else:
                    code = inp[inp.index(el) + 1]
                    print('DELETING: ' + FILES[code][0])
                    client = core.Core(os.getcwd() + "/", TOKEN_SECRET, ROOM_ID)
                    threading.Thread(target=telldelete, args=(client, code,)).start()
                    with open('config.discord', 'w') as f:
                        f.write(first)
                        jobject = json.loads(second)
                        del jobject[code]
                        f.write(json.dumps(jobject))
                    client.start()
                    break
            elif '-help' == el or '-h' == el:
                print('-----------------\n|DiscordStorage |')
                print('|github.com/F4ir|\n-----------------')
                print('\nUsage: python ds.py [command] (target)\n')
                print('COMMANDS:')
                print('[-h, -help]: Show the current message')
                print('[-l, -list]: Lists all the file informations that has been uploaded to the server')
                print('[-d, -download] (FILE CODE): Downloads a file from the server. A filecode is taken in as the file identifier')
                print('[-u, -upload] (FILE PATH/DRAG FILE): Uploads a file to the server. The full file directory is taken in for the argument')
                print('[-del, -delete] (FILE CODE): Deletes a file from the server and the configuration\n')

if not isConfigured():
    print('Welcome to DiscordStorage.')
    print('Go to http://github.com/F4ir/DiscordStorage for instructions.')
    TOKEN_SECRET = input('Bot token ID (Will be stored in plaintext in config file):')
    ROOM_ID = input('Enter channel ID to store files in:')
    if len(ROOM_ID) <= 0:
        ROOM_ID = None
    with open('config.discord', 'w') as f:
        f.write(str(json.dumps({'TOKEN': TOKEN_SECRET, 'ROOM_ID': ROOM_ID})) + "\n")
        f.write(str(json.dumps({})))
else:
    with open('config.discord', 'r') as f:
        first = f.readline()
        second = f.readline()
    BOT_INFO = json.loads(first)
    FILES = json.loads(second)
    TOKEN_SECRET = json.loads(first.replace("\\n", ""))['TOKEN']
    ROOM_ID = json.loads(first.replace("\\n", ""))['ROOM_ID']

try:
    parseArgs(sys.argv)
except IndexError:
    print('\nUsage: python ds.py [command] (target)\n')
    print('COMMANDS:')
    print('[-h, -help]: Show the help message')
    print('[-l, -list]: Lists all the file informations that has been uploaded to the server')
    print('[-d, -download] (FILE CODE): Downloads a file from the server. A filecode is taken in as the file identifier')
    print('[-u, -upload] (FILE PATH/DRAG FILE): Uploads a file to the server. The full file directory is taken in for the argument')
    print('[-del, -delete] (FILE CODE): Deletes a file from the server and the configuration\n')