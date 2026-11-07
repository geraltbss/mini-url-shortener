# Mini URL Shortener

A small Flask app that turns long URLs into short links. It also exposes basic click statistics and a health check.

## Features

- Create short links for valid `http` and `https` URLs
- Redirect short codes to their original URLs
- Track link creation and redirect clicks in memory
- Check service health with a lightweight endpoint
- Configure the service with environment variables or run it in Docker

## Requirements

- Python 3.11 or Docker

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

The app listens on [http://localhost:8080](http://localhost:8080) by default. Open that address to use the simple web form.

## API

### Create a short link

```http
POST /api/shorten
Content-Type: application/json
```

Request:

```json
{
  "url": "https://example.com/a/long/page"
}
```

The response includes the generated code, original URL, and short URL. Invalid or non-HTTP(S) URLs return `400`.

### View statistics

```http
GET /api/stats
```

Returns the total number of links, total redirects, and the in-memory link records.

### Check health

```http
GET /health
```

Returns `{"status":"ok"}` when the app is running.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | Port used by the Flask app |
| `BASE_URL` | `http://localhost:8080` | Base address included in generated short links |
| `CODE_LEN` | `6` | Number of characters in generated short codes |

## Run with Docker

```bash
docker build -t mini-url-shortener .
docker run --rm -p 8080:8080 mini-url-shortener
```

## Note about storage

Links and click counts are kept in memory. They are cleared whenever the app restarts, so this version is intended as a small demo rather than persistent production storage.
