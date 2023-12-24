import os
import secrets

import requests
from dotenv import load_dotenv
from flask import Flask, render_template_string, request

app = Flask(__name__)
load_dotenv()

@app.route('/')
def index():
    # Generate a new random token
    token = secrets.token_urlsafe()

    # Append the token to the URL
    image_url = f"https://goblinrum.mynetgear.com/count?p=/{token}"

    # HTML chunk to be rendered and copied
    html_chunk = f"""<html>
<body>
    <p>Copy starting here</p>
    <img src="{image_url}">
    <p>Copy stop here</p>
</body>
</html>"""

    # Render the HTML chunk in a user-friendly format
    return render_template_string("""
    <html>
    <head>
        <script>
        function copyToClipboard(elementId) {
            var copyText = document.getElementById(elementId);
            copyText.select();
            document.execCommand('copy');
        }
        </script>
    </head>
    <body>
        <h2>Generated Token</h2>
        <input type="text" value="{{ token }}" id="token" readonly>
        <button onclick="copyToClipboard('token')">Copy Token</button>

        <h2>Generated Chunk</h2>
        <textarea id="html_chunk" rows="10" cols="50" readonly>{{ html_chunk }}</textarea>

        <h2>Rendered HTML</h2>
        <div>
            {{ html_chunk|safe }}
        </div>
                                  
        <h2>View Count Page</h2>
        <a href="{{ url_for('views') }}"><button>Go to View Count Page</button></a>
                                  
    </body>
    </html>
    """, token=token, html_chunk=html_chunk)

@app.route('/views', methods=['GET', 'POST'])
def views():
    # Default view count message
    view_count = 'Enter an ID to get views'

    # Check if the form has been submitted
    if request.method == 'POST':
        id = request.form.get('id')
        view_count = get_views(id) if id else 'No ID provided'

    # Render the view count and the form in HTML format
    return render_template_string("""
    <html>
    <body>
        <h2>View Count</h2>
        <form method="post">
            <input type="text" name="id" placeholder="Enter ID" required>
            <input type="submit" value="Get Views">
        </form>
        <p>{{ view_count }}</p>
    </body>
    </html>
    """, view_count=view_count)

def get_views(id):
    # Placeholder for the get_views function
    # Replace with actual logic to retrieve view count
    apikey = os.getenv('GOATCOUNTER_KEY')

    paths_url = 'https://goblinrum.mynetgear.com/api/v0/paths'
    headers = {'Authorization': f'Bearer {apikey}', 'Content-Type': 'application/json'}
    response = requests.get(paths_url, headers=headers)
    paths = response.json()['paths']
    # find the path "path" with the id in the path
    path_id = -1
    for path in paths:
        if path['path'].find(id) != -1:
            path_id = path['id']
            break
    if path_id == -1:
        return f"ID {id} not found"
    # get the views for the path
    views_url = f'https://goblinrum.mynetgear.com/api/v0/stats/hits/{path_id}'
    response = requests.get(views_url, headers=headers)
    views = response.json()['refs']
    if len(views) == 0:
        return f"ID {id} has no views"
    # return the number of views
    views_count = views[0]['count']
    return f"Views for ID {id}: {views_count}"

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=9001)
