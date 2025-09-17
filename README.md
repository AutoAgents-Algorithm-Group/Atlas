<div align="center">

<img src="https://img.shields.io/badge/-Atlas-000000?style=for-the-badge&labelColor=faf9f6&color=faf9f6&logoColor=000000" alt="Atlas" width="280"/>

<h4>AI-Powered Browser Automation Platform</h4>

**English** | [简体中文](README-CN.md)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="media/dark_license.svg" />
  <img alt="License MIT" src="media/light_license.svg" />
</picture>

</div>

## Table of Contents

- [Why Atlas?](#why-atlas)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Why Atlas?

Atlas is a revolutionary AI browser controller that allows you to control browser operations through natural language conversations. Based on E2B cloud desktop technology, Atlas provides a secure, isolated browser automation environment for complex web operation tasks.

- **Zero Programming Barrier**: Complete complex operations through conversation without writing code
- **Secure and Reliable**: E2B cloud desktop ensures operational security and environment isolation
- **Quick Deployment**: One-click Docker deployment with production environment support
- **Flexible Control**: Seamless switching between AI automation and manual control

## Architecture

Atlas adopts a modern front-end and back-end separation architecture, combined with E2B cloud desktop technology, providing stable and reliable browser automation services.

### Backend (FastAPI + Python)
- **Entry Point**: `backend/API/main.py` - FastAPI application main entry
- **Core Agent**: `backend/Agent/unified_agent.py` - Integrates desktop management and browser automation
- **Desktop Management**: `backend/Desktop/manager.py` - E2B desktop session management
- **Browser Engine**: `backend/Engine/browser_runner.py` - Browser automation engine
- **Modular API**: `backend/API/routers/` - Modular routing design

### Frontend (Next.js + TypeScript)
- **Main Layout**: `frontend/app/layout.tsx` - Application main layout
- **Component Library**: `frontend/components/` - Modern components based on Shadcn/UI
- **Internationalization**: `frontend/messages/` - Support for English and Chinese switching
- **Responsive Design**: ResizablePanel layout with chat interface + desktop preview

### Core Integrations
- **E2B Cloud Desktop**: Remote browser execution environment
- **Browser Use AI**: Natural language browser automation
- **Shadcn/UI**: Modern React component library
- **FastAPI Routers**: Modular API endpoint design

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+

### Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/atlas.git
cd atlas

# 2. Install dependencies
cd frontend && npm install && cd ..
cd backend && pip install -r requirements.txt && cd ..

# 3. Configure environment variables (see Environment Configuration below)
# Create backend/.env and frontend/.env files

# 4. Start development services
make dev
```

### Environment Configuration

Atlas uses a separated environment variable configuration approach for frontend and backend, requiring separate configuration for each.

**Directory Structure**:
```
Atlas/
├── backend/
│   ├── .env              # Backend environment variables
│   └── .env.example      # Backend configuration template
└── frontend/
    ├── .env              # Frontend environment variables
    └── .env.example      # Frontend configuration template
```

**Environment Variable Setup Steps**:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

**Important Notes**:
- Add all `.env` files to `.gitignore` to avoid leaking API keys
- Commit `.env.example` files to version control as configuration templates

## Deployment

### Docker Deployment

#### Production Deployment with Docker Compose
```bash
# 1. Create deployment directory
mkdir -p /path/to/deployment/frank
cd frank

# 2. Download project package
wget -P /root/frank https://your-cdn.com/Atlas.zip
unzip Atlas.zip -x "__MACOSX/*"

# 3. Enter project directory
cd Atlas

# 4. Start services
docker compose -f docker/docker-compose.yml up -d

# 5. View application logs
docker compose -f docker/docker-compose.yml logs -f app
```

#### Environment Variables

**Configuration Method: Separate frontend and backend environment variables**

**Backend Environment Variables** (`backend/.env`):
```bash
# backend/.env
# ==================== Required Configuration ====================
E2B_API_KEY=your_e2b_api_key
OPENAI_API_KEY=your_openai_api_key

# ==================== Optional Configuration ====================
PORT=8100
PYTHONPATH=/app/backend
```

**Frontend Environment Variables** (`frontend/.env`):
```bash
# frontend/.env
# ==================== Frontend Configuration ====================
NEXT_PUBLIC_API_URL=http://localhost:8100

# ==================== Optional Configuration ====================
PORT=3100
NODE_ENV=production
```

**Configuration Description**:
- `E2B_API_KEY`: API key obtained from [E2B](https://e2b.dev)
- `OPENAI_API_KEY`: API key obtained from [OpenAI](https://platform.openai.com)
- `NEXT_PUBLIC_API_URL`: Frontend API address for connecting to backend

**Important Notes**:
- `E2B_API_KEY` and `OPENAI_API_KEY` are **required**, otherwise services will not start properly
- Frontend requires `NEXT_PUBLIC_API_URL` to connect to backend API
- Production environments should use Docker Secrets for managing sensitive information
- Ensure all `.env` files are added to `.gitignore`

#### Troubleshooting
```bash
# Stop and remove old containers
docker stop atlas && docker rm atlas

# Remove old images
docker rmi atlas-app

# Clean up all unused containers and images
docker system prune -f

# If container startup fails, check logs
docker compose -f docker/docker-compose.yml logs app
```

## Contributing

We welcome community contributions! Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

### Development Workflow
1. Fork this project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Enjoy the AI-powered browser automation experience!**

If you have any questions or suggestions, please contact us through [Issues](https://github.com/your-org/atlas/issues).