#!/usr/bin/python3

from datetime import datetime

version = 2.0
bot_name = "@SamfunMusicBot"
creator = "@Samfun75"
donation = "https://www.paypal.com/paypalme/samfun75"

active_since = "24/07/2021"
date_start = datetime.now()
last_reset = datetime.strftime(date_start, "%d/%m/%Y %H:%M:%S")

not_found_query_gif = "https://i1.wp.com/blog-pantheon-prod.global.ssl.fastly.net/blog/wp-content/uploads/2017/03/coding-programming-errors-404-page-not-found.gif?resize=625%2C469&ssl=1"
banning_msg1 = "WE ARE DETECTING A FLOOD OF MESSAGES PLEASE DON'T SEND TOO MUCH MESSAGES"
banning_msg2 = "CONGRATULATIONS YOU ARE BANNED =)"
album_too_long = "DON'T YOU GET BORE LISTENING AN ALBUM SO LONG :)))"
track_too_long = "IS THIS TRACK FOR A SATAN CELEBRATION? :)))"
shazam_function_msg = "You found a fantastic function, if you send a vocal message or an audio, you will see :)"
max_download_user_msg = "You have reached, max download per time avalaible, wait or kill someone :)"
help_msg = f"WELCOME IN {bot_name} here you can find the commands avalaible, JUST TRY IT :)"
help_photo = open("photos/help_msg.jpg", "rb")
feedback_text = f"If you have any question, just ask to this dude {creator}"
donate_text = f"If you are poor like me, I understand you, IF NOT, I will appreciate a little donation 🥺"

reasons_text = ("WHY I MADE THIS BOT?\
	\n1): This was a nice challenge for me as a little dev\
	\n2): No all of us have the possibility to pay for music content, so I did this to give to everybody for free the chance to download songs\
	\n3): I am thinking about put this code opensource, but last time I did, some people just copied it and used for their own purpose, so IDK :)))\
	\n4): THIS BOT PROBABLY WILL LASTS FOR A FEW TIME, so USE IT UNTIL YOU CAN =)"
                )

what_can_I_do = ("Glad you asked, I can do:\
	\n1): Download songs in three different qualities (/quality)\
	\n2): Shazam engine like to download songs around you\
	\n3): Zip sending\
	\n4): I hope enough performing JAJAJAJAJAJ\
	\n5): I am too lazy to continue, found out by yourself :)")

bot_settings_config = [("Quality", "quality", "MP3_320"),
                       ("Send zips", "zips", True),
                       ("Send tracks", "tracks", True),
                       ("Language", "lang", "en"),
                       ("Search Method", "search_method",
                        "results_audio_article")]

search_methods = [("results_audio", "Results in Audio"),
                  ("results_article", "Results in Articles"),
                  ("results_audio_article", "Results Smooth ;)")]

send_image_track_query = ("🎧 Track title: %s\
	\n👤 Artist: %s\
	\n💽 Album: %s\
	\n📅 Release date: %s")

send_image_album_query = ("💽 Album: %s\
	\n👤 Artist: %s\
	\n📅 Date: %s\
	\n🎧 Tracks amount: %d")

send_image_artist_query = ("👤 Artist: %s\
	\n💽 Album numbers: %d\
	\n👥 Fans on Deezer: %d")

send_image_playlist_query = ("📅 Creation: %s\
	\n👤 User: %s\
	\n🎧 Tracks amount: %d\
	\n👥 Fans on Deezer: %d")

shazam_audio_query = ("🎧 Track title: %s\
    \n👤 Artist: %s\
	\n💽 Album: %s\
	\n🔖 Label: %s\
	\n📅 Release date: %s\
    \n🎇 Genre: %s")

inline_textes = {
    "download_track": {
        "text": "⬇️ Download track 🎧"
    },
    "download_album": {
        "text": "⬇️ Download album 💽"
    },
    "download_artist": {
        "text": "⬇️ Get artist 👤"
    },
    "back": {
        "text": "BACK 🔙"
    }
}

commands_queries = {
    "s_art": {
        "query": "art: %s",
        "text": "Search by artist 👤"
    },
    "s_alb": {
        "query": "alb: %s",
        "text": "Search by album 💽"
    },
    "s_pla": {
        "query": "pla: %s",
        "text": "Search playlist 📂"
    },
    "s_trk": {
        "query": "trk: %s",
        "text": "Search track 🎧"
    },
    "s_global": {
        "query": "%s",
        "text": "Global search 📊"
    }
}

artist_commands_queries = {
    "top": {
        "query": "%s:top",
        "text": "TOP 30 🔝"
    },
    "albums": {
        "query": "%s:albums",
        "text": "ALBUMS 💽"
    },
    "related": {
        "query": "%s:related",
        "text": "RELATED 🗣"
    },
    "radio": {
        "query": "%s:radio",
        "text": "RADIO 📻"
    },
    "playlists": {
        "query": "%s:playlists",
        "text": "PLAYLISTS 📂"
    }
}