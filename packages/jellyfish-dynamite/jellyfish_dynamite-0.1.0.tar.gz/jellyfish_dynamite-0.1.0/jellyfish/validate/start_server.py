#!/usr/bin/env python3

# /jellyfish/validate/start_server.py

def start_validation_server():
    """Start the PSD analysis validation server."""

    import http.server
    import socketserver
    import webbrowser
    import os
    import sys
    import glob

    PORT = 8000

    # Change to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("🌐 Starting PSD Analysis Server...")
    print(f"📁 Serving files from: {os.getcwd()}")

    # Find all HTML files
    html_files = glob.glob("*.html")
    html_files.sort()

    if not html_files:
        print("❌ No HTML files found!")
        sys.exit(1)

    main_html = html_files[0]

    try:
        with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
            print(f"✅ Server running at http://localhost:{PORT}")
            print(f"🎵 Audio files accessible from slices/ directory")
            print(f"📊 Opening {main_html} in browser...")
            print(f"📄 Available pages: {len(html_files)} HTML files found")
            
            webbrowser.open(f'http://localhost:{PORT}/{main_html}')
            
            print("\n🔍 Instructions:")
            print("- The first validation page should open automatically")
            print("- Use navigation buttons in the HTML to move between pages")
            print(f"- Available pages: {', '.join(html_files)}")
            print("- Press Ctrl+C to stop the server")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except OSError as e:
        if "Address already in use" in str(e) or "10048" in str(e):
            print(f"\n❌ ERROR: Port {PORT} is already in use!")
            print("🔥 Another server is already running. Please kill all processes first.")
            print("\n🛠️  How to fix:")
            print("   1. Close any other command prompt/terminal windows")
            print("   2. Or run this command to kill Python processes:")
            print("      taskkill /IM python.exe /F")
            print("   3. Or find and kill the specific process:")
            print(f"      netstat -ano | findstr :{PORT}")
            print("      taskkill /PID [PID_NUMBER] /F")
            print("   4. Then try running this server again")
            print("\n📖 Alternative: Change PORT = 8001 in start_server.py")
        else:
            print(f"❌ Error starting server: {e}")

    input("\nPress Enter to exit...")

# For backward compatibility, keep the direct execution
if __name__ == "__main__":
    start_validation_server()