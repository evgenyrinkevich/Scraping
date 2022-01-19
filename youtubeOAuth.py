import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


def get_credentials():
    credentials = None

    # token.pickle stores the user's credentials from previously successful logins
    if os.path.exists('token.pickle'):
        print('Loading Credentials From File...')
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    # If there are no valid credentials available, then either refresh the token or log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing Access Token...')
            credentials.refresh(Request())
        else:
            print('Fetching New Tokens...')
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json',
                scopes=[
                    'https://www.googleapis.com/auth/youtube.readonly'
                ]
            )

            flow.run_local_server(port=8080, prompt='consent',
                                  authorization_prompt_message='')
            credentials = flow.credentials

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as f:
                print('Saving Credentials for Future Use...')
                pickle.dump(credentials, f)
    return credentials


def get_latest_subs(credentials):
    youtube = build('youtube', 'v3', credentials=credentials)

    request = youtube.subscriptions().list(
        part='subscriberSnippet, contentDetails',
        myRecentSubscribers=True
        )
    response = request.execute()

    for item in response.get('items'):
        sub_id = item.get('subscriberSnippet').get('channelId')
        yt_link = f'https://youtube.com/channel/{sub_id}'
        print(yt_link)


credentials = get_credentials()
get_latest_subs(credentials)


# Результат выполнения скритпа:
# Loading Credentials From File...
# Refreshing Access Token...
# https://youtube.com/channel/UCKqXGAFfeW5q4CsviLaDJEw
# https://youtube.com/channel/UCCgv0j1N5svDhbEjPUdAs1g
# https://youtube.com/channel/UCadjttr9oM0So-io-n8legQ
# https://youtube.com/channel/UCrBLRgaLnfhdKUbFIw_CLkQ
# https://youtube.com/channel/UCAd6irVCWcV0ZCdzDF3KlkQ
#
# Process finished with exit code 0
