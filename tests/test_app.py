import json
from unittest import TestCase

from chalice.config import Config
from chalice.local import LocalGateway

from app import app


class TestApp(TestCase):
    def setUp(self):
        self.lg = LocalGateway(app, Config())

    def test_list_data_objects(self):
        """
        Test the listing feature returns a response.

        :return:
        """
        page_size = 10
        response = self.lg.handle_request(
            method='POST',
            path='/ga4gh/dos/v1/dataobjects/list',
            headers={'content-type': 'application/json'},
            body=json.dumps({'page_size': page_size}))

        self.assertEquals(response['statusCode'], 200)
        response_body = json.loads(response['body'])
        self.assertEquals(len(response_body['data_objects']), page_size)

    def test_get_data_object(self):
        """
        Lists Data Objects and then gets one by ID.
        :return:
        """
        list_response = self.lg.handle_request(
            method='POST',
            path='/ga4gh/dos/v1/dataobjects/list',
            headers={'content-type': 'application/json'},
            body=json.dumps({}))

        data_objects = json.loads(list_response['body'])['data_objects']
        data_object_id = data_objects[0]['id']
        response = self.lg.handle_request(
            method='GET',
            path='/ga4gh/dos/v1/dataobjects/{}'.format(data_object_id),
            headers={},
            body='')
        self.assertEquals(response['statusCode'], 200)
        data_object = json.loads(response['body'])['data_object']
        self.assertEquals(data_object['id'], data_object_id)

    def test_paging(self):
        """
        Demonstrates basic paging features.

        :return:
        """
        body = {
            'page_size': 1}
        list_response = self.lg.handle_request(
            method='POST',
            path='/ga4gh/dos/v1/dataobjects/list',
            headers={'content-type': 'application/json'},
            body=json.dumps(body))
        response_body = json.loads(list_response['body'])
        data_objects = response_body['data_objects']

        self.assertEquals(len(data_objects), 1)

        self.assertEquals(response_body['next_page_token'], '1')

        body = {
            'alias': 'specimenUUID:d842b267-a154-5192-988b-b9f9f0265840',
            'page_size': 1,
            'page_token': response_body['next_page_token']}
        list_response = self.lg.handle_request(
            method='POST',
            path='/ga4gh/dos/v1/dataobjects/list',
            headers={'content-type': 'application/json'},
            body=json.dumps(body))
        response_body = json.loads(list_response['body'])
        data_objects = response_body['data_objects']

        self.assertEquals(len(data_objects), 1)
