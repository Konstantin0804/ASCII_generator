from flask import Flask, render_template, request
from PIL import Image, ImageFilter
import os
import random
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DEFAULT_ASCII_CHARS = ["M", "W", "C", "S", "B", "G", "%", "+", "o", "a", "e", "s", "i", "n", "d", "f", "u", "l", "t",
                       "y", ":", ".", "-", " "]

# Add to the top of the file with other constants
EDGE_CHARS = ['(', ')', '/', '\\', '|', ']', '[', '}', '{', '>', '<', ',', '.']


def fibonacci_sequence(n):
    """Generate first n numbers of Fibonacci sequence"""
    fib = [1, 1]
    while len(fib) < n:
        fib.append(fib[-1] + fib[-2])
    return fib


def get_weighted_char(chars, fib_seq, fib_total):
    """Get a character using Fibonacci weights"""
    rand_val = random.randint(1, fib_total)
    running_sum = 0
    for i, weight in enumerate(fib_seq):
        running_sum += weight
        if rand_val <= running_sum:
            return chars[i]
    return chars[-1]


# Resize image to desired output dimensions
# Account for font aspect ratio (typically ~0.55 for monospace fonts)
def resize_image(image, new_height):
    width, height = image.size
    aspect_ratio = width / height
    font_aspect_ratio = 0.55  # Adjust for typical character width-to-height ratio
    new_width = int(new_height * aspect_ratio / font_aspect_ratio)
    return image.resize((new_width, new_height)), new_width


# Convert the image to grayscale
def grayscale(image):
    return image.convert("L")


def detect_edges(image):
    """Detect edges in the image"""
    # Convert to grayscale if not already
    if image.mode != 'L':
        image = image.convert('L')

    # Apply edge detection
    edges = image.filter(ImageFilter.FIND_EDGES)
    return edges


def get_edge_char(x, y, prev_char):
    """Get appropriate edge character based on position and previous char"""
    # Define character groups with weights
    brackets = ['(', ')', '[', ']', '{', '}']
    slashes = ['/', '\\']
    others = ['|', '>', '<', ',', '.']

    if prev_char in EDGE_CHARS:
        # Continue patterns with moderate slash probability
        if prev_char in ['(', '[', '{']:
            return random.choice([')', ']', '}'])
        elif prev_char in ['/', '\\'] and random.random() < 0.4:  # 40% chance to continue slash pattern
            return random.choice(slashes)
        elif prev_char in ['|', '<', '>'] and random.random() < 0.6:  # 60% chance to continue vertical/angular pattern
            return random.choice(others)
        else:
            # Weighted distribution
            choices = brackets * 4 + slashes * 2 + others * 3
            return random.choice(choices)
    else:
        # Initial character with balanced distribution
        choices = brackets * 4 + slashes * 2 + others * 3
        return random.choice(choices)


def is_edge_pixel(pixel_value, threshold=100):  # Lowered threshold to detect more edges
    """Determine if a pixel is part of an edge"""
    return pixel_value > threshold


def map_pixels_to_ascii(image, ascii_chars):
    if not ascii_chars:
        raise ValueError("ASCII character list is empty.")

    # Get edge information
    edges = detect_edges(image)
    edges_data = edges.getdata()
    original_data = image.getdata()
    width, height = image.size

    range_width = max(1, 256 // len(ascii_chars))

    # Get character groups for variation
    dark_chars = ascii_chars[:5]  # Darkest characters
    light_chars = ascii_chars[-6:-1]  # Light characters (excluding space)
    fib_seq = fibonacci_sequence(5)  # [1, 1, 2, 3, 5]
    fib_total = sum(fib_seq)

    result = []
    prev_chars = []
    prev_edge_char = None

    # Generate multiple Fibonacci sequences for varied space distribution
    space_fib1 = fibonacci_sequence(7)  # [1, 1, 2, 3, 5, 8, 13]
    space_fib2 = fibonacci_sequence(6)  # [1, 1, 2, 3, 5, 8]
    space_cycle1 = sum(space_fib1)
    space_cycle2 = sum(space_fib2)

    for i, (pixel, edge) in enumerate(zip(original_data, edges_data)):
        x, y = i % width, i // width

        # First check if this should be a space
        space_counter1 = i % space_cycle1
        space_counter2 = (i * 2) % space_cycle2

        if pixel >= 240:  # If it's a white pixel
            result.append(' ')
            continue

        # Check for edge pixels first
        if is_edge_pixel(edge):
            new_char = get_edge_char(x, y, prev_edge_char)
            prev_edge_char = new_char
        else:
            # Add occasional spaces within the silhouette
            if (space_counter1 in space_fib1[4:] and random.random() < 0.6) or \
                    (space_counter2 in space_fib2[3:] and random.random() < 0.4) or \
                    (random.random() < 0.05):  # Reduced random space probability
                result.append(' ')
                continue

            char_index = min(len(ascii_chars) - 1, pixel // range_width)

            if char_index == len(ascii_chars) - 1:
                new_char = ' '
            elif char_index == 0:
                new_char = get_weighted_char(dark_chars, fib_seq, fib_total)
            elif char_index >= len(ascii_chars) - 6:
                new_char = get_weighted_char(light_chars, fib_seq, fib_total)
            else:
                new_char = ascii_chars[char_index]

            # Prevent repetition (but not for spaces or edge characters)
            if new_char != ' ' and len(prev_chars) >= 2 and all(c == new_char for c in prev_chars[-2:]):
                if new_char in dark_chars:
                    new_char = get_weighted_char(dark_chars, fib_seq, fib_total)
                elif new_char in light_chars:
                    new_char = get_weighted_char(light_chars, fib_seq, fib_total)
                else:
                    offset = random.choice([-1, 1])
                    new_index = (char_index + offset) % (len(ascii_chars) - 1)
                    new_char = ascii_chars[new_index]

        result.append(new_char)
        if new_char != ' ':
            prev_chars.append(new_char)
            if len(prev_chars) > 3:
                prev_chars.pop(0)

    return "".join(result)


# Convert the image to ASCII art
def convert_image_to_ascii(image, ascii_chars, new_height):
    image, new_width = resize_image(image, new_height)
    image = grayscale(image)
    ascii_str = map_pixels_to_ascii(image, ascii_chars)
    ascii_art = "\n".join(
        ascii_str[i: i + new_width] for i in range(0, len(ascii_str), new_width)
    )
    rows = len(ascii_art.split('\n'))  # Count the number of rows
    return ascii_art, new_width, rows  # Return ascii_art, cols (new_width), and rows


def insert_word_into_ascii(ascii_art, word, position='MID_CENTER'):
    lines = ascii_art.split('\n')
    if not lines:
        return ascii_art

    height = len(lines)
    width = len(lines[0]) if lines else 0
    word_len = len(word)

    if word_len + 2 > width:
        return ascii_art

    # Define regions
    h_third = max(1, height // 3)
    w_third = max(1, width // 3)

    # Define region boundaries based on position
    positions = {
        'TOP_LEFT': (0, max(h_third, 1), 0, max(w_third, word_len + 3)),
        'TOP_CENTER': (0, max(h_third, 1), w_third, max(2 * w_third, w_third + word_len + 3)),
        'TOP_RIGHT': (0, max(h_third, 1), 2 * w_third, width),
        'MID_LEFT': (h_third, max(2 * h_third, h_third + 1), 0, max(w_third, word_len + 3)),
        'MID_CENTER': (h_third, max(2 * h_third, h_third + 1), w_third, max(2 * w_third, w_third + word_len + 3)),
        'MID_RIGHT': (h_third, max(2 * h_third, h_third + 1), 2 * w_third, width),
        'LOW_LEFT': (2 * h_third, height, 0, max(w_third, word_len + 3)),
        'LOW_CENTER': (2 * h_third, height, w_third, max(2 * w_third, w_third + word_len + 3)),
        'LOW_RIGHT': (2 * h_third, height, 2 * w_third, width)
    }

    y_start, y_end, x_start, x_end = positions[position]

    # Ensure valid ranges
    if y_end <= y_start or x_end <= x_start + word_len + 2:
        # If region is too small, try to find any valid position
        y_start = 0
        y_end = height
        x_start = 0
        x_end = width

    # Find suitable position within the selected region
    max_attempts = 50
    for _ in range(max_attempts):
        try:
            y_pos = random.randint(y_start, max(y_start, y_end - 1))
            x_pos = random.randint(x_start, max(x_start, x_end - word_len - 2))

            # Check if the position has enough non-space characters
            section = lines[y_pos][x_pos:x_pos + word_len + 2]
            if sum(1 for c in section if c != ' ') >= len(section) // 2:
                new_line = (
                        lines[y_pos][:x_pos] +
                        ' ' + word + ' ' +
                        lines[y_pos][x_pos + word_len + 2:]
                )
                lines[y_pos] = new_line
                return '\n'.join(lines)
        except (ValueError, IndexError):
            continue

    # If no suitable position found in the desired region, try anywhere
    try:
        y_pos = random.randint(0, height - 1)
        x_pos = random.randint(0, width - word_len - 2)
        new_line = (
                lines[y_pos][:x_pos] +
                ' ' + word + ' ' +
                lines[y_pos][x_pos + word_len + 2:]
        )
        lines[y_pos] = new_line
    except (ValueError, IndexError):
        pass  # If still fails, return original art

    return '\n'.join(lines)


def clear_uploads_folder():
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {filename}: {e}")


@app.route("/", methods=["GET", "POST"])
def index():
    ascii_art = ""
    cols, rows = 80, 25  # Default values for columns and rows
    if request.method == "POST":
        file = request.files.get("file")  # Get uploaded image file
        height = int(request.form.get("height", 50))  # Get desired output height
        ascii_chars = list(request.form.get("ascii_chars")) + DEFAULT_ASCII_CHARS # Convert ASCII chars to list
        word = request.form.get("word", "").strip()  # Word to insert (if any)
        text_position = request.form.get("text_position", "MID_CENTER")  # Default text position

        if file:
            try:
                # Read and process the uploaded image
                image = Image.open(io.BytesIO(file.read()))

                # Convert image to ASCII art
                ascii_art, cols, rows = convert_image_to_ascii(image, ascii_chars, height)

                # If a word is provided, insert it into the ASCII art
                if word:
                    ascii_art = insert_word_into_ascii(ascii_art, word, text_position)

                # Clear the uploads folder to remove the uploaded file
                clear_uploads_folder()
            except Exception as e:
                ascii_art = f"Error: {e}"  # If error occurs, show it

    return render_template("index.html", ascii_art=ascii_art, cols=cols, rows=rows)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')