#!/bin/bash
service dbus restart
export PATH=/usr/bin/chrome-linux64:$PATH
python start_mcp_server.py --host 0.0.0.0 --port 18080 --transport sse 
