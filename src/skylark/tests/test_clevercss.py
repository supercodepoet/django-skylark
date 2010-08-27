from skylark.processor import clevercss

def test_webkit_properties():
    property ="""div:
    background-image: -webkit-gradient(linear, 0% 0%, 0% 100%, from(#E0E0E0), to(#C4C4C4))"""

    expected = """div {
  background-image: -webkit-gradient(linear, 0% 0%, 0% 100%, from(#E0E0E0), to(#C4C4C4));
}"""

    assert clevercss.convert(property) == expected 
