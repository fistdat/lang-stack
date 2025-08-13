# Langflow với Langfuse Integration

Hướng dẫn này giúp bạn chạy Langflow với Docker và tích hợp Langfuse để theo dõi và phân tích workflows.

## Điều kiện tiên quyết

1. Docker và Docker Compose đã được cài đặt
2. Tài khoản Langfuse (Cloud hoặc self-hosted)

## Cài đặt và Chạy

### Bước 1: Thiết lập Langfuse credentials

1. Tạo API keys từ [Langfuse](https://cloud.langfuse.com):
   - Truy cập vào project settings
   - Tạo Secret Key và Public Key

2. Copy file environment:
   ```bash
   cp .env.example .env
   ```

3. Điền thông tin Langfuse vào file `.env`:
   ```bash
   LANGFUSE_SECRET_KEY=sk-your-actual-secret-key
   LANGFUSE_PUBLIC_KEY=pk-your-actual-public-key
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```

### Bước 2: Chạy Docker Compose

```bash
# Chạy services
docker-compose up -d

# Xem logs
docker-compose logs -f langflow

# Kiểm tra status
docker-compose ps
```

### Bước 3: Truy cập ứng dụng

- **Langflow**: http://localhost:7860
- **PostgreSQL**: localhost:5432 (username: langflow, password: langflow)

### Bước 4: Kiểm tra kết nối Langfuse

```bash
docker-compose exec langflow python -c "import requests, os; addr = os.environ.get('LANGFUSE_HOST'); print(addr); res = requests.get(addr, timeout=5); print(res.status_code)"
```

Kết quả thành công sẽ hiển thị:
```
https://cloud.langfuse.com
200
```

## Sử dụng

1. Tạo workflow trong Langflow UI
2. Chạy workflow - tất cả traces sẽ tự động được gửi đến Langfuse
3. Xem traces và analytics tại Langfuse dashboard

## Dừng services

```bash
docker-compose down

# Dừng và xóa volumes (mất data)
docker-compose down -v
```

## Troubleshooting

### Langfuse không nhận traces:
- Kiểm tra lại API keys trong file `.env`
- Đảm bảo `LANGFUSE_HOST` đúng định dạng
- Restart container sau khi thay đổi environment variables

### Không kết nối được database:
- Đợi PostgreSQL container khởi động hoàn toàn
- Kiểm tra logs: `docker-compose logs postgres`

### Port conflicts:
- Thay đổi port mapping trong docker-compose.yml nếu port 7860 hoặc 5432 đã được sử dụng