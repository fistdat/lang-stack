# Streamlit + Langflow Integration App

A Streamlit application that integrates with Langflow API for AI-powered conversations.

## Features

- 💬 Interactive chat interface
- 🔗 Langflow API integration
- 🐳 Docker deployment ready
- ⚙️ Configurable API settings
- 📊 Real-time status monitoring

## Quick Start

### Using Docker Compose (Recommended)

1. Clone or navigate to this directory
2. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` file with your Langflow API credentials:
   ```
   LANGFLOW_API_KEY=your_actual_api_key
   LANGFLOW_API_URL=http://localhost:7860/api/v1/run/your_flow_id
   ```

4. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

5. Open your browser to [http://localhost:8501](http://localhost:8501)

### Using Docker

1. Build the image:
   ```bash
   docker build -t streamlit-langflow .
   ```

2. Run the container:
   ```bash
   docker run -p 8501:8501 \
     -e LANGFLOW_API_KEY=your_api_key \
     -e LANGFLOW_API_URL=your_api_url \
     streamlit-langflow
   ```

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export LANGFLOW_API_KEY=your_api_key
   export LANGFLOW_API_URL=your_api_url
   ```

3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Configuration

### Environment Variables

- `LANGFLOW_API_KEY`: Your Langflow API key
- `LANGFLOW_API_URL`: Complete Langflow API endpoint URL
- `STREAMLIT_SERVER_PORT`: Port for Streamlit server (default: 8501)

### API URL Format

The Langflow API URL should follow this format:
```
http://your-langflow-host:port/api/v1/run/your-flow-id
```

Example (for Docker deployment):
```
http://host.docker.internal:7860/api/v1/run/3f229440-4079-4ee6-bcd3-341accdd9761
```

Example (for local development):
```
http://localhost:7860/api/v1/run/3f229440-4079-4ee6-bcd3-341accdd9761
```

## Usage

1. Configure your API key and URL in the sidebar
2. Test the connection to ensure everything is working
3. Start chatting using the input field at the bottom
4. View raw API responses by enabling the toggle in the sidebar

## Troubleshooting

### Connection Issues

- Ensure Langflow is running and accessible
- Verify the API key is correct
- Check that the API URL format is correct
- Ensure network connectivity between containers (if using Docker)

### Docker Issues

- Make sure Docker and Docker Compose are installed
- Check that ports 8501 is available
- Review Docker logs: `docker-compose logs streamlit-app`

## Development

### File Structure

```
streamlit_app/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker image definition
├── docker-compose.yml # Docker Compose configuration
├── .env.example       # Environment variables template
├── .dockerignore      # Docker ignore file
└── README.md          # This file
```

### Adding New Features

1. Modify `app.py` for new functionality
2. Update `requirements.txt` if new dependencies are needed
3. Test locally before building Docker image
4. Update this README with new configuration options

## License

This project is part of the lang-stack integration system.