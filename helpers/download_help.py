#!/usr/bin/python3

from time import sleep
from io import BytesIO
from pyrogram import Client
from telegram import ChatAction
from sqlite3 import IntegrityError
from telegram.error import BadRequest
from logging import error as log_error
from contextlib import redirect_stdout
from deezloader.models.track import Track
from deezloader.models.album import Album
from deezloader.__utils__ import what_kind
from deezloader.exceptions import TrackNotFound, QualityNotFound
from deezloader.__dee_api__ import API as deezer_API
from deezloader.__deezer_settings__ import qualities
from configs.set_configs import deez_api, tg_bot_api, tg_user_api
from inlines.inline_keyboards import create_keyboard_artist
from pyrogram.errors import BadRequest as PyrogramBR

from .MongoDb_help import DeezS

from deezloader.exceptions import (NoDataApi, InvalidLink, AlbumNotFound)

from utils.utils import (get_quality, get_url_path, set_path, get_size)

from configs.customs import (send_image_track_query, send_image_artist_query,
                             send_image_playlist_query, send_image_album_query,
                             album_too_long, track_too_long)

from utils.utils_data import (track_spo_data, track_dee_data, artist_dee_data,
                              playlist_dee_data, playlist_spo_data,
                              album_dee_data, album_spo_data,
                              convert_spoty_to_dee_link_track)

from configs.bot_settings import (bunker_channel, seconds_limits_album,
                                  seconds_limits_track, max_song_per_playlist,
                                  method_save, output_songs, recursive_quality,
                                  recursive_download, make_zip,
                                  upload_max_size_user, user_errors,
                                  log_uploads, user_session)

deezer_api = deezer_API()
tg_bot = tg_bot_api.bot


def write_db(track_md5, chat_id, msg_id, n_quality):
    try:
        DeezS.write_dwsongs(track_md5, chat_id, msg_id, n_quality)
    except IntegrityError:
        pass


class DOWNLOAD_HELP:
    def __init__(self, queues_started: list, queues_finished: list,
                 tg_user_api: Client) -> None:

        self.tg_user_api = tg_user_api
        self.queues_started = queues_started
        self.queues_finished = queues_finished


class DW:
    def __init__(self, helper: DOWNLOAD_HELP, chat_id: int, user_data: dict,
                 hash_link: int) -> None:

        self.__tg_user_api = helper.tg_user_api
        self.__queues_started = helper.queues_started
        self.__queues_finished = helper.queues_finished
        self.__chat_id = chat_id
        self.__quality = user_data['quality']
        self.__n_quality = get_quality(self.__quality)
        self.__send_to_user_tracks = user_data['tracks']
        self.__send_to_user_zips = user_data['zips']
        self.__hash_link = hash_link
        self.__c_download = user_data['c_downloads']

    def __before_dw(self):
        self.__queues_started[0] += 1

    def __after_dw(self):
        self.__queues_finished[0] += 1

    def __finished(self):
        try:
            del self.__c_download[self.__hash_link]
        except KeyError:
            pass

    def __upload_audio(self, file_id, caption=""):
        if self.__send_to_user_tracks:
            tg_bot.send_chat_action(chat_id=self.__chat_id,
                                    action=ChatAction.UPLOAD_AUDIO)

            sleep(0.1)

            with open(log_uploads, "a") as f:
                with redirect_stdout(f):
                    print(f"UPLOADING: {file_id}")

            tg_bot.send_audio(chat_id=self.__chat_id,
                              audio=file_id,
                              caption=caption)

    def __upload_zip(self, file_id):
        if self.__send_to_user_zips:
            tg_bot.send_chat_action(chat_id=self.__chat_id,
                                    action=ChatAction.UPLOAD_DOCUMENT)

            sleep(0.1)

            with open(log_uploads, "a") as f:
                with redirect_stdout(f):
                    print(f"UPLOADING: {file_id}")

            tg_bot.send_document(chat_id=self.__chat_id, document=file_id)

    def __upload_audio_track(self, track: Track):
        c_path = track.song_path
        track_md5 = track.track_md5
        md5_image = track.md5_image
        image_bytes1 = deezer_api.choose_img(md5_image, "90x90")
        io_image = BytesIO(image_bytes1)
        io_image.name = md5_image
        duration = track.duration
        performer = track.artist
        title = track.music
        f_format = track.file_format
        tag = track.tags
        track_quality = track.quality
        caption = ""

        file_name = set_path(tag, self.__n_quality, f_format, 1)
        track_size = get_size(c_path, "gb")

        if track_size > upload_max_size_user:
            tg_bot.send_message(
                chat_id=self.__chat_id,
                text=f"THE SONG {track.song_name} IS TOO BIG TO BE UPLOADED\
					, MAX {upload_max_size_user} GB\
					, CURRENT {track_size} GB :(")

            return

        if track_quality != self.__n_quality:
            caption = f"⚠ {self.__quality} Unavailable. Downloaded {track_quality}"

        file = self.__tg_user_api.send_audio(chat_id=bunker_channel,
                                             audio=c_path,
                                             thumb=io_image,
                                             duration=duration,
                                             performer=performer,
                                             title=title,
                                             file_name=file_name,
                                             caption=caption)

        write_db(track_md5, file.chat.id, file.message_id, track_quality)

        self.__upload_audio(file.audio.file_id, caption=caption)

    def __download_track(self, url, quality=None):
        if not quality:
            quality = self.__quality
        try:
            track = deez_api.download_trackdee(
                url,
                output_dir=output_songs,
                quality_download=quality,
                recursive_quality=recursive_quality,
                recursive_download=recursive_download,
                method_save=method_save)
        except TrackNotFound as error:
            log_error(error, exc_info=True)

            tg_bot.send_message(chat_id=self.__chat_id,
                                text=f"Cannot download {url} :(")
            return

        progress_message_id = tg_bot.send_message(
            chat_id=self.__chat_id,
            text=f"Starting uploading {track.song_name} ...").message_id

        self.__upload_audio_track(track)

        tg_bot.delete_message(chat_id=self.__chat_id,
                              message_id=progress_message_id)

    def __progress_status(self, current, total, times, album_name):
        c_time = times[0]

        if current == total:
            msg_id = times[1]

            tg_bot.delete_message(chat_id=self.__chat_id, message_id=msg_id)

        if c_time % 10 == 0:
            c_progress = f"{current * 100 / total:.1f}%"
            c_text = f"Uploading {album_name}: {c_progress}"

            with open(log_uploads, "a") as f:
                with redirect_stdout(f):
                    print(c_text)

            if c_time == 0:
                msg_id = tg_bot.send_message(chat_id=self.__chat_id,
                                             text=c_text).message_id

                times.append(msg_id)
            else:
                msg_id = times[1]

                try:
                    tg_bot.edit_message_text(chat_id=self.__chat_id,
                                             message_id=msg_id,
                                             text=c_text)
                except BadRequest:
                    pass

        times[0] += 1

    def __upload_zip_album(self, album: Album):
        times = [0]
        album_name = album.album_name
        md5_image = album.md5_image
        image_bytes2 = deezer_api.choose_img(md5_image, "320x320")
        image_io2 = BytesIO(image_bytes2)
        image_io2.name = md5_image
        progress_args = (times, album_name)
        path_zip = album.zip_path
        album_md5 = album.album_md5
        zip_size = get_size(path_zip, "gb")
        album_quality = album.tracks[0].quality

        if zip_size > upload_max_size_user:
            tg_bot.send_message(chat_id=self.__chat_id,
                                text=f"THE ZIP IS TOO BIG TO BE UPLOADED\
					, MAX {upload_max_size_user} GB\
					, CURRENT {zip_size} GB :(")

            write_db(album_md5, 0, 0, album_quality)

            return

        file = self.__tg_user_api.send_document(
            chat_id=bunker_channel,
            document=path_zip,
            thumb=image_io2,
            progress=self.__progress_status,
            progress_args=progress_args)

        write_db(album_md5, file.chat.id, file.message_id, album_quality)

        self.__upload_zip(file.document.file_id)

    def __upload_audio_album(self, track: Track, image_bytes1, num_track,
                             nb_tracks, progress_message_id):
        c_path = track.song_path
        track_md5 = track.track_md5
        image_io1 = BytesIO(image_bytes1)
        image_io1.name = track_md5
        duration = track.duration
        performer = track.artist
        title = track.music
        f_format = track.file_format
        tag = track.tags
        file_name = set_path(tag, self.__n_quality, f_format, 1)
        c_progress = f"Uploading ({num_track}/{nb_tracks}): {title}"
        c_progress += f" {num_track * 100 / nb_tracks:.1f}%"

        with open(log_uploads, "a") as f:
            with redirect_stdout(f):
                print(c_progress)

        tg_bot.edit_message_text(chat_id=self.__chat_id,
                                 message_id=progress_message_id,
                                 text=c_progress)

        if track.success:
            track_size = get_size(c_path, "gb")

            if track_size > upload_max_size_user:
                tg_bot.send_message(
                    chat_id=self.__chat_id,
                    text=f"THE SONG {track.song_name} IS TOO BIG TO BE UPLOADED\
						, MAX {upload_max_size_user} GB\
						, CURRENT {track_size} GB :(")

                return

            track_quality = track.quality
            caption = ""

            if track_quality != self.__n_quality:
                caption = f"⚠ {self.__quality} quality unavailable. Downloaded {track_quality}."

            file = self.__tg_user_api.send_audio(chat_id=bunker_channel,
                                                 audio=c_path,
                                                 thumb=image_io1,
                                                 duration=duration,
                                                 performer=performer,
                                                 title=title,
                                                 file_name=file_name,
                                                 caption=caption)

            write_db(track_md5, file.chat.id, file.message_id, track_quality)

            self.__upload_audio(file.audio.file_id, caption=caption)
        else:
            tg_bot.send_message(chat_id=self.__chat_id,
                                text=f"Cannot download {track.song_name} :(")

    def __download_album(self, url, quality=None):
        if not quality:
            quality = self.__quality
        album = deez_api.download_albumdee(
            url,
            output_dir=output_songs,
            quality_download=quality,
            recursive_quality=recursive_quality,
            recursive_download=recursive_download,
            make_zip=make_zip,
            method_save=method_save)

        md5_image = album.md5_image
        nb_tracks = album.nb_tracks
        image_bytes1 = deezer_api.choose_img(md5_image, "90x90")
        num_track = 1

        progress_message_id = tg_bot.send_message(
            chat_id=self.__chat_id, text="Starting uploading...").message_id

        for track in album.tracks:
            self.__upload_audio_album(track, image_bytes1, num_track,
                                      nb_tracks, progress_message_id)

            num_track += 1

        tg_bot.delete_message(chat_id=self.__chat_id,
                              message_id=progress_message_id)

        self.__upload_zip_album(album)

    def __send_for_debug(self, link, error):
        err_str = f"**{user_session}**\nERROR WITH THIS LINK {link} {self.__quality}"

        tg_bot.send_message(chat_id=self.__chat_id, text=err_str)

        tg_bot.send_message(chat_id=user_errors,
                            text=err_str + "\n" + str(error))

        log_error(error, exc_info=True)
        log_error(err_str)

    def __check_track(self, link):
        link_path = get_url_path(link)
        matchs = DeezS.select_dwsong(link_path)
        c_match = next(
            (track
             for track in matchs if self.__n_quality == track['quality']),
            None)
        if c_match:
            try:
                file_msg = tg_user_api.get_messages(c_match['chat_id'],
                                                    c_match['msg_id'])
                self.__upload_audio(file_msg.audio.file_id)
            except (BadRequest, PyrogramBR):
                DeezS.delete_dwsongs(c_match['msg_id'])
                self.__check_track(link)
        else:
            try:
                self.__download_track(link)
            except QualityNotFound:
                for ql in qualities.keys():
                    if ql != self.__quality:
                        alt_match = next((
                            track for track in matchs
                            if qualities[ql]['s_quality'] == track['quality']),
                                         None)
                        if alt_match:
                            try:
                                alt_file_msg = tg_user_api.get_messages(
                                    alt_match['chat_id'], alt_match['msg_id'])
                                caption = f"⚠ {self.__quality} Unavailable. Downloaded {qualities[ql]['s_quality']}"
                                self.__upload_audio(alt_file_msg.audio.file_id,
                                                    caption=caption)
                                break
                            except (BadRequest, PyrogramBR):
                                DeezS.delete_dwsongs(alt_match['msg_id'])
                                self.__check_track(link)
                        else:
                            try:
                                self.__download_track(link, quality=ql)
                            except QualityNotFound:
                                continue
            except Exception as error:
                self.__send_for_debug(link, error)

    def __check_album(self, link, tracks):
        link_path = get_url_path(link)
        matchs = DeezS.select_dwsong(link_path)
        c_links = [get_url_path(track['link'] for track in tracks)]
        c_match = next(
            (track
             for track in matchs if self.__n_quality == track['quality']),
            None)

        if c_match:
            if c_match['msg_id'] != 0:
                try:
                    file_msg = tg_user_api.get_messages(
                        c_match['chat_id'], c_match['msg_id'])
                    self.__upload_zip(file_msg.document.file_id)
                except (BadRequest, PyrogramBR):
                    DeezS.delete_dwsongs(c_match['msg_id'])
                    self.__check_album(link, tracks)

            if self.__send_to_user_tracks:
                c_matchs = DeezS.select_multiple_dwsongs(
                    c_links, self.__n_quality)
                messages = []

                if c_matchs:
                    try:
                        messages = tg_user_api.get_messages(
                            bunker_channel, [
                                tracks['msg_id']
                                for tracks in c_matchs if tracks['msg_id'] != 0
                            ])
                    except PyrogramBR as error:
                        self.__send_for_debug(link, error)

                for track in tracks:
                    c_link = track['link']
                    c_link_path = get_url_path(c_link)
                    c_match = next((c_track for c_track in c_matchs
                                    if c_link_path == c_track['link']), None)

                    if not c_match:
                        self.__check_track(c_link)
                        continue

                    audio_file_id = next(
                        (msg.audio.file_id for msg in messages
                         if c_match['msg_id'] == msg.message_id), None)

                    try:
                        self.__upload_audio(audio_file_id)
                    except BadRequest:
                        DeezS.delete_dwsongs(c_match['msg_id'])
                        self.__check_track(c_link)
        else:
            try:
                self.__download_album(link)
            except QualityNotFound:
                done = 0
                for ql in qualities.keys():
                    if ql != self.__quality:
                        alt_match = next((
                            track for track in matchs
                            if qualities[ql]['s_quality'] == track['quality']),
                                         None)
                        if alt_match:
                            if alt_match['msg_id'] != 0:
                                try:
                                    file_msg = tg_user_api.get_messages(
                                        alt_match['chat_id'],
                                        alt_match['msg_id'])
                                    self.__upload_zip(
                                        file_msg.document.file_id)
                                except BadRequest:
                                    DeezS.delete_dwsongs(alt_match['msg_id'])
                                    self.__check_album(link, tracks)

                            if self.__send_to_user_tracks:
                                c_matchs = DeezS.select_multiple_dwsongs(
                                    c_links, qualities[ql]['s_quality'])
                                messages = []

                                if c_matchs:
                                    try:
                                        messages = tg_user_api.get_messages(
                                            bunker_channel, [
                                                tracks['msg_id']
                                                for tracks in c_matchs
                                                if tracks['msg_id'] != 0
                                            ])
                                    except PyrogramBR as error:
                                        self.__send_for_debug(link, error)

                                for track in tracks:
                                    c_link = track['link']
                                    c_link_path = get_url_path(c_link)
                                    c_match = next(
                                        (c_track for c_track in c_matchs
                                         if c_link_path == c_track['link']),
                                        None)

                                    if not c_match:
                                        self.__check_track(c_link)
                                        continue

                                    audio_file_id = next(
                                        (msg.audio.file_id for msg in messages
                                         if c_match['msg_id'] == msg.message_id
                                         ), None)
                                    caption = f"⚠ {self.__quality} Unavailable. Downloaded {qualities[ql]['s_quality']}"
                                    try:
                                        self.__upload_audio(audio_file_id,
                                                            caption=caption)
                                    except BadRequest:
                                        DeezS.delete_dwsongs(c_match['msg_id'])
                                        self.__check_track(c_link)
                            done = 1
                        else:
                            try:
                                self.__download_album(link, quality=ql)
                                done = 1
                            except QualityNotFound:
                                continue
                if done == 0:
                    raise TrackNotFound
            except Exception as error:
                self.__send_for_debug(link, error)

    def __check_playlist(self, tracks, mode):
        links = []
        matchs = []
        spotify = {}
        ignore = {}
        messages = []

        if mode == "deezer":
            links = [get_url_path(track['link'] for track in tracks)]
        else:
            for idx, track in enumerate(tracks):
                c_track = track['track']
                if c_track:
                    if c_track['external_urls']:
                        spoty_url = c_track['external_urls']['spotify']
                        try:
                            link = convert_spoty_to_dee_link_track(spoty_url)
                            links.append(link)
                            spotify[idx] = link
                        except (NoDataApi, TrackNotFound):
                            ignore[idx] = f"Cannot download {spoty_url} :("
                            continue
                    else:
                        ignore[
                            idx] = f"The track \"{c_track['name']}\" is not avalaible on Spotify :("
                        continue
                else:
                    ignore[idx] = "None"
                    continue

        if links:
            matchs = DeezS.select_multiple_dwsongs(links, self.__n_quality)

            if matchs:
                messages = tg_user_api.get_messages(bunker_channel, [
                    tracks['msg_id']
                    for tracks in matchs if tracks['msg_id'] != 0
                ])

        for c_idx, track in enumerate(tracks):
            if mode == 'spotify':
                if c_idx in ignore:
                    if ignore[idx] != "None":
                        tg_bot.send_message(chat_id=self.__chat_id,
                                            text=ignore[idx])
                    continue
                elif c_idx in spotify:
                    c_link = spotify[c_idx]
            else:
                c_link = track['link']

            c_link_path = get_url_path(c_link)
            c_match = next(
                (c_track
                 for c_track in matchs if c_link_path == c_track['link']),
                None)

            if not c_match:
                self.__check_track(c_link)
                continue

            audio_file_id = next(
                (msg.audio.file_id
                 for msg in messages if c_match['msg_id'] == msg.message_id),
                None)

            try:
                self.__upload_audio(audio_file_id)
            except BadRequest:
                DeezS.delete_dwsongs(c_match['msg_id'])
                self.__check_track(c_link)

    def download(self, link):
        try:
            stat = 1
            self.__before_dw()
            link = what_kind(link)

            if "track/" in link:
                if "spotify.com" in link:
                    try:
                        image_url, name,\
                         artist, album,\
                          date, link_dee, duration = track_spo_data(link)
                    except TrackNotFound:
                        tg_bot.send_message(chat_id=self.__chat_id,
                                            text=f"Cannot download {link} :(")

                        return

                elif "deezer.com" in link:
                    image_url, name,\
                     artist, album,\
                      date, link_dee, duration = track_dee_data(link)

                if duration > seconds_limits_track:
                    tg_bot.send_message(chat_id=self.__chat_id,
                                        text=track_too_long)

                    return

                msg_id = tg_bot.send_photo(
                    chat_id=self.__chat_id,
                    photo=image_url,
                    caption=(send_image_track_query %
                             (name, artist, album, date))).message_id

                self.__check_track(link_dee)

            elif "artist/" in link:
                stat = 0

                if "deezer.com" in link:
                    name, image_url,\
                     nb_album, nb_fan = artist_dee_data(link)
                else:
                    return

                msg_id = tg_bot.send_photo(
                    chat_id=self.__chat_id,
                    photo=image_url,
                    reply_markup=create_keyboard_artist(link),
                    caption=(send_image_artist_query %
                             (name, nb_album, nb_fan))).message_id

            elif "album/" in link:
                if "spotify.com" in link:
                    image_url, album,\
                     artist, date,\
                     nb_tracks, tracks,\
                     duration, link_dee = album_spo_data(link)

                elif "deezer.com" in link:
                    image_url, album,\
                     artist, date,\
                     nb_tracks, tracks,\
                     duration, link_dee = album_dee_data(link)

                if duration > seconds_limits_album:
                    tg_bot.send_message(chat_id=self.__chat_id,
                                        text=album_too_long)

                    return

                msg_id = tg_bot.send_photo(
                    chat_id=self.__chat_id,
                    photo=image_url,
                    caption=(send_image_album_query %
                             (album, artist, date, nb_tracks))).message_id

                self.__check_album(link_dee, tracks)

            elif "playlist/" in link:
                if "spotify.com" in link:
                    mode = "spotify"

                    try:
                        nb_tracks, n_fans,\
                         image_url, creation_data,\
                          creator, tracks = playlist_spo_data(link)
                    except IndexError:
                        tg_bot.send_message(
                            chat_id=self.__chat_id,
                            text=f"This playlist is unreadable :(")

                        return

                elif "deezer.com" in link:
                    mode = "deezer"

                    nb_tracks, n_fans,\
                     image_url, creation_data,\
                      creator, tracks = playlist_dee_data(link)

                msg_id = tg_bot.send_photo(
                    chat_id=self.__chat_id,
                    photo=image_url,
                    caption=(send_image_playlist_query %
                             (creation_data, creator, nb_tracks,
                              n_fans))).message_id

                if nb_tracks > max_song_per_playlist:
                    tg_bot.send_message(
                        chat_id=self.__chat_id,
                        text=
                        f"This playlist contains {nb_tracks} tracks only the first {max_song_per_playlist} will be downloaded"
                    )

                self.__check_playlist(tracks[:max_song_per_playlist], mode)

            else:
                tg_bot.send_message(
                    chat_id=self.__chat_id,
                    text="Can you just send normal links?, THANKS :)")

                return

            if stat == 1:
                tg_bot.send_message(chat_id=self.__chat_id,
                                    text="FINISHED =)",
                                    reply_to_message_id=msg_id)
        except AlbumNotFound as error:
            tg_bot.send_message(chat_id=self.__chat_id, text=error.msg)
        except (NoDataApi, InvalidLink) as error:
            if type(error) is NoDataApi:
                text = f"This {link} doesn't exist :("

            elif type(error) is InvalidLink:
                text = f"INVALID LINK {link} :("

            tg_bot.send_message(chat_id=self.__chat_id, text=text)
        except Exception as error:
            try:
                self.__send_for_debug(link, error)
            except Exception as error:
                log_error(f"{link} {self.__quality} {self.__chat_id}")
                log_error(error, exc_info=True)
        finally:
            self.__after_dw()
            self.__finished()
