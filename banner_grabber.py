import socket
import ssl
import argparse

def grab_banner(target, port):
    try:
        target_clean = target.replace("https://", "").replace("http://", "").split('/')[0]
        target_ip = socket.gethostbyname(target_clean)
        
        if port == 443:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((target_ip, port), timeout=3.0) as sock:
                with context.wrap_socket(sock, server_hostname=target_clean) as ssock:
                    request = f"HEAD / HTTP/1.1\r\nHost: {target_clean}\r\nUser-Agent: BannerGrabber/1.0\r\nConnection: close\r\n\r\n"
                    ssock.sendall(request.encode())
                    return ssock.recv(2048).decode('utf-8', errors='ignore').strip()
                    
        else:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3.0)
                s.connect((target_ip, port))
                
                if port in [80, 8080]:
                    request = f"HEAD / HTTP/1.1\r\nHost: {target_clean}\r\nUser-Agent: BannerGrabber/1.0\r\nConnection: close\r\n\r\n"
                    s.sendall(request.encode())
                else:
                    s.sendall(b"\r\n")
                    
                return s.recv(2048).decode('utf-8', errors='ignore').strip()

    except socket.timeout:
        return "[-] Timeout: Server neodpověděl včas."
    except ConnectionRefusedError:
        return f"[-] Připojení odmítnuto: Port {port} je zavřený."
    except Exception as e:
        return f"[-] Chyba: {e}"

parser = argparse.ArgumentParser(description="Python Banner Grabber")
parser.add_argument("-t", "--target", required=True, help="Cílová doména nebo IP")
parser.add_argument("-p", "--port", type=int, required=True, help="Port (např. 80, 443, 22)")
args = parser.parse_args()

print("=" * 60)
print(f" Získávám banner z: {args.target} na portu {args.port}")
print("=" * 60 + "\n")

banner = grab_banner(args.target, args.port)
print(banner)
