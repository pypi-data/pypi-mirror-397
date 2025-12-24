from sharktanklang.interpreter import compile_source

def test_ashneer_catchphrase():
    src = """
    sab_bekaar_hai("pricing")
    """
    py = compile_source(src)
    assert "Sab bekaar hai" in py


def test_no_argument_catchphrase():
    src = """
    for_that_reason_im_out()
    """
    py = compile_source(src)
    assert "For that reason, I am out" in py
