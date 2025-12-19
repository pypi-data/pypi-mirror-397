# createsonline/server.py
"""
CREATESONLINE Pure Python HTTP Server

Zero external dependencies - runs ASGI apps with just Python stdlib.
Features:
- Internal ASGI HTTP server (no uvicorn needed)
- Built-in auto-reload using stdlib file watcher (no watchdog needed)
- Pure Python implementation
"""

import asyncio
import socket
import json
import time
import traceback
from datetime import datetime
from typing import Callable
from urllib.parse import parse_qs, urlparse
import logging

logger = logging.getLogger("createsonline.server")

# Response classes for easier usage in routes
class InternalResponse:
    def __init__(self, content=b"", status_code=200, headers=None, **kwargs):
        if isinstance(content, str):
            content = content.encode('utf-8')
        self.content = content
        self.body = content  # For compatibility
        self.status_code = status_code
        self.headers = headers or {}

class InternalHTMLResponse(InternalResponse):
    def __init__(self, content="", status_code=200, headers=None, **kwargs):
        if headers is None:
            headers = {}
        headers['content-type'] = 'text/html; charset=utf-8'
        super().__init__(content, status_code, headers, **kwargs)

class InternalJSONResponse(InternalResponse):
    def __init__(self, data, status_code=200, headers=None, **kwargs):
        if headers is None:
            headers = {}
        headers['content-type'] = 'application/json'
        import json
        content = json.dumps(data, indent=2)
        super().__init__(content, status_code, headers, **kwargs)

class CreatesonlineServer:
    """Pure Python HTTP server for ASGI applications"""
    
    def __init__(self, app: Callable, host: str = "0.0.0.0", port: int = 8000):
        self.app = app
        self.host = host
        self.original_port = port
        self.port = self._find_available_port(host, port)
        self.server = None
        
        # Notify if port changed
        if self.port != self.original_port:
            import logging
            logger = logging.getLogger("createsonline")
            logger.warning(f"Port {self.original_port} is busy, using port {self.port} instead")
    
    def _find_available_port(self, host: str, start_port: int, max_attempts: int = 100) -> int:
        """Find an available port starting from start_port"""
        for port in range(start_port, start_port + max_attempts):
            try:
                # Try to bind to the port
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                test_socket.bind((host, port))
                test_socket.close()
                return port
            except OSError:
                # Port is in use, try next one
                continue
        
        # If no port found, raise error
        raise RuntimeError(f"No available ports found between {start_port} and {start_port + max_attempts}")
        
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle individual client connection"""
        start_time = time.time()
        response_size = 0
        status_code = 500
        
        try:
            # Read HTTP request
            request_line = await reader.readline()
            if not request_line:
                return
                
            request_line = request_line.decode('utf-8').strip()
            method, path, _ = request_line.split(' ', 2)
            
            # Read headers
            headers = {}
            while True:
                line = await reader.readline()
                if line == b'\r\n':
                    break
                if line:
                    key, value = line.decode('utf-8').strip().split(':', 1)
                    headers[key.lower()] = value.strip()
            
            # Read body if present
            body = b''
            if 'content-length' in headers:
                content_length = int(headers['content-length'])
                body = await reader.readexactly(content_length)
            
            # Parse URL
            parsed_url = urlparse(path)
            query_string = parsed_url.query.encode() if parsed_url.query else b''
            
            # Build ASGI scope
            scope = {
                'type': 'http',
                'asgi': {'version': '3.0'},
                'http_version': '1.1',
                'method': method,
                'scheme': 'http',
                'path': parsed_url.path,
                'query_string': query_string,
                'root_path': '',
                'headers': [[k.encode(), v.encode()] for k, v in headers.items()],
                'server': (self.host, self.port),
            }
            
            # ASGI receive callable
            body_sent = False
            async def receive():
                nonlocal body_sent
                if not body_sent:
                    body_sent = True
                    return {
                        'type': 'http.request',
                        'body': body,
                        'more_body': False,
                    }
                return {'type': 'http.disconnect'}
            
            # ASGI send callable
            response_started = False
            async def send(message):
                nonlocal response_started, response_size, status_code
                
                if message['type'] == 'http.response.start':
                    response_started = True
                    status_code = message['status']
                    headers = message.get('headers', [])
                    
                    # Write status line
                    writer.write(f'HTTP/1.1 {status_code} OK\r\n'.encode())
                    
                    # Write headers
                    for name, value in headers:
                        writer.write(f'{name.decode()}: {value.decode()}\r\n'.encode())
                    writer.write(b'\r\n')
                    
                elif message['type'] == 'http.response.body':
                    body = message.get('body', b'')
                    if body:
                        response_size += len(body)
                        writer.write(body)
                    await writer.drain()
            
            # Call ASGI app
            await self.app(scope, receive, send)
            
            # Log request after completion
            elapsed_ms = (time.time() - start_time) * 1000
            timestamp = datetime.now().strftime("%H:%M:%S")
            status_indicator = self._get_status_indicator(status_code)
            
            # Format size
            if response_size < 1024:
                size_str = f"{response_size}B"
            elif response_size < 1024 * 1024:
                size_str = f"{response_size / 1024:.1f}KB"
            else:
                size_str = f"{response_size / (1024 * 1024):.1f}MB"
            
            # Color-coded status for better visibility
            status_display = f"{status_code}"
            logger.info(f"[{timestamp}] [{status_indicator}] {method:<6} {path:<50} {status_display:<4} {size_str:>8} {elapsed_ms:>5.0f}ms")
        except Exception as e:
            # Log error to console with full traceback
            elapsed_ms = (time.time() - start_time) * 1000
            timestamp = datetime.now().strftime("%H:%M:%S")
            logger.error(f"[{timestamp}] [XXX] {method:<6} {path:<50} 500  ERROR    {elapsed_ms:>5.0f}ms | {str(e)}")
            
            # Print full traceback to stderr for debugging
            traceback.print_exc()
            
            # Send 500 error
            error_response = json.dumps({
                "error": "Internal Server Error",
                "message": str(e)
            }).encode()
            
            response = (
                b'HTTP/1.1 500 Internal Server Error\r\n'
                b'Content-Type: application/json\r\n'
                b'Content-Length: ' + str(len(error_response)).encode() + b'\r\n'
                b'\r\n'
            ) + error_response
            
            writer.write(response)
            await writer.drain()
        
        finally:
            writer.close()
            await writer.wait_closed()
    
    def _get_status_indicator(self, status: int) -> str:
        """Get visual indicator for HTTP status code"""
        if 200 <= status < 300:
            return "OK "  # Success
        elif 300 <= status < 400:
            return "->>"  # Redirect
        elif 400 <= status < 500:
            return "ERR"  # Client error
        else:
            return "XXX"  # Server error
    
    async def serve(self):
        """Start the server"""
        try:
            self.server = await asyncio.start_server(
                self.handle_client,
                self.host,
                self.port
            )

            # Print enhanced server info with helpful details
            from . import __version__
            startup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Load config for display
            try:
                import user_config
                debug_mode = getattr(user_config, 'DEBUG', False)
                db_url = getattr(user_config, 'DATABASE_URL', 'Not configured')
            except ImportError:
                debug_mode = False
                db_url = 'sqlite:///createsonline.db'

            print("\n" + "=" * 80)
            print(f"  CREATESONLINE v{__version__} - AI-Native Web Framework")
            print("  Pure Python | Zero External Dependencies | Production Ready")
            print("=" * 80)
            print(f"  Started:       {startup_time}")
            print(f"  Server URL:    http://{self.host}:{self.port}")
            print(f"  Debug Mode:    {'Enabled' if debug_mode else 'Disabled'}")
            print(f"  Database:      {db_url.split('?')[0][:60]}")  # Truncate if too long
            print("=" * 80)
            print(f"  Quick Links:")
            print(f"    Home:        http://{self.host}:{self.port}/")
            print(f"    Health:      http://{self.host}:{self.port}/health")
            print(f"    API Docs:    http://{self.host}:{self.port}/docs")
            print("=" * 80)
            print(f"  Press CTRL+C to stop server")
            print("=" * 80)
            print(f"\n{'TIME':<12} {'STATUS':<7} {'METHOD':<8} {'PATH':<50} {'CODE':<6} {'SIZE':<10} {'TIME'}")
            print("-" * 120)
        except OSError as e:
            logger.error(f"Failed to start server on {self.host}:{self.port}")
            logger.error(f"Error: {e}")
            raise
        
        
        async with self.server:
            await self.server.serve_forever()
    
    def run(self):
        """Run the server (blocking)"""
        try:
            asyncio.run(self.serve())
        except KeyboardInterrupt:
            logger.info("Server stopped")
def run_server(app: Callable, host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """
    Run CREATESONLINE pure Python server

    Args:
        app: ASGI application callable
        host: Host to bind to
        port: Port to listen on
        reload: Enable auto-reload on file changes (using internal stdlib file watcher)
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    if reload:
        # Use internal stdlib-only file watcher (no external dependencies)
        import sys
        import subprocess
        import os
        from pathlib import Path

        class InternalFileWatcher:
            """Pure Python file watcher using only stdlib"""

            def __init__(self, watch_path=None, interval=1.0):
                self.watch_path = Path(watch_path or Path.cwd())
                self.interval = interval
                self.process = None
                self.file_mtimes = {}
                self.running = False
                self._scan_files()

            def _scan_files(self):
                """Scan all Python files and record modification times"""
                for py_file in self.watch_path.rglob('*.py'):
                    try:
                        self.file_mtimes[str(py_file)] = py_file.stat().st_mtime
                    except OSError:
                        pass

            def _check_changes(self):
                """Check if any Python files have been modified"""
                changed_files = []

                # Check existing files for modifications
                for filepath, old_mtime in list(self.file_mtimes.items()):
                    try:
                        current_mtime = Path(filepath).stat().st_mtime
                        if current_mtime != old_mtime:
                            changed_files.append(filepath)
                            self.file_mtimes[filepath] = current_mtime
                    except OSError:
                        # File was deleted
                        del self.file_mtimes[filepath]
                        changed_files.append(filepath)

                # Check for new files
                for py_file in self.watch_path.rglob('*.py'):
                    filepath = str(py_file)
                    if filepath not in self.file_mtimes:
                        try:
                            self.file_mtimes[filepath] = py_file.stat().st_mtime
                            changed_files.append(filepath)
                        except OSError:
                            pass

                return changed_files

            def start_server(self):
                """Start the server process"""
                if self.process:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        self.process.kill()

                logger.info("Starting server...")
                self.process = subprocess.Popen([sys.executable] + sys.argv)

            def watch(self):
                """Watch for file changes and restart server"""
                self.running = True
                self.start_server()

                try:
                    import time
                    while self.running:
                        time.sleep(self.interval)
                        changed = self._check_changes()
                        if changed:
                            logger.info(f"File changed: {changed[0]}")
                            if len(changed) > 1:
                                logger.info(f"   (+{len(changed)-1} more files)")
                            self.start_server()
                except KeyboardInterrupt:
                    logger.info("\nStopping auto-reload...")
                    self.running = False
                    if self.process:
                        self.process.terminate()
                        try:
                            self.process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            self.process.kill()

        logger.info("Auto-reload enabled (using internal file watcher)")
        watcher = InternalFileWatcher(interval=1.0)
        watcher.watch()
    else:
        server = CreatesonlineServer(app, host, port)
        server.run()
