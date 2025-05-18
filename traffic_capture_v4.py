# -*- coding: utf-8 -*-
import csv
import threading
import time
from scapy.all import sniff, IP, TCP, UDP, ICMP, get_if_list
from datetime import datetime

# File lưu data
csv_file = 'traffic_data.csv'

# Packet counter
packet_count = 0
lock = threading.Lock()
attack_mode = False

# Tạo file CSV và ghi header
with open(csv_file, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp', 'src_ip', 'dst_ip', 'proto', 'src_port', 'dst_port', 'pkt_len', 'label'])

# Hàm theo dõi tốc độ packet mỗi giây
def monitor_traffic_rate():
    global packet_count, attack_mode
    while True:
        time.sleep(1)  # Mỗi giây kiểm tra 1 lần
        with lock:
            if packet_count > 500:
                attack_mode = True
            else:
                attack_mode = False
            packet_count = 0

# Hàm xử lý từng packet
def process_packet(packet):
    global packet_count, attack_mode
    if IP in packet:
        ip_layer = packet[IP]
        proto = ip_layer.proto
        src_ip = ip_layer.src
        dst_ip = ip_layer.dst
        pkt_len = len(packet)

        src_port = 0
        dst_port = 0

        if TCP in packet:
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
            proto_name = 'TCP'
        elif UDP in packet:
            src_port = packet[UDP].sport
            dst_port = packet[UDP].dport
            proto_name = 'UDP'
        elif ICMP in packet:
            proto_name = 'ICMP'
        else:
            proto_name = 'Other'

        # Tăng packet counter
        with lock:
            packet_count += 1

        # Gán nhãn tự động
        label = 'attack' if attack_mode else 'normal'

        # Ghi vào file CSV
        with open(csv_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                src_ip, dst_ip, proto_name, src_port, dst_port, pkt_len, label
            ])

        print(f"[+] {src_ip}:{src_port} -> {dst_ip}:{dst_port} | Proto: {proto_name} | Size: {pkt_len} bytes | Label: {label}")

# Bắt gói trên từng interface
def capture_on_interface(interface):
    print(f"🔵 Bắt gói trên interface: {interface}")
    sniff(iface=interface, prn=process_packet, store=0)

# Main
if __name__ == "__main__":
    interfaces = get_if_list()
    excluded = ['lo', 'ovs-system']  # Loại bỏ các interface không cần bắt
    target_interfaces = [iface for iface in interfaces if iface not in excluded]

    print("\n✅ Bắt gói trên các interface sau:")
    for iface in target_interfaces:
        print(f"- {iface}")

    print("\nNhấn Ctrl+C để dừng...\n")

    # Khởi động thread monitor tốc độ packet
    t_monitor = threading.Thread(target=monitor_traffic_rate)
    t_monitor.start()

    # Mỗi interface tạo 1 thread để bắt
    threads = []
    for iface in target_interfaces:
        t = threading.Thread(target=capture_on_interface, args=(iface,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

