import pytest
from sharktanklang.interpreter import compile_source, SharkSyntaxError

def test_invalid_syntax_raises_error():
    src = 'print("this is invalid")'
    with pytest.raises(SharkSyntaxError):
        compile_source(src)


def test_missing_end_raises_error():
    src = """
    shark Ashneer ->
        sab_bekaar_hai("pricing")
    """
    with pytest.raises(SharkSyntaxError):
        compile_source(src)
