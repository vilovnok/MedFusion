from .auth import router as router_auth
from .message import router as router_message


all_routers = [
    router_auth,
    router_message
]
