import re
import glob
from sys import argv
import os
import ast
from typing import List

WARNINGS = {
    'S001': 'Too long',
    'S002': 'Indentation is not a multiple of four',
    'S003': 'Unnecessary semicolon',
    'S004': 'At least two spaces required before inline comments',
    'S005': 'TODO found',
    'S006': 'More than two blank lines used before this line',
    'S007': 'Too many spaces after keyword',
    'S008': 'should use CamelCase',
    'S009': 'should use snake_case',
    'S010': 'does not follow snake_case convention',
    'S011': 'does not follow snake_case convention',
    'S012': 'The default argument value is mutable'
}
function_name = ''
class_name = ''


def get_number_spaces(line: str) -> int:
    """Get the number of spaces at the beginning of line"""
    return len(line) - len(line.lstrip())


class StaticCodeAnalyzer:

    def __init__(self) -> None:
        pass

    @staticmethod
    def semicolon_warning(line: str) -> bool:
        """Check if there is a semicolon(;) after a statement"""
        comment_matches = re.finditer(r"#.*|['\"](.*?)['\"]", line, re.MULTILINE)  # extract comments form line
        semicolon_matches = re.finditer(";", line)  # get all indexes of semicolons
        matched_groups = [match.span() for match in comment_matches]

        # check if semicolon within comment or strings
        for match_semicolon in semicolon_matches:
            start = match_semicolon.start()
            if not any(start_pos <= start <= end_pos for start_pos, end_pos in matched_groups):
                return True
        return False

    @staticmethod
    def long_line_warning(line: str, max_length: int = 79) -> bool:
        """Check if the number of characters in line is more than 79"""
        return len(line) > max_length

    @staticmethod
    def indentation_error(current_line: str) -> bool:
        """Check whether an indentation of line is multiple of four or not"""
        indent_of_current = get_number_spaces(current_line)
        return indent_of_current != 0 and indent_of_current % 4 != 0

    @staticmethod
    def comment_warning(line: str) -> bool:
        """Check if comment is preceded by two spaces or not"""
        comment_index = line.find('#')
        return comment_index != -1 and (comment_index < 2 or line[comment_index - 2:comment_index] != '  ')

    @staticmethod
    def todo_warning(line: str) -> bool:
        """Check if there is a todo within a comment or not"""
        line = line.lower()
        comment_matches = re.finditer(r"#.*", line, re.MULTILINE)
        comment_matched_groups = [match.span() for match in comment_matches]

        if not comment_matched_groups:
            return False

        return any("todo" in line[start:end] for start, end in comment_matched_groups)

    @staticmethod
    def constructor_warning(line: str) -> bool:
        """Check if constructs like (def, class, etc.) flowed by only one space or not"""
        if re.search(r"\b(def|class)\b", line):
            return not re.match(r"\s*\b(def|class)\b \w+", line)
        return False

    @staticmethod
    def class_naming_warning(line: str) -> bool:
        """
        Check if class name written in CamelCase or not
        """
        class_keyword = re.search(r"\bclass\b", line)
        if class_keyword:
            tokens: List[str] = re.findall(r"[A-Z-a-z0-9_]+\w*", line)

            for i in range(1, len(tokens)):
                if not (tokens[i].istitle() and tokens[i].isidentifier()):
                    global class_name
                    class_name = tokens[i]
                    return True
            return False

    @staticmethod
    def function_naming_warning(line: str) -> bool:
        """
        Check if function name lower case or not
        """
        function_keyword = re.search(r"\bdef\b", line)
        if function_keyword:
            tokens: List[str] = re.findall(r"[A-Z-a-z0-9_]+\w*", line)
            template = re.compile(r'^[_a-z0-9]+$')
            if template.match(tokens[1]) is None:
                global function_name
                function_name = tokens[1]
                return True
        return False

    @staticmethod
    def get_construct_name(line):
        if re.search(r"\bdef\b\s+", line):
            return "def"
        return "class"

    @staticmethod
    def extra_errors(file_path):
        """python source file to be checked using abstract syntax tree module (ast)"""
        errors = []

        with open(file_path, 'r') as f_name:
            code = f_name.read()

        tree = ast.parse(code)
        snake_case_regex = re.compile(r'^[_a-z0-9]+$')

        argument_names = [node.args.args for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        default_values = [node.args.defaults for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        assignment_nodes = [node.body for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

        # check argument names
        for args_list in argument_names:
            for arg in args_list:
                arg_name = arg.arg
                line = arg.lineno
                if snake_case_regex.match(arg_name) is None:
                    errors.append(f"Line {line}: S010 Argument name '{arg_name}' {WARNINGS['S010']}")

        for node in default_values:
            for sub_node in node:
                if isinstance(sub_node, (ast.List, ast.Set, ast.Dict)):
                    errors.append(f"Line {sub_node.lineno}: S012 {WARNINGS['S012']}\n")
                    break

        # check Assignment expression
        for node in assignment_nodes:
            for sub_node in node:
                if isinstance(sub_node, ast.Assign):
                    variable_name = sub_node.targets[0].id if isinstance(sub_node.targets[0], ast.Name) else \
                        sub_node.targets[0].attr
                    line = sub_node.lineno
                    if snake_case_regex.match(variable_name) is None:
                        errors.append(f"Line {line}: S011  Variable '{variable_name}' {WARNINGS['S011']}")
        return errors

    def check_file(self, file_path):
        """Check the file for some PEP8 errors"""

        with open(file_path, 'r') as file:
            i = 1
            blank_lines = 0
            warnings = []

            for current_line in file:
                current_line = current_line.rstrip()  # remove trailing spaces and \n
                if self.long_line_warning(current_line):
                    warnings.append(f'Line {i}: {WARNINGS["S001"]}')

                if self.indentation_error(current_line):
                    warnings.append(f'Line {i}: {WARNINGS["S002"]}')

                if self.semicolon_warning(current_line):
                    warnings.append(f'Line {i}: {WARNINGS["S003"]}')

                if self.comment_warning(current_line):
                    warnings.append(f'Line {i}: {WARNINGS["S004"]}')

                if self.todo_warning(current_line):
                    warnings.append(f'Line {i}: {WARNINGS["S005"]}')

                if current_line:  # the current line is not empty
                    if blank_lines > 2:
                        warnings.append( f'Line {i}: {WARNINGS["S006"]}')

                    blank_lines = 0
                if not current_line:
                    blank_lines += 1
                    i += 1
                    continue

                if self.constructor_warning(current_line):
                    warnings.append(f"Line {i}: {WARNINGS['S007']} {self.get_construct_name(current_line)}")

                if self.class_naming_warning(current_line):
                    warnings.append(f"Line {i}: Class name '{class_name}' {WARNINGS['S008']}")

                if self.function_naming_warning(current_line):
                    warnings.append(f"Line {i}: Function name '{function_name}' {WARNINGS['S009']}")

                i += 1

        extra_warnings = self.extra_errors(file_path)
        warnings.extend(extra_warnings)
        return warnings


def main():
    if len(argv) < 2:
        print("Usage: python file.py (file|directory)")
    path_name = argv[1]

    code_analyzer = StaticCodeAnalyzer()

    if os.path.isfile(path_name):
        result = code_analyzer.check_file(path_name)
        print(*result, sep='\n')
    else:
        for f_name in sorted(glob.iglob(f"{path_name}//*.py", recursive=True)):
            file_warnings = code_analyzer.check_file(f_name)
            for warning in file_warnings:
                print(f"{f_name}: {warning}")


if __name__ == "__main__":
    main()
