import unittest
from unittest.mock import patch, Mock
from lightspeed_google_feed.storage import Storage

class TestStorage(unittest.TestCase):

    def test_simple_save_read_local_file(self):
        '''Test simple save and read'''
        content = "test content"
        filename = "test.xml"
        storage = Storage(cloud=False)
        storage.save_file(filename, content)
        content_read = storage.read_file(filename)
        self.assertEqual(content, content_read)

    @patch('lightspeed_google_feed.storage.storage')
    @patch('builtins.open')
    def test_save_file_local(self, mock_open, mock_storage):
        '''Test saving file locally'''
        content = "test content"
        filename = "test.xml"
        
        storage = Storage(cloud=False)
        storage.save_file(filename, content)
        
        mock_open.assert_called_once_with(filename, 'w', encoding='utf-8')
        mock_open.return_value.__enter__().write.assert_called_once_with(content)
        mock_storage.Client.assert_not_called()

    @patch('lightspeed_google_feed.storage.storage')
    def test_save_file_cloud(self, mock_storage):
        '''Test saving file to cloud storage'''
        content = "test content"
        filename = "test.xml"
        
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        storage = Storage(cloud=True)
        storage.save_file(filename, content)
        
        mock_storage.Client.assert_called_once()
        mock_client.bucket.assert_called_once()
        mock_bucket.blob.assert_called_once_with(filename)
        mock_blob.upload_from_string.assert_called_once_with(content, content_type='application/xml')

    @patch('builtins.open')
    def test_read_file_local(self, mock_open):
        '''Test reading local file'''
        filename = "test.xml"
        expected_content = "test content"
        
        mock_open.return_value.__enter__().read.return_value = expected_content
        
        storage = Storage(cloud=False)
        content = storage.read_file(filename)
        
        self.assertEqual(content, expected_content)
        mock_open.assert_called_once_with(filename, 'r', encoding='utf-8')

    @patch('builtins.open')
    def test_read_file_local_not_found(self, mock_open):
        '''Test reading non-existent local file'''
        filename = "nonexistent.xml"
        mock_open.side_effect = FileNotFoundError
        
        storage = Storage(cloud=False)
        content = storage.read_file(filename)
        
        self.assertEqual(content, "<error>Feed file not found. Please generate a feed first.</error>")

    @patch('lightspeed_google_feed.storage.storage')
    def test_read_file_cloud(self, mock_storage):
        '''Test reading file from cloud storage'''
        filename = "test.xml"
        expected_content = "test content"
        
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.download_as_string.return_value = expected_content
        
        storage = Storage(cloud=True)
        content = storage.read_file(filename)
        
        self.assertEqual(content, expected_content)
        mock_storage.Client.assert_called_once()
        mock_client.bucket.assert_called_once()
        mock_bucket.blob.assert_called_once_with(filename)
        mock_blob.download_as_string.assert_called_once()

    @patch('lightspeed_google_feed.storage.storage')
    def test_read_file_cloud_error(self, mock_storage):
        '''Test reading file from cloud storage with error'''
        filename = "test.xml"
        
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.download_as_string.side_effect = Exception("Cloud storage error")
        
        storage = Storage(cloud=True)
        content = storage.read_file(filename)
        
        self.assertEqual(content, "<error>Feed file not found. Please generate a feed first.</error>")

    if __name__ == '__main__':
        unittest.main()