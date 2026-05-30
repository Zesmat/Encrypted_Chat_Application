# =============================================
#  client_ui.py — Application Logic Entry Point
# =============================================
#  Handles: crypto pipeline, send/receive, and wiring
#  All UI widget construction lives in chat_widgets.py
#  Crypto: rsa.py, aes.py, hybrid_system.py, encoding.py



import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import threading
import socket
import json
import os
import io
import base64
from PIL import Image

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
        
        # --- Media Setup ---
        self.media_dir = "./received_media"
        if not os.path.exists(self.media_dir):
            os.makedirs(self.media_dir)

        self._build_layout()

        self.my_rsa_public, self.my_rsa_private = generate_rsa_keypair(bits=512)
        e, n = self.my_rsa_public
        self.debug_panel.log("[SYSTEM] RSA Keypair Generated", f"e={e}, n={n}")

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
            self.debug_panel.log("[NETWORK] Connected to server", "127.0.0.1:5555")
            
            # Send our public key
            e, n = self.my_rsa_public
            pubkey_msg = {"type": "pubkey", "e": e, "n": n}
            self._send_socket_data(pubkey_msg)
            
            # Start background thread to listen for messages
            threading.Thread(target=self._listen_for_messages, daemon=True).start()
        except Exception as err:
            self.debug_panel.log("[NETWORK ERROR] Could not connect", str(err))
            self.debug_panel.log("[NETWORK] Retrying in 3 seconds...", "")
            self.root.after(3000, self._connect_to_server)

    def _send_socket_data(self, data_dict):
        if self.client_socket:
            try:
                data_str = json.dumps(data_dict) + "\n"
                self.client_socket.sendall(data_str.encode('utf-8'))
            except Exception as e:
                self.debug_panel.log("[NETWORK ERROR] Failed to send", str(e))

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
                self.root.after(0, self.debug_panel.log, "[NETWORK ERROR]", f"Connection lost: {e}")
                break
                
    def _process_incoming(self, msg):
        msg_type = msg.get("type")
        if msg_type == "pubkey":
            self.remote_rsa_public = (msg["e"], msg["n"])
            self.debug_panel.log("[SYSTEM] Received Remote Public Key", f"e={msg['e']}, n={msg['n']}")
            
            # Reply back with our key so the sender gets it
            e, n = self.my_rsa_public
            self._send_socket_data({"type": "pubkey_reply", "e": e, "n": n})
            
        elif msg_type == "pubkey_reply":
            self.remote_rsa_public = (msg["e"], msg["n"])
            self.debug_panel.log("[SYSTEM] Received Remote Public Key (Reply)", f"e={msg['e']}, n={msg['n']}")
            
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
        self.input_bar = InputBar(
            chat_panel, 
            on_send=self.send_message, 
            on_attach=self._select_attachment, 
            on_mic=self._select_voice_note
        )
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
            self.debug_panel.log("[WARNING]", "Cannot send: No remote public key received yet.")
            return

        self.input_bar.clear()
        time_str = self._now()
        self.chat_area.add_bubble(plaintext, time_str, is_sent=True)

        # Pack text in structural JSON for standard handling
        wrapper_msg = json.dumps({"is_media": False, "text": plaintext})

        # Run encryption and transmission in a separate thread so UI stays interactive
        threading.Thread(
            target=self._encrypt_and_send_text_background,
            args=(wrapper_msg,),
            daemon=True
        ).start()

    def _encrypt_and_send_text_background(self, wrapper_msg):
        try:
            self.debug_panel.log("━━━ ENCRYPTION PIPELINE ━━━", "Preparing payload...")
            envelope = hybrid_encrypt(
                wrapper_msg, self.remote_rsa_public,
                on_debug=self._thread_safe_debug_log,
            )
            self.root.after(0, self.debug_panel.log, "[NETWORK] Transmitting over TCP Socket...", "[NETWORK WIRE]")
            self._send_socket_data({"type": "message", "envelope": envelope})
        except Exception as err:
            self.root.after(0, self.debug_panel.log, "[ERROR] Encryption/Send Failed", str(err))

    def _handle_incoming_message(self, incoming_envelope):
        """Decrypts and displays an incoming encrypted envelope from the network socket."""
        self.debug_panel.log("━━━ DECRYPTION PIPELINE ━━━", "Incoming message payload received.")
        
        # Spin up a thread to decrypt so we don't freeze the main UI loop
        threading.Thread(
            target=self._decrypt_incoming_background,
            args=(incoming_envelope,),
            daemon=True
        ).start()

    def _decrypt_incoming_background(self, incoming_envelope):
        try:
            # Hybrid decrypt using OUR private key
            decrypted_str = hybrid_decrypt(
                incoming_envelope, self.my_rsa_private,
                on_debug=self._thread_safe_debug_log,
            )
            time_str = self._now()
            
            # Pre-decode and generate thumbnail in background thread if payload is an image
            pil_img = None
            try:
                payload = json.loads(decrypted_str)
                if isinstance(payload, dict) and payload.get("is_media") and payload.get("media_type") == "image":
                    img_bytes = base64.b64decode(payload.get("data_b64"))
                    pil_img = Image.open(io.BytesIO(img_bytes))
                    pil_img.thumbnail((240, 180))
            except Exception as ex:
                self.root.after(0, self.debug_panel.log, "[PRE-LOAD FAILED]", str(ex))
            
            # Dispatch back to main UI thread to render bubble
            self.root.after(0, self._render_decrypted_incoming, decrypted_str, time_str, pil_img)
        except Exception as e:
            self.root.after(0, self.debug_panel.log, " Decryption Failed!", str(e))

    def _render_decrypted_incoming(self, decrypted_str, time_str, pil_img=None):
        try:
            # Try to parse decrypted content as structured JSON envelope
            payload = json.loads(decrypted_str)
            if isinstance(payload, dict) and payload.get("is_media"):
                media_type = payload.get("media_type")
                filename = payload.get("filename")
                file_size = payload.get("file_size")
                data_b64 = payload.get("data_b64") if "data_b64" in payload else payload.get("data_hex")
                
                self.chat_area.add_media_bubble(
                    media_type=media_type,
                    filename=filename,
                    file_size=file_size,
                    data_b64=data_b64,
                    time_str=time_str,
                    is_sent=False,
                    on_open_click=lambda: self._open_received_file(filename, data_b64),
                    pil_img=pil_img
                )
            else:
                text = payload.get("text", decrypted_str)
                self.chat_area.add_bubble(text, time_str, is_sent=False)
        except Exception:
            # Decrypted string is NOT valid JSON (backward compatibility with standard texts)
            self.chat_area.add_bubble(decrypted_str, time_str, is_sent=False)

    # ==========================================
    #  Rich Media File Selection & Sending Logic
    # ==========================================

    def _select_attachment(self):
        if not self.remote_rsa_public:
            self.debug_panel.log("[WARNING]", "Cannot attach: No remote public key received yet.")
            return

        file_path = filedialog.askopenfilename(
            title="Select File to Securely Transmit",
            filetypes=[("All Files", "*.*")]
        )
        if file_path:
            self._handle_file_selection(file_path, "file")

    def _select_voice_note(self):
        if not self.remote_rsa_public:
            self.debug_panel.log("[WARNING]", "Cannot record: No remote public key received yet.")
            return

        import ctypes
        if not hasattr(self, "recording_voice_note"):
            self.recording_voice_note = False

        if not self.recording_voice_note:
            # Start Recording
            try:
                # Open a new waveaudio recording alias
                ctypes.windll.winmm.mciSendStringW("open new type waveaudio alias recsound", None, 0, 0)
                ctypes.windll.winmm.mciSendStringW("record recsound", None, 0, 0)
                
                self.recording_voice_note = True
                self.debug_panel.log("[LIVE RECORDING]", "Voice recording started... Click Record again to stop and send.")
                
                # Update UI elements to show recording state
                self.input_bar.mic_label.config(text="REC", fg="red")
                self.input_bar.entry.delete(0, tk.END)
                self.input_bar.entry.insert(0, "[RECORDING VOICE NOTE... Click mic again to send]")
                self.input_bar.entry.config(fg="red", state="disabled")
            except Exception as e:
                self.debug_panel.log("❌ Recording Error", str(e))
                messagebox.showerror("Recording Error", f"Could not start recording: {e}")
        else:
            # Stop and Send
            try:
                temp_path = os.path.abspath("temp_voice.wav")
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass
                
                ctypes.windll.winmm.mciSendStringW("stop recsound", None, 0, 0)
                ctypes.windll.winmm.mciSendStringW(f"save recsound {temp_path}", None, 0, 0)
                ctypes.windll.winmm.mciSendStringW("close recsound", None, 0, 0)
                
                self.recording_voice_note = False
                self.debug_panel.log("[LIVE RECORDING]", "Recording stopped. Encoding and encrypting WAV payload...")
                
                # Revert UI state
                self.input_bar.mic_label.config(text="Record", fg="#8696a0") # FG_SECONDARY
                self.input_bar.entry.config(state="normal", fg="#d1d7db") # FG_INPUT
                self.input_bar.entry.delete(0, tk.END)
                self.input_bar.entry.insert(0, self.input_bar.PLACEHOLDER)
                self.input_bar.entry.config(fg="#8696a0") # FG_SECONDARY
                
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 44:
                    self._handle_file_selection(temp_path, "voice")
                else:
                    self.debug_panel.log("[WARNING]", "Voice note was empty or could not be saved.")
            except Exception as e:
                self.debug_panel.log("[ERROR] Recording Save Error", str(e))
                messagebox.showerror("Recording Save Error", f"Could not save voice recording: {e}")

    def _handle_file_selection(self, file_path, default_type):
        # 1. Validate File Size (Pure-Python E2E Cryptography Limit of 3 MB)
        try:
            file_size_bytes = os.path.getsize(file_path)
            max_size_bytes = 3 * 1024 * 1024 # 3 MB
            if file_size_bytes > max_size_bytes:
                messagebox.showwarning(
                    "File Too Large",
                    "This prototype secure chat uses pure Python E2E encryption.\n"
                    "To prevent sluggish performance, files are strictly limited to 3 MB."
                )
                return
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file details: {e}")
            return

        # Determine if it's pdf, video, image, or generic file based on extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp"]:
            media_type = "image"
        elif ext == ".pdf":
            media_type = "pdf"
        elif ext in [".mp4", ".avi", ".mkv", ".mov", ".wmv"]:
            media_type = "video"
        elif ext in [".wav", ".mp3", ".m4a", ".ogg", ".wma", ".aac"] or default_type == "voice":
            media_type = "voice"
        else:
            media_type = "file"

        # 2. Spin background thread to encrypt and transmit
        threading.Thread(
            target=self._process_and_send_file_background,
            args=(file_path, media_type, file_size_bytes),
            daemon=True
        ).start()

    def _process_and_send_file_background(self, file_path, media_type, file_size_bytes):
        filename = os.path.basename(file_path)
        
        # Format size string
        if file_size_bytes < 1024:
            file_size_str = f"{file_size_bytes} B"
        elif file_size_bytes < 1024 * 1024:
            file_size_str = f"{file_size_bytes / 1024:.1f} KB"
        else:
            file_size_str = f"{file_size_bytes / (1024 * 1024):.1f} MB"

        self.root.after(0, self.debug_panel.log, "[FILE]", f"Reading {filename}...")

        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()

            # Pre-load image and scale thumbnail on background thread
            pil_img = None
            if media_type == "image":
                try:
                    pil_img = Image.open(io.BytesIO(file_bytes))
                    pil_img.thumbnail((240, 180))
                except Exception as ex:
                    self.root.after(0, self.debug_panel.log, "[PRE-THUMBNAIL FAILED]", str(ex))

            # Encode using standard base64 for 33% smaller payload and 33% faster AES E2E encryption
            self.root.after(0, self.debug_panel.log, "[BASE64]", "Base64-encoding binary stream...")
            data_b64 = base64.b64encode(file_bytes).decode("utf-8")

            # Package into structured JSON payload
            payload_dict = {
                "is_media": True,
                "media_type": media_type,
                "filename": filename,
                "file_size": file_size_str,
                "data_b64": data_b64
            }
            payload_str = json.dumps(payload_dict)

            # Display on local screen
            time_str = self._now()
            self.root.after(0, self._render_local_media_bubble, media_type, filename, file_size_str, data_b64, time_str, pil_img)

            # Encrypt
            self.root.after(0, self.debug_panel.log, "━━━ ENCRYPTION PIPELINE ━━━", f"Encrypting file package: {filename}")
            envelope = hybrid_encrypt(
                payload_str, self.remote_rsa_public,
                on_debug=self._thread_safe_debug_log,
            )

            # Transmit
            self.root.after(0, self.debug_panel.log, " Transmitting over TCP Socket...", "[NETWORK WIRE]")
            self._send_socket_data({"type": "message", "envelope": envelope})

        except Exception as e:
            self.root.after(0, self.debug_panel.log, " [FILE ERROR]", str(e))
            self.root.after(0, lambda: messagebox.showerror("Transmission Failure", f"Failed to securely transmit file: {e}"))

    def _render_local_media_bubble(self, media_type, filename, file_size, data_b64, time_str, pil_img=None):
        self.chat_area.add_media_bubble(
            media_type=media_type,
            filename=filename,
            file_size=file_size,
            data_b64=data_b64,
            time_str=time_str,
            is_sent=True,
            on_open_click=lambda: self._open_received_file(filename, data_b64),
            pil_img=pil_img
        )

    def _thread_safe_debug_log(self, step, data=""):
        self.root.after(0, self.debug_panel.log, step, data)

    def _open_received_file(self, filename, data_b64):
        """Saves received file from custom base64 decoding and triggers OS native opening in a background thread."""
        threading.Thread(
            target=self._open_received_file_background,
            args=(filename, data_b64),
            daemon=True
        ).start()

    def _open_received_file_background(self, filename, data_b64):
        try:
            dest_path = os.path.abspath(os.path.join(self.media_dir, filename))
            
            self.root.after(0, self.debug_panel.log, "[BASE64]", f"Decoding payload bytes for {filename}...")
            file_bytes = base64.b64decode(data_b64)
            
            with open(dest_path, "wb") as f:
                f.write(file_bytes)
                
            self.root.after(0, self.debug_panel.log, "[SYSTEM] Saved Received File", dest_path)
            
            # If it's a WAV file (recorded voice note), play it natively inside the app
            ext = os.path.splitext(filename)[1].lower()
            if ext == ".wav":
                import winsound
                self.root.after(0, self.debug_panel.log, "[PLAYING VOICE NOTE]", f"Playing {filename} asynchronously...")
                # Stop any currently playing sound first
                winsound.PlaySound(None, winsound.SND_PURGE)
                # Play asynchronously in the background so GUI doesn't freeze
                winsound.PlaySound(dest_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            else:
                # Open via default system app
                os.startfile(dest_path)
                self.root.after(0, self.debug_panel.log, "[SYSTEM] Opened File Natively", filename)
        except Exception as ex:
            self.root.after(0, self.debug_panel.log, "[ERROR] File Open Failed", str(ex))
            self.root.after(0, lambda: messagebox.showerror("Error Opening File", f"Could not save or open file: {ex}"))

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