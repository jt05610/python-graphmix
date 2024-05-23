import subprocess


def test_main():
    assert subprocess.check_output(["graphmix", "foo", "foobar"], text=True) == "foobar\n"
