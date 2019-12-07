from bcolors import Color
from lexer import Template, tokenize
from lr_parser import Scanner, Parser
from parser_generator import *
from production import Production
from vzhuh_interpreter import Interpreter

NT = {'GOAL', 'PRG', 'VAR_DECS', 'VAR_DEC', 'COMPS', 'VARS', 'OPS', 'FUNC', 'ARGS', 'ASSIGN', 'EXP', 'OR_EXP',
      'AND_EXP', 'TERM', 'P_TERM', 'OPERAND'}
T = {'var', 'type', 'begin', 'end', 'true', 'false', '!', '&', '|', ':', ';', ',', '(', ')', '=', 'ident', 'str', '$'}

P = [
    Production('GOAL', 'PRG',                  lambda p: p[0]),
    Production('PRG', 'var VAR_DECS COMPS',    lambda p: ('program', ('declaration', p[1]), p[2])),
    Production('VAR_DECS', 'VAR_DEC VAR_DECS', lambda p: [p[0]] + p[1]),
    Production('VAR_DECS', 'VAR_DEC',          lambda p: [p[0]]),
    Production('VAR_DEC', 'VARS : type ;',     lambda p: (p[2], p[0])),
    Production('VARS', 'ident , VARS',         lambda p: [p[0]] + p[2]),
    Production('VARS', 'ident',                lambda p: [p[0]]),
    Production('COMPS', 'begin OPS end',       lambda p: ('operations', p[1])),
    Production('OPS', 'FUNC ; OPS',            lambda p: [p[0]] + p[2]),
    Production('OPS', 'FUNC ;',                lambda p: [p[0]]),
    Production('OPS', 'ASSIGN ; OPS',          lambda p: [p[0]] + p[2]),
    Production('OPS', 'ASSIGN ;',              lambda p: [p[0]]),
    Production('FUNC', 'ident ( ARGS )',       lambda p: ('call', p[0], p[2])),
    Production('ARGS', 'EXP , ARGS',           lambda p: [p[0]] + p[2]),
    Production('ARGS', 'EXP',                  lambda p: [p[0]]),
    Production('ASSIGN', 'ident = EXP',        lambda p: ('assign', p[0], p[2])),
    Production('EXP', 'OR_EXP',                lambda p: p[0]),
    Production('OR_EXP', 'OR_EXP | AND_EXP',   lambda p: ('or', p[0], p[2])),
    Production('OR_EXP', 'AND_EXP',            lambda p: p[0]),
    Production('AND_EXP', 'AND_EXP & TERM',    lambda p: ('and', p[0], p[2])),
    Production('AND_EXP', 'TERM',              lambda p: p[0]),
    Production('TERM', '! P_TERM',             lambda p: ('not', p[1])),
    Production('TERM', 'P_TERM',               lambda p: p[0]),
    Production('P_TERM', 'OPERAND',            lambda p: p[0]),
    Production('P_TERM', '( EXP )',            lambda p: p[1]),
    Production('OPERAND', 'ident',             lambda p: ('var', p[0])),
    Production('OPERAND', 'str',               lambda p: ('str', p[0])),
    Production('OPERAND', 'true',              lambda p: ('const', p[0])),
    Production('OPERAND', 'false',             lambda p: ('const', p[0]))
]
templates = [
    Template('var', 'var'),
    Template('type', 'logical|string'),
    Template('begin', 'begin'),
    Template('end', 'end'),
    Template('true', 'true', lambda a: True),
    Template('false', 'false', lambda a: False),
    Template('!', '\!'),
    Template('&', '\&'),
    Template('|', '\|'),
    Template(':', ':'),
    Template(';', ';'),
    Template(',', ','),
    Template('(', '\('),
    Template(')', '\)'),
    Template('=', '='),
    Template('ident', '\w+'),
    Template('str', '".*?"', lambda a: a.strip('"')),
    Template('space', ' +', lambda a: None),
    Template('newline', '\n', lambda a: None),
    Template('comment', '//.*', lambda a: None)
]


def main():
    print(*P, sep='\n', end='\n\n')

    generator = ParserGenerator(P, T, NT)
    action, goto = generator.build_tables()

    with open("source.txt") as file:
        string = ''.join(file.readlines())

    try:
        tokens = tokenize(string, templates)

        scanner = Scanner(tokens)
        parser = Parser(action, goto)
        tree = parser.parse(scanner, T, NT, SHOW_TREE)

        interpreter = Interpreter(tree)
        interpreter.run()
    except Exception as e:
        print(Color.ERROR + 'ERROR: ' + str(e) + Color.ENDC)


if __name__ == '__main__':
    main()
