import socket

def send_file(filename, host, port):
    with open(filename, 'rb') as f:
        file_data = f.read()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        print(f"Server listening on {host}:{port}...")
        conn, addr = s.accept()
        print(f"Connected to {addr}")

        conn.sendall(file_data)
        print("File sent successfully")

filename = 'path/to/your/file.txt'
host = 'your_ip_address'
port = 12345  # Choose any available port

send_file(filename, host, port)
