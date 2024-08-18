import qrcode
import base64
from io import BytesIO


# Returns a base64 string of a QR code generated for the given string
def qrcode_img_src(qr_string):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    with BytesIO() as buffer:
        img.save(buffer)
        buffer.seek(0)
        img_bytes = buffer.read()
        base64_string = base64.b64encode(img_bytes).decode("utf-8")
    return "data:image/png;base64," + base64_string
