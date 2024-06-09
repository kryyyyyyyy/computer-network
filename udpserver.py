import socket
import random
import time
import struct
import threading

def handle_client(server_socket, client_address, data):
    sequence_number, ver, message_bytes = struct.unpack('!HB17s', data)
    message = message_bytes.decode('utf-8')
    print(f"Received request from {client_address} with sequence number {sequence_number}, version {ver}, and message: {message}")

    if random.random() < 0.4:  # 模拟丢包率为40%
        print("Packet dropped")
        return

    # 模拟处理时间
    time.sleep(random.uniform(0.03, 0.08))

    # 获取系统时间
    current_time = time.strftime('%H:%M:%S', time.localtime())
    response = struct.pack('!HB8s', sequence_number, ver, bytes(current_time, 'utf-8'))
    server_socket.sendto(response, client_address)

def main():
    server_ip = "127.0.0.1"  # 服务器IP
    server_port = 2428  # 服务器端口
    server_address = (server_ip, server_port)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(server_address)

    print("UDP server is listening...")

    while True:
        data, client_address = server_socket.recvfrom(1024)

        # Check if it's a special request indicating connection close
        if data == u'关闭连接':
            print("Received close connection request from client")
            # Respond with a special message indicating connection close
            server_socket.sendto(u'关闭连接', client_address)
            break

        # Create a new thread to handle the client request
        client_thread = threading.Thread(target=handle_client, args=(server_socket, client_address, data))
        client_thread.start()

    server_socket.close()

if __name__ == "__main__":
    main()

