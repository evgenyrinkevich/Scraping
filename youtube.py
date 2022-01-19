# 2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis). Найти среди них любое,
# требующее авторизацию (любого типа). Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.
import json
# import os
from googleapiclient.discovery import build

YT_API_KEY = 'AIzaSyCjDZKyOencGq1oYTxeRnbjnxGc8WFZ3YQ'

# YT_API_KEY = os.environ.get('YT_API_KEY')
# Сделал более безопасно ключ из переменной окружения, но чтобы у вас скрипт сработал оставил ключ явно

youtube = build('youtube', 'v3', developerKey=YT_API_KEY)


def get_yt_channel_stats(channel_id):
    """
    Prints out YouTube channel stats and creates JSON file with more detailed info
    """
    request = youtube.channels().list(
        part='statistics',
        id=channel_id)
    response = request.execute()
    with open('YT_channel_stats.json', 'w') as f:
        json.dump(response, f)
    channel_stats = response.get('items')[0].get('statistics')
    print(f"Channel's subs count - {channel_stats.get('subscriberCount')}"
          f"\nTotal views - {channel_stats.get('viewCount')}")


def get_yt_channel_playlists(channel_id):
    """
    Prints out YouTube channel's list of playlists
    """
    request = youtube.playlists().list(
        part='snippet',
        channelId=channel_id)
    response = request.execute()
    print("Channel's playlists:")
    for playlist in response.get('items'):
        print(playlist.get('snippet').get('title'))

    while request:
        request = youtube.playlists().list_next(request, response)
        if request:
            response = request.execute()
            for playlist in response.get('items'):
                print(playlist.get('snippet').get('title'))


yt_channel_id = 'UCCbmVPjggWU-mspagT9oECQ'

get_yt_channel_stats(yt_channel_id)
get_yt_channel_playlists(yt_channel_id)

# Результат выполнения скритпа:
# Channel's subs count - 937
# Total views - 117316
# Channel's playlists:
# Rock
# Electronic
# Fitness/Workout
# Hip Hop
# For children
# Tropical
# Ambient
# Romantic
# Dance
# Cinematic
# Pop
# Acoustic
# Corporate
