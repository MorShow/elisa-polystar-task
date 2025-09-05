import os
import sys
import socket
import logging
from pathlib import Path
from argparse import ArgumentParser

PROJECT_ROOT = Path(__file__).parent.absolute()
DATA_DIR = PROJECT_ROOT / 'data'

logging.basicConfig(level=logging.INFO, filename='logs/server.log')
logger = logging.getLogger('Server log')

arg_parser = ArgumentParser()
arg_parser.add_argument('-file_path', type=str, default='dracula.txt')
arg_parser.add_argument('-host', type=str, default='localhost')
arg_parser.add_argument('-port', default=5002, type=int)


class Server:
    def __init__(self, file_path: str | Path, host: str = 'localhost', port: int = 5000) -> None:
        self._file_path = file_path
        self._host = host
        self._port = port
        self._socket = None

    @property
    def file_path(self) -> str | Path:
        return self._file_path

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    def start(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self.host, self.port))
        self._socket.listen(1)
        self._socket.settimeout(1.0)

        print(f"Server listening on {self.host}:{self.port} for {self.file_path}")
        logger.info(f"Server listening on {self.host}:{self.port} for {self.file_path}")

        try:
            while True:
                try:
                    client_conn, client_addr = self._socket.accept()
                except socket.timeout:
                    continue

                print(f"Connected by {client_addr} (Server: {self.file_path})")
                logger.info(f"Connected by {client_addr} (Server: {self.file_path})")

                try:
                    with open(os.path.join(DATA_DIR, self.file_path), "r", encoding="utf-8") as f:
                        for line in f:
                            client_conn.sendall(line.encode("utf-8"))

                    print(f"File sent successfully (Server: {self.file_path})")
                    logger.info(f"File sent successfully (Server: {self.file_path})")
                except (ConnectionResetError, ConnectionAbortedError) as e:
                    print(f"Connection with {client_addr} closed unexpectedly: {e} (Server: {self.file_path})")
                    logger.error(f"Connection with {client_addr} closed unexpectedly: {e} (Server: {self.file_path})")
                    raise

                self._close_client_connection(client_conn)
        except KeyboardInterrupt:
            print(f"The server for {self.file_path} is stopped")
            logger.info(f"The server for {self.file_path} is stopped")
        except Exception as e:
            print(f"An exception occurred, the server is stopped: {e}")
            logger.error(f"An exception occurred, the server is stopped: {e}")

    def _close_client_connection(self, client_conn) -> None:
        if self._socket is not None:
            client_conn.close()
            print(f"Connection closed (Server: {self.file_path})")
            logger.info(f"Connection closed (Server: {self.file_path})")

    def stop(self) -> None:
        if self._socket:
            self._socket.close()
            self._socket = None


if __name__ == "__main__":
    args = arg_parser.parse_args()
    file_path = args.file_path
    host = args.host
    port = args.port

    if not file_path.endswith(".txt") or not os.path.isfile(os.path.join(DATA_DIR, file_path)):
        print(f"File {file_path} does not exist")
        logger.error(f"File {file_path} does not exist")
        sys.exit(1)
    if host not in ["localhost", "127.0.0.1"]:
        print(f"Host {host} is not valid")
        logger.error(f"Host {host} is not valid")
        sys.exit(1)
    if port not in [5001, 5002]:
        print(f"Port {port} is not valid")
        logger.error(f"Port {port} is not valid")
        sys.exit(1)

    server = Server(file_path, host=host, port=port)
    server.start()
