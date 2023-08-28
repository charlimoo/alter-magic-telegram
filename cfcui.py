import subprocess
import threading
import time
import socket

def iframe_thread(port):
    while True:
        time.sleep(0.5)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        if result == 0:
            break
        sock.close()
    print("\nComfyUI finished loading, trying to launch cloudflared (if it gets stuck here cloudflared is having issues)\n")

    p = subprocess.Popen(["cloudflared", "tunnel", "--url", "http://127.0.0.1:{}".format(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in p.stderr:
        l = line.decode()
        if "trycloudflare.com " in l:
            print("This is the URL to access ComfyUI:", l[l.find("http"):], end='')

threading.Thread(target=iframe_thread, daemon=True, args=(8188,)).start()

# Run main.py from the 'comfyui' folder
subprocess.run(["python", "comfyui/main.py"])
