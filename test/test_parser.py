import unittest

import plyj.parser as plyj
import plyj.model as model

import test_base

class ParserTest(test_base.ParserTestBase):

    def setUp(self):
        self.parser = plyj.Parser()

    def test_linecomment_with_no_newline_at_eof(self):
        m = self.parser.parse_string('''
        class Foo {}
         // line comment''')
        cls = self._assert_declaration(m, 'Foo')
        self.assertEqual(len(cls.modifiers), 0)

    def test_empty_type_declaration(self):
        m = self.parser.parse_string('''
        class Foo {
          ;
        };
        ''')
        self.assertEquals(2, len(m.type_declarations))
        self.assertEquals(1, len(m.type_declarations[0].body))

class VisitorTest(unittest.TestCase):

    def setUp(self):
        self.parser = plyj.Parser()
        self.visitor = model.Visitor()

    def test_empty_type_declaration(self):
        m = self.parser.parse_string('''
        class Foo {
          ;
        };
        ''')
        m.accept(self.visitor)

