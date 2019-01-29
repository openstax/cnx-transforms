# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
import os
import subprocess
import sys
import uuid
import unittest

import pytest

from cnxdb.ident_hash import (CNXHash, IdentHashSyntaxError, IdentHashShortId,
                              IdentHashMissingVersion)


def py3_too_old(*args):
    if sys.version_info >= (3,) and os.path.exists('/usr/bin/python3'):
        out = subprocess.check_output(['/usr/bin/python3', '--version'])
        return out < b'Python 3.4'


class SplitIdentTestCase(unittest.TestCase):

    def call_target(self, *args, **kwargs):
        from cnxdb.ident_hash import split_ident_hash
        return split_ident_hash(*args, **kwargs)

    def test_empty_value(self):
        # Case of supplying the utility function with an empty indent-hash.
        ident_hash = ''

        with self.assertRaises(IdentHashSyntaxError):
            self.call_target(ident_hash)

    def test_complete_data(self):
        # Simple case of supplying the correct information and checking
        # for the correct results.
        expected_id, expected_version = (
            '85e57f79-02b3-47d2-8eed-c1bbb1e1d5c2', '1.12',
        )
        ident_hash = "{}@{}".format(expected_id, expected_version)

        id, version = self.call_target(ident_hash)

        self.assertEqual(id, expected_id)
        self.assertEqual(version, expected_version)

    def test_uuid_only_w_at_sign(self):
        expected_id = '85e57f79-02b3-47d2-8eed-c1bbb1e1d5c2'
        ident_hash = "{}@".format(expected_id)

        with self.assertRaises(IdentHashSyntaxError):
            self.call_target(ident_hash)

    def test_uuid_only(self):
        # Case where the UUID has been the only value supplied in the
        # ident-hash.
        # This is mostly testing that the version value returns None.
        expected_id = '85e57f79-02b3-47d2-8eed-c1bbb1e1d5c2'
        ident_hash = expected_id

        with self.assertRaises(IdentHashMissingVersion) as cm:
            self.call_target(ident_hash)

        exc = cm.exception
        self.assertEqual(exc.id, expected_id)

    def test_invalid_id(self):
        # Case for testing for an invalid identifier.
        ident_hash = "not-a-valid-id@"

        from cnxdb.ident_hash import IdentHashSyntaxError
        with self.assertRaises(IdentHashSyntaxError):
            self.call_target(ident_hash)

    def test_invalid_syntax(self):
        # Case for testing the ident-hash's syntax guards.
        ident_hash = "85e57f7902b347d28eedc1bbb1e1d5c2@1.2@select*frommodules"

        from cnxdb.ident_hash import IdentHashSyntaxError
        with self.assertRaises(IdentHashSyntaxError):
            self.call_target(ident_hash)

    def test_w_split_version(self):
        expected_id, expected_version = (
            '85e57f79-02b3-47d2-8eed-c1bbb1e1d5c2',
            ('1', '12', ),
        )
        ident_hash = "{}@{}".format(expected_id, '.'.join(expected_version))

        id, version = self.call_target(ident_hash, split_version=True)

        self.assertEqual(id, expected_id)
        self.assertEqual(version, expected_version)

    def test_w_split_version_on_major_version(self):
        expected_id, expected_version = (
            '85e57f79-02b3-47d2-8eed-c1bbb1e1d5c2',
            ('1', None, ),
        )
        ident_hash = "{}@{}".format(expected_id, expected_version[0])

        id, version = self.call_target(ident_hash, split_version=True)

        self.assertEqual(id, expected_id)
        self.assertEqual(version, expected_version)

    def test_w_split_version_no_version(self):
        expected_id = '85e57f79-02b3-47d2-8eed-c1bbb1e1d5c2'
        ident_hash = expected_id

        with self.assertRaises(IdentHashMissingVersion) as cm:
            self.call_target(ident_hash, True)

        exc = cm.exception
        self.assertEqual(exc.id, expected_id)

    def test_short_id_wo_version(self):
        ident_hash = 'abcdefgh'

        with self.assertRaises(IdentHashShortId) as cm:
            self.call_target(ident_hash)

        exc = cm.exception
        self.assertEqual(exc.id, 'abcdefgh')
        self.assertEqual(exc.version, '')

    def test_short_id_w_version(self):
        ident_hash = 'abcdefgh@10'

        with self.assertRaises(IdentHashShortId) as cm:
            self.call_target(ident_hash)

        exc = cm.exception
        self.assertEqual(exc.id, 'abcdefgh')
        self.assertEqual(exc.version, '10')


class JoinIdentTestCase(unittest.TestCase):

    def call_target(self, *args, **kwargs):
        from cnxdb.ident_hash import join_ident_hash
        return join_ident_hash(*args, **kwargs)

    def test(self):
        id = '85e57f79-02b3-47d2-8eed-c1bbb1e1d5c2'
        version = ('2', '4', )
        expected = "{}@{}".format(id, '.'.join(version))
        ident_hash = self.call_target(id, version)
        self.assertEqual(expected, ident_hash)

    def test_w_UUID(self):
        id = uuid.uuid4()
        version = None
        expected = str(id)
        ident_hash = self.call_target(id, version)
        self.assertEqual(expected, ident_hash)

    def test_w_null_version(self):
        id = '85e57f79-02b3-47d2-8eed-c1bbb1e1d5c2'
        version = None
        expected = id
        ident_hash = self.call_target(id, version)
        self.assertEqual(expected, ident_hash)

    def test_w_null_str_version(self):
        id = '85e57f79-02b3-47d2-8eed-c1bbb1e1d5c2'
        version = ''
        expected = id
        ident_hash = self.call_target(id, version)
        self.assertEqual(expected, ident_hash)

    def test_w_str_version(self):
        id = '85e57f79-02b3-47d2-8eed-c1bbb1e1d5c2'
        version = '2'
        expected = "{}@{}".format(id, version)
        ident_hash = self.call_target(id, version)
        self.assertEqual(expected, ident_hash)

    def test_w_major_version(self):
        id = '85e57f79-02b3-47d2-8eed-c1bbb1e1d5c2'
        version = ('2', None, )
        expected = "{}@{}".format(id, version[0])
        ident_hash = self.call_target(id, version)
        self.assertEqual(expected, ident_hash)

    def test_w_double_null_version(self):
        id = '85e57f79-02b3-47d2-8eed-c1bbb1e1d5c2'
        version = (None, None, )
        expected = id
        ident_hash = self.call_target(id, version)
        self.assertEqual(expected, ident_hash)

    def test_w_invalid_version_sequence(self):
        id = '85e57f79-02b3-47d2-8eed-c1bbb1e1d5c2'
        version = ('1', )
        with self.assertRaises(AssertionError):
            self.call_target(id, version)

    def test_w_integer_version(self):
        id = '85e57f79-02b3-47d2-8eed-c1bbb1e1d5c2'
        version = (1, 2, )
        expected = '{}@1.2'.format(id)
        ident_hash = self.call_target(id, version)
        self.assertEqual(expected, ident_hash)


def identifiers_equal(identifier1, identifier2):
    fulluuid1 = None
    fulluuid2 = None
    base64hash1 = None
    base64hash2 = None
    shortid1 = None
    shortid2 = None

    try:
        type1 = CNXHash.validate(identifier1)
        type2 = CNXHash.validate(identifier2)
    except IdentHashSyntaxError:
        return False

    if type1 == CNXHash.FULLUUID and type2 == CNXHash.FULLUUID:
        if (isinstance(identifier1, CNXHash) or isinstance(identifier1,
                                                           uuid.UUID)):
            fulluuid1 = identifier1.__str__()
        else:
            fulluuid1 = identifier1
        if (isinstance(identifier2, CNXHash) or isinstance(fulluuid2,
                                                           uuid.UUID)):
            fulluuid2 = identifier2.__str__()
        else:
            fulluuid2 = identifier2
        return fulluuid1 == fulluuid2
    elif type1 == CNXHash.BASE64HASH and type2 == CNXHash.BASE64HASH:
        base64hash1 = identifier1
        base64hash2 = identifier2
        return base64hash1 == base64hash2
    elif type1 == CNXHash.SHORTID and type2 == CNXHash.SHORTID:
        shortid1 == identifier1
        shortid2 == identifier2
        return shortid1 == shortid2
    elif type1 == CNXHash.BASE64HASH and type2 == CNXHash.FULLUUID:
        base64hash1 = identifier1
        base64hash2 = CNXHash.uuid2base64(identifier2)
        return base64hash1 == base64hash2
    elif type1 == CNXHash.FULLUUID and type2 == CNXHash.BASE64HASH:
        base64hash1 = CNXHash.uuid2base64(identifier1)
        base64hash2 = identifier2
        return base64hash1 == base64hash2
    elif type1 == CNXHash.SHORTID and (type2 == CNXHash.BASE64HASH or
                                       type2 == CNXHash.FULLUUID):
        return False
    elif (type1 == CNXHash.BASE64HASH or
          type1 == CNXHash.FULLUUID) and type2 == CNXHash.SHORTID:
        return False
    else:
        return False


def identifiers_similar(identifier1, identifier2):
    shortid1 = None
    shortid2 = None

    try:
        type1 = CNXHash.validate(identifier1)
    except IdentHashSyntaxError:
        return False

    try:
        type2 = CNXHash.validate(identifier2)
    except IdentHashSyntaxError:
        return False

    if isinstance(identifier1, CNXHash):
        shortid1 = identifier1.get_shortid()
    elif type1 == CNXHash.FULLUUID:
        shortid1 = CNXHash.uuid2base64(identifier1)[
            :CNXHash._SHORT_HASH_LENGTH]
    elif type1 == CNXHash.BASE64HASH:
        shortid1 = identifier1[CNXHash.SHORT_HASH_LENGTH]
    elif type1 == CNXHash.SHORTID:
        shortid1 = identifier1
    else:
        return False

    if isinstance(identifier2, CNXHash):
        shortid2 = identifier2.get_shortid()
    elif type2 == CNXHash.FULLUUID:
        shortid2 = CNXHash.uuid2base64(identifier2)[
            :CNXHash._SHORT_HASH_LENGTH]
    elif type2 == CNXHash.BASE64HASH:
        shortid2 = identifier2[CNXHash.SHORT_HASH_LENGTH]
    elif type2 == CNXHash.SHORTID:
        shortid2 = identifier2
    else:
        return False

    return shortid1 == shortid2


class TestCNXHash(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._uuid = uuid.uuid4()
        cls._cnxhash = CNXHash(cls._uuid)

    def setUp(self):
        self.uuid = self._uuid
        self.cnxhash = self._cnxhash

    def test_convert_uuid(self):
        for i in range(0, 10000):
            expected_id = uuid.uuid4()
            returned_id = CNXHash.uuid2base64(expected_id)
            self.assertGreater(len(str(expected_id)), len(returned_id))
            returned_id = CNXHash.base642uuid(returned_id)
            self.assertEqual(expected_id, returned_id)

    def test_class_init(self):
        expected_uuid = self.uuid
        returned_uuid = CNXHash(expected_uuid)
        self.assertEqual(str(expected_uuid), str(returned_uuid))
        returned_uuid = CNXHash(hex=expected_uuid.hex)
        self.assertEqual(str(expected_uuid), str(returned_uuid))
        returned_uuid = CNXHash(str(expected_uuid))
        self.assertEqual(str(expected_uuid), str(returned_uuid))
        returned_uuid = CNXHash(bytes=expected_uuid.bytes)
        self.assertEqual(str(expected_uuid), str(returned_uuid))

    def test_truncated_hash(self):
        cnxhash = CNXHash(self.uuid)
        self.assertLessEqual(len(cnxhash.get_shortid()), len(str(cnxhash)))
        self.assertEqual(
            len(cnxhash.get_shortid()), CNXHash._SHORT_HASH_LENGTH)

    def test_validate(self):
        with self.assertRaises(IdentHashSyntaxError):
            self.assertFalse(CNXHash.validate(1))
        with self.assertRaises(IdentHashSyntaxError):
            self.assertFalse(CNXHash.validate([]))
        with self.assertRaises(IdentHashSyntaxError):
            self.assertFalse(CNXHash.validate('a'))
        self.assertEqual(CNXHash.validate(self.uuid), CNXHash.FULLUUID)
        self.assertEqual(CNXHash.validate(self.cnxhash), CNXHash.FULLUUID)
        self.assertEqual(
            CNXHash.validate(self.cnxhash.get_base64id()), CNXHash.BASE64HASH)
        self.assertEqual(
            CNXHash.validate(CNXHash.uuid2base64(self.uuid)),
            CNXHash.BASE64HASH)
        self.assertEqual(
            CNXHash.validate(self.cnxhash.get_shortid()), CNXHash.SHORTID)
        self.assertEqual(
            CNXHash.validate(self.cnxhash.get_shortid().decode('utf-8')),
            CNXHash.SHORTID)

    def test_error_handling(self):
        with self.assertRaises(TypeError):
            CNXHash.uuid2base64(1)
        with self.assertRaises(ValueError):
            CNXHash.uuid2base64('a')
        with self.assertRaises(TypeError):
            CNXHash.base642uuid(1)
        with self.assertRaises(ValueError):
            CNXHash.base642uuid('a')
        with self.assertRaises(IdentHashSyntaxError):
            CNXHash.validate(1)

    def test_similarity(self):
        self.assertFalse(
            identifiers_similar(self.cnxhash, uuid.uuid4()))
        self.assertFalse(
            identifiers_similar(self.cnxhash, []))
        self.assertTrue(
            identifiers_similar(self.cnxhash, self.uuid))
        self.assertTrue(
            identifiers_similar(self.cnxhash, self.cnxhash.get_shortid()))
        self.assertTrue(
            identifiers_similar(self.cnxhash.get_shortid(), self.cnxhash))
        self.assertTrue(
            identifiers_similar(self.cnxhash.get_shortid(), self.uuid))

    def test_equality(self):
        self.assertTrue(
            identifiers_equal(self.cnxhash, self.cnxhash))
        self.assertTrue(
            identifiers_equal(self.uuid, self.cnxhash))
        self.assertTrue(
            identifiers_equal(self.cnxhash, str(self.cnxhash)))
        self.assertTrue(
            identifiers_equal(str(self.cnxhash), self.cnxhash))
        self.assertFalse(
            identifiers_equal(self.cnxhash, self.cnxhash.get_shortid()))
        self.assertTrue(identifiers_equal(
            self.cnxhash.get_shortid(), self.cnxhash.get_shortid()))
        self.assertFalse(identifiers_equal(self.cnxhash, []))
        self.assertFalse(identifiers_equal(uuid.uuid4(), uuid.uuid4()))


class TestMiscellaneousFunctions:
    @pytest.mark.skipif(py3_too_old)
    def test_identifiers_equal_function(self, db_cursor):
        import inspect

        from .test_ident_hash import identifiers_equal

        db_cursor.execute("""\
CREATE OR REPLACE FUNCTION identifiers_equal (ident1 text, ident2 text)
  RETURNS BOOLEAN
AS $$
import uuid
from cnxarchive.utils import CNXHash, IdentHashSyntaxError

{}

return identifiers_equal(ident1, ident2)
$$ LANGUAGE plpythonu;

CREATE OR REPLACE FUNCTION identifiers_equal (ident1 uuid, ident2 uuid)
  RETURNS BOOLEAN
AS $$
  SELECT identifiers_equal(ident1::text, ident2::text)
$$ LANGUAGE sql;

CREATE OR REPLACE FUNCTION identifiers_equal (ident1 text, ident2 uuid)
  RETURNS BOOLEAN
AS $$
  SELECT identifiers_equal(ident1, ident2::text)
$$ LANGUAGE sql;

CREATE OR REPLACE FUNCTION identifiers_equal (ident1 uuid, ident2 text)
  RETURNS BOOLEAN
AS $$
  SELECT identifiers_equal(ident1::text, ident2)
$$ LANGUAGE sql;

CREATE OR REPLACE FUNCTION uuid2base64 (identifier uuid)
  RETURNS character(24)
AS $$
  from cnxarchive.utils import CNXHash
  return CNXHash.uuid2base64(identifier)
$$ LANGUAGE plpythonu;
""".format(inspect.getsource(identifiers_equal)))

        import uuid
        db_cursor.execute(
            "select identifiers_equal(uuid_generate_v4(),uuid_generate_v4())")
        assert db_cursor.fetchone()[0] is False

        db_cursor.execute(
            "select identifiers_equal(uuid_generate_v4(), "
            "uuid2base64(uuid_generate_v4()))")
        assert db_cursor.fetchone()[0] is False

        db_cursor.execute(
            "select identifiers_equal(uuid2base64(uuid_generate_v4()),"
            "uuid_generate_v4())")
        assert db_cursor.fetchone()[0] is False

        db_cursor.execute(
            "select identifiers_equal(uuid2base64(uuid_generate_v4()), "
            "uuid2base64(uuid_generate_v4()))")
        assert db_cursor.fetchone()[0] is False

        identifier = str(uuid.uuid4())

        db_cursor.execute(
            "select identifiers_equal('{}','{}')".format(identifier,
                                                         identifier))
        assert db_cursor.fetchone()[0] is True

        db_cursor.execute(
            "select identifiers_equal('{}'::uuid,"
            "'{}'::uuid)".format(identifier, identifier))
        assert db_cursor.fetchone()[0] is True

        db_cursor.execute(
            "select identifiers_equal('{}','{}'::uuid)".format(identifier,
                                                               identifier))
        assert db_cursor.fetchone()[0] is True

        db_cursor.execute(
            "select identifiers_equal('{}'::uuid,'{}')".format(identifier,
                                                               identifier))
        assert db_cursor.fetchone()[0] is True

        db_cursor.execute("select identifiers_equal('{}', "
                          "uuid2base64('{}'))".format(identifier, identifier))
        assert db_cursor.fetchone()[0] is True

        db_cursor.execute("select identifiers_equal('{}'::uuid, "
                          "uuid2base64('{}'))".format(identifier, identifier))
        assert db_cursor.fetchone()[0] is True

        db_cursor.execute("select identifiers_equal(uuid2base64('{}'),"
                          "'{}')".format(identifier, identifier))
        assert db_cursor.fetchone()[0] is True

        db_cursor.execute("select identifiers_equal(uuid2base64('{}'),"
                          "'{}'::uuid)".format(identifier, identifier))
        assert db_cursor.fetchone()[0] is True

        db_cursor.execute("select identifiers_equal(uuid2base64('{}'), "
                          "uuid2base64('{}'))".format(identifier, identifier))
        assert db_cursor.fetchone()[0] is True
