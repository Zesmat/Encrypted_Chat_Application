# Encrypted Chat Application

A pure-Python secure chat application with End-to-End Encryption (E2E) using a custom hybrid cryptographic system.

## Compilation Instructions
This project is written in Python and is interpreted directly. No explicit compilation step is required. Ensure you have Python 3 installed.

## Run Instructions
To start the chat application, you need to run one relay server and two clients:

1. **Start the Relay Server**:
   Open a terminal in the project directory and run:
   ```bash
   python server.py
   ```
   The server will start listening on `127.0.0.1:5555`.

2. **Start the Clients**:
   Open two separate terminals and in each run:
   ```bash
   python client_ui.py
   ```
   This will launch two chat interfaces. They will automatically connect to the server and exchange RSA public keys. Once the exchange is complete, you can start sending secure messages.

## Dependencies
The application mostly relies on the Python Standard Library (`socket`, `threading`, `json`, `tkinter`, `base64`, `datetime`, `os`). 

However, it uses the following non-crypto utility package for image processing (generating thumbnails for received images):
- **Pillow** (`PIL`)

To install the dependency, run:
```bash
pip install Pillow
```

## Example Inputs / Outputs

### 1. Sending a Text Message
- **Input (Client A)**: Types `"Hello, secure world!"` in the input bar and clicks Send.
- **Processing**: The client structures the payload as `{"is_media": False, "text": "Hello, secure world!"}`, encrypts it using the remote client's (Client B's) RSA public key, and transmits it.
- **Output (Network Wire)**: 
  ```json
  {"type": "message", "envelope": "<encrypted_payload>"}
  ```
- **Output (Client B)**: Receives the network packet, decrypts it using its own RSA private key, and renders `"Hello, secure world!"` as a received bubble in the chat UI.

### 2. Sending a Media File
- **Input (Client A)**: Selects an image (`screenshot.png`) via the Attach button.
- **Processing**: The client reads the file, encodes it to base64, packages it into a JSON envelope:
  ```json
  {
      "is_media": true, 
      "media_type": "image", 
      "filename": "screenshot.png", 
      "file_size": "1.2 MB", 
      "data_b64": "<base64_string>"
  }
  ```
  It then encrypts this entire JSON structure and sends it.
- **Output (Client B)**: Receives, decrypts, and renders a media bubble with a thumbnail and a button to open the file. The file is saved in the `./received_media` directory.