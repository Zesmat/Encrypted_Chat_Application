# =============================================
#  client_ui.py — Application Logic Entry Point
# =============================================
#  Handles: crypto pipeline, send/receive, and wiring
#  All UI widget construction lives in chat_widgets.py
#  All crypto algorithms live in crypto.py

import tkinter as tk
from datetime import datetime

from theme import BG_DARK
from chat_widgets import ChatHeader, ChatArea, InputBar, DebugPanel
from crypto import (
    generate_rsa_keypair, generate_aes_key,
    aes_encrypt, aes_decrypt,
    rsa_encrypt, rsa_decrypt,
    wrap_aes_key, unwrap_aes_key,
)


class SecureChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Chat App")
        self.root.geometry("950x620")
        self.root.configure(bg=BG_DARK)
        self.root.minsize(600, 400)

        # --- Cryptography Setup (dummy until real implementations arrive) ---
        self.my_rsa_public, self.my_rsa_private = generate_rsa_keypair()
        self.session_aes_key = generate_aes_key()

        self.debug_visible = True
        self._build_layout()

        # --- Initial debug log ---
        self.debug_panel.log("System Initialized.", "Keys generated.")
        self.debug_panel.log(f"RSA Public Key: {self.my_rsa_public}")
        self.debug_panel.log(f"AES Session Key: {self.session_aes_key}")

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
        if self.debug_visible:
            self.debug_panel.hide()
            self.header.set_debugger_off()
            self.debug_visible = False
        else:
            self.debug_panel.show()
            self.header.set_debugger_on()
            self.debug_visible = True

    # ==========================================
    #  Messaging — Encryption → Send → Receive → Decrypt
    # ==========================================

    def send_message(self):
        plaintext = self.input_bar.get_text()
        if not plaintext:
            return

        self.input_bar.clear()
        time_str = self._now()
        self.chat_area.add_bubble(plaintext, time_str, is_sent=True)

        # Step 1: Log raw plaintext
        self.debug_panel.log("Raw Plaintext", plaintext)

        # Step 2: AES encrypt the message (Member 2)
        ciphertext = aes_encrypt(plaintext, self.session_aes_key)
        self.debug_panel.log("AES Encrypted (Ciphertext)", ciphertext)

        # Step 3: Wrap the AES key with recipient's RSA public key (Member 3)
        wrapped_key = wrap_aes_key(self.session_aes_key, self.my_rsa_public)
        self.debug_panel.log("AES Key wrapped with RSA", wrapped_key)

        # Step 4: Transmit over network
        self.debug_panel.log("Transmitting over TCP Socket...", "[NETWORK WIRE]")

        # TODO: Actually send ciphertext + wrapped_key over your Python Socket.
        # For now, simulate receiving a reply after 1 second.
        self.root.after(1000, self.simulate_receive, ciphertext, wrapped_key)

    def simulate_receive(self, incoming_ciphertext, incoming_wrapped_key):
        """Simulates receiving an encrypted message from the network socket."""
        self.debug_panel.log("Received from Network (Ciphertext)", incoming_ciphertext)
        self.debug_panel.log("Received Wrapped AES Key", incoming_wrapped_key)

        try:
            # Step 1: Unwrap the AES key with our RSA private key (Member 3)
            session_key = unwrap_aes_key(incoming_wrapped_key, self.my_rsa_private)
            self.debug_panel.log("Unwrapped AES Key with RSA", session_key)

            # Step 2: AES decrypt the ciphertext (Member 2)
            decrypted_text = aes_decrypt(incoming_ciphertext, session_key)
            self.debug_panel.log("AES Decrypted (Plaintext)", decrypted_text)

            time_str = self._now()
            self.chat_area.add_bubble(decrypted_text, time_str, is_sent=False)
        except Exception as e:
            self.debug_panel.log("Decryption Failed!", str(e))

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