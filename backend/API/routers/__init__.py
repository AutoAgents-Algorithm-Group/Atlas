# API Routers Module
from .session import router as session_router, init_session_router
from .chat import router as chat_router, init_chat_router
from .files import router as files_router, init_files_router
from .desktop import router as desktop_router, init_desktop_router
from .system import router as system_router, init_system_router

__all__ = [
    'session_router', 'init_session_router',
    'chat_router', 'init_chat_router', 
    'files_router', 'init_files_router',
    'desktop_router', 'init_desktop_router',
    'system_router', 'init_system_router'
]