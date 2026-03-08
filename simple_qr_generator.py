#!/usr/bin/env python3
"""
Simple QR Code Generator for Interview Teleprompter
Creates QR codes for easy mobile access to the teleprompter interface
"""
import qrcode
import os
import socket
import webbrowser
from datetime import datetime

def get_local_ip():
    """Get local IP address"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

def create_qr_code(url, filename="teleprompter_qr.png"):
    """Create a QR code for the teleprompter URL"""
    
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    
    # Add data
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create image with green color scheme
    img = qr.make_image(fill_color=(0, 255, 136), back_color=(26, 26, 26))
    
    # Save the image
    img.save(filename, "PNG")
    print(f"✅ QR code saved as: {filename}")
    
    return filename

def create_simple_qr(url, filename="simple_teleprompter_qr.png"):
    """Create a simple black and white QR code"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"✅ Simple QR code saved as: {filename}")
    
    return filename

def main():
    print("🎯 QR Code Generator for Interview Teleprompter")
    print("=" * 50)
    
    # Get local IP
    local_ip = get_local_ip()
    port = 8080
    
    # Create URLs
    local_url = f"localhost:{port}"
    network_url = f"{local_ip}:{port}"
    
    print(f"🌐 Local URL: http://{local_url}")
    print(f"📱 Network URL: http://{network_url}")
    print("=" * 50)
    
    # Create QR codes
    print("🎨 Creating styled QR code...")
    styled_qr = create_qr_code(f"http://{network_url}", "teleprompter_qr_styled.png")
    
    print("📱 Creating simple QR code...")
    simple_qr = create_simple_qr(f"http://{network_url}", "teleprompter_qr_simple.png")
    
    print("\n🎯 QR Codes Created Successfully!")
    print("=" * 50)
    print("📱 Use these QR codes to access your teleprompter:")
    print(f"   • Styled QR: {styled_qr}")
    print(f"   • Simple QR: {simple_qr}")
    print("=" * 50)
    print("📋 Instructions:")
    print("1. Open your phone's camera app")
    print("2. Point it at the QR code")
    print("3. Tap the notification to open the teleprompter")
    print("4. Make sure your phone is on the same WiFi network")
    print("=" * 50)
    print("🔗 Direct URLs:")
    print(f"   • Local: http://{local_url}")
    print(f"   • Network: http://{network_url}")
    print("=" * 50)
    
    # Open the styled QR code
    try:
        webbrowser.open(f"file://{os.path.abspath(styled_qr)}")
        print("🖼️  QR code image opened in browser")
    except Exception as e:
        print(f"⚠️  Could not open QR code image: {e}")
    
    return styled_qr, simple_qr

if __name__ == "__main__":
    main()
