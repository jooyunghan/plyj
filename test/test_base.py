import unittest

import plyj.model as model

class ParserTestBase(unittest.TestCase):
    def _assert_declaration(self, compilation_unit, name, index=0, type=model.ClassDeclaration):
        self.assertIsInstance(compilation_unit, model.CompilationUnit)
        self.assertTrue(len(compilation_unit.type_declarations) >= index + 1)

        decl = compilation_unit.type_declarations[index]
        self.assertIsInstance(decl, type)

        self.assertEqual(decl.name, name)

        return decl
