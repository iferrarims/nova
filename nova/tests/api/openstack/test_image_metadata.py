# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import webob


from nova import flags
from nova.api import openstack
from nova import test
from nova.tests.api.openstack import fakes


FLAGS = flags.FLAGS


class ImageMetaDataTest(test.TestCase):

    def setUp(self):
        super(ImageMetaDataTest, self).setUp()
        fakes.stub_out_glance(self.stubs)

    def test_index(self):
        req = webob.Request.blank('/v1.1/123/images/123/metadata')
        res = req.get_response(fakes.wsgi_app())
        res_dict = json.loads(res.body)
        self.assertEqual(200, res.status_int)
        expected = {'metadata': {'key1': 'value1'}}
        self.assertEqual(res_dict, expected)

    def test_show(self):
        req = webob.Request.blank('/v1.1/fake/images/123/metadata/key1')
        res = req.get_response(fakes.wsgi_app())
        res_dict = json.loads(res.body)
        self.assertEqual(200, res.status_int)
        self.assertTrue('meta' in res_dict)
        self.assertEqual(len(res_dict['meta']), 1)
        self.assertEqual('value1', res_dict['meta']['key1'])

    def test_show_not_found(self):
        req = webob.Request.blank('/v1.1/fake/images/123/metadata/key9')
        res = req.get_response(fakes.wsgi_app())
        self.assertEqual(404, res.status_int)

    def test_show_image_not_found(self):
        req = webob.Request.blank('/v1.1/fake/images/100/metadata/key1')
        res = req.get_response(fakes.wsgi_app())
        self.assertEqual(404, res.status_int)

    def test_create(self):
        req = webob.Request.blank('/v1.1/fake/images/123/metadata')
        req.method = 'POST'
        req.body = '{"metadata": {"key7": "value7"}}'
        req.headers["content-type"] = "application/json"
        res = req.get_response(fakes.wsgi_app())

        self.assertEqual(200, res.status_int)
        actual_output = json.loads(res.body)
        expected_output = {'metadata': {'key1': 'value1', 'key7': 'value7'}}
        self.assertEqual(expected_output, actual_output)

    def test_create_image_not_found(self):
        req = webob.Request.blank('/v1.1/fake/images/100/metadata')
        req.method = 'POST'
        req.body = '{"metadata": {"key7": "value7"}}'
        req.headers["content-type"] = "application/json"
        res = req.get_response(fakes.wsgi_app())

        self.assertEqual(404, res.status_int)

    def test_update_all(self):
        req = webob.Request.blank('/v1.1/fake/images/123/metadata')
        req.method = 'PUT'
        req.body = '{"metadata": {"key9": "value9"}}'
        req.headers["content-type"] = "application/json"
        res = req.get_response(fakes.wsgi_app())

        self.assertEqual(200, res.status_int)
        actual_output = json.loads(res.body)
        expected_output = {'metadata': {'key9': 'value9'}}
        self.assertEqual(expected_output, actual_output)

    def test_update_all_image_not_found(self):
        req = webob.Request.blank('/v1.1/fake/images/100/metadata')
        req.method = 'PUT'
        req.body = '{"metadata": {"key9": "value9"}}'
        req.headers["content-type"] = "application/json"
        res = req.get_response(fakes.wsgi_app())

        self.assertEqual(404, res.status_int)

    def test_update_item(self):
        req = webob.Request.blank('/v1.1/fake/images/123/metadata/key1')
        req.method = 'PUT'
        req.body = '{"meta": {"key1": "zz"}}'
        req.headers["content-type"] = "application/json"
        res = req.get_response(fakes.wsgi_app())

        self.assertEqual(200, res.status_int)
        actual_output = json.loads(res.body)
        expected_output = {'meta': {'key1': 'zz'}}
        self.assertEqual(actual_output, expected_output)

    def test_update_item_image_not_found(self):
        req = webob.Request.blank('/v1.1/fake/images/100/metadata/key1')
        req.method = 'PUT'
        req.body = '{"meta": {"key1": "zz"}}'
        req.headers["content-type"] = "application/json"
        res = req.get_response(fakes.wsgi_app())

        self.assertEqual(404, res.status_int)

    def test_update_item_bad_body(self):
        req = webob.Request.blank('/v1.1/fake/images/123/metadata/key1')
        req.method = 'PUT'
        req.body = '{"key1": "zz"}'
        req.headers["content-type"] = "application/json"
        res = req.get_response(fakes.wsgi_app())
        self.assertEqual(400, res.status_int)

    def test_update_item_too_many_keys(self):
        req = webob.Request.blank('/v1.1/fake/images/123/metadata/key1')
        req.method = 'PUT'
        overload = {}
        for num in range(FLAGS.quota_metadata_items + 1):
            overload['key%s' % num] = 'value%s' % num
        req.body = json.dumps({'meta': overload})
        req.headers["content-type"] = "application/json"
        res = req.get_response(fakes.wsgi_app())
        self.assertEqual(400, res.status_int)

    def test_update_item_body_uri_mismatch(self):
        req = webob.Request.blank('/v1.1/fake/images/123/metadata/bad')
        req.method = 'PUT'
        req.body = '{"meta": {"key1": "value1"}}'
        req.headers["content-type"] = "application/json"
        res = req.get_response(fakes.wsgi_app())
        self.assertEqual(400, res.status_int)

    def test_update_item_xml(self):
        req = webob.Request.blank('/v1.1/fake/images/123/metadata/key1')
        req.method = 'PUT'
        req.body = '<meta key="key1">five</meta>'
        req.headers["content-type"] = "application/xml"
        res = req.get_response(fakes.wsgi_app())

        self.assertEqual(200, res.status_int)
        actual_output = json.loads(res.body)
        expected_output = {'meta': {'key1': 'five'}}
        self.assertEqual(actual_output, expected_output)

    def test_delete(self):
        req = webob.Request.blank('/v1.1/fake/images/123/metadata/key1')
        req.method = 'DELETE'
        res = req.get_response(fakes.wsgi_app())
        self.assertEqual(204, res.status_int)
        self.assertEqual('', res.body)

    def test_delete_not_found(self):
        req = webob.Request.blank('/v1.1/fake/images/123/metadata/blah')
        req.method = 'DELETE'
        res = req.get_response(fakes.wsgi_app())
        self.assertEqual(404, res.status_int)

    def test_delete_image_not_found(self):
        req = webob.Request.blank('/v1.1/fake/images/100/metadata/key1')
        req.method = 'DELETE'
        res = req.get_response(fakes.wsgi_app())
        self.assertEqual(404, res.status_int)

    def test_too_many_metadata_items_on_create(self):
        data = {"metadata": {}}
        for num in range(FLAGS.quota_metadata_items + 1):
            data['metadata']['key%i' % num] = "blah"
        json_string = str(data).replace("\'", "\"")
        req = webob.Request.blank('/v1.1/fake/images/123/metadata')
        req.method = 'POST'
        req.body = json_string
        req.headers["content-type"] = "application/json"
        res = req.get_response(fakes.wsgi_app())
        self.assertEqual(413, res.status_int)

    def test_too_many_metadata_items_on_put(self):
        FLAGS.quota_metadata_items = 1
        req = webob.Request.blank('/v1.1/fake/images/123/metadata/blah')
        req.method = 'PUT'
        req.body = '{"meta": {"blah": "blah"}}'
        req.headers["content-type"] = "application/json"
        res = req.get_response(fakes.wsgi_app())
        self.assertEqual(413, res.status_int)
