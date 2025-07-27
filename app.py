from flask import Flask, render_template_string
import random

app = Flask(__name__)

quotes = [
    "Containers > VMs",
    "You're doing amazing! 🚀",
    "One container to rule them all 🧱",
    "Docker is magic 🪄",
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Container Wisdom</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #1e1e2f;
            color: #d4d4d4;
            margin: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .quote {
            font-size: 1.6rem;
            margin-bottom: 2rem;
            text-align: center;
            color: #9cdcfe;
            max-width: 80%;
        }

        .button {
            position: relative;
            background-color: #007acc;
            border: none;
            border-radius: 12px;
            padding: 1rem 2rem;
            font-size: 1.2rem;
            color: #ffffff;
            cursor: pointer;
            box-shadow: 0 0 0 4px rgba(0, 122, 204, 0.3);
            transition: all 0.3s ease;
            overflow: hidden;
        }

        .button:hover {
            background-color: #005f9e;
            transform: scale(1.05);
            box-shadow: 0 0 0 6px rgba(0, 122, 204, 0.4);
        }

        .button::before {
            content: "";
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(120deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.75s ease;
        }

        .button:active::before {
            left: 100%;
        }

        .button:active {
            transform: scale(0.98);
            box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.2);
        }

        form {
            margin: 0;
        }
    </style>
</head>
<body>
    <div class="quote">{{ quote }}</div>
    <form method="get">
        <button class="button" type="submit">✨ Inspire Me Again ✨</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    quote = random.choice(quotes)
    return render_template_string(HTML_TEMPLATE, quote=quote)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
