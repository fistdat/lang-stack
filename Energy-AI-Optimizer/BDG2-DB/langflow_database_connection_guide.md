# Hướng Dẫn Kết Nối Langflow với Database TimescaleDB

## 🚨 Quick Fix - Connection Refused Error

Nếu bạn gặp lỗi `Connection refused`, hãy sử dụng connection string này trong **SQL Database** hoặc **SQL Executor** component:

```
postgresql://eaio_user:eaio_password@eaio_timescaledb_new:5432/eaio_energy
```

**Không sử dụng** `localhost:5434` từ trong Langflow container!

---

## Thông Tin Kết Nối Database

**Database**: `eaio_energy`  
**Container**: `eaio_timescaledb_new`  
**Host**: `eaio_timescaledb_new` (trong Docker network) / `localhost` (từ host machine)  
**Port**: `5432` (internal) / `5434` (external)  
**Username**: `eaio_user`  
**Password**: `eaio_password`  
**Database Type**: PostgreSQL (TimescaleDB)  

### ⚠️ Quan Trọng - Network Configuration

Khi kết nối từ **Langflow container** đến **TimescaleDB container**, sử dụng:
- **Host**: `eaio_timescaledb_new`
- **Port**: `5432`
- **Connection String**: `postgresql://eaio_user:eaio_password@eaio_timescaledb_new:5432/eaio_energy`

Khi kết nối từ **host machine** (ngoài Docker), sử dụng:
- **Host**: `localhost`  
- **Port**: `5434`
- **Connection String**: `postgresql://eaio_user:eaio_password@localhost:5434/eaio_energy`

---

## Phương Pháp 1: Sử Dụng SQL Database Component

### Bước 1: Thêm SQL Database Component

1. Mở Langflow UI tại `http://localhost:7860`
2. Tạo flow mới hoặc mở flow hiện có
3. Từ sidebar, tìm và kéo component **"SQL Database"** vào canvas
4. Component này thường nằm trong category **"Utilities"** hoặc **"Data"**

### Bước 2: Cấu Hình Connection String

Trong SQL Database component, cấu hình các thông số sau:

**✅ Cho Langflow Container (Khuyến nghị):**
```
Database URL: postgresql://eaio_user:eaio_password@eaio_timescaledb_new:5432/eaio_energy
```

**❌ Sai (sẽ bị lỗi Connection Refused):**
```
Database URL: postgresql://eaio_user:eaio_password@localhost:5434/eaio_energy
```

**Hoặc cấu hình từng thông số riêng biệt:**

- **Database Type**: `postgresql`
- **Host**: `eaio_timescaledb_new`
- **Port**: `5432`
- **Database Name**: `eaio_energy`
- **Username**: `eaio_user`
- **Password**: `eaio_password`

### Bước 3: Test Connection

1. Nhấn nút **"Test Connection"** nếu có sẵn
2. Hoặc chạy component để kiểm tra kết nối

---

## Phương Pháp 2: Sử Dụng SQL Executor Component

### Bước 1: Thêm SQL Executor Component

1. Từ sidebar, tìm và kéo component **"SQL Executor"** vào canvas
2. Component này thường nằm trong category **"Data"**

### Bước 2: Cấu Hình Database Connection

Trong SQL Executor component:

**Connection String:**
```
postgresql://eaio_user:eaio_password@eaio_timescaledb_new:5432/eaio_energy
```

**Query Example:**
```sql
SELECT building_id, primary_space_usage, eui 
FROM energy.buildings 
LIMIT 10;
```

---

## Phương Pháp 3: Sử Dụng Custom Python Component

### Bước 1: Tạo Custom Component

```python
from langflow.custom import CustomComponent
from langflow.inputs import SecretStrInput, StrInput, IntInput
from langflow.template import Output
import psycopg2
import pandas as pd

class TimescaleDBConnector(CustomComponent):
    display_name = "TimescaleDB Connector"
    description = "Connect to EAIO TimescaleDB database"
    
    inputs = [
        StrInput(name="query", display_name="SQL Query", required=True),
        StrInput(name="host", display_name="Host", value="eaio_timescaledb_new"),
        IntInput(name="port", display_name="Port", value=5432),
        StrInput(name="database", display_name="Database", value="eaio_energy"),
        StrInput(name="username", display_name="Username", value="eaio_user"),
        SecretStrInput(name="password", display_name="Password", value="eaio_password"),
    ]
    
    outputs = [
        Output(display_name="Query Result", name="result", method="execute_query"),
    ]
    
    def execute_query(self) -> pd.DataFrame:
        conn_string = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        
        try:
            conn = psycopg2.connect(conn_string)
            df = pd.read_sql_query(self.query, conn)
            conn.close()
            return df
        except Exception as e:
            raise Exception(f"Database connection error: {str(e)}")
```

---

## Các Query Mẫu Hữu Ích

### 1. Lấy Thông Tin Buildings

```sql
SELECT 
    building_id,
    primary_space_usage,
    square_meters,
    eui,
    energy_star_score
FROM energy.buildings
WHERE status = 'active'
ORDER BY eui DESC
LIMIT 20;
```

### 2. Lấy Dữ Liệu Meter Readings Gần Nhất

```sql
SELECT 
    building_id,
    meter_type,
    timestamp,
    value,
    unit
FROM energy.meter_readings
WHERE timestamp >= NOW() - INTERVAL '24 hours'
AND quality = 'good'
ORDER BY timestamp DESC
LIMIT 100;
```

### 3. Thống Kê Tiêu Thụ Theo Tòa Nhà

```sql
SELECT 
    building_id,
    meter_type,
    COUNT(*) as reading_count,
    AVG(value) as avg_consumption,
    MAX(value) as peak_consumption
FROM energy.meter_readings
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY building_id, meter_type
ORDER BY avg_consumption DESC;
```

### 4. Dữ Liệu Weather Tương Quan

```sql
SELECT 
    w.site_id,
    w.timestamp,
    w.air_temperature,
    w.wind_speed,
    AVG(m.value) as avg_energy_consumption
FROM energy.weather_data w
JOIN energy.buildings b ON w.site_id = b.site_id
JOIN energy.meter_readings m ON b.building_id = m.building_id
WHERE w.timestamp >= NOW() - INTERVAL '1 day'
AND m.timestamp BETWEEN w.timestamp - INTERVAL '30 minutes' 
                    AND w.timestamp + INTERVAL '30 minutes'
GROUP BY w.site_id, w.timestamp, w.air_temperature, w.wind_speed
ORDER BY w.timestamp DESC;
```

### 5. Lấy Analytics Results

```sql
SELECT 
    building_id,
    analysis_type,
    time_period_start,
    time_period_end,
    results,
    generated_insights,
    confidence_score
FROM energy.energy_analytics
WHERE created_at >= NOW() - INTERVAL '7 days'
ORDER BY confidence_score DESC;
```

---

## Ví Dụ Flow Hoàn Chỉnh

### Flow 1: Energy Consumption Analysis

```mermaid
flowchart LR
    A[Text Input: Building ID] --> B[SQL Executor]
    B --> C[Data Processing]
    C --> D[LLM Analysis]
    D --> E[Text Output: Insights]
    
    B2[SQL Database] --> B
```

**Cấu hình SQL Executor:**
```sql
SELECT 
    mr.timestamp,
    mr.value,
    mr.meter_type,
    b.primary_space_usage,
    w.air_temperature
FROM energy.meter_readings mr
JOIN energy.buildings b ON mr.building_id = b.building_id
LEFT JOIN energy.weather_data w ON b.site_id = w.site_id 
    AND DATE_TRUNC('hour', mr.timestamp) = DATE_TRUNC('hour', w.timestamp)
WHERE mr.building_id = '{building_id}'
AND mr.timestamp >= NOW() - INTERVAL '30 days'
ORDER BY mr.timestamp DESC;
```

### Flow 2: Real-time Energy Monitoring

```mermaid
flowchart LR
    A[Timer/Scheduler] --> B[SQL Executor: Latest Readings]
    B --> C[Data Validator]
    C --> D[Anomaly Detector]
    D --> E[Alert Generator]
    E --> F[Notification Output]
```

---

## Troubleshooting

### Lỗi Kết Nối Thường Gặp

**1. Connection Refused (Phổ biến nhất)**
```
Error: connection to server at "localhost" (::1), port 5434 failed: Connection refused
```
**Nguyên nhân:** Sử dụng `localhost:5434` từ trong Langflow container  
**❌ Sai:** `postgresql://eaio_user:eaio_password@localhost:5434/eaio_energy`  
**✅ Đúng:** `postgresql://eaio_user:eaio_password@eaio_timescaledb_new:5432/eaio_energy`

**Giải pháp chi tiết:**
1. Kiểm tra containers cùng network:
   ```bash
   docker network inspect lang-stack_lang-stack-network | grep -A 3 "Name.*eaio\|Name.*langflow"
   ```

2. Kiểm tra container database đang chạy:
   ```bash
   docker ps | grep timescale
   ```

3. Test kết nối từ bên ngoài Docker:
   ```bash
   docker exec eaio_timescaledb_new psql -U eaio_user -d eaio_energy -c "SELECT version();"
   ```

**2. Authentication Failed**
```
Error: FATAL: password authentication failed for user "eaio_user"
```
**Giải pháp:**
- Kiểm tra username/password
- Kiểm tra biến môi trường trong container

**3. Database Not Found**
```
Error: FATAL: database "eaio_energy" does not exist
```
**Giải pháp:**
- Kiểm tra tên database: `docker exec eaio_timescaledb_new psql -U eaio_user -l`

### Debug Commands

```bash
# Kiểm tra container status
docker ps | grep timescale

# Kiểm tra logs
docker logs eaio_timescaledb_new

# Test connection từ command line
docker exec eaio_timescaledb_new psql -U eaio_user -d eaio_energy -c "SELECT version();"

# Kiểm tra tables
docker exec eaio_timescaledb_new psql -U eaio_user -d eaio_energy -c "\dt energy.*"
```

---

## Best Practices

### 1. Performance Optimization

- **Sử dụng indexes**: Queries trên timestamp nên sử dụng các index có sẵn
- **Limit results**: Luôn sử dụng LIMIT cho các queries lớn
- **Time range filters**: Sử dụng WHERE conditions cho timestamp

### 2. Security

- **Không hardcode credentials**: Sử dụng environment variables
- **Least privilege**: Chỉ cấp quyền cần thiết cho database user
- **SQL injection prevention**: Sử dụng parameterized queries

### 3. Error Handling

```python
try:
    result = execute_sql_query(query)
except psycopg2.Error as e:
    handle_database_error(e)
except Exception as e:
    handle_general_error(e)
```

---

## Integration với AI/ML

### 1. Data Preparation cho LLM

```sql
-- Chuẩn bị dữ liệu cho LLM analysis
SELECT 
    building_id,
    string_agg(
        'Building: ' || building_id || 
        ', Usage: ' || primary_space_usage || 
        ', EUI: ' || COALESCE(eui::text, 'N/A') ||
        ', Energy Star Score: ' || COALESCE(energy_star_score::text, 'N/A'),
        E'\n'
    ) as building_summary
FROM energy.buildings
WHERE status = 'active'
GROUP BY building_id;
```

### 2. Time Series Analysis

```sql
-- Dữ liệu time series cho ML models
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    building_id,
    meter_type,
    AVG(value) as avg_consumption,
    COUNT(*) as reading_count
FROM energy.meter_readings
WHERE timestamp >= NOW() - INTERVAL '90 days'
AND quality = 'good'
GROUP BY DATE_TRUNC('hour', timestamp), building_id, meter_type
ORDER BY hour, building_id, meter_type;
```

---

## Monitoring và Maintenance

### Health Check Query

```sql
SELECT 
    'Database' as component,
    version() as info,
    current_timestamp as check_time
UNION ALL
SELECT 
    'TimescaleDB Extension',
    extversion,
    current_timestamp
FROM pg_extension 
WHERE extname = 'timescaledb';
```

### Performance Monitoring

```sql
-- Monitor hypertable chunks
SELECT 
    hypertable_name,
    num_chunks,
    compression_enabled
FROM timescaledb_information.hypertables;

-- Monitor query performance
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes
FROM pg_stat_user_tables
WHERE schemaname = 'energy';
```

---

*Tài liệu này cung cấp hướng dẫn đầy đủ để kết nối Langflow với TimescaleDB. Để có kết quả tối ưu, hãy test từng bước và monitor performance của các queries.*