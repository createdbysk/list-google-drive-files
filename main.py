from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
CLIENT_SECRET_FILE = '.credentials/client_secret.json'
APPLICATION_NAME = 'Find Duplicates'
PAGE_SIZE = 1000
FIELDS = "nextPageToken, files(name, id, quotaBytesUsed)"
ORDER_BY = "quotaBytesUsed desc"

flags = None

import object_store

object_store_instance = object_store.ObjectStore.create()

def get_credentials(suffix):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    from oauth2client.client import OAuth2WebServerFlow

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
            credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_total_quota_bytes_used(suffix):
    import json
    credentials = get_credentials(suffix)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
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


def get_item_list(credentials):
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


def find_duplicates(object_store_instance):
    """
    If there are multiple instances of an object, then there are duplicates.
    :param object_store_instance: The instance of the object store.
    :return: A dictionary of duplicate information
    """
    duplicates = {}
    for name in object_store_instance:
        object_list = object_store_instance.find_object(name)
        if len(object_list) > 1:
            duplicates[name] = object_list

    return duplicates


def get_item_permissions(object_list):
    services = {}
    # Make a copy of the parameter
    items = object_list[:]
    for item in items:
        credentials = item[0]
        if credentials not in services:
            http = credentials.authorize(httplib2.Http())
            service = discovery.build('drive', 'v3', http=http)
            services[credentials] = service
        else:
            service = services[credentials]
        item_details = item[1]
        id = item_details['id']
        permissions = service.permissions().list(fileId=id).execute()
        item_details['permissions'] = []
        for permission in permissions['permissions']:
            details = service.permissions().get(fileId=id,
                                                permissionId=permission['id'],
                                                fields='id, type, emailAddress').execute()
            item_details['permissions'].append(details)

    return items


def add_items_to_object_store(object_store_instance, credentials):
    item_list = get_item_list(credentials)
    for item in item_list:
        name = item['name']
        object_store_instance.add_object(name, item, credentials)

    return object_store_instance


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


def main():
    """
    Locates an object in the given google drive accounts
    """
    import json
    credentials_1 = get_credentials(1)
    credentials_2 = get_credentials(2)
    add_to_object_store(credentials_1)
    add_to_object_store(credentials_2)

    duplicates = find_duplicates(object_store_instance)
    print(json.dumps(duplicates, indent=4))
    print(json.dumps(possible_wasted_quota_bytes_used(duplicates), indent=4))

    file_duplicates = duplicates['2014.1']
    print(json.dumps(get_item_permissions(file_duplicates), indent=4))


def add_to_object_store(credentials):
    add_items_to_object_store(object_store_instance, credentials)


if __name__ == '__main__':
    try:
        import argparse

        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        flags = None

    main()