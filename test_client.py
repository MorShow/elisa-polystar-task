from client import Client
from server import Server

import threading

import pytest


@pytest.fixture
def setup(tmp_path):
    server1 = Server('frankenstein_test.txt', host='localhost', port=5005)
    server2 = Server('dracula_test.txt', host='localhost', port=5006)

    t1 = threading.Thread(target=server1.start, daemon=True)
    t2 = threading.Thread(target=server2.start, daemon=True)

    t1.start()
    t2.start()

    yield [5005, 5006]


def test_simple(setup):
    ports = setup
    servers = [('localhost', ports[0]), ('localhost', ports[1])]

    client = Client(servers)
    client.run()

    top_words = dict(client.counter.most_common(5))

    expected = {
        "hello": 3,
        "world": 4,
        "test": 3
    }

    assert top_words == expected


def test_wrong_connection():
    client = Client([('localhost', 5999)])
    client.run()
    assert len(client.counter) == 0
