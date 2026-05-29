# =============================================
#  client_ui.py — Application Logic Entry Point
# =============================================
#  Handles: crypto pipeline, send/receive, and wiring
#  All UI widget construction lives in chat_widgets.py
#  Crypto: rsa.py, aes.py, hybrid_system.py, encoding.py



import tkinter as tk
from datetime import datetime
import threading
import socket
import json

from ui.theme import BG_DARK
from ui.chat_widgets import ChatHeader, ChatArea, InputBar, DebugPanel
from crypto.hybrid_system import generate_rsa_keypair, hybrid_encrypt, hybrid_decrypt


class SecureChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Chat App")
        self.root.geometry("950x620")
        self.root.configure(bg=BG_DARK)
        self.root.minsize(600, 400)

        # --- Cryptography Setup ---
        self.debug_panel = None  # will be set in _build_layout
        self._build_layout()

        self.my_rsa_public, self.my_rsa_private = generate_rsa_keypair(bits=512)
        e, n = self.my_rsa_public
        self.debug_panel.log("🔑 [SYSTEM] RSA Keypair Generated", f"e={e}, n={n}")

        # --- Network Setup ---
        self.remote_rsa_public = None
        self.client_socket = None
        self._connect_to_server()

    # ==========================================
    #  Network Connection
    # ==========================================

    def _connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('127.0.0.1', 5555))
            self.debug_panel.log("🟢 [NETWORK] Connected to server", "127.0.0.1:5555")
            
            # Send our public key
            e, n = self.my_rsa_public
            pubkey_msg = {"type": "pubkey", "e": e, "n": n}
            self._send_socket_data(pubkey_msg)
            
            # Start background thread to listen for messages
            threading.Thread(target=self._listen_for_messages, daemon=True).start()
        except Exception as err:
            self.debug_panel.log("🔴 [NETWORK ERROR] Could not connect", str(err))

    def _send_socket_data(self, data_dict):
        if self.client_socket:
            try:
                data_str = json.dumps(data_dict) + "\n"
                self.client_socket.sendall(data_str.encode('utf-8'))
            except Exception as e:
                self.debug_panel.log("🔴 [NETWORK ERROR] Failed to send", str(e))

    def _listen_for_messages(self):
        buffer = ""
        while True:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                buffer += data.decode('utf-8')
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        msg = json.loads(line)
                        # Process msg safely in the main thread
                        self.root.after(0, self._process_incoming, msg)
            except Exception as e:
                self.root.after(0, self.debug_panel.log, "🔴 [NETWORK ERROR]", f"Connection lost: {e}")
                break
                
    def _process_incoming(self, msg):
        msg_type = msg.get("type")
        if msg_type == "pubkey":
            self.remote_rsa_public = (msg["e"], msg["n"])
            self.debug_panel.log("🔑 [SYSTEM] Received Remote Public Key", f"e={msg['e']}, n={msg['n']}")
        elif msg_type == "message":
            envelope = msg.get("envelope")
            self._handle_incoming_message(envelope)

    # ==========================================
    #  Layout Assembly
    # ==========================================

    def _build_layout(self):
        container = tk.Frame(self.root, bg=BG_DARK)
        container.pack(fill=tk.BOTH, expand=True)

        # Left: chat panel
        chat_panel = tk.Frame(container, bg=BG_DARK)
        chat_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.header = ChatHeader(chat_panel, on_toggle_debugger=self.toggle_debugger)
        self.input_bar = InputBar(chat_panel, on_send=self.send_message)
        self.chat_area = ChatArea(chat_panel)

        # Right: debug panel
        self.debug_panel = DebugPanel(container)

    # ==========================================
    #  Debugger Toggle
    # ==========================================

    def toggle_debugger(self):
        if self.debug_panel.is_visible():
            self.debug_panel.hide()
            self.header.set_debugger_off()
        else:
            self.debug_panel.show()
            self.header.set_debugger_on()

    # ==========================================
    #  Messaging — Hybrid Encrypt → Send → Receive → Decrypt
    # ==========================================

    def send_message(self):
        plaintext = self.input_bar.get_text()
        if not plaintext:
            return

        if not self.remote_rsa_public:
            self.debug_panel.log("⚠️ [WARNING]", "Cannot send: No remote public key received yet.")
            return

        self.input_bar.clear()
        time_str = self._now()
        self.chat_area.add_bubble(plaintext, time_str, is_sent=True)

        # Log raw plaintext
        self.debug_panel.log("━━━ ENCRYPTION PIPELINE ━━━", plaintext)

        # Hybrid encrypt using the REMOTE public key
        envelope = hybrid_encrypt(
            plaintext, self.remote_rsa_public,
            on_debug=self.debug_panel.log,
        )

        # Transmit over network
        self.debug_panel.log("📡 Transmitting over TCP Socket...", "[NETWORK WIRE]")
        self._send_socket_data({"type": "message", "envelope": envelope})

    def _handle_incoming_message(self, incoming_envelope):
        """Decrypts and displays an incoming encrypted envelope from the network socket."""
        self.debug_panel.log("━━━ DECRYPTION PIPELINE ━━━", "Incoming message")

        try:
            # Hybrid decrypt using OUR private key
            decrypted_text = hybrid_decrypt(
                incoming_envelope, self.my_rsa_private,
                on_debug=self.debug_panel.log,
            )

            time_str = self._now()
            self.chat_area.add_bubble(decrypted_text, time_str, is_sent=False)
        except Exception as e:
            self.debug_panel.log("❌ Decryption Failed!", str(e))

    # ==========================================
    #  Helpers
    # ==========================================

    @staticmethod
    def _now():
        return datetime.now().strftime("%I:%M %p").lstrip("0").lower()


if __name__ == "__main__":
    root = tk.Tk()
    app = SecureChatApp(root)
    root.mainloop()