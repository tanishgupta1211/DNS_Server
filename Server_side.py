# DNS Server with Round-Robin Load Balancing

import socket
import threading
import json
from datetime import datetime

# Encoding format for network communication
ENCODER = "utf-8"

# Server IP and Port
HOST_IP = socket.gethostbyname(socket.gethostname())
HOST_PORT = 8000

# Buffer size
BUFFER_SIZE = 4096


# DNS Server Class
class DNSServer:

    def __init__(self, ip, port):
        self.server_ip = ip
        self.port = port

        # Load DNS records from JSON file
        self.records = self.load_dns_records()

        # Round-robin index for each domain
        self.rr_index = {
            domain: 0 for domain in self.records
        }

        # Create UDP socket
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        # Bind server to IP and port
        self.socket.bind(
            (self.server_ip, self.port)
        )

        print(
            f"[DNS SERVER] Running on "
            f"{self.server_ip}:{self.port}"
        )

    # Load DNS records
    def load_dns_records(self):

        try:
            with open(
                "dns_records.json",
                "r"
            ) as file:

                return json.load(file)

        except Exception as e:

            print(
                f"[ERROR] Could not load DNS records: {e}"
            )

            return {}

    # Log DNS queries
    def log_query(
        self,
        client_ip,
        domain,
        query_type,
        response
    ):

        with open(
            "dns_queries.log",
            "a"
        ) as logfile:

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            log = (
                f"[{timestamp}] "
                f"{client_ip} requested "
                f"{query_type} record for "
                f"{domain} -> {response}\n"
            )

            logfile.write(log)

    # Handle client requests
    def handle_request(self, thread_id):

        print(
            f"[Thread-{thread_id}] Started."
        )

        while True:

            try:

                # Receive request
                data, client_addr = (
                    self.socket.recvfrom(
                        BUFFER_SIZE
                    )
                )

                # Decode request
                decoded = data.decode(
                    ENCODER
                )

                # Request format:
                # domain,query_type
                domain, query_type = decoded.split(
                    ","
                )

                domain = domain.strip()
                query_type = query_type.strip().upper()

                print(
                    f"[Thread-{thread_id}] "
                    f"Received query: "
                    f"{domain} ({query_type}) "
                    f"from {client_addr}"
                )

                # Check if domain exists
                if domain in self.records:

                    # Get records for requested type
                    ips = self.records[
                        domain
                    ].get(
                        query_type,
                        []
                    )

                    # Check if records exist
                    if not ips:

                        response = (
                            f"No {query_type} "
                            f"record found for "
                            f"{domain}"
                        )

                    else:

                        # Round-Robin selection
                        index = (
                            self.rr_index[domain]
                            % len(ips)
                        )

                        response = ips[index]

                        # Move to next IP
                        self.rr_index[domain] = (
                            index + 1
                        ) % len(ips)

                else:

                    response = (
                        f"No such domain: {domain}"
                    )

                # Log query
                self.log_query(
                    client_addr[0],
                    domain,
                    query_type,
                    response
                )

                # Send response
                self.socket.sendto(
                    response.encode(
                        ENCODER
                    ),
                    client_addr
                )

            except Exception as e:

                error_msg = (
                    f"Invalid request format. "
                    f"Error: {e}"
                )

                print(
                    f"[Thread-{thread_id}] "
                    f"{error_msg}"
                )

                try:

                    self.socket.sendto(
                        error_msg.encode(
                            ENCODER
                        ),
                        client_addr
                    )

                except Exception:
                    pass


# Main function
def main():

    # Create DNS server
    dns_server = DNSServer(
        HOST_IP,
        HOST_PORT
    )

    print(
        "[DNS SERVER] Starting worker threads..."
    )

    # Create 3 worker threads
    for i in range(3):

        thread = threading.Thread(
            target=dns_server.handle_request,
            args=(i + 1,),
            daemon=True
        )

        thread.start()

    print(
        "[DNS SERVER] Server is ready "
        "to receive queries."
    )

    # Keep server running
    threading.Event().wait()


# Program entry point
if __name__ == "__main__":
    main()
