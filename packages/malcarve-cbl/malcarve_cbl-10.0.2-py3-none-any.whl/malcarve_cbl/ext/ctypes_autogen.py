"""Ctypes python interop code autogenerator.

this is a quick and dirty code generator that works with the C code I have written.
it isn't really meant to work in the general case; there are far too many ways to write C
to support all of them.
"""

import os
import re
from enum import IntEnum
from keyword import iskeyword, issoftkeyword
from sys import argv

import black


class ParamType(IntEnum):
    """Markup on C function parameter."""

    IN: int = 0
    OUT: int = 1
    LIST_OUT: int = 2
    BYTES_OUT: int = 3


param_type_list: list[str] = []
for param_type_index in range(len(ParamType)):
    param_type_list.append(ParamType(param_type_index).name)


class Param:
    """C function parameter."""

    paramtype: ParamType
    datatype: str
    pointer_count: int
    name: str


class Struct:
    """C struct."""

    name: str
    members: list[Param]


class Function:
    """C function."""

    name: str
    params: list[Param]
    return_type: str
    return_pointer_count: int


def read_structs(c_content: bytes) -> list[Struct]:
    """Read C structs into list."""
    structs: list[Struct] = []

    name = r"[^{};\s]+"
    struct_pattern: str = rf"typedef struct ({name}) {{ ((?: {name} {name};)+) }} ({name});"
    struct_pattern = struct_pattern.replace(r" ", r"\s+")
    for match in re.finditer(struct_pattern, c_content):
        if match.group(1) != match.group(3):
            continue
        struct: Struct = Struct()
        struct.name = match.group(1)
        struct.members = []
        members_str = match.group(2)

        name = r"[^*;\s]+"
        struct_member_pattern: str = rf" ({name}) (\**) ({name});"
        struct_member_pattern = struct_member_pattern.replace(r" ", r"\s*")

        for match in re.finditer(struct_member_pattern, members_str):
            member: Param = Param()
            member.datatype = match.group(1)
            member.pointer_count = len(match.group(2))
            member.name = match.group(3)
            struct.members.append(member)
        structs.append(struct)
    return structs


def read_functions(c_content: bytes) -> list[Function]:
    """Read C functions into list."""
    functions: list[Function] = []

    name = r"[^\(\){},*\s]+"
    function_pattern: str = rf"PY_CALL ({name})(\**) ({name})\(((?:\P {name}\** {name}, )+\P {name}\** {name})\) {{"
    function_pattern = function_pattern.replace(r" ", r"\s+")

    param_type_pattern: str = ""
    for param_type in ParamType:
        if len(param_type_pattern) > 0:
            param_type_pattern += "|"
        param_type_pattern += f"PY_{param_type.name}"
    function_pattern = function_pattern.replace(r"\P", rf"(?:{param_type_pattern})")

    for match in re.finditer(function_pattern, c_content):
        function: Function = Function()
        function.return_type = match.group(1)
        function.return_pointer_count = len(match.group(2))
        function.name = match.group(3)
        function.params = []
        params_str = match.group(4)

        name = r"[^,*\s]+"
        param_pattern = rf"({name}) ({name})(\**) ({name})"
        param_pattern = param_pattern.replace(r" ", r"\s+")

        for match in re.finditer(param_pattern, params_str):
            param: Param = Param()

            param.paramtype = param_type_list.index(match.group(1).strip("PY_"))
            param.datatype = match.group(2)
            param.pointer_count = len(match.group(3))
            param.name = match.group(4)
            function.params.append(param)
        functions.append(function)
    return functions


def wrap_in_function(var_name: str, func_name: str, wrap_count: int) -> str:
    """Pass variable as parameter to function wrap_count times."""
    for _ in range(wrap_count):
        var_name = f"{func_name}({var_name})"
    return var_name


def type_c_to_py(
    type: str, pointer_count: int, type_translations: dict[str, tuple[str, type]], ctype_equiv: bool
) -> str:
    """Convert C type to Python type."""
    if type == "void" and pointer_count > 0:
        type = "c_void_p"
        pointer_count -= 1
    translated_type: str
    if type in type_translations:
        if ctype_equiv:
            translated_type = type_translations[type][0]
        else:
            translated_type = type_translations[type][1]
    else:
        translated_type = type
    translated_type = wrap_in_function(translated_type, "POINTER", pointer_count)
    return translated_type


def var_c_to_py(
    var: str,
    type: str,
    pointer_count: int,
    type_translations: dict[str, tuple[str, type]],
) -> str:
    """Convert C variable to Python variable."""
    if type == "void" and pointer_count > 0:
        type = "c_void_p"
        pointer_count -= 1
    translated_type: str
    if type in type_translations:
        translated_type = type_translations[type][0]
    else:
        translated_type = type
    new_var: str = f"{translated_type}({var})"
    new_var = wrap_in_function(new_var, "pointer", pointer_count)
    return new_var


def generate(c_path: str, so_path: str, py_path: str):
    """Generate C-Python interop file."""
    type_translations: dict[str, tuple[str, type]] = {
        "u8": ("c_uint8", "int"),
        "u32": ("c_uint32", "int"),
        "u64": ("c_uint64", "int"),
        "s64": ("c_int64", "int"),
        "b8": ("c_bool", "bool"),
        "int": ("c_int32", "int"),
        "void": ("None", "None"),
    }

    c_content: bytes = b""
    with open(c_path, "r") as c_file:
        c_content = c_file.read()
    dest_path = os.path.relpath(so_path, os.path.dirname(py_path))
    file_content = f"""##########################################
# DO NOT EDIT - THIS FILE IS AUTOGENERATED
##########################################

import os
from ctypes import (
    CDLL,
    POINTER,
    Structure,
    c_bool,
    c_int8,
    c_int16,
    c_int32,
    c_int64,
    c_uint8,
    c_uint16,
    c_uint32,
    c_uint64,
    c_void_p,
    cast,
    cdll,
    create_string_buffer,
    pointer,
    sizeof,
    string_at,
)

c_lib: CDLL = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "{dest_path}"))

"""

    # check if we need to convert the type to a corresponding python type
    for type_c, types_py in type_translations.items():
        # for some reason, __builtins__ can be a dict or a module
        if (
            not iskeyword(type_c)
            and not issoftkeyword(type_c)
            and not (
                (isinstance(__builtins__, dict) and type_c in list(__builtins__)) or (type_c in dir(__builtins__))
            )
        ):
            file_content += f"{type_c} = {types_py[0]}\n"
    file_content += "\n"

    structs: list[Struct] = read_structs(c_content)
    for struct in structs:
        file_content += f"class {struct.name}(Structure):\n    _fields_ = [\n"
        for member in struct.members:
            member_type = type_c_to_py(member.datatype, member.pointer_count, type_translations, True)
            file_content += f'        ("{member.name}", {member_type}),\n'
        file_content += "    ]\n"
        for member in struct.members:
            if member.pointer_count == 0:
                python_type: str
                if member.datatype in type_translations:
                    python_type = type_translations[member.datatype][1]
                else:
                    python_type = member.datatype
                file_content += f"    {member.name}: {python_type}\n"
        file_content += "\n"

    functions: list[Function] = read_functions(c_content)
    for function in functions:
        file_content += f"c_{function.name} = c_lib.{function.name}\n"
        file_content += f"c_{function.name}.argtypes = [\n"
        for param in function.params:
            param_type = type_c_to_py(param.datatype, param.pointer_count, type_translations, True)
            file_content += f"    {param_type}, #{param.name}\n"
        file_content += "]\n"

        file_content += f"c_{function.name}.restype = "
        return_type = type_c_to_py(function.return_type, function.return_pointer_count, type_translations, True)
        file_content += f"{return_type}\n\n"

        file_content += f"def {function.name}(\n"
        out_types: list[str] = []
        out_names: list[str] = []
        for param in function.params:
            if param.paramtype == ParamType.IN:
                python_type: str = ""
                if param.pointer_count == 0:
                    if param.datatype in type_translations:
                        python_type = type_translations[param.datatype][1]
                    else:
                        # when in doubt, its an int.
                        python_type = "int"
                else:
                    python_type = "bytes"
                file_content += f"    {param.name}: {python_type},\n"
            elif param.paramtype == ParamType.OUT:
                # NOTE: being lazy here and only handling int
                out_types.append("int")
                out_names.append(param.name)
            elif param.paramtype == ParamType.LIST_OUT:
                file_content += f"    {param.name}_element_count: int,\n"
                out_types.append(
                    f"list[{type_c_to_py(param.datatype, param.pointer_count - 1, type_translations, False)}]"
                )
                out_names.append(param.name)
            elif param.paramtype == ParamType.BYTES_OUT:
                file_content += f"    {param.name}_byte_count: int,\n"
                out_types.append("bytes")
                out_names.append(param.name)

        file_content += ")"
        if len(out_types) > 0:
            file_content += " -> "
        if len(out_types) > 1:
            file_content += "tuple["

        out_type_index: int = 0
        while out_type_index < len(out_types):
            file_content += out_types[out_type_index]
            if out_type_index < len(out_types) - 1:
                file_content += ", "
            out_type_index += 1
        if len(out_types) > 1:
            file_content += "]"
        file_content += ":\n"

        if len(out_types) > 0:
            file_content += '    """Returns '
            out_names_index = 0
            while out_names_index < len(out_names):
                file_content += out_names[out_names_index]
                if out_names_index < len(out_names) - 1:
                    file_content += ", "
                out_names_index += 1
            file_content += '."""\n'

        for param in function.params:
            if param.paramtype == ParamType.OUT:
                file_content += "    {pname}_indirect: {ptr_count} = {zero}\n".format(
                    pname=param.name,
                    ptr_count=type_c_to_py(param.datatype, param.pointer_count, type_translations, True),
                    zero=var_c_to_py("0", param.datatype, param.pointer_count, type_translations),
                )
            elif param.paramtype == ParamType.LIST_OUT:
                file_content += "    {pname}_buffer: {ptrCount} = cast(create_string_buffer({pname}_element_count * sizeof({ptrCountMinusOne})), {ptrCount})\n".format(  # noqa E501
                    pname=param.name,
                    ptrCount=type_c_to_py(param.datatype, param.pointer_count, type_translations, True),
                    ptrCountMinusOne=type_c_to_py(param.datatype, param.pointer_count - 1, type_translations, True),
                )
            elif param.paramtype == ParamType.BYTES_OUT:
                file_content += "    {pname}_buffer: {ptrCount} = cast(create_string_buffer({pname}_byte_count * sizeof({ptrCountMinusOne})), {ptrCount})\n".format(  # noqa E501
                    pname=param.name,
                    ptrCount=type_c_to_py(param.datatype, param.pointer_count, type_translations, True),
                    ptrCountMinusOne=type_c_to_py(param.datatype, param.pointer_count - 1, type_translations, True),
                )

        file_content += f"\n    c_{function.name}(\n"
        for param in function.params:
            var: str = param.name
            if param.paramtype == ParamType.OUT:
                file_content += f"        {var}_indirect,\n"
            elif param.paramtype == ParamType.LIST_OUT or param.paramtype == ParamType.BYTES_OUT:
                file_content += f"        {var}_buffer,\n"
            elif param.paramtype == ParamType.IN:
                if param.pointer_count == 0:
                    translated_type: str
                    if param.datatype in type_translations:
                        translated_type = type_translations[param.datatype][0]
                    else:
                        translated_type = param.datatype
                    file_content += f"        {translated_type}({param.name}),\n"
                else:
                    temp_val = type_c_to_py(param.datatype, param.pointer_count, type_translations, True)
                    file_content += f"        cast({var}, {temp_val}),\n"
        file_content += "    )\n\n"

        for param in function.params:
            if param.paramtype == ParamType.OUT:
                file_content += f"    {param.name}: int = {param.name}_indirect.contents.value\n"
            elif param.paramtype == ParamType.LIST_OUT:
                temp_val = type_c_to_py(param.datatype, param.pointer_count - 1, type_translations, False)
                file_content += (
                    f"    {param.name}: list[{temp_val}]"
                    f" = [{param.name}_buffer[i] for i in range({param.name}_element_count)]\n"
                )
            elif param.paramtype == ParamType.BYTES_OUT:
                file_content += f"    {param.name}: bytes = string_at({param.name}_buffer, {param.name}_byte_count)\n"

        file_content += "    return"

        out_names_index = 0
        while out_names_index < len(out_names):
            file_content += f" {out_names[out_names_index]}"
            if out_names_index < len(out_names) - 1:
                file_content += ","
            out_names_index += 1

        file_content += "\n\n"

    # format with black so that any linting is hopefully passed successfully.
    file_content = black.format_str(
        file_content, mode=black.Mode(target_versions=set([black.mode.TargetVersion.PY312]), line_length=119)
    )

    # write to file
    with open(py_path, "w") as py_file:
        py_file.write(file_content)


if __name__ == "__main__":
    c_path: str = None
    so_path: str = None
    py_path: str = None

    arg_index: int = 1
    path_index: int = 0
    while arg_index < len(argv):
        if path_index == 0:
            c_path = os.path.abspath(argv[arg_index])
            path_index += 1
        elif path_index == 1:
            so_path = os.path.abspath(argv[arg_index])
            path_index += 1
        elif path_index == 2:
            py_path = os.path.abspath(argv[arg_index])
            path_index += 1
        else:
            raise Exception("Too many parameters.")
            pass
        arg_index += 1

    if c_path and so_path and py_path:
        generate(c_path, so_path, py_path)
        print(f"generated {py_path.split('/')[-1]}")
    else:
        raise Exception("Not enough parameters.")
        pass
