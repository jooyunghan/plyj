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

class Visitor(model.Visitor):
    def __init__(self):
        self.visitted = []
    def __getattr__(self, name):
        def f(element):
            self.visitted.append(element)
            return True
        return f

class VisitorTest(unittest.TestCase):

    def setUp(self):
        self.parser = plyj.Parser()
        self.visitor = Visitor()

    def assertVisited(self, element):
        self.assertIn(element, self.visitor.visitted)

    def test_empty_type_declaration(self):
        m = self.parser.parse_string('''
        @interface ReflectionInfo {
          public Type type() default Type.PUBLIC;;
        }
        enum EnumType {
          VALUE1, VALUE2;
          public void test() {};
        }
        interface Bar {
          void foo();;
        }
        class Foo {
          ;
          Foo() {
            this(0);
          }
          Foo(int a) {
          }

        };
        ''')
        print m.type_declarations[0]
        m.accept(self.visitor) # should not raise exception

    def test_declaration(self):
        m = self.parser.parse_string('''
        abstract class Foo {
           Foo() {
             this(0);
           }
           Foo(int a) {
           }
           int a = Bar.baz() + Bar.foo(); 
           abstract void foo();
           void bar() {
             mConext = this;
           }
           Object mContext;
           static int sVar;
           static {
             sVar = Bar.goo();
           }
        };
        ''')
        m.accept(self.visitor)
        self.assertVisited(method_invoke('Bar.baz'))
        self.assertVisited(method_invoke('Bar.foo'))
        self.assertVisited(method_invoke('Bar.goo'))

    def test_visit_block(self):
        m = self.parser.parse_string('''
        class Foo {
          void foo() {
            int a;
            {
              int a = 1;
              Bar.foo(a);
            }
          }
        }''')
        m.accept(self.visitor)
        self.assertVisited(method_invoke('Bar.foo', [model.Name('a')]))

    def test_array_init(self):
        m = self.parser.parse_string('''
        class Foo {
          Object[] a = new Object[] {
            Bar.bas(m),this
          };
        }''')
        m.accept(self.visitor)
        self.assertVisited(method_invoke('Bar.bas', [model.Name('m')]))
 
    def test_ternary(self):
        m = self.parser.parse_string('''
        class Foo {
          void foo() {
            int a = true ? Bar.bas() : Bar.foo();
          }
        }''')
        m.accept(self.visitor)
        self.assertVisited(method_invoke('Bar.bas'))
        self.assertVisited(method_invoke('Bar.foo'))

    def test_method_invoke(self):
        m = self.parser.parse_string('''
        class Foo {
          void foo() {
            bar(Bar.bas());
          }
        }''')
        m.accept(self.visitor)
        self.assertVisited(method_invoke('Bar.bas'))
        
    def test_if_then(self):
        m = self.parser.parse_string('''
        public class Test {
          void foo() {
            int a;
            if (true) {
              a = Bar.foo();
            } else {
              b = Bar.bar();
            }
          }
        }
        ''')
        m.accept(self.visitor)
        self.assertVisited(method_invoke('Bar.foo'))
        self.assertVisited(method_invoke('Bar.bar'))

    def test_instance_create(self):
        m = self.parser.parse_string('''
        import java.util.*;

        public class Test {
            ArrayList<Integer> a = new ArrayList<Integer>() {{
                  add(1);
                  add(this);
            }};
        }
        ''')
        m.accept(self.visitor)
        self.assertVisited(method_invoke('add', [model.Literal('1')]))
        self.assertVisited(method_invoke('add', ['this']))

    def test_try_catch_finallY(self):
        m = self.parser.parse_string('''
        public class Test {
          void foo() {
            try {
              Bar.foo();
            } catch (Exception e) {
              Bar.goo();
            } finally {
              Bar.hoo();
            }
          }
        }
        ''')
        m.accept(self.visitor)
        self.assertVisited(method_invoke('Bar.foo'))
        self.assertVisited(method_invoke('Bar.goo'))
        self.assertVisited(method_invoke('Bar.hoo'))

# test helper factories
def method_invoke(name, args = None):
    parts = name.split(".")
    if len(parts) == 1:
      return model.MethodInvocation(name, args)
    else:
      target, method = parts
      return model.MethodInvocation(method, args, target=model.Name(target))

if __name__ == '__main__':
    unittest.main()
