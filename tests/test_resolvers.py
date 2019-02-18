# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2014, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
import os
import io
import unittest

# XXX (2017-10-12) deps-on-cnx-archive: Depends on cnx-archive
from cnxarchive.tests import testing


class HTMLReferenceResolutionTestCase(unittest.TestCase):
    fixture = testing.data_fixture
    maxDiff = None

    def setUp(self):
        self.fixture.setUp()
        self.fixture.setUpAccountsDb()
        from ... import _set_settings
        settings = testing.integration_test_settings()
        _set_settings(settings)

    def tearDown(self):
        self.fixture.tearDown()

    @property
    def target(self):
        from cnxdb.triggers.transforms.resolvers import resolve_cnxml_urls
        return resolve_cnxml_urls

    @testing.db_connect
    def test_reference_rewrites(self, cursor):
        # Case to test that a document's internal references have
        #   been rewritten to the cnx-archive's read-only API routes.
        ident = 3
        from cnxdb.triggers.transforms.converters import cnxml_to_full_html
        content_filepath = os.path.join(testing.DATA_DIRECTORY,
                                        'm42119-1.3-modified.cnxml')
        with open(content_filepath, 'r') as fb:
            content = cnxml_to_full_html(fb.read())
            content = io.BytesIO(content)
            content, bad_refs = self.target(content, cursor.connection, ident)

        # Read the content for the reference changes.
        expected_img_ref = '<img src="/resources/d47864c2ac77d80b1f2ff4c4c7f1b2059669e3e9/Figure_01_00_01.jpg" data-media-type="image/jpg" alt="The spiral galaxy Andromeda is shown."/>'
        self.assertIn(expected_img_ref, content)
        expected_internal_ref = '<a href="/contents/209deb1f-1a46-4369-9e0d-18674cf58a3e@7">'
        self.assertIn(expected_internal_ref, content)
        expected_resource_ref = '<a href="/resources/d47864c2ac77d80b1f2ff4c4c7f1b2059669e3e9/Figure_01_00_01.jpg">'
        self.assertIn(expected_resource_ref, content)

    @testing.db_connect
    def test_reference_not_parseable(self, cursor):
        ident = 3
        from cnxdb.triggers.transforms.converters import cnxml_to_full_html
        import glob
        content_filepath = os.path.join(testing.DATA_DIRECTORY,
                                        'm45070.cnxml')
        with open(content_filepath, 'r') as fb:
            content = cnxml_to_full_html(fb.read())
        content = io.BytesIO(content)
        content, bad_refs = self.target(content, cursor.connection, ident)

        self.assertEqual(sorted(bad_refs), [
            "Invalid reference value: document=3, reference=/m",
            "Missing resource with filename 'InquiryQuestions.svg', moduleid None version None.: document=3, reference=InquiryQuestions.svg",
            "Unable to find a reference to 'm43540' at version 'None'.: document=3, reference=/m43540",
            ])
        self.assertIn('<a href="/m">', content)

    @testing.db_connect
    def test_reference_resolver(self, cursor):
        html = io.BytesIO('''\
<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
    <body>
        <a href="/m42092#xn">
            <img src="Figure_01_00_01.jpg"/>
        </a>
        <a href="/ m42709@1.4">
            <img src="/Figure_01_00_01.jpg"/>
        </a>
        <a href="/m42092/latest?collection=col11406/latest#figure">
            Module link with collection
        </a>
        <a href="/m42955/latest?collection=col11406/1.6">
            Module link with collection and version
        </a>
        <img src=" Figure_01_00_01.jpg"/>
        <img src="/content/m42092/latest/PhET_Icon.png"/>
        <img src="/content/m42092/1.4/PhET_Icon.png"/>
        <img src="/content/m42092/1.3/PhET_Icon.png"/>
        <span data-src="Figure_01_00_01.jpg"/>

        <audio src="Figure_01_00_01.jpg" id="music" mime-type="audio/mpeg"></audio>

        <video src="Figure_01_00_01.jpg" id="music" mime-type="video/mp4"></video>

        <object width="400" height="400" data="Figure_01_00_01.jpg"></object>

        <object width="400" height="400">
            <embed src="Figure_01_00_01.jpg"/>
        </object>

        <audio controls="controls">
            <source src="Figure_01_00_01.jpg" type="audio/mpeg"/>
        </audio>
    </body>
</html>''')

        html, bad_references = self.target(html,
                                           db_connection=cursor.connection,
                                           document_ident=3)
        cursor.connection.commit()

        self.assertEqual(bad_references, [
            "Missing resource with filename 'PhET_Icon.png', moduleid m42092 version 1.3.: document=3, reference=PhET_Icon.png",
            ])
        self.assertMultiLineEqual(html, '''\
<html xmlns="http://www.w3.org/1999/xhtml">
    <body>
        <a href="/contents/d395b566-5fe3-4428-bcb2-19016e3aa3ce@4#xn">
            <img src="/resources/d47864c2ac77d80b1f2ff4c4c7f1b2059669e3e9/Figure_01_00_01.jpg"/>
        </a>
        <a href="/contents/ae3e18de-638d-4738-b804-dc69cd4db3a3@4">
            <img src="/resources/d47864c2ac77d80b1f2ff4c4c7f1b2059669e3e9/Figure_01_00_01.jpg"/>
        </a>
        <a href="/contents/e79ffde3-7fb4-4af3-9ec8-df648b391597:d395b566-5fe3-4428-bcb2-19016e3aa3ce#figure">
            Module link with collection
        </a>
        <a href="/contents/e79ffde3-7fb4-4af3-9ec8-df648b391597@6.1:209deb1f-1a46-4369-9e0d-18674cf58a3e">
            Module link with collection and version
        </a>
        <img src="/resources/d47864c2ac77d80b1f2ff4c4c7f1b2059669e3e9/Figure_01_00_01.jpg"/>
        <img src="/resources/075500ad9f71890a85fe3f7a4137ac08e2b7907c/PhET_Icon.png"/>
        <img src="/resources/075500ad9f71890a85fe3f7a4137ac08e2b7907c/PhET_Icon.png"/>
        <img src="/content/m42092/1.3/PhET_Icon.png"/>
        <span data-src="/resources/d47864c2ac77d80b1f2ff4c4c7f1b2059669e3e9/Figure_01_00_01.jpg"/>

        <audio src="/resources/d47864c2ac77d80b1f2ff4c4c7f1b2059669e3e9/Figure_01_00_01.jpg" id="music" mime-type="audio/mpeg"/>

        <video src="/resources/d47864c2ac77d80b1f2ff4c4c7f1b2059669e3e9/Figure_01_00_01.jpg" id="music" mime-type="video/mp4"/>

        <object width="400" height="400" data="/resources/d47864c2ac77d80b1f2ff4c4c7f1b2059669e3e9/Figure_01_00_01.jpg"/>

        <object width="400" height="400">
            <embed src="/resources/d47864c2ac77d80b1f2ff4c4c7f1b2059669e3e9/Figure_01_00_01.jpg"/>
        </object>

        <audio controls="controls">
            <source src="/resources/d47864c2ac77d80b1f2ff4c4c7f1b2059669e3e9/Figure_01_00_01.jpg" type="audio/mpeg"/>
        </audio>
    </body>
</html>''')


    @testing.db_connect
    def test_get_resource_info(self, cursor):
        from cnxdb.triggers.transforms.resolvers import (
            CnxmlToHtmlReferenceResolver as ReferenceResolver,
            ReferenceNotFound,
            )

        resolver = ReferenceResolver(io.BytesIO('<html></html>'),
                                     cursor.connection, 3)

        # Test file not found
        self.assertRaises(ReferenceNotFound, resolver.get_resource_info,
                          'PhET_Icon.png')

        # Test getting a file in module 3
        self.assertEqual(resolver.get_resource_info('Figure_01_00_01.jpg'),
                {'hash': 'd47864c2ac77d80b1f2ff4c4c7f1b2059669e3e9', 'id': 6})

        # Test file not found outside of module 3
        self.assertRaises(ReferenceNotFound, resolver.get_resource_info,
                          'PhET_Icon.png', document_id='m42955')

        # Test getting a file in another module
        self.assertEqual(resolver.get_resource_info('PhET_Icon.png',
            document_id='m42092'),
            {'hash': '075500ad9f71890a85fe3f7a4137ac08e2b7907c', 'id': 23})

        # Test file not found with version
        self.assertRaises(ReferenceNotFound, resolver.get_resource_info,
                          'PhET_Icon.png', document_id='m42092',
                          version='1.3')

        # Test getting a file with version
        self.assertEqual(resolver.get_resource_info('PhET_Icon.png',
            document_id='m42092', version='1.4'),
            {'hash': '075500ad9f71890a85fe3f7a4137ac08e2b7907c', 'id': 23})

    def test_parse_reference(self):
        from cnxdb.triggers.transforms.resolvers import (
            MODULE_REFERENCE, RESOURCE_REFERENCE,
            parse_legacy_reference as parse_reference,
            )

        self.assertEqual(parse_reference('/m12345'),
                (MODULE_REFERENCE, ('m12345', None, None, None, '')))

        self.assertEqual(parse_reference('/content/m12345'),
                (MODULE_REFERENCE, ('m12345', None, None, None, '')))

        self.assertEqual(parse_reference('http://cnx.org/content/m12345'),
                (MODULE_REFERENCE, ('m12345', None, None, None, '')))

        # m10278 "The Advanced CNXML"
        self.assertEqual(parse_reference('/m9007'),
                (MODULE_REFERENCE, ('m9007', None, None, None, '')))

        # m11374 "KCL"
        self.assertEqual(parse_reference('/m0015#current'),
                (MODULE_REFERENCE, ('m0015', None, None, None, '#current')))

        # m11351 "electron and hole density equations"
        self.assertEqual(parse_reference('/m11332#ntypeq'),
                (MODULE_REFERENCE, ('m11332', None, None, None, '#ntypeq')))

        # m19809 "Gavin Bakers entry..."
        self.assertEqual(parse_reference('/ m19770'),
                (MODULE_REFERENCE, ('m19770', None, None, None, '')))

        # m16562 "Flat Stanley.pdf"
        self.assertEqual(parse_reference(' Flat Stanley.pdf'),
                (RESOURCE_REFERENCE, ('Flat Stanley.pdf', None, None)))

        # m34830 "Auto_fatalities_data.xls"
        self.assertEqual(parse_reference('/Auto_fatalities_data.xls'),
                (RESOURCE_REFERENCE, ('Auto_fatalities_data.xls', None, None)))

        # m35999 "version 2.3 of the first module"
        self.assertEqual(parse_reference('/m0000@2.3'),
                (MODULE_REFERENCE, ('m0000', '2.3', None, None, '')))

        # m14396 "Adding a Table..."
        # m11837
        # m37415
        # m37430
        # m10885
        self.assertEqual(parse_reference(
            '/content/m19610/latest/eip-edit-new-table.png'),
            (RESOURCE_REFERENCE, ('eip-edit-new-table.png', 'm19610', None)))

        # m45070
        self.assertEqual(parse_reference('/m'), (None, ()))

        # m45136 "legacy format"
        self.assertEqual(parse_reference(
            'http://cnx.org/content/m48897/latest?collection=col11441/latest'),
            (MODULE_REFERENCE, ('m48897', None, 'col11441', None, '')))
        self.assertEqual(parse_reference(
            'http://cnx.org/content/m48897/1.2?collection=col11441/1.10'),
            (MODULE_REFERENCE, ('m48897', '1.2', 'col11441', '1.10', '')))
        self.assertEqual(parse_reference(
            'http://cnx.org/content/m48897/1.2?collection=col11441/1.10'
            '#figure'),
            (MODULE_REFERENCE, ('m48897', '1.2', 'col11441', '1.10',
             '#figure')))

        # legacy.cnx.org links
        self.assertEqual(parse_reference(
            'http://legacy.cnx.org/content/m48897/latest'),
            (None, ()))
        self.assertEqual(parse_reference(
            'http://legacy.cnx.org/content/m48897/latest?collection=col11441/'
            'latest'), (None, ()))
