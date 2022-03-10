class Config(object):
    LOGGER = True

    # REQUIRED
    TOKEN = ""  # Take from @BotFather
    OWNER_ID = (
        ""  # If you dont know, run the bot and do /id in your private chat with it
    )
    OWNER_USERNAME = ""
    API_HASH = None  # for purge stuffs
    API_ID = None

    # DB'S
    SQLALCHEMY_DATABASE_URI = "sqldbtype://username:pw@hostname:port/db_name"  # needed for any database modules
    REDIS_URL = "redis://something@nothing/anything:10002"  # needed for afk module, get from redislabs
    MONGO_URL = "your mongo db url"

    # RECOMMENDED
    MESSAGE_DUMP = None  # needed to make sure 'save from' messages persist
    LOAD = []
    NO_LOAD = []
    WEBHOOK = False
    URL = None

    # OPTIONAL
    DEV_USERS = (
        []
    )  # List of id's (not usernames) for users which have sudo access to the bot.
    DRAGONS = (
        []
    )  # List of id's (not usernames) for users which WONT be banned/kicked by the bot.

    DEMONS = (
        []
    )  # List of id's (not usernames) for users which are allowed to gban, but can also be banned.

    WOLVES = (
        []
    )  # List of id's (not usernames) for users which WONT be banned/kicked by the bot.

    WOLVES = (
        []
    )  # List of id's (not usernames) for users which WONT be banned/kicked by the bot.

    # HEROKU STUFFS
    HEROKU_API_KEY = "your Heroku api key"
    HEROKU_APP_NAME = "your Heroku app name"

    WHITELIST_CHATS = []
    BLACKLIST_CHATS = []
    DONATION_LINK = None  # EG, paypal
    CERT_PATH = None
    PORT = 5000
    DEL_CMDS = False  # Whether or not you should delete "blue text must click" commands
    STRICT_GBAN = True
    WORKERS = 8  # Number of subthreads to use. This is the recommended amount - see for yourself what works best!
    BAN_STICKER = None  # banhammer marie sticker
    ALLOW_EXCL = False  # DEPRECATED, USE BELOW INSTEAD! Allow ! commands as well as /
    ALLOW_CHATS = None  # Lockdown mode
    CUSTOM_CMD = False  # Set to ('/', '!') or whatever to enable it, like ALLOW_EXCL but with more custom handler!
    API_OPENWEATHER = None  # OpenWeather API
    SPAMWATCH_API = None  # Your SpamWatch token
    WALL_API = None


class Production(Config):
    LOGGER = False


class Development(Config):
    LOGGER = True
