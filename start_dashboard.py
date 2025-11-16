#!/usr/bin/env python3
"""
Start the Casino Scanner Dashboard
"""

import sys
from pathlib import Path

# Add user site-packages to path if needed
import site
user_site = site.getusersitepackages()
if user_site:
    sys.path.insert(0, user_site)

import uvicorn
from dashboard.database import get_db
from dashboard.integration import import_all_results

if __name__ == "__main__":
    # Initialize database
    db = get_db()
    db.init_db()
    
    # Import existing results
    print("Importing existing scan results...")
    try:
        imported = import_all_results()
        print(f"Imported {imported} scan(s)")
    except Exception as e:
        print(f"Warning: Could not import existing results: {e}")
    
    # Check for Node-RED (optional)
    try:
        import httpx
        import asyncio
        async def check_node_red():
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    response = await client.get("http://localhost:1880")
                    if response.status_code == 200:
                        print("✓ Node-RED detected and running (automation available)")
                        return True
            except:
                pass
            return False
        
        # Quick check (non-blocking)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        node_red_running = loop.run_until_complete(check_node_red())
        loop.close()
        
        if not node_red_running:
            print("ℹ Node-RED not detected (optional - automation features will be limited)")
            print("  To enable: Install Node-RED and import flows from node-red/flows.json")
    except:
        pass
    
    # Start server
    print("Starting Casino Scanner Dashboard on http://0.0.0.0:8000")
    print("Open http://localhost:8000 in your browser")
    try:
        uvicorn.run(
            "dashboard.api_server:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nShutting down dashboard...")
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()

