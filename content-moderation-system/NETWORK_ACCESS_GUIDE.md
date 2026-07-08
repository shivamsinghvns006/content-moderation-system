# Network Access Guide

## Changes Made

The Content Moderation System has been updated to listen on **all network interfaces** (`0.0.0.0`), making it accessible to everyone on your network (and internet if exposed).

### What Changed:
- ✅ Changed from `127.0.0.1` (localhost-only) to `0.0.0.0` (all interfaces)
- ✅ Added support for `APP_HOST` and `APP_PORT` environment variables
- ✅ Updated `.env.example` with network configuration options

---

## How to Access the Website

### 1. **On the Same Machine (Localhost)**
```
http://localhost:5000
http://127.0.0.1:5000
```

### 2. **From Another Device on the Same Network**
Find your computer's IP address, then access:
```
http://<YOUR_IP>:5000
```

**To find your IP address:**

**Windows (PowerShell):**
```powershell
ipconfig
```
Look for "IPv4 Address" under your network adapter (e.g., `192.168.x.x`)

**Linux/Mac (Terminal):**
```bash
ifconfig
# or
ip addr show
```

### 3. **From the Internet (If Port-Forwarded)**
If you've configured your router to forward port 5000 to your machine:
```
http://<YOUR_PUBLIC_IP>:5000
```

---

## Customizing Host and Port

### Using Environment Variables:

**Option 1: Set via .env file**
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and uncomment:
APP_HOST=0.0.0.0
APP_PORT=5000
```

**Option 2: Set via command line (Windows PowerShell):**
```powershell
$env:APP_HOST = "0.0.0.0"
$env:APP_PORT = "8080"
python app.py
```

**Option 3: Set via command line (Linux/Mac):**
```bash
export APP_HOST=0.0.0.0
export APP_PORT=8080
python app.py
```

---

## Production Deployment

⚠️ **For production use:**
1. Set `debug=False` in `app.py`
2. Use a production WSGI server (gunicorn, waitress, etc.):
   ```bash
   pip install gunicorn
   gunicorn -b 0.0.0.0:5000 app:app
   ```
3. Configure a firewall to restrict access appropriately
4. Use HTTPS (SSL/TLS certificate)
5. Set a strong `SECRET_KEY` in your `.env` file
6. Use a proper database (PostgreSQL, MySQL) instead of SQLite

---

## Testing Network Access

### Test from another device on the network:

**Windows (Command Prompt):**
```cmd
curl http://192.168.x.x:5000
```

**Linux/Mac (Terminal):**
```bash
curl http://192.168.x.x:5000
```

**Browser:**
Simply visit `http://192.168.x.x:5000` in your browser.

---

## Troubleshooting

### "Connection refused" error:
- Verify the app is running: `python app.py`
- Check if port 5000 is already in use: `netstat -an | findstr 5000` (Windows)
- Try a different port: `APP_PORT=8080 python app.py`

### "No route to host" error:
- Ensure both devices are on the same network
- Check firewall settings (Windows Defender, etc.)
- Verify the IP address is correct

### Can access localhost but not from other devices:
- Check your firewall is allowing port 5000
- Verify `APP_HOST` is set to `0.0.0.0` (not `127.0.0.1`)
- Restart the app after changing configuration

---

## API Access via URL

The REST API is also now accessible from any device:

```bash
# Submit text for moderation
curl -X POST http://192.168.x.x:5000/api/moderate/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Sample text to moderate"}'

# Submit image for moderation
curl -X POST http://192.168.x.x:5000/api/moderate/image \
  -F "file=@path/to/image.jpg"

# Get moderation records
curl http://192.168.x.x:5000/api/records

# Get statistics
curl http://192.168.x.x:5000/api/stats
```

---

## Security Considerations

When exposing your app to a network or the internet:
1. **Always use a strong SECRET_KEY** - change the default value in `.env`
2. **Enable HTTPS** - never transmit data over plain HTTP in production
3. **Use authentication** - add login credentials to sensitive endpoints
4. **Restrict access** - use firewall rules to limit who can connect
5. **Monitor logs** - watch for suspicious activity in the logs folder
6. **Keep dependencies updated** - run `pip install --upgrade -r requirements.txt`

---
