from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from http_server import HttpServer

httpserver = HttpServer()

logging.basicConfig(level=logging.INFO, 
                    format='[%(asctime)s] %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

def ProcessTheClient(connection, address):
    full_request_bytes = b''
    
    while b'\r\n\r\n' not in full_request_bytes:
        try:
            data = connection.recv(1024)
            if not data:
                break
            full_request_bytes += data
        except OSError as e:
            logging.error(f"Error saat menerima data dari {address}: {e}")
            break

    if not full_request_bytes:
        logging.warning(f"Tidak ada data yang diterima dari {address}, koneksi ditutup.")
        connection.close()
        return

    headers_part_str = full_request_bytes.split(b'\r\n\r\n', 1)[0].decode(errors='ignore')
    
    request_line = headers_part_str.split('\r\n')[0]
    logging.info(f"Menerima request dari {address}: \"{request_line}\"")

    content_length = 0
    headers = headers_part_str.split('\r\n')
    for header in headers:
        if header.lower().startswith('content-length:'):
            try:
                content_length = int(header.split(':')[1].strip())
            except (ValueError, IndexError):
                content_length = 0
            break

    body_part_bytes = full_request_bytes.split(b'\r\n\r\n', 1)[1]
    
    while len(body_part_bytes) < content_length:
        try:
            bytes_to_read = content_length - len(body_part_bytes)
            data = connection.recv(bytes_to_read)
            if not data:
                break
            body_part_bytes += data
        except OSError:
            break

    final_request_str = headers_part_str + '\r\n\r\n' + body_part_bytes.decode(errors='ignore')
    
    hasil = httpserver.proses(final_request_str)
    hasil += b"\r\n\r\n"
    
    connection.sendall(hasil)
    logging.info(f"Respons dikirim ke {address} dan koneksi ditutup.")
    connection.close()
    return


def Server():
	my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	my_socket.bind(('0.0.0.0', 8889))
	my_socket.listen(1)
 
	logging.info("Server berjalan dan mendengarkan di port 8889...")

	with ProcessPoolExecutor(max_workers=10) as executor:
		while True:
				connection, client_address = my_socket.accept()
				logging.info(f"Menerima koneksi baru dari {client_address}")
				executor.submit(ProcessTheClient, connection, client_address)

def main():
	Server()

if __name__=="__main__":
	main()