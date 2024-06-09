import socket
import struct
import time

def main():
    server_ip = input("请输入服务器IP: ")  # 服务器IP
    server_port = int(input("请输入服务器端口: "))  # 服务器端口
    server_address = (server_ip, server_port)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  #ipv4 udp
    client_socket.settimeout(0.1)  # 设置超时时间为100ms

    packets_sent = 0
    packets_received = 0
    rtt_list = []
    first_response_time = None  # 记录第一次响应时间
    last_response_time = None   # 记录最后一次响应时间

    for i in range(1, 13):
        sequence_number = i
        ver = 2
        message = "computer networks"
        message_bytes = bytes(message, 'utf-8')
        request = struct.pack('!HB17s', sequence_number, ver, message_bytes)  #无符号短整型占两个字节  无符号字符占一个字节
        start_time = time.time()
        client_socket.sendto(request, server_address)
        packets_sent += 1
        retries = 2
        start_retry_time = time.time()  # 记录重试开始时间

        while retries > 0:
            try:
               client_socket.settimeout(0.1)  # 设置超时时间为100ms
               data, _ = client_socket.recvfrom(1024)
               end_time = time.time()
               rtt = (end_time - start_time) * 1000
               sequence_number, ver, server_time = struct.unpack('!HB8s', data)
               rtt_list.append(rtt)
               print(f"Sequence number {sequence_number}, Version {ver}, Server time: {server_time.decode()}, RTT: {rtt:.2f} ms")
               packets_received += 1
               if first_response_time is None:  # 记录第一次响应时间
                   first_response_time = end_time
               last_response_time = end_time    # 更新最后一次响应时间
               break  # 如果成功接收到数据，则退出循环
            except socket.timeout:
               print(f"Sequence number {sequence_number}, Request timed out, retrying...")
               client_socket.sendto(request, server_address)  # 重传数据包
               retries -= 1  # 重传次数减1
               if retries > 0:
               # 如果还有重传次数，则等待剩余的超时时间
                 time.sleep(0.1)
               else:
                 print(f"Sequence number {sequence_number}, No response after retrying, giving up")

               # 注意：这里不再需要检查是否超过超时时间的逻辑，因为超时已经在recvfrom中处理了。

    # 向服务器申请关闭连接
    client_socket.sendto("关闭连接".encode('utf-8'), server_address)

    # 等待服务器回复
    try:
        data, _ = client_socket.recvfrom(1024)
        if data.decode('utf-8') == '关闭连接':
            print("Connection closed successfully")
    except socket.timeout:
        print("Timeout waiting for connection close confirmation")

    client_socket.close()

    loss_rate = (packets_sent - packets_received) / packets_sent * 100 if packets_sent > 0 else 0
    max_rtt = max(rtt_list) if rtt_list else 0
    min_rtt = min(rtt_list) if rtt_list else 0
    avg_rtt = sum(rtt_list) / len(rtt_list) if rtt_list else 0
    rtt_std_dev = (sum((rtt - avg_rtt) ** 2 for rtt in rtt_list) / len(rtt_list)) ** 0.5 if rtt_list else 0

    print("\n--- 汇总 ---")
    print(f"Total UDP packets received: {packets_received}")
    print(f"Packet loss rate: {loss_rate:.2f}%")
    print(f"Maximum RTT: {max_rtt:.2f} ms")
    print(f"Minimum RTT: {min_rtt:.2f} ms")
    print(f"Average RTT: {avg_rtt:.2f} ms")
    print(f"RTT standard deviation: {rtt_std_dev:.2f} ms")
    server_response_time = (last_response_time - first_response_time) * 1000
    print(f"Server overall response time: {server_response_time:.2f} ms")

if __name__ == "__main__":
    main()
