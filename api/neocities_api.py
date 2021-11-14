from os import mkdir
from os.path import exists, isdir
from requests import get, post

import json
import logging
from time import sleep
from re import sub

from api.neocities_api_helper import BASE_URL, DELETE, LIST, UPLOAD, INFO, KEY

# THIS IS A DEVELOPMENT BUILD - LOGGING DEFAULTS TO DEBUG LEVEL
default_log_level = logging.DEBUG

default_sleep_period = 10


class NeoCitiesApi:
    """
    API for managing a NeoCities website.

    Uses information stored in config.json to perform most operations.
    """
    def __init__(self, site: str, key: str, path: str = None, sleep_period: int = default_sleep_period):
        """
        :param site: domain of the site being used, optional
        :param key: api key of the site owner, optional

        Will check config.json (if it exists) for values. Supplied values will override config file values. If no
        config file exists, one will be created from supplied values. See further documentation on config files
        """
        self.logger = logging.getLogger('api')
        self.logger.setLevel(default_log_level)
        self.logger.info(f'Creating api object for site: {site}')
        self.site = site
        self.path = path if path else site + '/'
        self.logger.info(f'Site files located at {path}')
        self.logger.debug(f'API key: {key}')
        self.sleep_period = sleep_period
        self.logger.debug(f'Delay between requests: {self.sleep_period} seconds')
        self.key = key

    def _api_call(self, request_type, call_type: str, sleep_time= default_sleep_period, **kwargs,) -> dict:
        """
        :param request_type: requests method of the appropriate type to be executed
        :param call_type: the type of call that will be made
        :return: dictionary with response information

        Performs the API call
        """
        self.logger.debug('Making request...')
        res =  request_type(BASE_URL + call_type, headers={'Authorization': 'Bearer ' + self.key}, **kwargs)
        self.logger.debug(f'Response acquired, pausing for {sleep_time} seconds...')
        sleep(sleep_time)
        return res

    def info(self, site: str = None) -> dict:
        """
        :param site: name of the site to get information on
        :return: dictionary containing site information

        Will query either the site this API object is for or another if a site name is provided
        """
        return self._api_call(get, INFO, sleep_time=self.sleep_period,
                              params={'sitename': site if site else self.site}).json()

    def list(self, path: str = None) -> list:
        """
        :param path: the path of the site to return a list of files for; defaults to root
        :return: list of dictionaries containing file information
        """
        return self._api_call(get, LIST, sleep_time=self.sleep_period,
                              params={'path': path if path else None}).json()

    def upload(self, files: list) -> dict:
        """
        :param files: all the files to be uploaded
        :return: success/fail result information
        :raises FileNotFoundError: if any file in the list does not exist

        Uploads the files listed; file paths are stripped down to site directory name
        """
        return self._api_call(post, UPLOAD, sleep_time=self.sleep_period,
                              files={sub(f'^{self.path}', '', file): open(file, 'rb') for file in files}).json()

    def delete(self, files: list) -> dict:
        """
        :param files: all the files to be deleted
        :return: success/fail result information
        :raises FileNotFoundError: if any file in the list does not exist

        Deletes the files listed; file paths are stripped down to site directory name
        """
        return self._api_call(post, DELETE, sleep_time=self.sleep_period,
                              data={'filenames[]': [sub(f'^{self.path}', '', file) for file in files]}).json()

    def sync(self) -> dict:
        """
        :return: success/fail result information

        Requests a list of all files currently on the site and compares it with files in the project folder. Any
        updated local files will be uploaded and any updated remote files will replace local files.
        """
        raise NotImplementedError()

    def update(self, site_name: str = None, key: str = None, path: str = None):
        raise NotImplementedError()

    @staticmethod
    def key(user, password) -> str:
        """
        :return: the API key for this user
        """
        return get(BASE_URL + KEY, auth=(user, password)).json()

    @staticmethod
    def load_site(path: str = ''):
        logging.getLogger('api').info(f'loading from file {path + "config.json"}')
        config = json.load(open(f'../{path}config.json', 'r'))
        return NeoCitiesApi(config['site'], config['key'])

    @staticmethod
    def load_sync_site(path: str = ''):
        """
        :param path: the path of the site to be loaded
        :return:
        """
        raise NotImplementedError()

    @staticmethod
    def create_site(site_name: str, key: str, path: str = None):
        site_path = f'../{path if path else ""}{site_name}'
        if not (exists(site_path) and isdir(site_path)):
            mkdir(site_path)
        if not (exists('../' + site_path + '/config.json')):
            with open('../' + site_name + '/config.json', 'a+') as f:
                json.dump({'site': site_name, 'key': key}, f)
        return


def _download_file(self, url):
    """
    :param url: the address to get the file from

    Used as part of the synchronization process when files exist on the server but not in the project
    """
    raise NotImplementedError()


if __name__ == '__main__':
    # this is just temporary debugging code
    from pprint import pprint
    logging.basicConfig(level=default_log_level)
    logging.getLogger('api').setLevel(default_log_level)
    api = NeoCitiesApi.load_site('../')
    pprint(api.list())
