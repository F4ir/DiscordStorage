import os
import io
import aiohttp
import asyncio
import discord
from tqdm import tqdm  # Import tqdm for progress bars
from .Session import Session

class Core:
    def __init__(self, directory, token, channel):
        self.directory = directory  # set root directory for downloaded/files to be uploaded
        self.session = Session(token, channel)  # discord API
        self.client = self.session.getClient()  # discord API client object

    # check if the client is connected to discord servers
    def isready(self):
        return not (self.session.getLoop() is None)

    # starts connection to discord servers.
    # RUNS ON MAIN THREAD, ASYNC.
    def start(self):
        self.session.start()

    # Halts all connection to discord servers.
    def logout(self):
        future = asyncio.run_coroutine_threadsafe(self.session.logout(), self.session.getLoop())

    # runs the async_upload in a threadsafe way,
    # can be run from anything outside of main thread.
    def upload(self, inp, code):
        future = asyncio.run_coroutine_threadsafe(self.async_upload(inp, code), self.session.getLoop())
        try:
            return future.result()
        except Exception as exc:
            print(exc)
            return -1

    # runs the async_download in a threadsafe way,
    # can be run from anything outside of main thread.
    def download(self, inp):
        future = asyncio.run_coroutine_threadsafe(self.async_download(inp), self.session.getLoop())
        try:
            return future.result()
        except Exception as exc:
            print('[ERROR]', exc)
            return -1

    # runs the async_delete in a threadsafe way,
    # can be run from anything outside of main thread.
    def delete(self, code):
        future = asyncio.run_coroutine_threadsafe(self.async_delete(code), self.session.getLoop())
        try:
            return future.result()
        except Exception as exc:
            print('[ERROR]', exc)
            return -1

    # Downloads a file from the server.
    # The list object in this format is needed: [filename, size, [DL URLs]]
    # RUNS ON MAIN THREAD, ASYNC.
    async def async_download(self, inp):
        os.makedirs(os.path.dirname(self.directory + "downloads/" + inp[0]), exist_ok=True)
        with open(self.directory + "downloads/" + inp[0], 'wb') as f:
            for i in tqdm(range(len(inp[2])), desc=f'Downloading {inp[0]}', unit='file'):
                agent = {'User-Agent': 'DiscordStorageBot (http://github.com/F4ir/discordstorage)'}
                async with aiohttp.ClientSession() as session:
                    async with session.get(inp[2][i], headers=agent) as r:
                        if r.status == 200:
                            async for data in r.content.iter_any():
                                f.write(data)

    # Uploads a file to the server from the root directory, or any other directory specified
    # inp = directory, code = application-generated file code
    # RUNS ON MAIN THREAD, ASYNC.
    async def async_upload(self, inp, code):
        urls = []
        with open(inp, 'rb') as f:
            file_size = os.path.getsize(inp)
            num_chunks = self.split_file(inp)
            for i in tqdm(range(num_chunks), desc=f'Uploading {os.path.basename(inp)}', unit='chunk'):
                o = io.BytesIO(f.read(24000000))
                discord_file = discord.File(fp=o, filename=f'{code}.{i}')
                await self.session.getChannel().send(file=discord_file)
                async for message in self.session.getChannel().history(limit=None):
                    if message.author == self.client.user:
                        urls.append(message.attachments[0].url)
                        break
        return [os.path.basename(inp), file_size, urls]

    # Deletes a file from the server.
    # code = application-generated file code
    # RUNS ON MAIN THREAD, ASYNC.
    async def async_delete(self, code):
        channel = self.session.getChannel()
        async for message in channel.history(limit=None):
            if message.attachments and message.attachments[0].filename.startswith(code):
                await message.delete()
                print(f'[DONE] Deleted {message.attachments[0].filename}')
        print('[DONE] File delete complete')

    # Finds out how many file blocks are needed to upload a file.
    # Regular max upload size at a time: 8MB.
    # Discord NITRO max upload size at a time: 50MB.
    # Change accordingly if needed.
    def split_file(self, file_path):
        return (os.path.getsize(file_path) // 24000000) + 1
