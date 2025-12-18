#!/usr/bin/env python3
"""
Standalone script to run the approval server.
Ensures binding to 0.0.0.0 for external access.
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import uvicorn
from claude_vault_mcp.approval_server import ApprovalServer

if __name__ == "__main__":
    server = ApprovalServer()
    print(f"🔐 Claude-Vault Approval Server")
    print(f"Running on http://0.0.0.0:{server.port}")
    print(f"Accessible at http://192.168.0.122:{server.port}")
    print(f"Press Ctrl+C to stop")

    # Explicitly bind to 0.0.0.0
    uvicorn.run(
        server.app, host="0.0.0.0", port=server.port, log_level="info"  # Listen on all interfaces
    )
