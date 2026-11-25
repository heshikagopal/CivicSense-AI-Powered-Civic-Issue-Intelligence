# CivicSense REST API Specification

Base URL: `/api/v1`  
Interactive Swagger Docs: `/docs`  
ReDoc Documentation: `/redoc`

---

## 1. Authentication & Users

### `POST /auth/register`
Creates a new citizen account.
- **Request Body:**
  ```json
  {
    "email": "citizen@civicsense.org",
    "password": "Password123!",
    "full_name": "Maya Patel",
    "phone": "+91 98765 43210",
    "role": "citizen"
  }
  ```
- **Response (201 Created):** `UserResponse`

### `POST /auth/login`
Authenticates user and issues JWT bearer token.
- **Request Body (Form URL Encoded):** `username`, `password`
- **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": { ... }
  }
  ```

### `GET /users/me`
Returns currently authenticated user profile (Requires Bearer token).

---

## 2. Image Processing & AI Detection

### `POST /uploads`
Uploads citizen photo, validates MIME type, strips EXIF metadata for privacy, and stores optimized image.
- **Content-Type:** `multipart/form-data`
- **Response (200 OK):**
  ```json
  {
    "image_url": "/static/uploads/a1b2c3d4.jpg",
    "original_filename": "pothole.jpg",
    "file_size_bytes": 142580,
    "mime_type": "image/jpeg"
  }
  ```

### `POST /detect`
Runs YOLO11 object detection on uploaded image URL.
- **Response (200 OK):**
  ```json
  {
    "detections": [
      {
        "category_code": "pothole",
        "category_name": "Pothole",
        "confidence": 0.84,
        "bbox": [0.22, 0.35, 0.68, 0.72],
        "status": "HIGH"
      }
    ],
    "model_version": "YOLO11-Civic-v1.0",
    "inference_ms": 38.4,
    "preview_url": "/static/uploads/preview_a1b2c3d4.jpg",
    "suggested_category": "pothole",
    "confidence_tier": "HIGH"
  }
  ```

---

## 3. Citizen Reports & Duplicates

### `POST /reports`
Submits citizen complaint, generates visual embedding, checks duplicate radius, and creates or auto-links to Issue.
- **Request Body:**
  ```json
  {
    "latitude": 12.9716,
    "longitude": 77.5946,
    "address_text": "MG Road Cross, Metro Corridor",
    "image_url": "/static/samples/pothole_sample.jpg",
    "citizen_category_suggestion": "Pothole",
    "citizen_comment": "Dangerous road void.",
    "consent_given": true,
    "confirmed_category_code": "pothole"
  }
  ```

### `POST /duplicates/check`
Returns candidate duplicates nearby ranked by multi-factor similarity.

### `POST /duplicates/{match_id}/review`
Administrative decision on candidate match (`CONFIRM_DUPLICATE` or `REJECT_DUPLICATE`).

---

## 4. Priority & Geospatial Intelligence

### `GET /issues/{id}/priority`
Returns explainable mathematical breakdown of 5 triage factors.

### `POST /issues/{id}/priority/override`
Overrides triage score with mandatory reason and audit record.

### `GET /map/issues`
Returns geo-located issues with bounding box (`min_lat`, `max_lat`, `min_lng`, `max_lng`) and category/status filtering.

### `GET /map/hotspots`
Returns DBSCAN spatial recurrence clusters.

---

## 5. Administration & Resolution

### `POST /issues/{id}/assign`
Assigns department and field officer. Status updates to `IN_PROGRESS`.

### `POST /issues/{id}/resolution`
Field team submits work notes and proof image. Status updates to `RESOLVED`.

### `POST /resolution/{id}/verify`
Supervisor verifies resolution. Confirms verified status and stamps completion audit.
