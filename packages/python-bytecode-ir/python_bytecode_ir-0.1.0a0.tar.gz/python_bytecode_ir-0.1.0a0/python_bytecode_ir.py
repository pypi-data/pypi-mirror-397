# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from enum import Enum
from itertools import chain


# ==== Base Classes ====
class IRInstruction(object): pass


class IRValue(object): pass


# ==== Code Stucture ====
class IRRegion(IRValue):
    def __init__(self, name, posonlyargs, args, varargs, kwonlyargs, varkeywords):
        self.name = name
        self.basic_blocks = []
        self.posonlyargs = posonlyargs
        self.args = args
        self.varargs = varargs
        self.kwonlyargs = kwonlyargs
        self.varkeywords = varkeywords


class IRBasicBlock(IRValue):
    def __init__(self):
        self.instructions = []


# ==== Atoms ====
class IRConstant(IRInstruction, IRValue):
    def __init__(self, literal_value):
        self.literal_value = literal_value


# ==== Named Variable Access ====
class IRLoad(IRInstruction, IRValue):
    def __init__(self, name):
        self.name = name


class IRStore(IRInstruction):
    def __init__(self, name, value, force_global=False):
        self.name = name
        self.value = value
        self.force_global = force_global


class IRDelete(IRInstruction):
    def __init__(self, name):
        self.name = name


# ==== Special Loads ====
class IRImport(IRInstruction, IRValue):
    def __init__(self, name, level):
        self.name = name
        self.level = level


class IRImportFrom(IRInstruction, IRValue):
    def __init__(self, module, name):
        self.module = module
        self.name = name


class IRImportStar(IRInstruction):
    def __init__(self, module):
        self.module = module


class IRLoadBuiltIn(IRInstruction, IRValue):
    def __init__(self, builtin):
        self.builtin = builtin


class IRLoadRegion(IRInstruction, IRValue):
    def __init__(self, name):
        self.name = name


# ==== Unary Expressions ====
class IRUnaryOperator(Enum):
    INVERT = '~'
    NOT = 'not'
    UNARY_ADD = '+'
    UNARY_SUB = '-'


class IRUnaryOp(IRInstruction, IRValue):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand


# ==== Binary/In-place Expressions ====
class IRBinaryOperator(Enum):
    AND = 'and'
    OR = 'or'
    ADD = '+'
    SUB = '-'
    MULT = '*'
    MAT_MULT = '@'
    DIV = '/'
    MOD = '%'
    POW = '**'
    LEFT_SHIFT = '<<'
    RIGHT_SHIFT = '>>'
    BITWISE_OR = '|'
    BITWISE_XOR = '^'
    BITWISE_AND = '&'
    FLOOR_DIV = '//'
    EQ = '=='
    NOT_EQ = '!='
    LT = '<'
    LE = '<='
    GT = '>'
    GE = '>='
    IS = 'is'
    IS_NOT = 'is not'
    IN = 'in'
    NOT_IN = 'not in'


ARGVAL_TO_IR_BINARY_OPERATORS = {
    0: IRBinaryOperator.ADD,
    1: IRBinaryOperator.BITWISE_AND,
    2: IRBinaryOperator.FLOOR_DIV,
    4: IRBinaryOperator.MAT_MULT,
    5: IRBinaryOperator.MULT,
    6: IRBinaryOperator.MOD,
    7: IRBinaryOperator.BITWISE_OR,
    8: IRBinaryOperator.POW,
    10: IRBinaryOperator.SUB,
    11: IRBinaryOperator.DIV,
    12: IRBinaryOperator.BITWISE_XOR,
    '==': IRBinaryOperator.EQ,
    '!=': IRBinaryOperator.NOT_EQ,
    '<': IRBinaryOperator.LT,
    '>': IRBinaryOperator.GT,
    '>=': IRBinaryOperator.GE,
    '<=': IRBinaryOperator.LE,
}

ARGVAL_TO_IR_INPLACE_BINARY_OPERATORS = {
    13: IRBinaryOperator.ADD,
    15: IRBinaryOperator.FLOOR_DIV,
    18: IRBinaryOperator.MULT,
    23: IRBinaryOperator.SUB,
    24: IRBinaryOperator.DIV,
}


class IRBinaryOp(IRInstruction, IRValue):
    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs


class IRInPlaceBinaryOp(IRInstruction):
    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs


# ==== Collection Literals ====
class IRBuildList(IRInstruction, IRValue):
    def __init__(self, values):
        self.values = values


class IRBuildTuple(IRInstruction, IRValue):
    def __init__(self, values):
        self.values = values


class IRBuildSet(IRInstruction, IRValue):
    def __init__(self, values, frozen=False):
        self.values = values
        self.frozen = frozen


class IRBuildMap(IRInstruction, IRValue):
    def __init__(self, keys, values):
        self.keys = keys
        self.values = values


# ==== Subscriptions ====
class IRBuildSlice(IRInstruction, IRValue):
    def __init__(self, start, stop, step):
        self.start = start
        self.stop = stop
        self.step = step


class IRLoadSubscr(IRInstruction, IRValue):
    def __init__(self, key, container):
        self.key = key
        self.container = container


class IRStoreSubscr(IRInstruction):
    def __init__(self, key, container, value):
        self.key = key
        self.container = container
        self.value = value


class IRDeleteSubscr(IRInstruction):
    def __init__(self, key, container):
        self.key = key
        self.container = container


# ==== Attribute Accesses ====
class IRLoadAttr(IRInstruction, IRValue):
    def __init__(self, value, attribute):
        self.value = value
        self.attribute = attribute


class IRLoadSuperAttr(IRInstruction, IRValue):
    def __init__(self, cls_value, self_value, attribute):
        self.cls_value = cls_value
        self.self_value = self_value
        self.attribute = attribute


class IRStoreAttr(IRInstruction):
    def __init__(self, obj, attribute, value):
        self.obj = obj
        self.attribute = attribute
        self.value = value


class IRDeleteAttr(IRInstruction):
    def __init__(self, obj, attribute):
        self.obj = obj
        self.attribute = attribute


# ==== Unpacking ====
class IRUnpackSequence(IRInstruction, IRValue):
    def __init__(self, sequence, size):
        self.sequence = sequence
        self.size = size


class IRUnpackEx(IRInstruction, IRValue):
    def __init__(self, sequence, leading, trailing):
        self.sequence = sequence
        self.leading = leading
        self.trailing = trailing


# ==== F-string Related ====
class IRFormatString(IRInstruction, IRValue):
    def __init__(self, value, fmt_spec):
        self.value = value
        self.fmt_spec = fmt_spec


class IRConcatenateStrings(IRInstruction, IRValue):
    def __init__(self, strings):
        self.strings = strings


# ==== Function Definitions and Calls ====
class IRMakeFunction(IRInstruction, IRValue):
    def __init__(
            self,
            loaded_region,
            parameter_default_values,
            keyword_only_parameter_default_values,
            free_variable_cells,
            annotations,
    ):
        self.loaded_region = loaded_region
        self.parameter_default_values = parameter_default_values
        self.keyword_only_parameter_default_values = keyword_only_parameter_default_values
        self.free_variable_cells = free_variable_cells
        self.annotations = annotations


class IRCall(IRInstruction, IRValue):
    def __init__(self, callee, arguments, keywords):
        self.callee = callee
        self.arguments = arguments
        self.keywords = keywords


class IRCallFunctionEx(IRInstruction, IRValue):
    def __init__(self, callee, args, kwargs):
        self.callee = callee
        self.args = args
        self.kwargs = kwargs


# ==== Iterators ====
class IRGetIter(IRInstruction, IRValue):
    def __init__(self, value):
        self.value = value


# ==== Basic Block Terminators ====
class IRForIter(IRInstruction, IRValue):
    def __init__(self, iterator, target):
        self.iterator = iterator
        self.target = target


class IRYield(IRInstruction, IRValue):
    def __init__(self, value):
        self.value = value


class IRBranch(IRInstruction):
    def __init__(self, condition, if_true):
        self.condition = condition
        self.if_true = if_true


class IRJump(IRInstruction):
    def __init__(self, target):
        self.target = target


class IRReturn(IRInstruction):
    def __init__(self, value):
        self.value = value


class IRRaise(IRInstruction):
    def __init__(self, exception_instance_or_type):
        self.exception_instance_or_type = exception_instance_or_type


# ==== Exception Stack Manipulation ====
class IRGetException(IRInstruction, IRValue): pass


class IRSetException(IRInstruction):
    def __init__(self, exception):
        self.exception = exception


# ==== Other ====
class IRSetupAnnotations(IRInstruction): pass


# ==== Utilities ====
def dumps_lines(region_names_to_regions):
    for region_name, region in region_names_to_regions.items():
        yield (
            'Region name=%r posonlyargs=%r args=%r varargs=%r kwonlyargs=%r varkeywords=%r:' % (
                region_name,
                region.posonlyargs,
                region.args,
                region.varargs,
                region.kwonlyargs,
                region.varkeywords
            )
        )

        values_to_indices = {}

        def get_index(value):
            if value not in values_to_indices:
                values_to_indices[value] = len(values_to_indices)
            return values_to_indices[value]

        for basic_block in region.basic_blocks:
            yield 'Basic block $%d:' % (get_index(basic_block),)

            for instruction in basic_block.instructions:
                if isinstance(instruction, IRValue):
                    index = get_index(instruction)

                    if isinstance(instruction, IRConstant):
                        yield '$%d = constant %r' % (index, instruction.literal_value)
                    elif isinstance(instruction, IRLoad):
                        yield '$%d = load %r' % (index, instruction.name)
                    elif isinstance(instruction, IRLoadRegion):
                        yield '$%d = load_region %r' % (index, instruction.name)
                    elif isinstance(instruction, IRMakeFunction):
                        yield (
                            '$%d = make_function $%d $%d $%d $%d %s' % (
                                index,
                                get_index(instruction.loaded_region),
                                get_index(instruction.parameter_default_values),
                                get_index(instruction.keyword_only_parameter_default_values),
                                get_index(instruction.free_variable_cells),
                                ' '.join(
                                    '%s=$%d' % (parameter, get_index(annotation))
                                    for parameter, annotation in instruction.annotations.items()
                                ),

                            )
                        )
                    elif isinstance(instruction, IRImport):
                        yield '$%d = import %r %d' % (index, instruction.name, instruction.level)
                    elif isinstance(instruction, IRImportFrom):
                        yield '$%d = import_from $%d %r' % (index, get_index(instruction.module), instruction.name)
                    elif isinstance(instruction, IRLoadAttr):
                        yield '$%d = load_attr $%d %r' % (index, get_index(instruction.value), instruction.attribute)
                    elif isinstance(instruction, IRLoadSuperAttr):
                        yield (
                            '$%d = load_super_attr $%d $%d %r' % (
                                index,
                                get_index(instruction.cls_value),
                                get_index(instruction.self_value),
                                instruction.attribute
                            )
                        )
                    elif isinstance(instruction, IRLoadBuiltIn):
                        yield '$%d = load_builtin %r' % (index, instruction.builtin.__name__)
                    elif isinstance(instruction, IRUnaryOp):
                        yield (
                            '$%d = %s $%d' % (
                                index,
                                instruction.op.value,
                                get_index(instruction.operand)
                            )
                        )
                    elif isinstance(instruction, IRBinaryOp):
                        yield (
                            '$%d = $%d %s $%d' % (
                                index,
                                get_index(instruction.lhs),
                                instruction.op.value,
                                get_index(instruction.rhs)
                            )
                        )
                    elif isinstance(instruction, IRLoadSubscr):
                        yield '$%d = $%d[$%d]' % (index, get_index(instruction.container), get_index(instruction.key))
                    elif isinstance(instruction, IRUnpackSequence):
                        yield (
                            '$%d = unpack_sequence $%d %d' % (
                                index,
                                get_index(instruction.sequence),
                                instruction.size
                            )
                        )
                    elif isinstance(instruction, IRUnpackEx):
                        yield (
                            '$%d = unpack_ex $%d %d %d' % (
                                index,
                                get_index(instruction.sequence),
                                instruction.leading,
                                instruction.trailing
                            )
                        )
                    elif isinstance(instruction, IRBuildList):
                        yield (
                            '$%d = build_list %s' % (
                                index,
                                ' '.join(
                                    '$%d' % (get_index(value),)
                                    for value in instruction.values
                                )
                            )
                        )
                    elif isinstance(instruction, IRBuildTuple):
                        yield (
                            '$%d = build_tuple %s' % (
                                index,
                                ' '.join(
                                    '$%d' % (get_index(value),)
                                    for value in instruction.values
                                )
                            )
                        )
                    elif isinstance(instruction, IRBuildSet):
                        yield (
                            '$%d = build_set %s frozen=%r' % (
                                index,
                                ' '.join(
                                    '$%d' % (get_index(value),) for value in instruction.values
                                ),
                                instruction.frozen
                            )
                        )
                    elif isinstance(instruction, IRBuildSlice):
                        yield (
                            '$%d = build_slice $%d $%d $%d' % (
                                index,
                                get_index(instruction.start),
                                get_index(instruction.stop),
                                get_index(instruction.step)
                            )
                        )
                    elif isinstance(instruction, IRCall):
                        yield (
                            '$%d = call $%d %s' % (
                                index,
                                get_index(instruction.callee),
                                ' '.join(
                                    chain(
                                        ('$%d' % (get_index(value),) for value in instruction.arguments),
                                        (
                                            '%s=$%d' % (keyword_name, get_index(keyword))
                                            for keyword_name, keyword in instruction.keywords.items()
                                        ),
                                    )
                                )
                            )
                        )
                    elif isinstance(instruction, IRCallFunctionEx):
                        yield (
                            '$%d = call_function_ex $%d $%d $%d' % (
                                index,
                                get_index(instruction.callee),
                                get_index(instruction.args),
                                get_index(instruction.kwargs),
                            )
                        )
                    elif isinstance(instruction, IRGetIter):
                        yield '$%d = get_iter $%d' % (index, get_index(instruction.value))
                    elif isinstance(instruction, IRForIter):
                        yield (
                            '$%d = for_iter $%d $%d' % (
                                index,
                                get_index(instruction.iterator),
                                get_index(instruction.target)
                            )
                        )
                    elif isinstance(instruction, IRFormatString):
                        yield (
                            '$%d = format_string $%d $%d' % (
                                index,
                                get_index(instruction.value),
                                get_index(instruction.fmt_spec)
                            )
                        )
                    elif isinstance(instruction, IRConcatenateStrings):
                        yield (
                            '$%d = concatenate_strings %s' % (
                                index,
                                ' '.join(
                                    '$%d' % (get_index(string),)
                                    for string in instruction.strings
                                )
                            )
                        )
                    elif isinstance(instruction, IRYield):
                        yield '$%d = yield $%d' % (index, get_index(instruction.value))
                    elif isinstance(instruction, IRBuildMap):
                        yield (
                            '$%d = build_map %s' % (
                                index,
                                ' '.join(
                                    '$%d:$%d' % (get_index(key), get_index(value))
                                    for key, value in zip(instruction.keys, instruction.values)
                                )
                            )
                        )
                    else:
                        raise NotImplementedError(instruction)
                else:
                    if isinstance(instruction, IRInPlaceBinaryOp):
                        yield (
                            '$%d %s= $%d' % (
                                get_index(instruction.lhs),
                                instruction.op.value,
                                get_index(instruction.rhs)
                            )
                        )
                    elif isinstance(instruction, IRStore):
                        yield (
                            'store $%d %r force_global=%r' % (
                                get_index(instruction.value),
                                instruction.name,
                                instruction.force_global
                            )
                        )
                    elif isinstance(instruction, IRStoreSubscr):
                        yield (
                            '$%d[$%d] = $%d' % (
                                get_index(instruction.container),
                                get_index(instruction.key),
                                get_index(instruction.value)
                            )
                        )
                    elif isinstance(instruction, IRDeleteSubscr):
                        yield 'del $%d[$%d]' % (get_index(instruction.container), get_index(instruction.key))
                    elif isinstance(instruction, IRStoreAttr):
                        yield (
                            'store_attr $%d %r $%d' % (
                                get_index(instruction.obj),
                                instruction.attribute,
                                get_index(instruction.value)
                            )
                        )
                    elif isinstance(instruction, IRDelete):
                        yield 'del %r' % (instruction.name,)
                    elif isinstance(instruction, IRBranch):
                        yield 'branch $%d $%d' % (get_index(instruction.condition), get_index(instruction.if_true))
                    elif isinstance(instruction, IRJump):
                        yield 'jump $%d' % (get_index(instruction.target),)
                    elif isinstance(instruction, IRReturn):
                        yield 'return $%d' % (get_index(instruction.value),)
                    elif isinstance(instruction, IRRaise):
                        yield 'raise $%d' % (get_index(instruction.exception_instance_or_type),)
                    elif isinstance(instruction, IRImportStar):
                        yield 'import_star $%d' % (get_index(instruction.module),)
                    elif isinstance(instruction, IRDeleteAttr):
                        yield 'delete_attr $%d %r' % (get_index(instruction.obj), instruction.attribute)
                    elif isinstance(instruction, IRSetupAnnotations):
                        yield 'setup_annotations'
                    else:
                        raise NotImplementedError(instruction)

            yield ''

        yield ''


def dumps(region_names_to_regions):
    return '\n'.join(dumps_lines(region_names_to_regions))
