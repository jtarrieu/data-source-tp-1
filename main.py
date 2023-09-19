from flask import Flask

app = Flask(__name__)

@app.route("/")
def root():
    return "Hello from Space! 🚀"


def hello_world():
    prefix_google = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-MZ43902EQ2"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-MZ43902EQ2');
</script>"""

    return prefix_google + "Hello World!"
