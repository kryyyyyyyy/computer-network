import socket
import struct
import threading

def reverse_text(text):
    return text[::-1]

def handle_client(conn, address):
    print("连接来自: " + str(address))
    
    # 接收客户端发送的初始化消息
    init_message = conn.recv(6)
    message_type, block_count = struct.unpack('!HI', init_message)
    
    if message_type == 1:
        # 发送agree消息
        agree_message = struct.pack('!H', 2)
        conn.send(agree_message)
    
    
    for _ in range(block_count):
        # 接收客户端发送的数据
        data = conn.recv(1024)
        if not data:
            # 如果没有数据，关闭连接
            break
            
        # 解析reverseRequest报文
        reverse_request_type, block_length = struct.unpack('!HI', data[:6])
        text_block = data[6:].decode()  # 将字节流转换为字符串
        
        if reverse_request_type != 3:
            print("错误的报文类型。")
            break
        
        if len(text_block) != block_length:
            print("数据块长度不匹配。")
            break
        
        print("收到数据块: " + text_block)
        
        # 反转文本
        reversed_data = reverse_text(text_block)
        print("反转后数据块: " + reversed_data)
        
        # 构建并发送反转后的数据报文
        reverse_data_message = struct.pack('!HI', 4, len(reversed_data)) + reversed_data.encode()
        conn.send(reverse_data_message)
    
    conn.close()

def server_program():
    # 设置本地服务器端口
    host = '127.0.0.1'
    port = 12345
    
    server_socket = socket.socket()  
    server_socket.bind((host, port))  

    server_socket.listen(5)
    print("服务器已启动，等待连接...")
    
    running = True  # 控制服务器循环的标志
    
    while running:
        conn, address = server_socket.accept()  
        # 为每个连接创建一个新线程
        client_thread = threading.Thread(target=handle_client, args=(conn, address))
        client_thread.start()

        # 在循环中添加一个输入监听，允许用户终止连接
        stop_command = input("输入 'stop' 以终止连接并结束服务器: ")
        if stop_command.strip().lower() == 'stop':
            print("终止连接并结束服务器.")
            running = False  # 设置标志为 False，退出循环
            conn.close()  # 关闭当前连接
    
    # 关闭所有连接
    server_socket.close()  # 关闭服务器套接字，结束服务器进程

if __name__ == '__main__':
    server_program()
