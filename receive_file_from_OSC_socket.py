import socket

def receive_file(filename, host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"Connected to {host}:{port}")

        with open(filename, 'wb') as f:
            while True:
                data = s.recv(1024)
                if not data:
                    break
                f.write(data)

        print("File received successfully")

filename = 'received_file.txt'
host = 'server_ip_address'
port = 12345  # Use the same port as the server

receive_file(filename, host, port)
