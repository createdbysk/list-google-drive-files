from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
CLIENT_SECRET_FILE = '.credentials/client_secret.json'
APPLICATION_NAME = 'Find Duplicates'
PAGE_SIZE = 1000
FIELDS = "nextPageToken, files(name, quotaBytesUsed)"
ORDER_BY = "quotaBytesUsed desc"
SERVICE_ACCOUNT_EMAIL = "816614257662-dacf8kk6pcve3jv0laitst90le1pmako.apps.googleusercontent.com"
KEYFILE_PATH = ".credentials/keyfile.p12"

def get_credentials(suffix):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-{suffix}.json'.format(suffix=suffix))

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_total_quota_bytes_used(suffix):
    import json
    credentials = get_credentials(suffix)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    pageToken = None
    totalQuotaBytesUsed = 0L

    about_results = service.about().get(fields="user, storageQuota").execute()
    print(json.dumps(about_results))
    results = service.files().list(
        pageSize=PAGE_SIZE,
        orderBy=ORDER_BY,
        fields=FIELDS).execute()
    quotaBytesUsed = 0
    while True:
        items = results.get('files', [])
        if not items:
            break
        else:
            pageToken = results.get('nextPageToken', None)
            for item in items:
                quotaBytesUsed = int(item['quotaBytesUsed'])
                # Quota bytes are in descending sort order.
                # If the number of bytes is zero, then all subsequent values will be 0.
                # Break because there is no need to add the rest of the sizes.
                if quotaBytesUsed == 0:
                    break
                totalQuotaBytesUsed = totalQuotaBytesUsed + quotaBytesUsed
            print('quota bytes used until now {}'.format(totalQuotaBytesUsed))
            # Quota bytes are in descending sort order.
            # If the number of bytes is zero, then all subsequent values will be 0.
            # Break because there is no need to add the rest of the sizes.
            if quotaBytesUsed == 0:
                break
            if pageToken is None:
                break
            results = service.files().list(
                pageToken=pageToken,
                pageSize=PAGE_SIZE,
                orderBy=ORDER_BY,
                fields=FIELDS).execute()


def get_item_list(suffix):
    credentials = get_credentials(suffix)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    item_list = []

    results = service.files().list(
        pageSize=PAGE_SIZE,
        orderBy=ORDER_BY,
        fields=FIELDS).execute()
    while True:
        items = results.get('files', [])
        if not items:
            break
        else:
            item_list.extend(items)
            page_token = results.get('nextPageToken', None)
            if page_token is None:
                break
            results = service.files().list(
                pageToken=page_token,
                pageSize=PAGE_SIZE,
                orderBy=ORDER_BY,
                fields=FIELDS).execute()
    return item_list


def find_duplicates(suffixes):
    """
    Algorithm:
        If an item is not already seen,
            add it to already seen along with the suffix in which it is seen.
        If an item is already seen
            if duplicates does not have the item,
                add the information stored in already seen
            add the current item along with the suffix in which it is seen.
    :param suffix1: 
    :param suffix2: 
    :return: 
    """
    def build(item_list, suffix):
        for item in item_list:
            name = item['name']
            if name in already_seen:
                if name not in duplicates:
                    duplicates[name] = [already_seen[name]]
                duplicates[name].append((suffix, item))
            else:
                already_seen[name] = (suffix, item)

    # Now extract the duplicates by name
    already_seen = {}
    duplicates = {}
    for suffix in suffixes:
        item_list = get_item_list(suffix)
        build(item_list, suffix)

    return duplicates


def possible_wasted_quota_bytes_used(duplicates):
    """
    Algorithm:
    for each item in the duplicates
        for each duplicate other than the first one
            get the suffix
            if the suffix is not already accounted for in wasted quota bytes used
                initialize it to 0
            add the quota bytes used by this duplicate instance to the wasted quota bytes used

    :param duplicates: The duplicates in the format returned by find_duplicates.
    :return:
    """
    wasted_quota_bytes_used = {}
    for name, duplicate_list in duplicates.iteritems():
        for duplicate in duplicate_list[1:]:
            suffix = duplicate[0]
            if suffix not in wasted_quota_bytes_used:
                wasted_quota_bytes_used[suffix] = 0L
            wasted_quota_bytes_used[suffix] = wasted_quota_bytes_used[suffix] \
                                              + long(duplicate[1]["quotaBytesUsed"])

    return wasted_quota_bytes_used

def service_account_credentials_factory():
    import oauth2client.service_account

    return oauth2client.service_account.ServiceAccountCredentials.from_p12_keyfile(
        SERVICE_ACCOUNT_EMAIL,
        KEYFILE_PATH
    )

def main():
    """Finds duplicates between 2 accounts. Can be extended to any number of accounts.

    Creates a Google Drive API service object, lists all the files within the
    authorized accounts, and determines duplicates based on file name within and
    between the accounts.
    """
    import json
    duplicates = find_duplicates([1, 2])
    print(json.dumps(duplicates, indent=4))
    print(json.dumps(possible_wasted_quota_bytes_used(duplicates), indent=4))

    service_account_credentials = service_account_credentials_factory()
    print(service_account_credentials)

if __name__ == '__main__':
    main()