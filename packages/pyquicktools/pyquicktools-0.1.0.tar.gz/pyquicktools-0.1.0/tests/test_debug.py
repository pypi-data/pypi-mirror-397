from pyquicktools import dprint


def test_dprint_runs():
    # Should not crash
    dprint("hello", 123)
