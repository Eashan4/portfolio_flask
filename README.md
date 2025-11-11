# Flask Portfolio + IoT Hardware Dashboard

A Flask-based portfolio website with IoT hardware integration, designed to showcase projects and manage real-time data from ESP8266/ESP32 devices.

## 🚀 Features

- **Portfolio Website**: Showcase your projects, skills, and achievements
- **IoT Dashboard**: Real-time data monitoring from ESP8266/ESP32 devices
- **Admin Panel**: Manage projects, devices, and content
- **Hardware Integration**: API endpoints for ESP8266/ESP32 to send sensor data
- **Project Management**: Store and manage Arduino code and HTML dashboards
- **User Authentication**: Login/signup system with admin roles

## 📁 Project Structure

```
portfolio_flask/
├── api/
│   └── index.py              # Vercel serverless entry point
├── database/
│   └── db_connection.py      # Database configuration
├── models/                   # Database models
│   ├── __init__.py
│   ├── user_model.py
│   ├── project_model.py
│   ├── contact_model.py
│   └── hardware_model.py
├── routes/
│   └── hardware_routes.py    # Hardware API routes
├── static/                   # Static files (CSS, JS, images)
├── templates/                # HTML templates
├── app.py                    # Main Flask application
├── vercel.json               # Vercel deployment configuration
├── requirements.txt          # Python dependencies
└── README.md
```

## 🛠️ Local Development Setup

### Prerequisites

- Python 3.8+
- MySQL/MariaDB database
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd portfolio_flask
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database**
   - Create a MySQL database:
     ```sql
     CREATE DATABASE portfolio_flask;
     ```
   - Create a `.env` file in the root directory:
     ```env
     SECRET_KEY=your-secret-key-here
     DATABASE_URL=mysql+pymysql://username:password@localhost:3306/portfolio_flask
     SESSION_COOKIE_SECURE=false
     ```

5. **Initialize database**
   ```bash
   python app.py
   ```
   This will create all necessary tables automatically.

6. **Run the application**
   ```bash
   python app.py
   ```
   The app will run on `http://localhost:5001`

### Create Admin User

1. Sign up at `/signup`
2. Update user role to 'admin' in database:
   ```sql
   UPDATE user SET role='admin' WHERE email='your-email@example.com';
   ```

## 🌐 Vercel Deployment

### Prerequisites for Vercel

- Vercel account
- MySQL database (managed service recommended):
  - [PlanetScale](https://planetscale.com) (MySQL compatible, serverless-friendly)
  - [AWS RDS](https://aws.amazon.com/rds/)
  - [Railway](https://railway.app)
  - [Supabase](https://supabase.com) (PostgreSQL - requires code changes)

### Deployment Steps

1. **Prepare your database**
   - Set up a managed MySQL database
   - Get your database connection URL
   - Format: `mysql+pymysql://user:pass@host:port/db?charset=utf8mb4`

2. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

3. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Configure environment variables:
     - `SECRET_KEY`: A random secret string
     - `DATABASE_URL`: Your MySQL connection string
     - `SESSION_COOKIE_SECURE`: `true` (for HTTPS)
   - Click "Deploy"

4. **Initialize database tables**
   - After deployment, visit your app URL
   - The tables will be created automatically on first request
   - Or run migrations manually if needed

### Vercel Configuration

The project includes `vercel.json` configured for Flask:
- Entry point: `api/index.py`
- All routes are handled by the Flask app
- Static files are served from `/static`

### Environment Variables for Vercel

Set these in your Vercel project settings:

```env
SECRET_KEY=your-random-secret-key
DATABASE_URL=mysql+pymysql://user:pass@host:port/db?charset=utf8mb4
SESSION_COOKIE_SECURE=true
```

## 📡 ESP8266/ESP32 Integration

### Register a Device

1. Login as admin
2. Go to hardware dashboard
3. Register a new device via API or admin panel

### Send Data from ESP8266/ESP32

```cpp
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "your-wifi-ssid";
const char* password = "your-wifi-password";
const char* serverUrl = "https://your-app.vercel.app/api/hardware";
const char* apiKey = "your-api-key";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-API-KEY", apiKey);
    
    String jsonData = "{\"name\":\"temperature\",\"value\":\"27.6\"}";
    int httpResponseCode = http.POST(jsonData);
    
    if (httpResponseCode > 0) {
      Serial.println("Data sent successfully");
    }
    
    http.end();
  }
  
  delay(10000); // Send every 10 seconds
}
```

### API Endpoints

- `POST /api/hardware` - Send sensor data
  - Headers: `X-API-KEY: your-api-key`
  - Body: `{"name": "sensor_name", "value": "sensor_value"}`

- `GET /api/hardware/latest` - Get latest readings
- `POST /api/register-device` - Register new device

## 🔧 Configuration

### Database Models

- **User**: User accounts and authentication
- **Project**: Portfolio projects with categories
- **ProjectSecret**: Secret IDs for IoT projects
- **Contact**: Contact form submissions
- **HardwareDevice**: Registered IoT devices
- **HardwareData**: Sensor data from devices

### Project Storage

- HTML dashboards and ESP8266 code are stored in the database
- No filesystem writes required (serverless-compatible)
- Static images should be uploaded to external storage (S3, Cloudinary) for production

## 📝 Notes

### Serverless Considerations

- **File Storage**: HTML and code are stored in database, not filesystem
- **Sessions**: Uses secure cookies (works across serverless instances)
- **Database**: Requires connection pooling for serverless (configured)
- **Static Files**: Serve from `/static` directory (Vercel handles this)
- **Image Uploads**: For production, use external storage (S3, Cloudinary)

### Limitations

- In-memory `latest_data` store is per-instance (use Redis for production)
- File uploads need external storage for Vercel
- Database connections are pooled but may have cold starts

## 🐛 Troubleshooting

### Database Connection Issues

- Check `DATABASE_URL` format
- Ensure database allows connections from Vercel IPs
- For PlanetScale, use connection pooling URL
- Check SSL requirements

### Session Issues

- Ensure `SECRET_KEY` is set
- Set `SESSION_COOKIE_SECURE=true` for HTTPS
- Clear browser cookies if sessions don't work

### Import Errors

- Ensure all models are imported in `models/__init__.py`
- Check Python path configuration
- Verify `api/index.py` imports correctly

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or support, please open an issue on GitHub.
