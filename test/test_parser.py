import unittest

import plyj.parser as plyj
import plyj.model as model

import test_base

class ParserTest(test_base.ParserTestBase):

    def setUp(self):
        self.parser = plyj.Parser()

    def test_linecomment_with_no_newline_at_eof(self):
        m = self.parser.parse_string('''class Foo {}
         // line comment''')
        cls = self._assert_declaration(m, 'Foo')
        self.assertEqual(len(cls.modifiers), 0)

