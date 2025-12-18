from rich.console import Console

from deliberate.verbose_logger import VerboseLogger


def test_stream_output_stores_tail():
    logger = VerboseLogger(Console(record=True), enabled=True, show_stdout=True)
    logger.stream_output("agent-a", b"hello\nworld\n")
    assert "world" in list(logger._stdout_tail["agent-a"])


def test_stream_output_ignored_when_disabled():
    logger = VerboseLogger(Console(record=True), enabled=False, show_stdout=True)
    logger.stream_output("agent-a", b"hello\n")
    assert "agent-a" not in logger._stdout_tail
