import sys, re

def check_for_help(args: list):
    if len(args) > 1 and args[1] == "--help":
        m1 = "Welcome to Shadow Slave Scrapper"
        message = [
            m1,
            "-" * len(m1),
            "mode,   Sets your scraping medium. Value is 'telegram' Example: python entry.py telegram\n",
            "--age,   Sets the age of the chapters you want to retrieve. Values are 'earliest' or 'latest. Optional, will start from the earliest chapters if not set. Example: python entry.py telegram --age=earliest\n",
            "--number,   Sets the number of chapters to be retrieved. Optional, will retrieve all available chapters you do not possess if not set. Example: 'python entry.py telegram --number=10 --age=latest' to retrieve the 10 latest available chapters\n",
            "--messages,   Sets the number of messages you want to scrape through for chapters.\n",
            "-" * len(m1),
            "Miscallenous",
            "-" * len(m1),
            "Get your telegram api key and hash from 'my.telegram.org'\n"
        ]
        
        for mess in message:
            print(mess)
        exit(0)


def get_options(args: list):
    age = None
    number = None
    messages = None

    for arg in args:
        age_match = re.search(r"--age=", arg)
        if age_match is not None:
            o, avalue = arg.split("=")
            if avalue in ['latest', 'earliest']:
                age = avalue
                continue
        
        number_match = re.search(r"--number=", arg)
        if number_match is not None:
            o, nvalue = arg.split("=")
            try:
                nvalue = int(nvalue)
                number = nvalue
            except:
                pass

        message_match = re.search(r"--messages=", arg)
        if number_match is not None:
            o, mvalue = arg.split("=")
            try:
                mvalue = int(mvalue)
                messages = nvalue
            except:
                pass
    
    return {'age': age, 'number': number, 'messages': messages}


if __name__ == "__main__":
    args = sys.argv

    # print(args)
    check_for_help(args)
    options = get_options(args)

    if 'telegram' in args and 'telegram' == args[1]:
        from telegram.scrapper import telegram_entry

        telegram_entry(options)