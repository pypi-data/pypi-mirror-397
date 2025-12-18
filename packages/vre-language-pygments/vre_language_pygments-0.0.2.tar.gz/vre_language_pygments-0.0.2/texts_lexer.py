"""Pygments plugin lexer for the textS/textM languages"""
from pygments.lexers.python import PythonLexer
from pygments.token import Keyword, Text, Name, Operator

# from textx_gen_coloring.generators import _parse_grammar
# g_info = _parse_grammar('src/virtmat/language/grammar/virtmat.tx', 'texts')

types = ('String', 'Quantity', 'Bool', 'Series', 'Table', 'BoolArray',
         'StrArray', 'IntArray', 'FloatArray', 'ComplexArray')
builtins = ('print', 'view', 'vary', 'if', 'real', 'imag', 'all',
            'any', 'sum', 'range', 'map', 'filter', 'reduce', 'info', 'tag')
keywords = ('else', 'use', 'from', 'to', 'with', 'select', 'file', 'url',
            'where', 'column', 'chunks', 'step', 'lineplot', 'on', 'for')
operators = ('not', 'and', 'or', 'in')
constants = ('true', 'false', 'null', 'default')

texts_keywords = types + builtins + keywords + operators + constants


class TextSLexer(PythonLexer):
    """the texts lexer class"""
    name = 'The textS Language'
    aliases = ['texts']
    filenames = ['*.vm']
    mimetypes = ['text/x-texts']

    def get_tokens_unprocessed(self, text, stack=('root',)):
        tokens = (Keyword, Keyword.Constant, Keyword.Type, Keyword.Namespace,
                  Name.Builtin, Operator.Word)
        super_iter = super().get_tokens_unprocessed(text, stack=stack)
        for index, token, value in super_iter:
            # print(f'{value}: {token}\n')
            if token in tokens and value not in texts_keywords:
                yield index, Text, value
            elif value in keywords:
                yield index, Keyword, value
            elif value in constants:
                yield index, Keyword.Constant, value
            elif value in types:
                yield index, Keyword.Type, value
            elif value in builtins:
                yield index, Name.Builtin, value
            elif value in operators:
                yield index, Operator.Word, value
            else:
                yield index, token, value


amml_types = ('Structure', 'Calculator', 'Algorithm', 'Property', 'FixedAtoms',
              'FixedLine', 'FixedPlane', 'Species', 'Reaction')
amml_keywords = ('collinear', 'normal', 'structure', 'many_to_one', 'task',
                 'composition')


class TextMLexer(TextSLexer):
    """the textm lexer class"""
    name = 'The textM Language'
    aliases = ['textm']
    filenames = ['*.vm']
    mimetypes = ['text/x-textm']

    def get_tokens_unprocessed(self, text, stack=('root',)):
        super_iter = super().get_tokens_unprocessed(text, stack=stack)
        for index, token, value in super_iter:
            if value in amml_keywords:
                yield index, Keyword, value
            elif value in amml_types:
                yield index, Keyword.Type, value
            else:
                yield index, token, value


class VMLexer(TextMLexer):
    """the lexer to be used in VRE-Language interactive sessions"""
    name = 'The textM Language'
    aliases = ['vre-language']
    filenames = ['*.vm']
    mimetypes = ['text/x-vre-language']

    def get_tokens_unprocessed(self, text, stack=('root',)):
        super_iter = super().get_tokens_unprocessed(text, stack=stack)
        magic = False
        other = None
        for index, token, value in super_iter:
            if '%' in value:
                if other in (Text, None):
                    magic = True
                    yield index, Keyword.Pseudo, value
                    continue
                other = True
                yield index, token, value
                continue
            if token is not Text:
                other = token
            if magic:
                if token is Name:
                    yield index, Keyword.Pseudo, value
                    continue
                if token is Text:
                    magic = False
            yield index, token, value
