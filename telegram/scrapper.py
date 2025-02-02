import asyncio, re, json

from telethon import TelegramClient
from decouple import config

from settings import root_dir

api_id = config("TELEGRAM_API_ID")
api_hash = config("TELEGRAM_API_HASH")
client = TelegramClient('anon', api_id, api_hash)
chapter_range_pattern_object = re.compile(r"\d{1,4}\s?-\s?\d{1,4}")
individual_chapter_pattern_object = re.compile(r"\d{1,4}")
chapter_file_path = root_dir/"chapters"


async def check_existing_chapter(chapter: str, chapter_type: str = "individual") -> tuple[bool|list[int]]:
    """Check if all provided chapters are already in chapter info file"""

    if chapter_type == "range":
        stringlist = chapter.replace(" ", "").split("-")
        start = int(stringlist[0])
        stop = int(stringlist[1])

    non_exist_list = []
    exist_bool = True
    with open(chapter_file_path/"chapter_info.json", 'r') as jfile:
        try:
            chapter_info = json.load(jfile)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            chapter_info = []
            with open(chapter_file_path/"chapter_info.json", 'w') as jfile2:
                json.dump(chapter_info, jfile2)
        
        if chapter_type == "range":
            for i in range(start, stop+1):
                if i not in chapter_info:
                    non_exist_list.append(i)
                    exist_bool = False
        else:
            if int(chapter) not in chapter_info:
                non_exist_list.append(int(chapter))
                exist_bool = False
    
    return exist_bool, non_exist_list

        

async def update_chapter_info(chapter_list: list[int]):
    """Update chapter info file given list of chapter numbers"""

    with open(chapter_file_path/"chapter_info.json", 'r') as jfile:
        chapter_info = json.load(jfile)
    
    chapter_info.extend(chapter_list)
    chapter_info.sort()
    with open(chapter_file_path/"chapter_info.json", 'w') as jfile2:
        json.dump(chapter_info, jfile2)    
    



async def get_channel():
    """Get the required channel and return it"""

    channel = None
    async for dialog in client.iter_dialogs(3):
        # print(dialog.stringify())
        if dialog.name == "Shadow Slave":
            # print(dialog.input_entity)
            channel = dialog.input_entity
            break
    
    return channel



def callback(current, total):
    print('Downloaded', current, 'out of', total,
          'bytes: {:.2%}'.format(current / total))


async def download_file(message):
    """Download the file associated with the given message"""

    print(f"Downloading {message.file.name}")
    await message.download_media(chapter_file_path, progress_callback=callback)




async def get_messages(channel, age: str|None, number: int|None):
    """Get messages from the provided channel"""

    #parse options
    if age is not None and age == "earliest":
        reverse = True
    else:
        reverse = False

    download_count = 0

    # async for message in client.iter_messages(channel, 1, reverse=True, offset_id=2):
    async for message in client.iter_messages(channel, reverse=reverse):
        # print(message.media.stringify())
        # print(message.document)
        # print(message.file, type(message.file))
        # print(message.file.name, "\n", type(message.file.name))

        #check if there is a file, if it exists, check the chapter it possesses
        if message.file is not None and message.file.name is not None:
            #check if chapter or range of chapters are present
            chapter_range_match = chapter_range_pattern_object.search(message.file.name)
            indi_chapter_match = individual_chapter_pattern_object.search(message.file.name)
            if chapter_range_match is not None or indi_chapter_match is not None:
                if chapter_range_match is not None:
                    matched_string = chapter_range_match.group()
                    chapter_type = "range"
                    # print('\n', "Chapter range found")
                    # print(message.file.name)
                elif indi_chapter_match is not None:
                    matched_string = indi_chapter_match.group()
                    chapter_type = "individual"
                    # print('\n', "Individual Chapter found")
                    # print(message.file.name)
                
                already_exists, chapter_list = await check_existing_chapter(matched_string, chapter_type)
                if not already_exists:
                    result = await asyncio.gather(download_file(message), update_chapter_info(chapter_list))

                    download_count = download_count + 1
                    if number is not None and download_count >= number:
                        break
            else:
                print("No match found", '\n')

    if download_count > 0:
        print(f"{download_count} available unowned chapter{'' if download_count == 1 else 's'} downloaded successfully")
    else:
        print("No new unowned chapters available")




async def main(options):
    channel = await get_channel()
    if channel is not None:
        await get_messages(channel, **options)    


def telegram_entry(options: dict):
    with client:
        client.loop.run_until_complete(main(options))

# def telegram_entry():
#     with open(root_dir/"chapters/chapter_info.json", 'w') as jfile:
#         pass