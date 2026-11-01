# DNS Client

import socket

# Encoding format
ENCODER = "utf-8"

# IP address of DNS Server
# Change this to the server computer's IP
DEST_IP = "192.168.114.64"

# DNS Server port
DEST_PORT = 8000

# Buffer size
BUFFER_SIZE = 4096


# DNS Client Class
class DNSClient:

    def __init__(
        self,
        server_ip,
        port
    ):

        self.server_ip = server_ip
        self.port = port

        # Create UDP socket
        self.client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

    # Send DNS query
    def query(
        self,
        domain,
        query_type="A"
    ):

        # Create request
        message = (
            f"{domain},{query_type}"
        )

        # Send request to DNS server
        self.client_socket.sendto(
            message.encode(ENCODER),
            (
                self.server_ip,
                self.port
            )
        )

        # Receive response
        response, _ = (
            self.client_socket.recvfrom(
                BUFFER_SIZE
            )
        )

        return response.decode(
            ENCODER
        )

    # Close client socket
    def close(self):

        self.client_socket.close()


# Main function
def main():

    # Create DNS client
    client = DNSClient(
        DEST_IP,
        DEST_PORT
    )

    print(
        "[DNS CLIENT] Started"
    )

    print(
        "Type 'exit' as domain "
        "to close the client."
    )

    while True:

        # Get domain
        domain = input(
            "\nEnter domain: "
        ).strip()

        # Exit
        if domain.lower() == "exit":

            print(
                "[DNS CLIENT] Exiting..."
            )

            break

        # Get record type
        query_type = input(
            "Enter record type "
            "(A or AAAA): "
        ).strip().upper()

        # Validate record type
        if query_type not in (
            "A",
            "AAAA"
        ):

            print(
                "[ERROR] Invalid query type."
            )

            print(
                "Please use A or AAAA."
            )

            continue

        try:

            # Send query
            response = client.query(
                domain,
                query_type
            )

            # Display response
            print(
                f"Response: {response}"
            )

        except Exception as e:

            print(
                f"[ERROR] Failed to get "
                f"response: {e}"
            )

    # Close socket
    client.close()


# Program entry point
if __name__ == "__main__":
    main()
