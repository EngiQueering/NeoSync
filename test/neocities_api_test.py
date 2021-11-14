import logging
import unittest

from os import mkdir, rmdir
from os.path import exists, isdir
from unittest.mock import MagicMock, patch

from api import neocities_api, neocities_api_helper

'''
CAUTION: Do NOT change this to make actual calls to the NeoCities API with these tests! You will likely get banned!!
'''

sample_key_a = '00000000000000000000000000000000'
sample_sitename_a = 'test_site_a'
sample_path_a = ''


class NeoCitiesAPI_api_call_tests(unittest.TestCase):
    """
    Tests the methods of the API object to ensure they can produce proper calls to the API
    """
    '''
     IMPORTANT NOTE: each of these tests is dependent on _api_call's "request_type" parameter, which has the caller
     pass a requests.get/requests.post method. If the ability to directly pass a method to be called is ever removed,
     these tests will need to be rewritten
    '''
    def setUp(self) -> None:
        self.api = neocities_api.NeoCitiesApi(sample_sitename_a, sample_key_a, sample_path_a, sleep_period=0)

    def test_api_call(self):
        """
        Tests that the underlying API calling functionality passes params correctly to the requests library
        """
        mock_call_method = MagicMock()
        mock_call_type = 'mock'
        mock_params = {'parammock': 'parammock'}
        mock_files = {'filemock': MagicMock(), 'filemock1': MagicMock()}
        mock_data = {'datamock[]': ['datamock']}

        self.api._api_call(mock_call_method, mock_call_type, params=mock_params, files=mock_files, data=mock_data)
        mock_call_method.assert_called_with(neocities_api_helper.BASE_URL + mock_call_type,
                                            headers={'Authorization': 'Bearer ' + self.api.key},
                                            params=mock_params, files=mock_files, data=mock_data)

    @patch.object(neocities_api, 'get')
    def test_info(self, mock_call):
        """
        Tests that the info method can make the proper calls to the API
        """
        # tests with default site name
        mock_call.return_value.json.return_value = 'success'
        mock_call_type = neocities_api_helper.INFO

        # ensures proper calling method is used
        self.assertEqual(self.api.info(), 'success')
        mock_call.assert_called_with(neocities_api_helper.BASE_URL + mock_call_type,
                                            headers={'Authorization': 'Bearer ' + self.api.key},
                                            params={'sitename': self.api.site})
        mock_call.reset_mock()

        # tests with provided site name
        mock_site_name = 'alt_site'
        self.assertEqual(self.api.info(mock_site_name), 'success')
        mock_call.assert_called_with(neocities_api_helper.BASE_URL + mock_call_type,
                                            headers={'Authorization': 'Bearer ' + self.api.key},
                                            params={'sitename': mock_site_name})

    @patch.object(neocities_api, 'get')
    def test_list(self, mock_call):
        """
        Tests that the list method can make the proper calls to the API
        """
        # tests with root-level (default) path
        mock_call.return_value.json.return_value = 'success'
        mock_call_type = neocities_api_helper.LIST

        self.assertEqual(self.api.list(), 'success')
        mock_call.assert_called_with(neocities_api_helper.BASE_URL + mock_call_type,
                                     headers={'Authorization': 'Bearer ' + self.api.key},
                                     params={'path': None})
        mock_call.reset_mock()

        # tests with provided path
        mock_site_path = 'alt_path'
        self.assertEqual(self.api.list(mock_site_path), 'success')
        mock_call.assert_called_with(neocities_api_helper.BASE_URL + mock_call_type,
                                     headers={'Authorization': 'Bearer ' + self.api.key},
                                     params={'path': mock_site_path})

    @patch.object(neocities_api, 'get')
    def test_key(self, mock_call):
        mock_call.return_value.json.return_value = 'success'
        mock_call_type = neocities_api_helper.KEY
        mock_user = 'fake_user'
        mock_password = 'fake_password'

        self.assertEqual(neocities_api.NeoCitiesApi.key(user=mock_user, password=mock_password), 'success')
        mock_call.assert_called_with(neocities_api_helper.BASE_URL + mock_call_type,
                                     auth=(mock_user, mock_password))

    @patch.object(neocities_api, 'post')
    @patch.object(neocities_api, 'open')
    def test_upload(self, mock_open, mock_call):
        sample_files_root = ['file0.x', 'sub/file1.x', 'file2.x', 'sub/dir/file3.x']
        sample_files_dir = ['dir/file0.x', 'dir/sub/file1.x', 'dir/file2.x', 'dir/sub/dir/file3.x']
        correct_files_out = {'file0.x': 'file', 'sub/file1.x': 'file', 'file2.x': 'file', 'sub/dir/file3.x': 'file'}
        self.api.path = 'dir/'
        mock_call.return_value.json.return_value = 'success'
        mock_open.return_value = 'file'
        mock_call_type = neocities_api_helper.UPLOAD

        # tests that files are properly placed into the post 'files' param
        self.assertEqual(self.api.upload(sample_files_root), 'success')
        mock_call.assert_called_with(neocities_api_helper.BASE_URL + mock_call_type,
                                     headers={'Authorization': 'Bearer ' + self.api.key},
                                     files=correct_files_out)
        mock_call.reset_mock()

        # tests that files have excess path info stripped out in placement name for NeoCities server
        self.assertEqual(self.api.upload(sample_files_dir), 'success')
        mock_call.assert_called_with(neocities_api_helper.BASE_URL + mock_call_type,
                                     headers={'Authorization': 'Bearer ' + self.api.key},
                                     files=correct_files_out)

    @patch.object(neocities_api, 'post')
    @patch.object(neocities_api, 'open')
    def test_delete(self, mock_open, mock_call):
        sample_files_root = ['file0.x', 'sub/file1.x', 'file2.x', 'sub/dir/file3.x']
        sample_files_dir = ['dir/file0.x', 'dir/sub/file1.x', 'dir/file2.x', 'dir/sub/dir/file3.x']
        correct_files_out = {'filenames[]': ['file0.x', 'sub/file1.x', 'file2.x', 'sub/dir/file3.x']}
        self.api.path = 'dir/'
        mock_call.return_value.json.return_value = 'success'
        mock_open.return_value = 'file'
        mock_call_type = neocities_api_helper.DELETE

        self.assertEqual(self.api.delete(sample_files_root), 'success')
        mock_call.assert_called_with(neocities_api_helper.BASE_URL + mock_call_type,
                                     headers={'Authorization': 'Bearer ' + self.api.key},
                                     data=correct_files_out)
        mock_call.reset_mock()

        self.assertEqual(self.api.delete(sample_files_dir), 'success')
        mock_call.assert_called_with(neocities_api_helper.BASE_URL + mock_call_type,
                                     headers={'Authorization': 'Bearer ' + self.api.key},
                                     data=correct_files_out)


test_dir = '../test_site_files/'

class NeoCitiesAPI_create_update_save_tests(unittest.TestCase):
    """
    Tests the ability of the API object to successfully create and load site configuration data
    """
    '''
    Will create the directory "test_site_files" at the same level as the module and delete after testing is complete
    '''

    def setUp(self) -> None:
        if exists(test_dir):
            logging.getLogger(f'FILE "{test_dir}" ALREADY EXISTS, ABORTING TEST')
            raise Exception(f'Will not run tests while {test_dir} exists')
        mkdir(test_dir)

    def tearDown(self) -> None:
        rmdir('../test_site_files/')

    def test_load_site(self):
        pass

    def test_load_sync(self):
        pass

    def test_create_site(self):
        pass


class NeoCitiesAPI_synchronizer_tests(unittest.TestCase):
    """
    Tests the ability of the API object to successfully identify which files need to be synchronized and make the proper
    calls to facilitate the action
    """
    def setUp(self) -> None:
        pass

    def test_sync(self):
        pass

    def test_download_file(self):
        pass

    def test_creates_correct_list(self):
        pass


if __name__ == '__main__':
    unittest.main()
