from sharktanklang.interpreter import compile_source

def test_basic_pitch_and_deal():
    src = """
    pitch("Hello Sharks")
    valuation(100)
    ask(10, 5)
    deal()
    """
    py = compile_source(src)

    assert "print(\"Hello Sharks\")" in py
    assert "Valuation:" in py
    assert "[DEAL]" in py
