import os
from app import create_app, get_local_ipv4

app = create_app()

if __name__ == "__main__":
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
    local_ip = get_local_ipv4()

    print("\n" + "=" * 65)
    print("  AttendX Campus ERP (WSGI Runner) is Running!")
    print(f"  * Local Access:       http://localhost:{port} (or http://127.0.0.1:{port})")
    print(f"  * IPv4 Network Link:  http://{local_ip}:{port}")
    print("  * Access from any phone/laptop on the same Wi-Fi network!")
    print("=" * 65 + "\n")

    app.run(host=host, port=port, debug=debug)
