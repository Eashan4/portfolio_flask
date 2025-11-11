import os
import uuid
import secrets
import html
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify, abort, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# ---------------- Load Environment ----------------
load_dotenv()

app = Flask(__name__)
CORS(app)

# In-memory store for latest hardware data per secret_id (for real-time data)
# Note: In production with multiple serverless instances, use Redis or database
latest_data = {}

# Use centralized DB connection
from database.db_connection import db, init_db_app
from routes.hardware_routes import hardware_bp
from models import User, Project, ProjectSecret, Contact, HardwareData

# Initialize config and DB
app.secret_key = os.getenv("SECRET_KEY", "change_this_secret")
# Configure session for serverless (use secure cookies)
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

init_db_app(app)

# ------------------ Helpers ------------------
def is_admin(): 
    return "user" in session and session.get("role") == "admin"

def is_logged_in(): 
    return "user" in session

# Helper to generate a unique secret key
def generate_secret_id():
    return uuid.uuid4().hex[:24]

# ------------------ Web Routes ------------------
@app.route("/")
def index(): 
    return render_template("index.html")

@app.route("/about")
def about(): 
    return render_template("about.html")

@app.route("/academia")
def academia(): 
    return render_template("academia.html")

@app.route("/projects")
def projects(): 
    return render_template("projects.html")

@app.route("/projects/arduino")
def arduino_page():
    projects = Project.query.filter_by(category="arduino").all()
    for p in projects:
        p.secret_ids = [s.secret_id for s in p.secrets]
    return render_template("arduino.html", arduino_projects=projects)

@app.route("/projects/iot")
def iot_page():
    projects = Project.query.filter_by(category="iot").all()
    for p in projects:
        p.secret_ids = [s.secret_id for s in p.secrets]
    return render_template("iot.html", iot_projects=projects)

@app.route("/projects/home-automation")
def home_auto_page():
    projects = Project.query.filter_by(category="home").all()
    # If home_automation.html doesn't exist, use a generic template or create it
    # For now, redirect to projects page
    return render_template("projects.html", home_projects=projects)

@app.route("/projects/robot-car")
def robot_page(): 
    # Redirect to projects page if template doesn't exist
    return render_template("projects.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        if not (name and email and message):
            flash("All fields are required", "danger")
            return redirect(url_for("contact"))
        db.session.add(Contact(name=name, email=email, message=message))
        db.session.commit()
        flash("Message sent successfully!", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user"] = user.email
            session["role"] = user.role
            session["user_name"] = user.name
            flash("Login successful!", "success")
            return redirect(url_for("admin_dashboard") if user.role == "admin" else url_for("projects"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        if password != confirm:
            flash("Passwords do not match", "danger")
            return redirect(url_for("signup"))
        if User.query.filter_by(email=email).first():
            flash("User already exists", "warning")
            return redirect(url_for("signup"))
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Signup successful! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/logout")
def logout(): 
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/admin")
def admin_dashboard():
    if not is_admin(): 
        return redirect(url_for("login"))
    projects = Project.query.order_by(Project.created_at.desc()).all()
    for p in projects:
        p.secret_ids = [s.secret_id for s in p.secrets]
    return render_template("admin_dashboard.html", all_projects=projects)

@app.route('/hardware/code/<secret_id>', methods=['GET'])
def hardware_code(secret_id):
    # Get ESP8266 code from database via ProjectSecret
    project_secret = ProjectSecret.query.filter_by(secret_id=secret_id).first()
    if not project_secret:
        return '<h2>No project found for this secret ID.</h2>', 404
    
    project = project_secret.project
    if not project or not project.esp_code:
        return '<h2>No ESP8266 code found for this project.</h2>', 404
    
    # Return code as downloadable file
    response = Response(project.esp_code, mimetype='text/plain')
    response.headers['Content-Disposition'] = f'attachment; filename="{secret_id}.ino"'
    return response

# Deprecated: Use /admin/add_project instead
# Keeping for backward compatibility but redirecting to add_project
@app.route("/admin/add", methods=["POST"])
def admin_add():
    # Redirect to add_project route which handles everything properly
    return add_project()

@app.route("/admin/delete/<int:pid>")
def admin_delete(pid):
    if not is_admin(): 
        abort(403)
    project = Project.query.get_or_404(pid)
    db.session.delete(project)
    db.session.commit()
    flash("Project deleted successfully!", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/edit/<int:pid>", methods=["GET", "POST"])
def admin_edit(pid):
    if not is_admin():
        return redirect(url_for("login"))
    project = Project.query.get_or_404(pid)
    if request.method == "POST":
        project.title = request.form.get("title")
        project.category = request.form.get("category")
        project.description = request.form.get("description")
        image_url = request.form.get("image")
        image_file = request.files.get("image_file")
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            # In serverless, upload to external storage
            image_url = f"static/images/{filename}"  # Placeholder
        project.image = image_url
        project.github = request.form.get("github")
        project.components = request.form.get("components")
        project.custom_html = request.form.get("custom_html", "")
        project.esp_code = request.form.get("esp_code", "")
        db.session.commit()
        flash("Project updated successfully!", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_edit.html", project=project)

@app.route("/hardware")
def hardware_dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    arduino_projects = Project.query.filter_by(category="arduino").all()
    iot_projects = Project.query.filter_by(category="iot").all()
    
    # Populate secret_ids for each project
    for p in arduino_projects + iot_projects:
        p.secret_ids = [s.secret_id for s in p.secrets]
        # Set first secret_id for backward compatibility with templates
        p.secret_id = p.secret_ids[0] if p.secret_ids else None
    
    readings = HardwareData.query.order_by(HardwareData.timestamp.desc()).limit(50).all()
    return render_template(
        "hardware.html",
        logged_in=True,
        hardware_data=readings,
        arduino_projects=arduino_projects,
        iot_projects=iot_projects
    )

@app.route('/hardware/live/<secret_id>')
def hardware_live(secret_id):
    # Handle empty secret_id
    if not secret_id or secret_id.strip() == '':
        return '<h2>Invalid secret ID.</h2>', 404
    
    # Get HTML from database via ProjectSecret
    project_secret = ProjectSecret.query.filter_by(secret_id=secret_id).first()
    if not project_secret:
        return f'<h2>No project found for secret ID: {secret_id}</h2><p><a href="/hardware">Back to Hardware Dashboard</a></p>', 404
    
    project = project_secret.project
    if not project:
        return '<h2>Project not found.</h2>', 404
    
    # If no custom HTML, show a placeholder with instructions
    if not project.custom_html or project.custom_html.strip() == '':
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Live Page - {project.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 40px; text-align: center; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .alert {{ background: #fff3cd; border: 1px solid #ffc107; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .btn {{ display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{project.title}</h1>
                <div class="alert">
                    <h3>No Live Page Content</h3>
                    <p>This project doesn't have a custom HTML dashboard yet.</p>
                    <p>To add live page content:</p>
                    <ol style="text-align: left; display: inline-block;">
                        <li>Go to Admin Dashboard</li>
                        <li>Edit this project</li>
                        <li>Add HTML content in the "Custom HTML" field</li>
                        <li>Save the project</li>
                    </ol>
                    <p><strong>Secret ID:</strong> <code>{secret_id}</code></p>
                </div>
                <a href="/admin/edit/{project.id}" class="btn">Edit Project</a>
                <a href="/hardware" class="btn">Back to Dashboard</a>
            </div>
        </body>
        </html>
        ''', 200
    
    # Get the HTML content
    html_content = project.custom_html
    
    # If ESP code exists, inject a code viewer into the HTML
    if project.esp_code and project.esp_code.strip():
        # Escape HTML entities for safe display
        esp_code_escaped = html.escape(project.esp_code)
        
        # Create code viewer with download functionality via data attribute
        code_viewer_html = f'''
        <div id="esp-code-viewer" style="position: fixed; bottom: 0; left: 0; right: 0; background: #1e1e1e; color: #d4d4d4; padding: 0; z-index: 10000; max-height: 50vh; overflow: hidden; box-shadow: 0 -2px 10px rgba(0,0,0,0.3); font-family: 'Courier New', monospace;">
            <div style="background: #2d2d2d; padding: 10px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #444;">
                <strong style="color: #4ec9b0;">📄 ESP8266/ESP32 Code</strong>
                <div>
                    <button onclick="toggleCodeViewer()" style="background: #0078d4; color: white; border: none; padding: 5px 15px; border-radius: 3px; cursor: pointer; margin-right: 10px;">Toggle</button>
                    <button onclick="downloadEspCode()" style="background: #107c10; color: white; border: none; padding: 5px 15px; border-radius: 3px; cursor: pointer; margin-right: 10px;">Download</button>
                    <button onclick="closeCodeViewer()" style="background: #d13438; color: white; border: none; padding: 5px 15px; border-radius: 3px; cursor: pointer;">✕ Close</button>
                </div>
            </div>
            <div id="code-content" style="padding: 15px; overflow-y: auto; max-height: calc(50vh - 50px); font-size: 13px; line-height: 1.5;">
                <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word; color: #d4d4d4;"><code id="esp-code-text">{esp_code_escaped}</code></pre>
            </div>
        </div>
        <script>
            (function() {{
                let codeViewerVisible = true;
                
                function toggleCodeViewer() {{
                    const viewer = document.getElementById('esp-code-viewer');
                    const content = document.getElementById('code-content');
                    if (codeViewerVisible) {{
                        content.style.display = 'none';
                        viewer.style.maxHeight = '50px';
                    }} else {{
                        content.style.display = 'block';
                        viewer.style.maxHeight = '50vh';
                    }}
                    codeViewerVisible = !codeViewerVisible;
                }}
                
                function closeCodeViewer() {{
                    document.getElementById('esp-code-viewer').style.display = 'none';
                }}
                
                function downloadEspCode() {{
                    const codeElement = document.getElementById('esp-code-text');
                    const code = codeElement.textContent || codeElement.innerText;
                    const blob = new Blob([code], {{ type: 'text/plain' }});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = '{secret_id}.ino';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                }}
                
                // Make functions globally accessible
                window.toggleCodeViewer = toggleCodeViewer;
                window.closeCodeViewer = closeCodeViewer;
                window.downloadEspCode = downloadEspCode;
            }})();
        </script>
        '''
        
        # Inject before closing body tag, or append if no body tag
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', code_viewer_html + '</body>')
        elif '</html>' in html_content:
            html_content = html_content.replace('</html>', code_viewer_html + '</html>')
        else:
            html_content = html_content + code_viewer_html
    
    # Return HTML content with code viewer
    return Response(html_content, mimetype='text/html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Logged out as admin.')
    return redirect(url_for('admin_dashboard'))

@app.route('/hardware/data/<secret_id>', methods=['POST'])
def hardware_data_post(secret_id):
    # Receive JSON data from ESP board
    data = request.get_json()
    latest_data[secret_id] = data
    # Note: In production, store this in database or Redis for persistence
    return jsonify({'status': 'success'}), 200

@app.route('/hardware/data/<secret_id>', methods=['GET'])
def hardware_data_get(secret_id):
    data = latest_data.get(secret_id)
    if not data:
        return jsonify({'error': 'No data'}), 404
    return jsonify(data)

@app.route('/admin/add_project', methods=['POST'])
def add_project():
    if not is_admin():
        abort(403)
    
    title = request.form.get('title')
    category = request.form.get('category')
    description = request.form.get('description')
    components = request.form.get('components')
    image_url = request.form.get('image')
    image_file = request.files.get('image_file')
    github = request.form.get('github')
    custom_html = request.form.get('custom_html', '')
    esp_code = request.form.get('esp_code', '')
    secret_ids = request.form.get('secret_ids', '')  # comma-separated
    
    # Handle image upload
    if image_file and image_file.filename:
        filename = secure_filename(image_file.filename)
        # For local development, save to static/images
        # For production/Vercel, use external storage
        try:
            import os
            os.makedirs('static/images', exist_ok=True)
            save_path = os.path.join('static/images', filename)
            image_file.save(save_path)
            image_url = f'static/images/{filename}'
        except Exception as e:
            flash(f'Image upload failed: {e}. Using image URL if provided.', 'warning')
    
    # Parse secret IDs
    secret_id_list = [sid.strip() for sid in secret_ids.split(',') if sid.strip()]
    
    # If no secret IDs provided, generate one automatically
    if not secret_id_list:
        secret_id_list = [generate_secret_id()]
        flash(f'No secret ID provided. Generated secret ID: {secret_id_list[0]}', 'info')
    
    # Create project
    project = Project(
        title=title,
        category=category,
        description=description,
        components=components,
        image=image_url,
        github=github,
        custom_html=custom_html,
        esp_code=esp_code
    )
    db.session.add(project)
    db.session.flush()  # Get project ID
    
    # Create secrets for this project
    created_secrets = []
    for secret_id in secret_id_list:
        # Check if secret_id already exists
        existing = ProjectSecret.query.filter_by(secret_id=secret_id).first()
        if existing:
            flash(f'Secret ID {secret_id} already exists. Skipping.', 'warning')
            continue
        db.session.add(ProjectSecret(secret_id=secret_id, project_id=project.id))
        created_secrets.append(secret_id)
    
    db.session.commit()
    
    if created_secrets:
        secret_msg = ', '.join(created_secrets)
        flash(f'Project created successfully! Secret ID(s): {secret_msg}', 'success')
    else:
        flash('Project created but no secrets were added.', 'warning')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_secret', methods=['POST'])
def delete_secret():
    if not is_admin():
        abort(403)
    
    secret_id = request.form.get('secret_id')
    ProjectSecret.query.filter_by(secret_id=secret_id).delete()
    db.session.commit()
    flash(f'Secret ID {secret_id} deleted!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_secret', methods=['POST'])
def add_secret():
    if not is_admin():
        abort(403)
    
    project_id = request.form.get('project_id')
    new_secret_id = generate_secret_id()
    db.session.add(ProjectSecret(secret_id=new_secret_id, project_id=project_id))
    db.session.commit()
    flash(f'New secret ID <b>{new_secret_id}</b> added! Copy this key for ESP8266 and frontend.', 'success')
    return redirect(url_for('admin_dashboard'))

# Register hardware blueprint (handles /hardware and related APIs)
app.register_blueprint(hardware_bp)

# ------------------ Run App ------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5001, debug=True)
