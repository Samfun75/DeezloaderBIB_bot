#!/usr/bin/python3

from utils.converter_bytes import convert_bytes_to
from telegram.constants import MAX_FILESIZE_DOWNLOAD

logs_path = "logs/"
log_errors = f"{logs_path}deez_bot.log"
log_downloads = f"{logs_path}downloads.log"
log_uploads = f"{logs_path}uploads.log"
warning_for_banning = 4
user_session = "SamfunMusicBot"
user_errors = -1001477054892  #Chat id user to send errors
bunker_channel = -1001458398324  #Chat id channel to send all downloaded sons
owl_channel = -1001739851565  #Chat id channel for send broadcast message
settings_file = "deez_settings.ini"
root_ids = {304377418}
output_songs = "Songs/"
output_shazam = "Records/"
recursive_quality = True
recursive_download = True
make_zip = True
method_save = 2
download_dir_max_size = 6  #GB
donation_link = "https://www.paypal.com/paypalme/An0nimia"

supported_link = [
    "www.deezer.com", "open.spotify.com", "deezer.com", "spotify.com",
    "deezer.page.link"
]

time_sleep = 8
seconds_limits_album = 30000  #seconds
seconds_limits_track = 7200
upload_max_size_user = 2  #GB
max_song_per_playlist = 300
max_download_user = 5

recorded_file_max_size = int(convert_bytes_to(MAX_FILESIZE_DOWNLOAD, "mb"))
