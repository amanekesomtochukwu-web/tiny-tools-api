from flask import Flask, request, jsonify, send_file
import random, string
import pyshorteners
import qrcode
import io

app = Flask(__name__)

# 🏠 Home
@app.route('/')
def home():
    return {"message": "Tiny Tools API is live 🔥"}

# 🔐 Password Generator
@app.route('/generate-password')
def generate_password():
    length = int(request.args.get('length', 12))
    chars = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(chars) for _ in range(length))
    return {"password": password}

# 🔗 Real URL Shortener
@app.route('/shorten-url')
def shorten_url():
    url = request.args.get('url')
    if not url:
        return {"error": "URL required"}, 400

    try:
        s = pyshorteners.Shortener()
        short_url = s.tinyurl.short(url)
        return {"original": url, "short_url": short_url}
    except Exception as e:
        return {"error": str(e)}, 500

# 🔳 Real QR Generator
@app.route('/qr')
def generate_qr():
    text = request.args.get('text')
    if not text:
        return {"error": "Text required"}, 400

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save image to memory
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    buf.seek(0)

    return send_file(buf, mimetype='image/png', download_name='qr.png')

if __name__ == '__main__':
    app.run(debug=True)