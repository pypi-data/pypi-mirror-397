from structflo.helloworld import helloworld


def test_helloworld_returns_message() -> None:
    assert helloworld() == "Hello, world!"
