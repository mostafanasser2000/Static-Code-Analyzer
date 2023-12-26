import re
import glob
from sys import argv
import os
import ast


def get_number_spaces(line: str) -> int:
    """Get the number of spaces at the beginning of line"""
    return len(line) - len(line.lstrip())


WARNINGS = {
    'S001': 'Too long',
    'S002': 'Indentation is not a multiple of four',
    'S003': 'Unnecessary semicolon',
    'S004': 'At least two spaces required before inline comments',
    'S005': 'TODO found',
    'S006': 'More than two blank lines used before this line',
    'S007': 'Too many spaces after',
    'S008': 'should use CamelCase',
    'S009': 'should use snake_case',
    'S010': 'should be written in snake_case',
    'S011': 'should be written in snake_case',
    'S012': 'The default argument value is mutable'
}
function_name = ''
class_name = ''


class StaticCodeAnalyzer:
    
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def semicolon_error(line: str) -> bool:
        """Check if there is a semicolon(;) after statement"""
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
    def long_line_error(line: str, max_length: int = 79) -> bool:
        """Check if the number of characters in line is more than 79"""
        return len(line) > max_length
    
    @staticmethod
    def indentation_error(current_line) -> bool:
        """Check whether an indentation of line is multiple of four or not"""
        
        indent_of_current = get_number_spaces(current_line)        
        if indent_of_current == 0 or indent_of_current % 4 == 0:
            return False
        return True

    @staticmethod
    def comment_error(line) -> bool:
        """Check if comment is preceded by two spaces or not"""

        if line.find('#') != -1:
            comment_index = line.index('#')
            if comment_index >= 2 and line[comment_index - 2:comment_index] != '  ':
                return True
        return False
    
    @staticmethod
    def todo_error(line) -> bool:
        """Check if there is a todo within a comment or not"""

        line = line.lower()
        comment_matches = re.finditer(r"#.*", line, re.MULTILINE)  # extract comments form line
        todo_matches = re.finditer("todo", line)  # get all indexes of semicolons
        matched_groups = []

        for match_comment in comment_matches:
            matched_groups.append((match_comment.span()))

        if not matched_groups:
            return False
        for match_todo in todo_matches:
            start = match_todo.start()
            found_match = False
            
            # check if semicolon within comment or strings
            for start_pos, end_pos in matched_groups:
                if start_pos <= start <= end_pos:
                    found_match = True
                    break

            if found_match:
                return True
        return False

    @staticmethod
    def construct_error(line) -> bool:
        """Check if constructs like (def, class, etc.) flowed by only one space or not"""

        template = re.compile(r"\s*\b(def|class)\b \w+")
        # check if line contain function definition or class definition
        if re.search(r"\bdef\b", line) or re.search(r"\bclass\b", line):
            if template.match(line):
                return False
            return True
        return False

    @staticmethod
    def class_error(line) -> bool:
        """Check if class name written in CamelCase or not"""

        # Template to match class in Camel Case ^([A-Z][a-z0-9]+)+(\((([A-Z][a-z0-9]+)+(, )*)*\))?$
        template = re.compile(r"([A-Z][a-z0-9]+)+")
        if re.search(r"\bclass\b", line):
            tokens = re.findall(r"[A-Z-a-z0-9_]+\w+", line)
            
            for i, token in enumerate(tokens):
                if i == 0:  # catch case when token is class
                    continue
                if template.match(token) is None:
                    global class_name
                    class_name = token
                    return True
            return False
        
    @staticmethod
    def function_error(line) -> bool:
        """Check if function name written in snake_case or not"""

        # ^[_a-z0-9]+\((([_a-z0-9]+(: \w+)?)(, )*){0,}\)$ for whole function definition
        template = re.compile(r'^[_a-z0-9]+$')
        if re.search(r"\bdef\b", line):
            tokens = re.findall(r"[A-Z-a-z0-9_]+\w+", line)
            
            for i, token in enumerate(tokens):
                if token == "def":  # catch case when token is class
                    if i+1 < len(tokens) and template.match(tokens[i+1]) is None:
                        global function_name
                        function_name = token
                        return True
                    return False
        return False
    
    @staticmethod
    def get_construct_name(line):
        if re.search(r"\bdef\b\s+", line):
            return "def"
        return "class"
    
    @staticmethod
    def extra_errors(file_path):
        """python source file to be chacked using abstract syntax tree module (ast)"""
        
        extra = ""
        f_name = open(file_path, 'r')
        code = f_name.read()
        f_name.close()
        
        tree = ast.parse(code)
        snake_case_regex = re.compile(r'^[_a-z0-9]+$')  # regular expression to test snake case

        argument_names = []  # hold the arguments nodes of AST
        default_values = []  # hold the defaults nodes of AST
        assignment_nodes = []  # hold Assign nodes of AST

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                argument_names.append(node.args.args)
                default_values.append(node.args.defaults)
                assignment_nodes.append(node.body)

        # check argument names
        for args in argument_names:
            for arg in args:
                arg_name = arg.arg
                line = arg.lineno
                if snake_case_regex.match(arg_name) is None:
                    extra += f"Line {line}: S010 Argument name '{arg_name}' {WARNINGS['S010']}\n"
                    # print(f"{source}: Line {line}: S010 Argument name '{arg_name}' {WARNINGS['S010']}")
        
        # check default values expression
        for node in default_values:
            for sub_node in node:
                if isinstance(sub_node, ast.List) or isinstance(sub_node, ast.Set) or isinstance(sub_node, ast.Dict):
                    extra += f"Line {sub_node.lineno}: S012 {WARNINGS['S012']}\n"
                    # print(f"{source}: Line {sub_node.lineno}: S012 {WARNINGS['S012']}")
                    break
                
        # check Assignment expression
        for node in assignment_nodes:
            for sub_node in node:
                if isinstance(sub_node, ast.Assign):
                    variable_name = sub_node.targets[0].id if isinstance(sub_node.targets[0], ast.Name) else sub_node.targets[0].attr
                    line = sub_node.lineno
                    if snake_case_regex.match(variable_name) is None:
                        extra += f"Line {line}: S011  Variable '{variable_name}' {WARNINGS['S011']}"
                        # print(f"{source}: Line {line}: S011  Variable '{variable_name}' {WARNINGS['S011']}")
        return extra

    def check_file(self, file_path):
        """Check file for some PEP8 errors"""
        
        final_result = ""
        with open(file_path, 'r') as file:
            i = 1
            previous_line = ''
            blank_lines = 0
            result  = ""
            
            for current_line in file:
                curren_line_result = ""
                current_line = current_line.rstrip()  # remove trailing spaces and \n
                if self.long_line_error(current_line):
                    curren_line_result += f'Line {i}: {WARNINGS["S001"]}\n'

                if self.indentation_error(current_line):
                    curren_line_result += f'Line {i}: {WARNINGS["S002"]}\n'

                if self.semicolon_error(current_line):
                    curren_line_result += f'Line {i}: {WARNINGS["S003"]}\n'

                if self.comment_error(current_line):
                    curren_line_result += f'Line {i}: {WARNINGS["S004"]}\n'

                if self.todo_error(current_line):
                    curren_line_result += f'Line {i}: {WARNINGS["S005"]}\n'

                if current_line:  # current line is not empty
                    if blank_lines > 2:
                        curren_line_result += f'Line {i}: {WARNINGS["S006"]}\n'
                        
                    blank_lines = 0
                if not current_line:  # if the current line is a blank
                    blank_lines += 1
                    i += 1
                    continue

                if self.construct_error(current_line):
                    curren_line_result += f"Line {i}: {WARNINGS['S007']} {self.get_construct_name(current_line)}\n"

                if self.class_error(current_line):
                    curren_line_result += f"Line {i}: Class name '{class_name}' {WARNINGS['S008']}\n"

                if self.function_error(current_line):
                    curren_line_result += f"Line {i}: Function name '{function_name}' {WARNINGS['S009']}\n"
                    
                i += 1
                previous_line = current_line
                if curren_line_result:
                    result += curren_line_result + "\n"
                
             
                    
        result += self.extra_errors(file_path)
        return result


def main():
    
    if len(argv) < 2:
        print("Usage: python file.py (file|directory)")
    path_name = argv[1]
    
    code_analyzer = SataicCodeAnalayzer()
    
    if os.path.isfile(path_name):  # if the input is a single python file
        code_analyzer.check_file(path_name)
    else:
        for f_name in sorted(glob.iglob(f"{path_name}//*.py", recursive=True)):
            code_analyzer.check_file(f_name)

if __name__ == "__main__":
    main()