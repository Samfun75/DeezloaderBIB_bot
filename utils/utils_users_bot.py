#!/usr/bin/python3

from configs.bot_settings import root_ids, warning_for_banning

from configs.customs import (bot_settings_config, banning_msg1, banning_msg2,
                             version, bot_name, creator, active_since,
                             last_reset)

from helpers.MongoDb_help import DeezSongs, DeezUsers


def users_set_cache(chat_id, users_data):
    if not chat_id in users_data:
        match = DeezUsers().select_users_settings(chat_id)

        if not match:
            quality = bot_settings_config[0][2]
            zips = bot_settings_config[1][2]
            tracks = bot_settings_config[2][2]
            lang = bot_settings_config[3][2]
            search_method = bot_settings_config[4][2]

            DeezUsers().write_users_settings(chat_id, quality, zips, tracks,
                                             lang, search_method)
        else:
            quality = match[0]
            zips = bool(match[1])
            tracks = bool(match[2])
            lang = match[3]
            search_method = match[4]

        users_data[chat_id] = {
            "quality": quality,
            "zips": zips,
            "tracks": tracks,
            "lang": lang,
            "search_method": search_method,
            "last_message": None,
            "messages_sent": 0,
            "times": 0,
            "c_downloads": {}
        }


def user_setting_save_db(chat_id, user_data):
    quality = user_data['quality']
    zips = user_data['zips']
    tracks = user_data['tracks']
    lang = user_data['lang']
    search_method = user_data['search_method']

    DeezUsers().update_users_settings(chat_id, quality, zips, tracks, lang,
                                      search_method)


def check_flood(date, user_data, chat_id):
    if chat_id in root_ids:
        return

    last_message = user_data['last_message']

    if not last_message:
        user_data['last_message'] = date
        return

    user_data['last_message'] = date
    time_passed = (date - last_message).seconds

    if time_passed < 4:
        user_data['messages_sent'] += 1
    else:
        user_data['messages_sent'] = 0

    messages_sent = user_data['messages_sent']

    if messages_sent == 3:
        user_data['messages_sent'] = 0
        user_data['times'] += 1
        return banning_msg1, 0

    times = user_data['times']

    if times == warning_for_banning:
        DeezUsers().write_banned(chat_id)
        return banning_msg2, 1


def kill_threads(users_data):
    for c_user_data in users_data.values():
        for c_thread in c_user_data['c_downloads'].values():
            c_thread['thread'].kill()

        c_user_data['c_downloads'].clear()


def is_banned(chat_id):
    match = DeezUsers().select_banned(chat_id)

    if match:
        return True

    return False


def get_banned_ids():
    match = DeezUsers().select_all_banned()

    chat_ids = [chat_doc['chat_id'] for chat_doc in match]

    chat_ids = set(chat_ids)
    return chat_ids


def get_tot_downloads():
    match = DeezSongs().select_all_downloads()
    tot = len(match)
    return tot


def get_tot_users():
    match = DeezUsers().select_all_users()
    tot = len(match)
    return tot


def get_info():
    tot_users = get_tot_users()
    tot_downloads = get_tot_downloads()

    info_msg = (f"🔺 Version: {version}\
		\n📅 Active since: {active_since}\
		\n🔻 Name: {bot_name}\
		\n✒️ Creator: {creator}\
		\n📅 Last reset: {last_reset}\
		\n👥 Users: {tot_users}\
		\n⬇️ Total downloads: {tot_downloads}")

    return info_msg
