#!/usr/bin/env python3
"""
Update Docker Compose Configuration Documentation
Updates Confluence page with comprehensive docker-compose.integrated.yml documentation
"""

import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

class DockerComposeDocUpdater:
    def __init__(self):
        load_dotenv()
        self.base_url = os.getenv('ATLASSIAN_URL')
        self.email = os.getenv('ATLASSIAN_EMAIL')
        self.api_token = os.getenv('ATLASSIAN_API_TOKEN')
        self.space_key = os.getenv('CONFLUENCE_SPACE', 'S')
        self.auth = (self.email, self.api_token)
        self.headers = {'Content-Type': 'application/json'}

        # Target page ID from user
        self.page_id = "38109365"

    def get_page_info(self, page_id: str) -> Optional[Dict]:
        """Get page info including current version"""
        url = f"{self.base_url}/wiki/rest/api/content/{page_id}?expand=version,body.storage"
        response = requests.get(url, auth=self.auth)
        if response.status_code == 200:
            return response.json()
        return None

    def update_page(self, page_id: str, title: str, body: str) -> Optional[Dict]:
        """Update existing Confluence page"""
        page_info = self.get_page_info(page_id)
        if not page_info:
            print(f"❌ Failed to get page info for {page_id}")
            return None

        version = page_info['version']['number']

        update_url = f"{self.base_url}/wiki/rest/api/content/{page_id}"
        payload = {
            'id': page_id,
            'type': 'page',
            'title': title,
            'space': {'key': self.space_key},
            'body': {
                'storage': {
                    'value': body,
                    'representation': 'storage'
                }
            },
            'version': {'number': version + 1}
        }
        response = requests.put(update_url, json=payload, auth=self.auth, headers=self.headers)
        if response.status_code == 200:
            print(f"✅ Updated: {title}")
            return response.json()
        else:
            print(f"❌ Failed to update {title}: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    def get_docker_compose_content(self) -> str:
        """Generate comprehensive Docker Compose documentation content"""
        return """
<h1>Docker Compose Configuration - EAIO Integrated Stack</h1>

<ac:structured-macro ac:name="info">
    <ac:rich-text-body>
        <p><strong>File</strong>: <code>docker-compose.integrated.yml</code></p>
        <p><strong>Purpose</strong>: Integrated Langflow + Langfuse Docker Compose stack for EAIO Energy AI Optimizer</p>
        <p><strong>Services</strong>: 8 containerized services with proper networking and dependencies</p>
        <p><strong>Version</strong>: Docker Compose 3.8</p>
    </ac:rich-text-body>
</ac:structured-macro>

<h2>1. Architecture Overview</h2>

<h3>1.1 Service Topology</h3>
<p>The EAIO system runs 8 interconnected Docker services across 2 main platforms:</p>

<table>
    <tr>
        <th>Platform</th>
        <th>Services</th>
        <th>Purpose</th>
    </tr>
    <tr>
        <td rowspan="2"><strong>Langflow Platform</strong></td>
        <td>langflow</td>
        <td>Visual AI workflow builder & orchestrator</td>
    </tr>
    <tr>
        <td>langflow-postgres</td>
        <td>PostgreSQL database for Langflow metadata</td>
    </tr>
    <tr>
        <td rowspan="6"><strong>Langfuse Platform</strong></td>
        <td>langfuse-web</td>
        <td>Web UI for observability dashboard</td>
    </tr>
    <tr>
        <td>langfuse-worker</td>
        <td>Background worker for trace processing</td>
    </tr>
    <tr>
        <td>langfuse-postgres</td>
        <td>PostgreSQL database for Langfuse metadata</td>
    </tr>
    <tr>
        <td>langfuse-clickhouse</td>
        <td>ClickHouse for analytics & trace storage</td>
    </tr>
    <tr>
        <td>langfuse-minio</td>
        <td>MinIO S3-compatible storage for events/media</td>
    </tr>
    <tr>
        <td>langfuse-redis</td>
        <td>Redis cache for session & job queue</td>
    </tr>
</table>

<h3>1.2 Network Architecture</h3>
<ul>
    <li><strong>Network Name</strong>: <code>lang-stack-network</code></li>
    <li><strong>Driver</strong>: Bridge (default Docker networking)</li>
    <li><strong>Inter-Service Communication</strong>: All 8 services can communicate via internal DNS</li>
    <li><strong>External Access</strong>: Selected ports exposed to host machine</li>
</ul>

<h3>1.3 Dependency Graph</h3>
<ac:structured-macro ac:name="code">
    <ac:parameter ac:name="language">mermaid</ac:parameter>
    <ac:plain-text-body><![CDATA[
graph TD
    A[langflow] --> B[langflow-postgres]
    C[langfuse-web] --> D[langfuse-postgres]
    C --> E[langfuse-clickhouse]
    C --> F[langfuse-minio]
    C --> G[langfuse-redis]
    H[langfuse-worker] --> D
    H --> E
    H --> F
    H --> G
    A -.integration.-> C
]]></ac:plain-text-body>
</ac:structured-macro>

<h2>2. Service Specifications</h2>

<h3>2.1 Langflow Services</h3>

<h4>Service: langflow</h4>
<table>
    <tr>
        <th>Property</th>
        <th>Value</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><strong>Build Context</strong></td>
        <td><code>./Dockerfile.langflow-integrated</code></td>
        <td>Custom build with EAIO agents pre-installed</td>
    </tr>
    <tr>
        <td><strong>Port Mapping</strong></td>
        <td><code>7860:7860</code></td>
        <td>Langflow web UI accessible at http://localhost:7860</td>
    </tr>
    <tr>
        <td><strong>Database</strong></td>
        <td><code>postgresql://langflow:***@langflow-postgres:5432/langflow</code></td>
        <td>Stores workflows, components, user data</td>
    </tr>
    <tr>
        <td><strong>Langfuse Integration</strong></td>
        <td>
            <code>LANGFUSE_HOST=http://langfuse-web:3000</code><br/>
            <code>LANGFUSE_SECRET_KEY</code><br/>
            <code>LANGFUSE_PUBLIC_KEY</code>
        </td>
        <td>Automatic trace sending to local Langfuse instance</td>
    </tr>
    <tr>
        <td><strong>Volume</strong></td>
        <td><code>langflow-data:/app/langflow</code></td>
        <td>Persistent storage for workflow configs</td>
    </tr>
    <tr>
        <td><strong>Dependencies</strong></td>
        <td>langflow-postgres</td>
        <td>Waits for database before starting</td>
    </tr>
</table>

<h4>Service: langflow-postgres</h4>
<table>
    <tr>
        <th>Property</th>
        <th>Value</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><strong>Image</strong></td>
        <td><code>postgres:16</code></td>
        <td>Latest stable PostgreSQL 16</td>
    </tr>
    <tr>
        <td><strong>Port Mapping</strong></td>
        <td><code>5432:5432</code></td>
        <td>Exposed for external DB tools (pgAdmin, DBeaver)</td>
    </tr>
    <tr>
        <td><strong>Credentials</strong></td>
        <td>
            User: <code>langflow</code><br/>
            Password: <code>${POSTGRES_PASSWORD_LANGFLOW}</code><br/>
            Database: <code>langflow</code>
        </td>
        <td>Set via .env file</td>
    </tr>
    <tr>
        <td><strong>Volume</strong></td>
        <td><code>langflow-postgres:/var/lib/postgresql/data</code></td>
        <td>Persistent database storage</td>
    </tr>
</table>

<h3>2.2 Langfuse Services</h3>

<h4>Service: langfuse-web</h4>
<table>
    <tr>
        <th>Property</th>
        <th>Value</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><strong>Image</strong></td>
        <td><code>langfuse/langfuse:3</code></td>
        <td>Official Langfuse version 3 (latest)</td>
    </tr>
    <tr>
        <td><strong>Port Mapping</strong></td>
        <td><code>3000:3000</code></td>
        <td>Langfuse dashboard at http://localhost:3000</td>
    </tr>
    <tr>
        <td><strong>Database</strong></td>
        <td><code>postgresql://postgres:***@langfuse-postgres:5432/postgres</code></td>
        <td>Metadata storage (users, projects, settings)</td>
    </tr>
    <tr>
        <td><strong>Analytics Database</strong></td>
        <td>
            <code>CLICKHOUSE_URL=http://langfuse-clickhouse:8123</code><br/>
            <code>CLICKHOUSE_USER=clickhouse</code>
        </td>
        <td>ClickHouse for fast trace analytics</td>
    </tr>
    <tr>
        <td><strong>Storage</strong></td>
        <td>
            <code>LANGFUSE_S3_EVENT_UPLOAD_BUCKET=langfuse</code><br/>
            <code>LANGFUSE_S3_MEDIA_UPLOAD_BUCKET=langfuse</code><br/>
            MinIO endpoint: <code>http://langfuse-minio:9000</code>
        </td>
        <td>S3-compatible storage for events & media files</td>
    </tr>
    <tr>
        <td><strong>Cache</strong></td>
        <td>
            <code>REDIS_HOST=langfuse-redis</code><br/>
            <code>REDIS_PORT=6379</code>
        </td>
        <td>Redis for session caching & job queue</td>
    </tr>
    <tr>
        <td><strong>Initialization</strong></td>
        <td>
            <code>LANGFUSE_INIT_ORG_NAME</code><br/>
            <code>LANGFUSE_INIT_PROJECT_NAME</code><br/>
            <code>LANGFUSE_INIT_USER_EMAIL</code><br/>
            <code>LANGFUSE_INIT_USER_PASSWORD</code>
        </td>
        <td>Auto-create default organization/project/user on first run</td>
    </tr>
    <tr>
        <td><strong>Security</strong></td>
        <td>
            <code>NEXTAUTH_SECRET</code><br/>
            <code>SALT</code><br/>
            <code>ENCRYPTION_KEY</code>
        </td>
        <td>Authentication & encryption secrets</td>
    </tr>
    <tr>
        <td><strong>Dependencies</strong></td>
        <td>
            langfuse-postgres (healthy)<br/>
            langfuse-clickhouse (healthy)<br/>
            langfuse-minio (healthy)<br/>
            langfuse-redis (healthy)
        </td>
        <td>Waits for all backends to be ready</td>
    </tr>
</table>

<h4>Service: langfuse-worker</h4>
<table>
    <tr>
        <th>Property</th>
        <th>Value</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><strong>Image</strong></td>
        <td><code>langfuse/langfuse-worker:3</code></td>
        <td>Background worker for async trace processing</td>
    </tr>
    <tr>
        <td><strong>Port Mapping</strong></td>
        <td><code>127.0.0.1:3030:3030</code></td>
        <td>Internal worker API (localhost only)</td>
    </tr>
    <tr>
        <td><strong>Environment</strong></td>
        <td>Shares same environment as langfuse-web via YAML anchor</td>
        <td>Ensures consistency between web & worker</td>
    </tr>
    <tr>
        <td><strong>Purpose</strong></td>
        <td>
            - Process incoming traces asynchronously<br/>
            - Aggregate analytics data<br/>
            - Execute batch export jobs
        </td>
        <td>Offloads heavy computation from web service</td>
    </tr>
</table>

<h4>Service: langfuse-postgres</h4>
<table>
    <tr>
        <th>Property</th>
        <th>Value</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><strong>Image</strong></td>
        <td><code>postgres:16</code></td>
        <td>PostgreSQL 16 for Langfuse metadata</td>
    </tr>
    <tr>
        <td><strong>Port Mapping</strong></td>
        <td><code>127.0.0.1:5433:5432</code></td>
        <td>Accessible only from localhost (security)</td>
    </tr>
    <tr>
        <td><strong>Credentials</strong></td>
        <td>
            User: <code>postgres</code><br/>
            Password: <code>${POSTGRES_PASSWORD_LANGFUSE}</code><br/>
            Database: <code>postgres</code>
        </td>
        <td>Set via .env file</td>
    </tr>
    <tr>
        <td><strong>Health Check</strong></td>
        <td><code>pg_isready -U postgres</code></td>
        <td>Every 3s, ensures DB is accepting connections</td>
    </tr>
    <tr>
        <td><strong>Volume</strong></td>
        <td><code>langfuse-postgres-data:/var/lib/postgresql/data</code></td>
        <td>Persistent storage for user data, projects, API keys</td>
    </tr>
</table>

<h4>Service: langfuse-clickhouse</h4>
<table>
    <tr>
        <th>Property</th>
        <th>Value</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><strong>Image</strong></td>
        <td><code>clickhouse/clickhouse-server:latest</code></td>
        <td>ClickHouse columnar database for analytics</td>
    </tr>
    <tr>
        <td><strong>Port Mapping</strong></td>
        <td>
            <code>127.0.0.1:8123:8123</code> (HTTP API)<br/>
            <code>127.0.0.1:9000:9000</code> (Native protocol)
        </td>
        <td>Localhost-only access for security</td>
    </tr>
    <tr>
        <td><strong>Credentials</strong></td>
        <td>
            User: <code>clickhouse</code><br/>
            Password: <code>${CLICKHOUSE_PASSWORD}</code>
        </td>
        <td>Set via .env file</td>
    </tr>
    <tr>
        <td><strong>Health Check</strong></td>
        <td><code>wget http://localhost:8123/ping</code></td>
        <td>Every 5s, 10 retries, 10s start period</td>
    </tr>
    <tr>
        <td><strong>Volumes</strong></td>
        <td>
            <code>langfuse-clickhouse-data:/var/lib/clickhouse</code><br/>
            <code>langfuse-clickhouse-logs:/var/log/clickhouse-server</code>
        </td>
        <td>Persistent storage for trace data & logs</td>
    </tr>
    <tr>
        <td><strong>User</strong></td>
        <td><code>101:101</code></td>
        <td>Non-root user for security</td>
    </tr>
    <tr>
        <td><strong>Purpose</strong></td>
        <td>
            - Store all LLM traces & generations<br/>
            - Fast aggregation queries for dashboard<br/>
            - Optimized for time-series analytics
        </td>
        <td>Handles millions of trace records efficiently</td>
    </tr>
</table>

<h4>Service: langfuse-minio</h4>
<table>
    <tr>
        <th>Property</th>
        <th>Value</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><strong>Image</strong></td>
        <td><code>minio/minio:latest</code></td>
        <td>S3-compatible object storage</td>
    </tr>
    <tr>
        <td><strong>Port Mapping</strong></td>
        <td>
            <code>9090:9000</code> (API)<br/>
            <code>127.0.0.1:9091:9001</code> (Console UI)
        </td>
        <td>API publicly accessible, console localhost-only</td>
    </tr>
    <tr>
        <td><strong>Credentials</strong></td>
        <td>
            <code>MINIO_ROOT_USER</code><br/>
            <code>MINIO_ROOT_PASSWORD</code>
        </td>
        <td>Access/secret keys for S3 API</td>
    </tr>
    <tr>
        <td><strong>Command</strong></td>
        <td><code>mkdir -p /data/langfuse && minio server /data</code></td>
        <td>Auto-create langfuse bucket on startup</td>
    </tr>
    <tr>
        <td><strong>Health Check</strong></td>
        <td><code>mc ready local</code></td>
        <td>Every 5s, MinIO client checks readiness</td>
    </tr>
    <tr>
        <td><strong>Volume</strong></td>
        <td><code>langfuse-minio-data:/data</code></td>
        <td>Persistent storage for event files & media uploads</td>
    </tr>
    <tr>
        <td><strong>Purpose</strong></td>
        <td>
            - Store large trace payloads<br/>
            - Media file uploads (images, audio)<br/>
            - Batch export archives
        </td>
        <td>Offloads large objects from PostgreSQL/ClickHouse</td>
    </tr>
</table>

<h4>Service: langfuse-redis</h4>
<table>
    <tr>
        <th>Property</th>
        <th>Value</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><strong>Image</strong></td>
        <td><code>redis:7</code></td>
        <td>Redis 7 in-memory cache</td>
    </tr>
    <tr>
        <td><strong>Port Mapping</strong></td>
        <td><code>127.0.0.1:6380:6379</code></td>
        <td>Localhost-only access (mapped to 6380 to avoid conflict)</td>
    </tr>
    <tr>
        <td><strong>Authentication</strong></td>
        <td><code>--requirepass ${REDIS_AUTH}</code></td>
        <td>Password-protected Redis instance</td>
    </tr>
    <tr>
        <td><strong>Health Check</strong></td>
        <td><code>redis-cli ping</code></td>
        <td>Every 3s, ensures Redis is responsive</td>
    </tr>
    <tr>
        <td><strong>Purpose</strong></td>
        <td>
            - Session storage for user authentication<br/>
            - Job queue for async worker tasks<br/>
            - Cache for frequently accessed data
        </td>
        <td>Improves performance & enables distributed locking</td>
    </tr>
</table>

<h2>3. Volumes & Persistence</h2>

<h3>3.1 Volume Summary</h3>
<table>
    <tr>
        <th>Volume Name</th>
        <th>Service</th>
        <th>Mount Point</th>
        <th>Data Stored</th>
    </tr>
    <tr>
        <td><code>langflow-postgres</code></td>
        <td>langflow-postgres</td>
        <td><code>/var/lib/postgresql/data</code></td>
        <td>Langflow workflows, components, users</td>
    </tr>
    <tr>
        <td><code>langflow-data</code></td>
        <td>langflow</td>
        <td><code>/app/langflow</code></td>
        <td>Workflow configurations, custom components</td>
    </tr>
    <tr>
        <td><code>langfuse-postgres-data</code></td>
        <td>langfuse-postgres</td>
        <td><code>/var/lib/postgresql/data</code></td>
        <td>Langfuse users, projects, API keys, settings</td>
    </tr>
    <tr>
        <td><code>langfuse-clickhouse-data</code></td>
        <td>langfuse-clickhouse</td>
        <td><code>/var/lib/clickhouse</code></td>
        <td>LLM traces, generations, scores (millions of records)</td>
    </tr>
    <tr>
        <td><code>langfuse-clickhouse-logs</code></td>
        <td>langfuse-clickhouse</td>
        <td><code>/var/log/clickhouse-server</code></td>
        <td>ClickHouse query logs & error logs</td>
    </tr>
    <tr>
        <td><code>langfuse-minio-data</code></td>
        <td>langfuse-minio</td>
        <td><code>/data</code></td>
        <td>Large trace payloads, media files, batch exports</td>
    </tr>
</table>

<h3>3.2 Volume Management Commands</h3>
<ac:structured-macro ac:name="code">
    <ac:parameter ac:name="language">bash</ac:parameter>
    <ac:plain-text-body><![CDATA[
# List all EAIO volumes
docker volume ls | grep langf

# Inspect a specific volume
docker volume inspect langfuse-clickhouse-data

# Backup a volume (example: Langfuse PostgreSQL)
docker run --rm -v langfuse-postgres-data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/langfuse-postgres-backup.tar.gz /data

# Restore a volume
docker run --rm -v langfuse-postgres-data:/data -v $(pwd):/backup \
  ubuntu tar xzf /backup/langfuse-postgres-backup.tar.gz -C /

# Delete all volumes (WARNING: Data loss!)
docker-compose -f docker-compose.integrated.yml down -v
]]></ac:plain-text-body>
</ac:structured-macro>

<h2>4. Environment Variables</h2>

<h3>4.1 Required .env File</h3>
<p>The following environment variables must be set in <code>.env</code> file in the same directory as docker-compose.yml:</p>

<ac:structured-macro ac:name="code">
    <ac:parameter ac:name="language">bash</ac:parameter>
    <ac:plain-text-body><![CDATA[
# Langflow Database
POSTGRES_PASSWORD_LANGFLOW=your_secure_password_here

# Langfuse Database
POSTGRES_PASSWORD_LANGFUSE=your_secure_password_here

# Langfuse ClickHouse
CLICKHOUSE_PASSWORD=your_secure_password_here

# Langfuse MinIO (S3)
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=your_secure_password_here

# Langfuse Redis
REDIS_AUTH=your_secure_password_here

# Langfuse Security Keys
LANGFUSE_SALT=random_salt_string_here
LANGFUSE_ENCRYPTION_KEY=32_char_encryption_key_here
LANGFUSE_NEXTAUTH_SECRET=random_nextauth_secret_here

# Langfuse Initialization (Optional - for first-time setup)
LANGFUSE_INIT_ORG_NAME="EAIO Energy AI"
LANGFUSE_INIT_PROJECT_NAME="Energy Optimizer"
LANGFUSE_INIT_USER_EMAIL="admin@eaio.local"
LANGFUSE_INIT_USER_NAME="EAIO Admin"
LANGFUSE_INIT_USER_PASSWORD="change_on_first_login"

# Langflow-Langfuse Integration
LANGFUSE_SECRET_KEY=sk-lf-...  # Get from Langfuse dashboard
LANGFUSE_PUBLIC_KEY=pk-lf-...  # Get from Langfuse dashboard
LANGFUSE_HOST=http://langfuse-web:3000
]]></ac:plain-text-body>
</ac:structured-macro>

<h3>4.2 Generating Secure Keys</h3>
<ac:structured-macro ac:name="code">
    <ac:parameter ac:name="language">bash</ac:parameter>
    <ac:plain-text-body><![CDATA[
# Generate random passwords
openssl rand -base64 32

# Generate encryption key (exactly 32 characters)
openssl rand -hex 16

# Generate NextAuth secret
openssl rand -base64 32
]]></ac:plain-text-body>
</ac:structured-macro>

<h2>5. Port Mapping Reference</h2>

<h3>5.1 Exposed Ports</h3>
<table>
    <tr>
        <th>Port</th>
        <th>Service</th>
        <th>Purpose</th>
        <th>Access URL</th>
    </tr>
    <tr>
        <td><strong>3000</strong></td>
        <td>langfuse-web</td>
        <td>Langfuse Dashboard</td>
        <td><code>http://localhost:3000</code></td>
    </tr>
    <tr>
        <td><strong>7860</strong></td>
        <td>langflow</td>
        <td>Langflow UI</td>
        <td><code>http://localhost:7860</code></td>
    </tr>
    <tr>
        <td><strong>5432</strong></td>
        <td>langflow-postgres</td>
        <td>Langflow Database</td>
        <td><code>postgresql://langflow:***@localhost:5432/langflow</code></td>
    </tr>
    <tr>
        <td><strong>5433</strong></td>
        <td>langfuse-postgres</td>
        <td>Langfuse Database (localhost only)</td>
        <td><code>postgresql://postgres:***@localhost:5433/postgres</code></td>
    </tr>
    <tr>
        <td><strong>8123</strong></td>
        <td>langfuse-clickhouse</td>
        <td>ClickHouse HTTP API (localhost only)</td>
        <td><code>http://localhost:8123</code></td>
    </tr>
    <tr>
        <td><strong>9000</strong></td>
        <td>langfuse-clickhouse</td>
        <td>ClickHouse Native Protocol (localhost only)</td>
        <td>TCP connection for ClickHouse clients</td>
    </tr>
    <tr>
        <td><strong>9090</strong></td>
        <td>langfuse-minio</td>
        <td>MinIO S3 API</td>
        <td><code>http://localhost:9090</code></td>
    </tr>
    <tr>
        <td><strong>9091</strong></td>
        <td>langfuse-minio</td>
        <td>MinIO Console (localhost only)</td>
        <td><code>http://localhost:9091</code></td>
    </tr>
    <tr>
        <td><strong>6380</strong></td>
        <td>langfuse-redis</td>
        <td>Redis Cache (localhost only)</td>
        <td><code>redis://localhost:6380</code></td>
    </tr>
    <tr>
        <td><strong>3030</strong></td>
        <td>langfuse-worker</td>
        <td>Worker API (localhost only)</td>
        <td>Internal use only</td>
    </tr>
</table>

<h2>6. Deployment Commands</h2>

<h3>6.1 Basic Operations</h3>
<ac:structured-macro ac:name="code">
    <ac:parameter ac:name="language">bash</ac:parameter>
    <ac:plain-text-body><![CDATA[
# Start all services (detached mode)
docker-compose -f docker-compose.integrated.yml up -d

# Start specific services only
docker-compose -f docker-compose.integrated.yml up -d langflow langfuse-web

# View logs (all services)
docker-compose -f docker-compose.integrated.yml logs -f

# View logs (specific service)
docker-compose -f docker-compose.integrated.yml logs -f langflow

# Stop all services (keep volumes)
docker-compose -f docker-compose.integrated.yml down

# Stop all services and remove volumes (WARNING: Data loss!)
docker-compose -f docker-compose.integrated.yml down -v

# Restart a specific service
docker-compose -f docker-compose.integrated.yml restart langflow

# View running services
docker-compose -f docker-compose.integrated.yml ps

# Execute command in running container
docker-compose -f docker-compose.integrated.yml exec langflow bash
]]></ac:plain-text-body>
</ac:structured-macro>

<h3>6.2 Health Checks</h3>
<ac:structured-macro ac:name="code">
    <ac:parameter ac:name="language">bash</ac:parameter>
    <ac:plain-text-body><![CDATA[
# Check health status of all services
docker-compose -f docker-compose.integrated.yml ps

# Check specific service health
docker inspect --format='{{.State.Health.Status}}' langfuse-clickhouse

# View health check logs
docker inspect --format='{{json .State.Health}}' langfuse-postgres | jq
]]></ac:plain-text-body>
</ac:structured-macro>

<h3>6.3 Troubleshooting</h3>
<ac:structured-macro ac:name="code">
    <ac:parameter ac:name="language">bash</ac:parameter>
    <ac:plain-text-body><![CDATA[
# Check if services are running
docker-compose -f docker-compose.integrated.yml ps

# Inspect service configuration
docker-compose -f docker-compose.integrated.yml config

# View resource usage
docker stats

# Check network connectivity
docker network inspect lang-stack-network

# Restart all services with fresh build
docker-compose -f docker-compose.integrated.yml up -d --build --force-recreate

# Remove all containers and start fresh (keeps volumes)
docker-compose -f docker-compose.integrated.yml down && \
docker-compose -f docker-compose.integrated.yml up -d
]]></ac:plain-text-body>
</ac:structured-macro>

<h2>7. Performance Tuning</h2>

<h3>7.1 Resource Limits (Optional)</h3>
<p>Add resource constraints to prevent any single service from consuming all system resources:</p>

<ac:structured-macro ac:name="code">
    <ac:parameter ac:name="language">yaml</ac:parameter>
    <ac:plain-text-body><![CDATA[
langfuse-clickhouse:
  # ... existing config
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 4G
      reservations:
        cpus: '1.0'
        memory: 2G
]]></ac:plain-text-body>
</ac:structured-macro>

<h3>7.2 Database Optimization</h3>
<ul>
    <li><strong>PostgreSQL</strong>: Tune <code>shared_buffers</code>, <code>work_mem</code> via config files</li>
    <li><strong>ClickHouse</strong>: Increase <code>max_memory_usage</code> for large trace datasets</li>
    <li><strong>Redis</strong>: Configure <code>maxmemory</code> and eviction policy</li>
</ul>

<h2>8. Security Best Practices</h2>

<h3>8.1 Network Security</h3>
<ul>
    <li>✅ <strong>Localhost-only ports</strong>: Databases and Redis only accessible from host</li>
    <li>✅ <strong>Internal communication</strong>: Services communicate via internal Docker network</li>
    <li>⚠️ <strong>Public ports</strong>: Only Langflow (7860), Langfuse (3000), and MinIO (9090) exposed</li>
    <li>❌ <strong>Production recommendation</strong>: Use reverse proxy (Nginx) with SSL/TLS</li>
</ul>

<h3>8.2 Credential Management</h3>
<ul>
    <li>✅ <strong>Environment variables</strong>: All secrets in .env file (not committed to Git)</li>
    <li>✅ <strong>Strong passwords</strong>: Use OpenSSL to generate random passwords</li>
    <li>⚠️ <strong>Encryption keys</strong>: LANGFUSE_ENCRYPTION_KEY must be exactly 32 characters</li>
    <li>❌ <strong>Default credentials</strong>: Change LANGFUSE_INIT_USER_PASSWORD on first login</li>
</ul>

<h3>8.3 Data Protection</h3>
<ul>
    <li>✅ <strong>Volume persistence</strong>: All critical data stored in named volumes</li>
    <li>⚠️ <strong>Backup strategy</strong>: Regular backups of PostgreSQL and ClickHouse volumes</li>
    <li>❌ <strong>Disaster recovery</strong>: Document restoration procedures</li>
</ul>

<h2>9. Integration with EAIO System</h2>

<h3>9.1 Langflow Integration</h3>
<p>EAIO agents are deployed as Langflow workflows with automatic tracing:</p>
<ul>
    <li><strong>Agent 1</strong>: Energy Data Intelligence (SQL generation)</li>
    <li><strong>Agent 2</strong>: Weather Intelligence (AccuWeather API)</li>
    <li><strong>Agent 3</strong>: Optimization Strategy (ROI calculations)</li>
    <li><strong>Agent 4</strong>: Forecast Intelligence (IBM Granite TTM)</li>
    <li><strong>Agent 5</strong>: System Control (orchestration)</li>
    <li><strong>Agent 6</strong>: Validator (data quality checks)</li>
</ul>

<h3>9.2 Langfuse Tracing</h3>
<p>All agent invocations are automatically traced to Langfuse via environment variables:</p>
<ac:structured-macro ac:name="code">
    <ac:parameter ac:name="language">python</ac:parameter>
    <ac:plain-text-body><![CDATA[
# Langflow automatically sends traces to Langfuse when configured
# No code changes required - environment variables enable integration

from langfuse import Langfuse

# Already configured via LANGFUSE_HOST, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY
langfuse = Langfuse()

# All LLM calls, agent invocations, and tool uses are traced
# View in Langfuse dashboard at http://localhost:3000
]]></ac:plain-text-body>
</ac:structured-macro>

<h2>10. Monitoring & Maintenance</h2>

<h3>10.1 Log Management</h3>
<ac:structured-macro ac:name="code">
    <ac:parameter ac:name="language">bash</ac:parameter>
    <ac:plain-text-body><![CDATA[
# View last 100 lines of Langflow logs
docker-compose -f docker-compose.integrated.yml logs --tail=100 langflow

# Follow logs in real-time
docker-compose -f docker-compose.integrated.yml logs -f

# Export logs to file
docker-compose -f docker-compose.integrated.yml logs > eaio-logs.txt

# Clear logs (restart containers)
docker-compose -f docker-compose.integrated.yml restart
]]></ac:plain-text-body>
</ac:structured-macro>

<h3>10.2 Database Maintenance</h3>
<ac:structured-macro ac:name="code">
    <ac:parameter ac:name="language">bash</ac:parameter>
    <ac:plain-text-body><![CDATA[
# Connect to Langflow PostgreSQL
docker exec -it langflow-postgres psql -U langflow -d langflow

# Connect to Langfuse PostgreSQL
docker exec -it langfuse-postgres psql -U postgres -d postgres

# Backup Langfuse database
docker exec langfuse-postgres pg_dump -U postgres postgres > langfuse-backup.sql

# ClickHouse query interface
docker exec -it langfuse-clickhouse clickhouse-client
]]></ac:plain-text-body>
</ac:structured-macro>

<h3>10.3 Disk Space Monitoring</h3>
<ac:structured-macro ac:name="code">
    <ac:parameter ac:name="language">bash</ac:parameter>
    <ac:plain-text-body><![CDATA[
# Check volume sizes
docker system df -v

# Clean up unused images/containers
docker system prune -a

# Remove old logs (ClickHouse)
docker exec langfuse-clickhouse rm -rf /var/log/clickhouse-server/*.log
]]></ac:plain-text-body>
</ac:structured-macro>

<h2>11. Troubleshooting Common Issues</h2>

<h3>11.1 Services Not Starting</h3>
<table>
    <tr>
        <th>Symptom</th>
        <th>Possible Cause</th>
        <th>Solution</th>
    </tr>
    <tr>
        <td>langfuse-web fails to start</td>
        <td>Database not ready</td>
        <td>Check <code>docker-compose logs langfuse-postgres</code>, ensure health check passes</td>
    </tr>
    <tr>
        <td>langflow cannot connect to database</td>
        <td>Wrong credentials</td>
        <td>Verify <code>POSTGRES_PASSWORD_LANGFLOW</code> in .env matches database password</td>
    </tr>
    <tr>
        <td>Port already in use error</td>
        <td>Conflicting service</td>
        <td>Change port mapping or stop conflicting service</td>
    </tr>
</table>

<h3>11.2 Performance Issues</h3>
<table>
    <tr>
        <th>Symptom</th>
        <th>Possible Cause</th>
        <th>Solution</th>
    </tr>
    <tr>
        <td>Slow Langfuse dashboard</td>
        <td>ClickHouse memory limit</td>
        <td>Increase Docker memory allocation (Preferences → Resources)</td>
    </tr>
    <tr>
        <td>Langflow workflows timeout</td>
        <td>Resource contention</td>
        <td>Add resource limits to docker-compose.yml, scale horizontally</td>
    </tr>
    <tr>
        <td>Database disk full</td>
        <td>Trace data accumulation</td>
        <td>Configure trace retention policy in Langfuse settings</td>
    </tr>
</table>

<h2>12. Related Documentation</h2>

<ul>
    <li><ac:link><ri:page ri:content-title="DOC_INFRA_Database_Schema_v1.0" /></ac:link></li>
    <li><ac:link><ri:page ri:content-title="DOC_OBS_Comprehensive_Architecture_v1.0" /></ac:link></li>
    <li><ac:link><ri:page ri:content-title="DOC_DEPLOY_Deployment_Guide_v1.0" /></ac:link></li>
    <li><ac:link><ri:page ri:content-title="SMMG6-27" /></ac:link> - US-001: Setup Development Environment</li>
</ul>

<hr/>
<p><strong>Document Version</strong>: 2.0</p>
<p><strong>Last Updated</strong>: October 5, 2025</p>
<p><strong>Maintainer</strong>: EAIO DevOps Team</p>
"""

    def run(self):
        """Execute the documentation update"""
        print("🚀 Updating Docker Compose Configuration Documentation")
        print("=" * 60)

        page_info = self.get_page_info(self.page_id)
        if not page_info:
            print("❌ Failed to retrieve page information")
            return

        print(f"📄 Current Page: {page_info['title']}")
        print(f"📄 Current Version: {page_info['version']['number']}")
        print()

        print("📝 Updating Docker Compose documentation...")
        result = self.update_page(
            page_id=self.page_id,
            title="DOC_INFRA_Docker_Compose_Configuration_v1.0",
            body=self.get_docker_compose_content()
        )

        if result:
            print()
            print("=" * 60)
            print("✅ DOCKER COMPOSE DOCUMENTATION UPDATED!")
            print("=" * 60)
            print("📊 Content Added:")
            print("  - Architecture Overview (8 services)")
            print("  - Service Specifications (detailed configs)")
            print("  - Volume & Persistence Management")
            print("  - Environment Variables Reference")
            print("  - Port Mapping Reference")
            print("  - Deployment Commands")
            print("  - Performance Tuning")
            print("  - Security Best Practices")
            print("  - Integration with EAIO System")
            print("  - Monitoring & Maintenance")
            print("  - Troubleshooting Guide")
            print("=" * 60)
            print(f"🔗 View: https://fistdat.atlassian.net/wiki/spaces/S/pages/{self.page_id}")
            print("=" * 60)
        else:
            print("❌ Failed to update documentation")

if __name__ == "__main__":
    updater = DockerComposeDocUpdater()
    updater.run()
