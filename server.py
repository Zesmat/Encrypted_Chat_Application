import socket
import threading
import json

# ==========================================
#  Simple Relay Server
# ==========================================
#  Accepts up to 2 clients.
#  Relays messages between them using line-delimited JSON.

HOST = '127.0.0.1'
PORT = 5555

clients = []

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    try:
        while True:
            # We use a simple protocol: messages are separated by newline
            data = conn.recv(4096)
            if not data:
                break
            
            # Broadcast the received data to all other clients
            for client in clients:
                if client != conn:
                    try:
                        client.sendall(data)
                    except Exception as e:
                        print(f"[ERROR] Could not send to a client: {e}")
                        
    except Exception as e:
        print(f"[DISCONNECT] Error handling {addr}: {e}")
    finally:
        print(f"[DISCONNECT] {addr} disconnected.")
        if conn in clients:
            clients.remove(conn)
        conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow address reuse so we don't get "Address already in use" errors on restarts
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
        server.listen(2)
        print(f"[STARTING] Server is listening on {HOST}:{PORT}")
        
        while True:
            conn, addr = server.accept()
            if len(clients) >= 2:
                print(f"[REJECTED] {addr} tried to connect but server is full.")
                conn.close()
                continue
                
            clients.append(conn)
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {len(clients)}")
            
    except Exception as e:
        print(f"[ERROR] Server failed: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    main()
