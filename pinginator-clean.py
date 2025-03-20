# Description: A simple Python script to monitor a list of IP addresses and send an email alert if any of them fail to respond to ping requests.
# v1-2: Added support for reading IP addresses and names from a file that can be commented out with #. Added logging to a file and console.

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import subprocess
import logging

# Configuration
ping_interval = 10  # seconds
failure_threshold = 3
email_sender = "sender@example.email.com"
email_receivers = ["your@email.com", "someone@email.com"]
smtp_server = "172.16.227.21"
smtp_port = 587
ip_list_file = "ip_list.txt"
log_file = "pinginator.log"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', handlers=[
    logging.FileHandler(log_file),
    logging.StreamHandler()
])

# Read IP addresses and names from file
def read_ip_addresses(file_path):
    ip_addresses = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            parts = line.split()
            if len(parts) == 2:
                ip, name = parts
                ip_addresses[ip] = name
    return ip_addresses

ip_addresses = read_ip_addresses(ip_list_file)
failure_counters = {ip: 0 for ip in ip_addresses}

def send_email(ip, name):
    subject = f"Ping Failure Alert: {ip} ({name})"
    body = f"The IP address {ip} ({name}) has failed to respond to ping requests {failure_threshold} times in a row at {time.strftime('%Y-%m-%d %H:%M:%S')}."

    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = ", ".join(email_receivers)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        text = msg.as_string()
        server.sendmail(email_sender, email_receivers, text)
        server.quit()
        logging.info(f"Email sent to {', '.join(email_receivers)} for IP {ip} ({name})")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

def ping(ip):
    try:
        output = subprocess.check_output(["ping", "-c", "1", "-W", "1", ip])
        return True
    except subprocess.CalledProcessError:
        return False

def monitor_ips():
    while True:
        for ip, name in ip_addresses.items():
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            if not ping(ip):
                failure_counters[ip] += 1
                logging.info(f"Failed to ping {ip} ({name}), failure count: {failure_counters[ip]}")
                if failure_counters[ip] >= failure_threshold:
                    send_email(ip, name)
                    failure_counters[ip] = 0  # Reset counter after sending email
            else:
                failure_counters[ip] = 0  # Reset counter on successful ping
        time.sleep(ping_interval)

if __name__ == "__main__":
    monitor_ips()