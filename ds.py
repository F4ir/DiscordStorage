from discordstorage import core
from discordstorage.upload import upload_to_gofile
import threading
import json
import sys
import os
import time
import random
from tqdm import tqdm

# DONT TOUCH ANYTHING
TOKEN_SECRET = ""  
ROOM_ID = ""  
BOT_INFO = None
FILES = None

# Generates a file code from 0-4097
def gen_code():
    code = str(random.randint(0, 4098))
    if FILES is None:
        return code
    while code in FILES.keys():
        code = str(random.randint(0, 4098))
    return code

# Returns if the botconfig file is configured or not.
def is_bot_configured():
    return os.path.isfile('botconfig.discord')

# Returns if the fileconfig file is configured or not.
def is_file_configured():
    return os.path.isfile('fileconfig.discord')

# Invokes file uploading, to be used on a thread that's not in main thread.
# Writes to fileconfig file accordingly.
def tell_upload(bot_config, file_config, cmd, code, client):
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
        jobject = json.loads(file_config)
        jobject[code] = flcode
        with open('fileconfig.discord', 'w') as f:
            f.write(json.dumps(jobject))
        print('[DONE] File upload complete')
    client.logout()

# Invokes file downloading, to be used on a thread that's not in main thread
def tell_download(client, inp):
    while not client.isready():
        time.sleep(0.5)
    client.download(inp)
    client.logout()

# Invokes file deleting, to be used on a thread that's not in main thread
def tell_delete(client, code):
    while not client.isready():
        time.sleep(0.5)
    client.delete(code)
    client.logout()

# Uploads file to gofile.io and returns the download link
def share_file(file_path):
    upload_to_gofile(file_path)

# Parses cmd line arguments
def parse_args(inp):
    commands = ['-h', '-help', '-l', '-list', '-d', '-download', '-u', '-upload', '-delete', '-del', '-s', '-share']
    if len(inp) == 1:
        print('----------------------\n|DiscordStorage v0.5 |')
        print('|github.com/F4ir     |\n----------------------')
        print('\nUsage: python ds.py [command] (target)\n')
        print('COMMANDS:')
        print('[-h, -help]: Show the current message')
        print('[-l, -list]: Lists all the file information that has been uploaded to the server')
        print('[-d, -download] (FILE CODE): Downloads a file from the server. A file code is taken in as the file identifier')
        print('[-u, -upload] (FILE PATH/DRAG FILE): Uploads a file to the server. The full file directory is taken in for the argument')
        print('[-del, -delete] (FILE CODE): Deletes a file from the server and the configuration')
        print('[-s, -share] (DRAG FILE): Shares a file by uploading it to gofile.io and providing a download link\n')
    elif is_bot_configured() and is_file_configured():
        with open('botconfig.discord', 'r') as f:
            bot_config = json.loads(f.read())
        with open('fileconfig.discord', 'r') as f:
            file_config = f.read()

        global TOKEN_SECRET, ROOM_ID, FILES
        TOKEN_SECRET = bot_config['TOKEN']
        ROOM_ID = bot_config['ROOM_ID']
        FILES = json.loads(file_config)

        for el in inp:
            if '-d' == el or '-download' == el:
                if not (FILES and inp[inp.index(el) + 1] in FILES.keys()):
                    print('\n[ERROR] File code not found\n')
                else:
                    obj = FILES[inp[inp.index(el) + 1]]
                    print('DOWNLOADING: ' + obj[0])
                    print('SIZE: ' + get_human_readable(obj[1]))
                    client = core.Core(os.getcwd() + "/", TOKEN_SECRET, ROOM_ID)
                    threading.Thread(target=tell_download, args=(client, obj,)).start()
                    client.start()
                    break
            elif '-u' == el or '-upload' == el:
                file_path = inp[inp.index(el) + 1]
                if not os.path.isfile(file_path):
                    print(f'\n[ERROR] File "{file_path}" does not exist.\n')
                    break
                print('UPLOADING: ' + file_path)
                client = core.Core(os.getcwd() + "/", TOKEN_SECRET, ROOM_ID)
                threading.Thread(target=tell_upload, args=(bot_config, file_config, file_path, gen_code(), client,)).start()
                client.start()
                break
            elif '-list' == el or '-l' == el:
                if FILES:
                    print('\nFILES UPLOADED TO DISCORD:\n')
                    for key in FILES.keys():
                        if FILES[key] is None:
                            # correct nullified attribute
                            print(' [CONSOLE] Removed incorrect file with file code ' + str(key))
                            with open('fileconfig.discord', 'w') as f:
                                del FILES[key]
                                f.write(json.dumps(FILES))
                        else:
                            print('name: ' + str(FILES[key][0]) + ' | code: ' + str(key) + ' | size: ' + get_human_readable(FILES[key][1]))
                    print('\n')
                break
            elif '-delete' == el or '-del' == el:
                if not (FILES and inp[inp.index(el) + 1] in FILES.keys()):
                    print('\n[ERROR] File code not found\n')
                else:
                    code = inp[inp.index(el) + 1]
                    print('DELETING: ' + FILES[code][0])
                    client = core.Core(os.getcwd() + "/", TOKEN_SECRET, ROOM_ID)
                    threading.Thread(target=tell_delete, args=(client, code,)).start()
                    with open('fileconfig.discord', 'w') as f:
                        del FILES[code]
                        f.write(json.dumps(FILES))
                    client.start()
                    break
            elif '-help' == el or '-h' == el:
                print('-----------------\n|DiscordStorage |')
                print('|github.com/F4ir|\n-----------------')
                print('\nUsage: python ds.py [command] (target)\n')
                print('COMMANDS:')
                print('[-h, -help]: Show the help message')
                print('[-l, -list]: Lists all the file information that has been uploaded to the server')
                print('[-d, -download] (FILE CODE): Downloads a file from the server. A file code is taken in as the file identifier')
                print('[-u, -upload] (FILE PATH/DRAG FILE): Uploads a file to the server. The full file directory is taken in for the argument')
                print('[-del, -delete] (FILE CODE): Deletes a file from the server and the configuration')
                print('[-s, -share] (DRAG FILE): Shares a file by uploading it to gofile.io and providing a download link\n')
            elif '-s' == el or '-share' == el:
                file_path = inp[inp.index(el) + 1]
                if not os.path.isfile(file_path):
                    print(f'\n[ERROR] File "{file_path}" does not exist.\n')
                    break
                share_file(file_path)
                break

def get_human_readable(size, precision=2):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    suffix_index = 0
    while size > 1024 and suffix_index < 4:
        suffix_index += 1  # increment the index of the suffix
        size = size / 1024.0  # apply the division
    return "%.*f%s" % (precision, size, suffixes[suffix_index])

if not is_bot_configured():
    print('Welcome to DiscordStorage.')
    print('Go to http://github.com/F4ir/DiscordStorage for instructions.')
    TOKEN_SECRET = input('Bot token ID (Will be stored in plaintext in config file):')
    ROOM_ID = input('Enter channel ID to store files in:')
    if len(ROOM_ID) <= 0:
        ROOM_ID = None
    with open('botconfig.discord', 'w') as f:
        f.write(json.dumps({'TOKEN': TOKEN_SECRET, 'ROOM_ID': ROOM_ID}))
else:
    with open('botconfig.discord', 'r') as f:
        BOT_INFO = json.loads(f.read())
    TOKEN_SECRET = BOT_INFO['TOKEN']
    ROOM_ID = BOT_INFO['ROOM_ID']

if not is_file_configured():
    with open('fileconfig.discord', 'w') as f:
        f.write(json.dumps({}))
else:
    with open('fileconfig.discord', 'r') as f:
        FILES = json.loads(f.read())

try:
    parse_args(sys.argv)
except IndexError:
    print('\n[ERROR] Invalid arguments. Use -h or -help for usage information.\n')
