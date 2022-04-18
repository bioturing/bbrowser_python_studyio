from walnut.readers import EncryptedTextReader, TextReader
from walnut.FileIO import FileIO
from walnut.converters import IOJSON
import tempfile

def test_json():
    tmp = tempfile.mkstemp()[1]
    e_reader = EncryptedTextReader("abcdefb260b46892812345df8c1d96ee")
    t_reader = TextReader()
    e_json = FileIO(tmp, e_reader, IOJSON)
    t_json = FileIO(tmp, t_reader, IOJSON)
    e_json.write({"text": "hello world"})
    content = t_json.read()
    assert ("iv" in content) and ("content" in content)
    content = e_json.read()
    assert content["text"] == "hello world"