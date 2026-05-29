# =============================================
#  client_ui.py — Application Logic Entry Point
# =============================================
#  Handles: crypto pipeline, send/receive, and wiring
#  All UI widget construction lives in chat_widgets.py
#  Crypto: rsa.py (Member 1), aes.py (Member 2),
#          hybrid_system.py (Member 3), encoding.py (Member 3)

import tkinter as tk
from datetime import datetime

from theme import BG_DARK
from chat_widgets import ChatHeader, ChatArea, InputBar, DebugPanel
from hybrid_system import generate_rsa_keypair, hybrid_encrypt, hybrid_decrypt


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

        self.debug_panel.log("Generating RSA keypair (512-bit)...", "Please wait")
        self.root.update_idletasks()

        self.my_rsa_public, self.my_rsa_private = generate_rsa_keypair(bits=512)

        # --- Initial debug log ---
        self.debug_panel.log("System Initialized.", "Keys generated.")
        e, n = self.my_rsa_public
        self.debug_panel.log("RSA Public Key", f"e={e}, n={n}")

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

        self.input_bar.clear()
        time_str = self._now()
        self.chat_area.add_bubble(plaintext, time_str, is_sent=True)

        # Log raw plaintext
        self.debug_panel.log("━━━ ENCRYPTION PIPELINE ━━━", plaintext)

        # Hybrid encrypt with full debug logging
        envelope = hybrid_encrypt(
            plaintext, self.my_rsa_public,
            on_debug=self.debug_panel.log,
        )

        # Transmit over network
        self.debug_panel.log("📡 Transmitting over TCP Socket...", "[NETWORK WIRE]")

        # TODO: Actually send envelope over your Python Socket here.
        # For now, simulate receiving a reply after 1 second.
        self.root.after(1000, self.simulate_receive, envelope)

    def simulate_receive(self, incoming_envelope):
        """Simulates receiving an encrypted envelope from the network socket."""
        self.debug_panel.log("━━━ DECRYPTION PIPELINE ━━━", "Incoming message")

        try:
            # Hybrid decrypt with full debug logging
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