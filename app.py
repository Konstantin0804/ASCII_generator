from flask import Flask, render_template, request
from PIL import Image
import os
import random
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DEFAULT_ASCII_CHARS = ["M", "W", "C", "S", "B", "G", "%", "+", "o", "a", "e", "s", "i", "n", "d", "f", "u", "l", "t", "y", ":", ".", "-", " "]


def fibonacci_sequence(n):
    fib = [1, 1]
    while len(fib) < n:
        fib.append(fib[-1] + fib[-2])
    return fib


def resize_image(image, new_height):
    width, height = image.size
    aspect_ratio = width / height
    font_aspect_ratio = 0.55
    new_width = int(new_height * aspect_ratio / font_aspect_ratio)
    return image.resize((new_width, new_height)), new_width


def grayscale(image):
    return image.convert("L")


def map_pixels_to_ascii(image, ascii_chars):
    if not ascii_chars:
        raise ValueError("ASCII character list is empty.")

    pixels = image.getdata()
    range_width = max(1, 256 // len(ascii_chars))

    dark_chars = ascii_chars[:5]
    fib_seq = fibonacci_sequence(5)
    fib_total = sum(fib_seq)

    result = []
    for pixel in pixels:
        char_index = min(len(ascii_chars) - 1, pixel // range_width)

        if char_index == 0:
            rand_val = random.randint(1, fib_total)
            running_sum = 0
            for i, weight in enumerate(fib_seq):
                running_sum += weight
                if rand_val <= running_sum:
                    result.append(dark_chars[i])
                    break
        else:
            result.append(ascii_chars[char_index])

    return "".join(result)


def convert_image_to_ascii(image, ascii_chars, new_height):
    image, new_width = resize_image(image, new_height)
    image = grayscale(image)
    ascii_str = map_pixels_to_ascii(image, ascii_chars)
    ascii_art = "\n".join(ascii_str[i: i + new_width] for i in range(0, len(ascii_str), new_width))
    return ascii_art, new_width, new_height


def insert_word_into_ascii(ascii_art, word):
    lines = ascii_art.split('\n')
    if not lines:
        return ascii_art

    height = len(lines)
    width = len(lines[0]) if lines else 0

    if len(word) + 2 > width:
        return ascii_art

    y_pos = random.randint(0, height - 1)
    max_x = width - len(word) - 2
    x_pos = random.randint(0, max_x)

    new_line = (
            lines[y_pos][:x_pos] +
            ' ' + word + ' ' +
            lines[y_pos][x_pos + len(word) + 2:]
    )
    lines[y_pos] = new_line

    return '\n'.join(lines)


@app.route("/", methods=["GET", "POST"])
def index():
    ascii_art = ""
    cols, rows = 80, 25
    if request.method == "POST":
        file = request.files.get("file")
        height = int(request.form.get("height", 50))
        ascii_chars = list(request.form.get("ascii_chars", "".join(DEFAULT_ASCII_CHARS)))
        word = request.form.get("word", "").strip()

        if file:
            try:
                image = Image.open(io.BytesIO(file.read()))
                ascii_art, cols, rows = convert_image_to_ascii(image, ascii_chars, height)
                if word:
                    ascii_art = insert_word_into_ascii(ascii_art, word)
            except Exception as e:
                ascii_art = f"Error: {e}"

    return render_template("index.html", ascii_art=ascii_art, cols=cols, rows=rows)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')