# Hướng Dẫn Deploy API ProtonX Legal

## Giới Thiệu

API này cung cấp dịch vụ phân loại văn bản pháp luật tiếng Việt sử dụng model ProtonX Legal từ HuggingFace.

## Yêu Cầu Hệ Thống

- Docker và Docker Compose đã cài đặt
- Kết nối Internet (để tải model lần đầu)
- Ít nhất 4GB RAM
- 5GB dung lượng đĩa

## Cách Deploy Nhanh

### Phương Pháp 1: Sử dụng Script Tự Động (Khuyên Dùng)

```bash
# Cho phép chạy script
chmod +x deploy.sh

# Chạy script deploy
./deploy.sh
```

Chọn tùy chọn 1 để build và khởi động API.

### Phương Pháp 2: Sử dụng Docker Compose Trực Tiếp

```bash
# Build và khởi động service
docker compose up -d

# Xem logs
docker compose logs -f

# Dừng service
docker compose down
```

## Truy Cập API

Sau khi deploy thành công, bạn có thể truy cập:

- **API chính**: http://localhost:8000
- **Tài liệu API (Swagger)**: http://localhost:8000/docs
- **Tài liệu thay thế (ReDoc)**: http://localhost:8000/redoc
- **Kiểm tra sức khỏe**: http://localhost:8000/health

## Kiểm Tra Deployment

### Sử dụng Script Kiểm Tra

```bash
chmod +x verify_deployment.sh
./verify_deployment.sh
```

### Kiểm Tra Thủ Công

```bash
# 1. Kiểm tra health
curl http://localhost:8000/health

# 2. Lấy thông tin model
curl http://localhost:8000/model-info

# 3. Test phân loại văn bản
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Điều 1. Phạm vi điều chỉnh. Luật này quy định về các vấn đề liên quan đến pháp luật."
  }'
```

## Các Tính Năng Chính

### 1. Phân Loại Văn Bản Đơn

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Văn bản pháp luật của bạn ở đây"
  }'
```

### 2. Phân Loại Nhiều Văn Bản (Batch)

```bash
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Văn bản thứ nhất",
      "Văn bản thứ hai"
    ]
  }'
```

### 3. OCR Từ Ảnh

```bash
curl -X POST http://localhost:8000/ocr/upload \
  -F "file=@/duong/dan/den/anh.jpg"
```

### 4. OCR + Phân Loại

```bash
curl -X POST http://localhost:8000/ocr/upload-and-classify \
  -F "file=@/duong/dan/den/van-ban-phap-luat.jpg"
```

## Sử Dụng Giao Diện Web

1. Mở trình duyệt và truy cập: http://localhost:8000/docs
2. Bạn sẽ thấy giao diện Swagger UI
3. Click vào endpoint bạn muốn test
4. Click "Try it out"
5. Nhập dữ liệu và click "Execute"
6. Xem kết quả trả về

## Xem Logs

```bash
# Xem logs real-time
docker compose logs -f

# Xem logs của container cụ thể
docker logs -f protonx-models-protonx-legal-api-1
```

## Dừng Service

```bash
# Dừng service
docker compose down

# Dừng và xóa volumes
docker compose down -v
```

## Xử Lý Sự Cố

### Lỗi: Port 8000 đã được sử dụng

**Giải pháp**: Thay đổi port trong file `docker-compose.yml`:
```yaml
ports:
  - "8080:8000"  # Sử dụng port 8080 thay vì 8000
```

### Lỗi: Không tải được model

**Giải pháp**:
1. Kiểm tra kết nối Internet
2. Đợi vài phút để model tải về (xem logs)
3. Thử tải model trước: `./deploy.sh` → Chọn tùy chọn 5

### Lỗi: Hết bộ nhớ

**Giải pháp**:
1. Tăng RAM cho Docker (Docker Desktop → Settings → Resources)
2. Giảm `API_WORKERS` trong file `.env`
3. Đóng các ứng dụng khác

### Request đầu tiên chậm

**Lý do**: Model đang được tải vào bộ nhớ lần đầu tiên (bình thường)

**Giải pháp**: Đợi vài phút cho model load xong, sau đó các request sẽ nhanh hơn

## Cấu Hình

Bạn có thể thay đổi cấu hình trong file `.env`:

```bash
# Cấu hình Model
MODEL_NAME=protonx-models/protonx-legal-tc
MODEL_CACHE_DIR=./model_cache
DEVICE=cpu  # Thay bằng 'cuda' nếu có GPU

# Cấu hình API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1  # Tăng nếu cần xử lý nhiều request đồng thời

# Logging
LOG_LEVEL=INFO

# Cấu hình OCR
OCR_ENGINE=easyocr
OCR_LANGUAGES=vi,en
MAX_UPLOAD_SIZE=10485760  # 10MB
```

## Hiệu Năng

- **Kiểm tra sức khỏe**: < 10ms
- **Phân loại đơn**: 100-500ms (CPU), 50-200ms (GPU)
- **Phân loại batch**: ~100ms mỗi văn bản
- **OCR**: 1-5 giây tùy kích thước ảnh

## Tài Liệu Bổ Sung

- [QUICKSTART.md](QUICKSTART.md) - Hướng dẫn nhanh (Tiếng Anh)
- [README.md](README.md) - Tài liệu đầy đủ (Tiếng Anh)
- [API_EXAMPLES.md](API_EXAMPLES.md) - Ví dụ sử dụng API
- [DEPLOYMENT.md](DEPLOYMENT.md) - Hướng dẫn deploy production
- [DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md) - Trạng thái deployment

## Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra logs: `docker compose logs -f`
2. Kiểm tra container: `docker compose ps`
3. Kiểm tra health: `curl http://localhost:8000/health`
4. Xem phần xử lý sự cố trong README.md

## Tổng Kết

Project đã sẵn sàng để deploy và test. Làm theo các bước sau:

1. ✅ **Deploy**: Chạy `./deploy.sh` và chọn option 1
2. ✅ **Kiểm tra**: Chạy `./verify_deployment.sh`
3. ✅ **Test**: Mở http://localhost:8000/docs để test API
4. ✅ **Sử dụng**: Tích hợp vào ứng dụng của bạn

---

**Trạng thái**: ✅ Sẵn sàng để deploy và test!

**Liên hệ**: Xem thông tin trong README.md
