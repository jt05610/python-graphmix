from graphmix import compute


def test_compute():
    assert compute(["a", "bc", "abc"]) == "abc"
