import socket
import random
import struct

def client_program():
    # 获取服务器IP地址和端口号
    host = input("请输入服务器IP地址: ")
    port = int(input("请输入服务器端口号: "))

    client_socket = socket.socket()  
    client_socket.connect((host, port))  
    
    try:
        # 读取文件内容
        with open('ascii.txt', 'r') as file:
            full_text = file.read()
        
        # 获取最小值和最大值
        min_block_size = int(input("请输入最小值: "))
        max_block_size = int(input("请输入最大值: "))
        
        # 计算块数N
        block_count = len(full_text) // min_block_size
        if len(full_text) % min_block_size != 0:
            block_count += 1
        
        # 发送初始化报文
        init_message = struct.pack('!HI', 1, block_count)
        client_socket.send(init_message)
        
        # 接收服务器的初始化响应消息
        agree_message = client_socket.recv(2)
        agree_type = struct.unpack('!H', agree_message)[0]
        
        if agree_type != 2:
            print("服务器初始化响应错误。")
            return
        
        # 发送数据块
        start = 0
        i = 0
        
        while start < len(full_text):
            # 随机选择数据块大小
            block_size = random.randint(min_block_size, max_block_size)
            
            end = min(start + block_size, len(full_text))
            text_block = full_text[start:end]
            
            # 构建 reverseRequest 报文
            block_length = len(text_block)
            reverse_request = struct.pack('!HI', 3, block_length) + text_block.encode()
            
            # 发送 reverseRequest 报文
            client_socket.send(reverse_request)
            
            # 接收反转后的数据报文
            reverse_data_message = client_socket.recv(1024)
            message_type, data_length = struct.unpack('!HI', reverse_data_message[:6])
            reversed_data = reverse_data_message[6:].decode()
            
            i += 1
            print(f"第{i}块: 反转的文本 {reversed_data}")
            
            start += block_size
            
    finally:
        # 关闭连接
        client_socket.close()

if __name__ == '__main__':
    client_program()
