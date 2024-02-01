from client import Client
from server import Server
from colorama import Fore, Style

if __name__ == '__main__':
    print(Fore.GREEN + "Welcome to our TCP program!")
    print(Fore.YELLOW + "Please select the mode you want to run:")
    print(Fore.BLUE + "1. Server")
    print(Fore.MAGENTA + "2. Client")

    print(Fore.RESET)
    command = input()
    print("")
    if command == "1":
        print("Please enter the port number: (default: 12345)")
        while True:
            port = input()
            if (port == ""):
                port = 12345
                break
            elif (not port.isdigit() or int(port) < 1024 or int(port) > 65535):
                print("Invalid port number! Please enter a valid port number:")
            else:
                port = int(port)
                break
        print("Port number: " + str(port) + "\n")
        print("Please enter the file path: (default: input/tes.pdf)")
        file_path = input()
        if file_path == "":
            file_path = "input/tes.pdf"
        print("File path: " + file_path + "\n")
        print("Parallel or not? (y/n)")
        command = input()
        if command == "y" or command == "Y":
            parallel = True
        else:
            parallel = False
        server = Server(parallel)
        server.start_server(port, file_path)

    elif command == "2":
        print("Please enter the client port number:")
        client_port = int(input())
        print("Client port number: " + str(client_port) + "\n")
        print("Please enter the server port number: (default: 12345")
        while True:
            server_port = input()
            if (server_port == ""):
                server_port = 12345
                break
            elif (not server_port.isdigit() or int(server_port) < 1024 or int(server_port) > 65535):
                print("Invalid port number! Please enter a valid port number:")
            else:
                server_port = int(server_port)
                break
        print("Server port number: " + str(server_port) + "\n")
        print("Please enter the file path: (default: tes.pdf)")
        file_path = input()
        if file_path == "":
            file_path = "tes.pdf"
        print("File path: " + file_path + "\n")
        file_path = "output/" + file_path
        client = Client()
        client.connect_to_server(client_port, server_port, file_path)
        connection = client.connection
        ack, addr = connection.listen_single_segment()
        client.three_way_handshake()
        client.listen_file_transfer()
    else:
        print("Invalid command!")
