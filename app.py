from flask import Flask, render_template, request
from bakong_khqr import KHQR
import qrcode
import requests

app = Flask(__name__)
toked = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImlkIjoiYjc3Y2EyOWY5YzdlNDJhNiJ9LCJpYXQiOjE3NjAxODc4NzcsImV4cCI6MTc2Nzk2Mzg3N30.drfIywSAjTJW6SaPSuFUfXpgzS_Bj6ot0QKQa5FR3dk"
khqr = KHQR(toked)


@app.route('/')
def home():
    return render_template('index.html')


@app.post('/checkout')
def checkout():
    price = request.form.get('price')
    currency = 'USD'  # USD or KHR
    # Create an instance of KHQR with Bakong Developer Token:
    qr = khqr.create_qr(
        bank_account='choeurn_pinchai@aclb',
        merchant_name='PINCHHAI CHOEURN',
        merchant_city='PhnomPenh',
        amount=price,  # 9800 Riel
        currency=currency,
        store_label='CHAI-Shop',
        phone_number='85599774967',
        bill_number='INV-00001',
        terminal_label='Cashier-01',
        static=False  # Static or Dynamic QR code (default: False)
    )

    # qr = "00020101021229240020choeurn_pinchai@aclb520459995802KH5916PINCHHAI CHOEURN6009PhnomPenh991700131760188077535541100000000100530311662530111TRX012345670211855997749670305MShop0710Cashier-0163046BF5"
    md5 = khqr.generate_md5(qr)
    # generate qr code image

    # Create QR code instance
    qr_object = qrcode.QRCode(
        version=1,  # controls size (1 = smallest)
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,  # pixel size of each box
        border=4,  # thickness of the border
    )
    qr_object.add_data(qr)
    qr_object.make(fit=True)
    img = qr_object.make_image(fill_color="black", back_color="white")
    img.save("./static/qrcode.png")

    return render_template('payment.html', amount=price, currency=currency, md5=md5, merchant_name="PINCHHAI CHOEURN")


@app.post('/check-payment')
def check_payment():
    json_data = request.get_json()
    md5 = json_data.get('md5')
    res = requests.post(
        'https://api-bakong.nbc.gov.kh/v1/check_transaction_by_md5',
        json={
            'md5': md5
        },
        headers={
            'authorization': f'Bearer {toked}',
            'Content-Type': 'application/json'
        }
    )

    return res.json()


@app.get('/customer_thanks')
def customer_thanks():
    return render_template('customer_thanks.html')


if __name__ == '__main__':
    app.run()
