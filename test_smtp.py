import smtplib

try:
    with smtplib.SMTP('smtp.gmail.com', 587, timeout=10) as server:
        print("Connected to server")
        server.starttls()
        print("TLS started")
        server.login('gallantbullemail@gmail.com', 'dbeggjpidxzrtojc')
        print("Login successful")
except Exception as e:
    print(f"Error: {e}")
