#!/usr/bin/python3

import os
from pyrogram import Client
from deezloader import Login
from acrcloud import ACRcloud
from telegram.ext import Updater
from configparser import ConfigParser
from utils.utils import check_config_file
from .bot_settings import settings_file

if bool(os.environ.get("ENV", None)):
    __arl_token = os.environ.get("deez_token", None)
    __email = os.environ.get("deez_mail", None)
    __password = os.environ.get("deez_password", None)
    __bot_token = os.environ.get("bot_token", None)
    __acrcloud_key = os.environ.get("acrcloud_key", None)
    __acrcloud_secret = os.environ.get("acrcloud_secret", None)
    __acrcloud_host = os.environ.get("acrcloud_host", None)
    api_id = int(os.environ.get("api_id", None))
    api_hash = os.environ.get("api_hash", None)
    session_string = os.environ.get("session_string", None)

    __acrcloud_config = {
        "key": __acrcloud_key,
        "secret": __acrcloud_secret,
        "host": __acrcloud_host
    }

    db_username = os.environ.get("db_username", None)
    db_password = os.environ.get("db_password", None)
    db_host = os.environ.get("db_host", None)
    db_name = os.environ.get("db_name", None)
    if os.environ.get("db_type", None).lower().split('_')[1] == 'community':
        db_type = 'mongodb'
    elif os.environ.get("db_type", None).lower().split('_')[1] == 'atlas':
        db_type = 'mongodb+srv'
else:
    config = ConfigParser(interpolation=None)
    config.read(settings_file)
    check_config_file(config)

    __arl_token = config['deez_login']['token'] or None
    __email = config['deez_login']['mail']
    __password = config['deez_login']['password']
    __bot_token = config['telegram']['bot_token']
    __acrcloud_key = config['acrcloud']['key']
    __acrcloud_secret = config['acrcloud']['secret']
    __acrcloud_host = config['acrcloud']['host']
    api_id = int(config['pyrogram']['api_id'])
    api_hash = config['pyrogram']['api_hash']
    session_string = config['pyrogram']['session_string']

    __acrcloud_config = {
        "key": __acrcloud_key,
        "secret": __acrcloud_secret,
        "host": __acrcloud_host
    }

    db_username = config['database']['db_username']
    db_password = config['database']['db_password']
    db_host = config['database']['db_host']
    db_name = config['database']['db_name']
    if config.get("database", "db_type").lower().split('_')[1] == 'community':
        db_type = 'mongodb'
    elif config.get("database", "db_type").lower().split('_')[1] == 'atlas':
        db_type = 'mongodb+srv'

tg_bot_api = Updater(token=__bot_token)
tg_bot_id = tg_bot_api.bot.name

deez_api = Login(email=__email, password=__password)

tg_user_api = Client(session_string, api_id=api_id, api_hash=api_hash)
acrcloud_api = ACRcloud(__acrcloud_config)
