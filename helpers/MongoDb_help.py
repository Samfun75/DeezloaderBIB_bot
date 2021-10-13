#!/usr/bin/python3

import sys
import certifi
import pymongo
import logging
from urllib.parse import quote_plus
from configs.bot_settings import user_errors, user_session
from configs.set_configs import db_host, db_name, db_password, db_type, db_username, tg_bot_api

tg_bot = tg_bot_api.bot
logg = logging.getLogger(__name__)


class DeezDB:
    def __init__(self):

        if db_username is not None and db_password is not None and db_host is not None:
            connection_string = f"{db_type}://{quote_plus(db_username)}:{quote_plus(db_password)}@{db_host}/?retryWrites=true&w=majority"

            self.__db_client = pymongo.MongoClient(connection_string,
                                                   tlsCAFile=certifi.where())
            self.db = self.__db_client[db_name]
        else:
            logg.info(
                "No Database Credentials or Database host Detected. \n Bot can't work without DB \n Exiting Bot..."
            )
            sys.exit()


class DeezSongs:
    def __init__(self):
        self.Songs_collection = DeezDB().db['Songs']

    def write_dwsongs(self, link, file_id, quality, chat_id):
        try:
            self.Songs_collection.insert_one({
                "link": link,
                "file_id": file_id,
                "chat_id": chat_id,
                "quality": quality
            })
        except Exception as e:
            tg_bot.send_message(
                chat_id=user_errors,
                text=f"**{user_session}**\nDatabase Error: {e}")

    def delete_dwsongs(self, file_id):
        try:
            self.Songs_collection.delete_one({"file_id": file_id})
        except Exception as e:
            tg_bot.send_message(
                chat_id=user_errors,
                text=f"**{user_session}**\nDatabase Error: {e}")

    def select_dwsongs(self, link, quality):
        try:
            return self.Songs_collection.find_one(
                {
                    "link": link,
                    "quality": quality
                }, {
                    "file_id": 1,
                    "_id": 0,
                    "link": 0,
                    "chat_id": 0,
                    "quality": 0
                })
        except Exception as e:
            tg_bot.send_message(
                chat_id=user_errors,
                text=f"**{user_session}**\nDatabase Error: {e}")

    def select_all_downloads(self):
        try:
            return self.Songs_collection.count_documents({})
        except Exception as e:
            tg_bot.send_message(
                chat_id=user_errors,
                text=f"**{user_session}**\nDatabase Error: {e}")


class DeezUsers:
    def __init__(self):
        self.Users_collection = DeezDB().db["Users"]
        self.Banned_collection = DeezDB().db["Banned"]

    def write_users_settings(self, chat_id, quality, zips, tracks, lang,
                             search_method):
        try:
            if self.Users_collection.count({"chat_id": chat_id}) > 0:
                return
            else:
                self.Users_collection.insert_one({
                    "chat_id": chat_id,
                    "quality": quality,
                    "zips": zips,
                    "tracks": tracks,
                    "lang": lang,
                    "search_method": search_method
                })
        except Exception as e:
            tg_bot.send_message(
                chat_id=user_errors,
                text=f"**{user_session}**\nDatabase Error: {e}")

    def write_banned(self, chat_id):
        try:
            self.Banned_collection.insert_one({"chat_id": chat_id})
        except Exception as e:
            tg_bot.send_message(
                chat_id=user_errors,
                text=f"**{user_session}**\nDatabase Error: {e}")

    def delete_banned(self, chat_id):
        try:
            self.Banned_collection.find_one_and_delete({"chat_id": chat_id})
        except Exception as e:
            tg_bot.send_message(
                chat_id=user_errors,
                text=f"**{user_session}**\nDatabase Error: {e}")

    def select_banned(self, chat_id):
        try:
            return self.Banned_collection.find_one({"chat_id": chat_id}, {
                "chat_id": 1,
                "_id": 0
            })
        except Exception as e:
            tg_bot.send_message(
                chat_id=user_errors,
                text=f"**{user_session}**\nDatabase Error: {e}")

    def select_all_banned(self):
        try:
            return self.Banned_collection.find({}, {"chat_id": 1, "_id": 0})
        except Exception as e:
            tg_bot.send_message(
                chat_id=user_errors,
                text=f"**{user_session}**\nDatabase Error: {e}")

    def update_users_settings(self, chat_id, quality, zips, tracks, lang,
                              search_method):
        try:
            self.Users_collection.find_one_and_replace(
                {"chat_id": chat_id}, {
                    "chat_id": chat_id,
                    "quality": quality,
                    "zips": zips,
                    "tracks": tracks,
                    "lang": lang,
                    "search_method": search_method
                })
        except Exception as e:
            tg_bot.send_message(
                chat_id=user_errors,
                text=f"**{user_session}**\nDatabase Error: {e}")

    def select_users_settings(self, chat_id):
        try:
            return self.Users_collection.find_one({"chat_id": chat_id}, {
                "_id": 0,
                "chat_id": 0
            })
        except Exception as e:
            tg_bot.send_message(
                chat_id=user_errors,
                text=f"**{user_session}**\nDatabase Error: {e}")

    def select_all_users(self):
        try:
            return self.Users_collection.find({}, {
                "_id": 0,
                "chat_id": 1,
                "quality": 0,
                "zips": 0,
                "tracks": 0,
                "lang": 0,
                "search_method": 0
            })
        except Exception as e:
            tg_bot.send_message(
                chat_id=user_errors,
                text=f"**{user_session}**\nDatabase Error: {e}")
