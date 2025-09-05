import socket
import logging
import string
from typing import List
from pathlib import Path
from collections import Counter
from threading import Thread

import nltk
from nltk.corpus import stopwords

PROJECT_ROOT = Path(__file__).parent.absolute()

logging.basicConfig(level=logging.INFO, filename='logs/client.log')
logger = logging.getLogger('Client log')

nltk.download('stopwords')
STOP_WORDS = set(stopwords.words('english'))


class Client:
    def __init__(self, servers: List) -> None:
        self._servers = servers
        self._counter = Counter()
        self._threads = []

    @property
    def servers(self) -> List:
        return self._servers

    @property
    def counter(self) -> Counter:
        return self._counter

    def run(self) -> None:
        for host, port in self.servers:
            t = Thread(target=self._count_words_from_server, args=(host, port))
            t.start()
            self._threads.append(t)

        for t in self._threads:
            t.join()

        print(f"The server threads have been created")
        logger.info(f"The server threads have been created")

    def _count_words_from_server(self, host: str, port: int) -> None:
        local_counter = Counter()

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((host, port))

                f = s.makefile('r', encoding='utf-8')
                for line in f:
                    words = line.split()
                    approved_words = [word.lower().strip(string.punctuation) for word in words
                                      if word.lower().strip(string.punctuation) not in STOP_WORDS
                                      and word not in string.punctuation]
                    local_counter.update(approved_words)

            self.counter.update(local_counter)

            print(f"Thread finished, the file is processed ({host}:{port})")
            logger.info(f"Thread finished, the file is processed ({host}:{port})")
        except (ConnectionRefusedError, socket.timeout) as e:
            print(f"Could not connect to {host}:{port}: {e}")
            logger.error(f"Could not connect to {host}:{port}: {e}")


if __name__ == "__main__":
    servers = [('localhost', 5001), ('localhost', 5002)]
    client = Client(servers)
    client.run()

    top_words = client.counter.most_common(5)
    print("Top 5 words:\n" + "-" * 100)
    for word, count in top_words:
        print(f"{word}: {count}")
