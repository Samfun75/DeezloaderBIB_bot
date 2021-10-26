#!/usr/bin/python3

from helpers.MongoDb_help import DeezS
from utils.utils import my_round, get_url_path
from configs.customs import not_found_query_gif
from configs.set_configs import tg_user_api
from configs.bot_settings import bunker_channel

from telegram import (InlineQueryResultArticle, InputTextMessageContent,
                      InlineQueryResultAudio, InlineQueryResultCachedAudio,
                      InlineQueryResultGif)


def create_result_article_artist(datas):
    results = [
        InlineQueryResultArticle(
            id=data['id'],
            title=data['name'],
            input_message_content=InputTextMessageContent(data['link']),
            description=(f"Album number: {data['nb_album']}" +
                         f"\nFan number: {data['nb_fan']}"),
            thumb_url=data['picture_big']) for data in datas
    ]

    return results


def create_result_article_track(datas):
    results = [
        InlineQueryResultArticle(
            id=data['id'],
            title=data['title'],
            input_message_content=InputTextMessageContent(data['link']),
            description=(f"Artist: {data['artist']['name']}" +
                         f"\nAlbum: {data['album']['title']}" +
                         f"\nDuration: {my_round(data['duration'] / 60)}" +
                         f"\nRank: {data['rank']}"),
            thumb_url=data['album']['cover_big']) for data in datas
    ]

    return results


def create_result_article_track_audio(datas, quality):
    results = []
    messages = []
    audio_file_id = None
    links = [get_url_path(data['link']) for data in datas]
    matchs = DeezS.select_multiple_dwsongs(links, quality)

    if matchs:
        messages = tg_user_api.get_messages(
            bunker_channel,
            [tracks['msg_id'] for tracks in matchs if tracks['msg_id'] != 0])
    print(len(messages))
    for data in datas:
        ids = data['id']
        link = get_url_path(data['link'])
        match = next((track for track in matchs if link == track['link']),
                     None)

        if match:
            print(data['title'])
            audio_file_id = next(
                (msg.audio.file_id
                 for msg in messages if match['msg_id'] == msg.message_id),
                None)

            article = InlineQueryResultCachedAudio(
                id=ids,
                audio_file_id=audio_file_id,
            )
        else:
            if data['preview']:
                article = InlineQueryResultAudio(
                    id=ids,
                    audio_url=data['preview'],
                    title=data['title'],
                    performer=data['artist']['name'],
                    audio_duration=data['duration'],
                    input_message_content=InputTextMessageContent(
                        data['link']))
            else:
                article = InlineQueryResultArticle(
                    id=data['id'],
                    title=data['title'],
                    input_message_content=InputTextMessageContent(
                        data['link']),
                    description=(
                        f"Artist: {data['artist']['name']}" +
                        f"\nAlbum: {data['album']['title']}" +
                        f"\nDuration: {my_round(data['duration'] / 60)}" +
                        f"\nRank: {data['rank']}"),
                    thumb_url=data['album']['cover_big'])

        results.append(article)

    return results


def create_result_article_track_and_audio(datas, quality):
    results = []
    messages = []
    audio_file_id = None
    links = [get_url_path(data['link']) for data in datas]
    matchs = DeezS.select_multiple_dwsongs(links, quality)

    if matchs:
        messages = tg_user_api.get_messages(
            bunker_channel,
            [tracks['msg_id'] for tracks in matchs if tracks['msg_id'] != 0])

    for data in datas:
        ids = data['id']
        link = get_url_path(data['link'])
        match = next((track for track in matchs if link == track['link']),
                     None)

        if match:
            audio_file_id = next(
                (msg.audio.file_id
                 for msg in messages if match['msg_id'] == msg.message_id),
                None)

            article = InlineQueryResultCachedAudio(
                id=ids,
                audio_file_id=audio_file_id,
            )
        else:
            article = InlineQueryResultArticle(
                id=data['id'],
                title=data['title'],
                input_message_content=InputTextMessageContent(data['link']),
                description=(f"Artist: {data['artist']['name']}" +
                             f"\nAlbum: {data['album']['title']}" +
                             f"\nDuration: {my_round(data['duration'] / 60)}" +
                             f"\nRank: {data['rank']}"),
                thumb_url=data['album']['cover_big'])

        results.append(article)

    return results


def create_result_article_album(datas):
    results = [
        InlineQueryResultArticle(
            id=data['id'],
            title=data['title'],
            input_message_content=InputTextMessageContent(data['link']),
            description=(f"Tracks number: {data['nb_tracks']}" +
                         f"\nArtist: {data['artist']['name']}"),
            thumb_url=data['cover_big']) for data in datas
    ]

    return results


def create_result_article_artist_album(datas):
    results = [
        InlineQueryResultArticle(
            id=data['id'],
            title=data['title'],
            input_message_content=InputTextMessageContent(data['link']),
            description=(f"Release date: {data['release_date']}" +
                         f"\nFans: {data['fans']}"),
            thumb_url=data['cover_big']) for data in datas
    ]

    return results


def create_result_article_playlist(datas):
    results = [
        InlineQueryResultArticle(
            id=data['id'],
            title=data['title'],
            input_message_content=InputTextMessageContent(data['link']),
            description=(f"Tracks number: {data['nb_tracks']}" +
                         f"\nUser: {data['user']['name']}" +
                         f"\nCreation: {data['creation_date']}"),
            thumb_url=data['picture_big']) for data in datas
    ]

    return results


def create_result_article_artist_playlist(datas):
    results = [
        InlineQueryResultArticle(
            id=data['id'],
            title=data['title'],
            input_message_content=InputTextMessageContent(data['link']),
            description=(f"User: {data['user']['name']}" +
                         f"\nCreation: {data['creation_date']}"),
            thumb_url=data['picture_big']) for data in datas
    ]

    return results


def create_result_article_artist_radio(datas):
    results = [
        InlineQueryResultArticle(
            id=data['id'],
            title=data['title'],
            input_message_content=InputTextMessageContent(
                f"https://deezer.com/track/{data['id']}"),
            description=(f"Artist: {data['artist']['name']}" +
                         f"\nAlbum: {data['album']['title']}" +
                         f"\nDuration: {my_round(data['duration'] / 60)}" +
                         f"\nRank: {data['rank']}"),
            thumb_url=data['album']['cover_big']) for data in datas
    ]

    return results


def create_result_article_chart_album(datas):
    results = [
        InlineQueryResultArticle(
            id=data['id'],
            title=data['title'],
            input_message_content=InputTextMessageContent(data['link']),
            description=(f"Position: {data['position']}" +
                         f"\nArtist: {data['artist']['name']}"),
            thumb_url=data['cover_big']) for data in datas
    ]

    return results


def create_result_article_chart_artist(datas):
    results = [
        InlineQueryResultArticle(
            id=data['id'],
            title=data['name'],
            input_message_content=InputTextMessageContent(data['link']),
            description=f"Position: {data['position']}",
            thumb_url=data['picture_big']) for data in datas
    ]

    return results


def create_result_article_chart_track(datas):
    results = [
        InlineQueryResultArticle(
            id=data['id'],
            title=data['title'],
            input_message_content=InputTextMessageContent(data['link']),
            description=(f"Artist: {data['artist']['name']}" +
                         f"\nAlbum: {data['album']['title']}" +
                         f"\nDuration: {my_round(data['duration'] / 60)}" +
                         f"\nRank: {data['rank']}" +
                         f"\nPosition: {data['position']}"),
            thumb_url=data['album']['cover_big']) for data in datas
    ]

    return results


def create_result_not_found():
    results = [
        InlineQueryResultGif(
            id="not_found",
            gif_url=not_found_query_gif,
            thumb_url=not_found_query_gif,
            title="ERROR 404 :)",
            input_message_content=InputTextMessageContent(
                "YOU ARE WONDERFUL =)"),
        )
    ]

    return results
