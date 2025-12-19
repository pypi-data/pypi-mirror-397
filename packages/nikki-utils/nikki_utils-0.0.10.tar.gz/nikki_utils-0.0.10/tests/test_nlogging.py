import re
from nikki_utils import nlogging

def test_tsprint_outputs(capsys):
    nlogging.tsprint("hello")
    captured = capsys.readouterr()
    assert "hello" in captured.out
    assert re.search(r"\[\d{1,2}/\d{1,2}/\d{2,4} \d{1,2}:\d{2}:\d{2}\]", captured.out)

def test_tsprint_logs_to_file(tmp_path):
    # Enable logging and point LOG_FILE to a temp file
    nlogging.DO_LOGGING = True
    log_path = tmp_path / "test.log"
    nlogging.LOG_FILE = log_path

    nlogging.tsprint("filetest")

    assert log_path.exists()
    content = log_path.read_text(encoding="utf-8")
    assert "filetest" in content

    # reset
    nlogging.DO_LOGGING = False
