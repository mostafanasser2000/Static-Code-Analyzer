import unittest
from analyzer import StaticCodeAnalyzer


class TestStaticCodeAnalyzer(unittest.TestCase):

    def test_semicolon_warning(self):
        self.assertTrue(StaticCodeAnalyzer.semicolon_warning("x = 10;"))
        self.assertFalse(StaticCodeAnalyzer.semicolon_warning("x = 10"))

    def test_lone_line_warning(self):
        self.assertTrue(StaticCodeAnalyzer.long_line_warning("x" * 80))
        self.assertFalse(StaticCodeAnalyzer.long_line_warning("x" * 79))

    def test_indentation_error(self):
        self.assertTrue(StaticCodeAnalyzer.indentation_error("    x = 10"))
        self.assertFalse(StaticCodeAnalyzer.indentation_error("x = 10"))

    def test_comment_warning(self):
        self.assertTrue(StaticCodeAnalyzer.comment_warning("x = 2 << 4 # this is equivalent to to 2 ^ (4 + 1)"))
        self.assertFalse(StaticCodeAnalyzer.comment_warning("x = 2 << 4  # this is equivalent to to 2 ^ (4 + 1)"))

    def test_todo_warning(self):
        self.assertTrue(StaticCodeAnalyzer.todo_warning("#TODO: test todo error function"))
        self.assertFalse(StaticCodeAnalyzer.todo_warning("# test to do error function"))

    def test_constructor_warning(self):
        self.assertTrue(StaticCodeAnalyzer.constructor_warning("def  foo():\n    pass\n"))
        self.assertTrue(StaticCodeAnalyzer.constructor_warning("class  A:\n    pass\n"))
        self.assertFalse(StaticCodeAnalyzer.constructor_warning("def foo():\n    pass\n"))
        self.assertFalse(StaticCodeAnalyzer.constructor_warning("class A:\n    pass\n"))
        self.assertFalse(StaticCodeAnalyzer.constructor_warning("for i in range(10):\n    print(i)"))

    def test_class_naming_warning(self):
        self.assertTrue(StaticCodeAnalyzer.class_naming_warning("class a:"))
        self.assertFalse(StaticCodeAnalyzer.class_naming_warning("class A:"))
        self.assertTrue(StaticCodeAnalyzer.class_naming_warning("class A(B, c):"))
        self.assertFalse(StaticCodeAnalyzer.class_naming_warning("class A(B, C):"))

    def test_function_naming_warning(self):
        self.assertTrue(StaticCodeAnalyzer.function_naming_warning("def Foo():\n pass\n"))
        self.assertFalse(StaticCodeAnalyzer.function_naming_warning("def foo():\n    pass\n"))


if __name__ == '__main__':
    unittest.main()
