"""
FastAPI Server for Casino Scanner Dashboard
REST API endpoints and WebSocket support for real-time monitoring
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.requests import Request
from typing import List, Dict, Optional
import asyncio
import uuid
import json
from datetime import datetime
from pathlib import Path
import logging
import httpx

from dashboard.database import get_db, Scan, ScanResult, Vulnerability, Target, Plugin as DBPlugin
from dashboard.plugin_manager import get_plugin_manager
from dashboard.plugins.base_plugin import ScanProgress

logger = logging.getLogger(__name__)

app = FastAPI(title="Casino Scanner Dashboard API", version="1.0.0")

# Mount static files and templates
dashboard_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=str(dashboard_dir / "static")), name="static")
templates = Jinja2Templates(directory=str(dashboard_dir / "templates"))

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.scan_subscriptions: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        # Remove from scan subscriptions
        for scan_id, connections in self.scan_subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass
    
    def subscribe_to_scan(self, scan_id: str, websocket: WebSocket):
        if scan_id not in self.scan_subscriptions:
            self.scan_subscriptions[scan_id] = []
        if websocket not in self.scan_subscriptions[scan_id]:
            self.scan_subscriptions[scan_id].append(websocket)
    
    async def send_scan_update(self, scan_id: str, progress: ScanProgress):
        message = json.dumps({
            'type': 'scan_progress',
            'scan_id': scan_id,
            'progress': progress.progress,
            'status': progress.status,
            'message': progress.message,
            'current_step': progress.current_step,
            'total_steps': progress.total_steps,
            'current_step_num': progress.current_step_num
        })
        
        if scan_id in self.scan_subscriptions:
            for connection in self.scan_subscriptions[scan_id]:
                try:
                    await connection.send_text(message)
                except:
                    pass

manager = ConnectionManager()

# Webhook helper function
async def trigger_webhook_async(endpoint: str, data: Dict):
    """
    Trigger a webhook endpoint asynchronously
    Used for Node-RED automation triggers
    """
    try:
        # Get base URL from environment or use default
        base_url = "http://localhost:8000"
        url = f"{base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(url, json=data)
    except Exception as e:
        logger.debug(f"Webhook trigger failed (this is OK if Node-RED not running): {e}")

# Progress callback for plugins
async def progress_callback(scan_id: str, progress: ScanProgress):
    """Callback to send progress updates via WebSocket"""
    await manager.send_scan_update(scan_id, progress)
    
    # Also update database
    db = get_db().get_session()
    try:
        scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
        if scan:
            scan.progress = progress.progress
            scan.status = progress.status
            if progress.status == 'completed':
                scan.completed_at = datetime.utcnow()
            elif progress.status == 'running' and not scan.started_at:
                scan.started_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        logger.error(f"Error updating scan progress: {e}")
    finally:
        db.close()


# Root endpoint - serve dashboard
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})


# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get('type') == 'subscribe':
                scan_id = message.get('scan_id')
                if scan_id:
                    manager.subscribe_to_scan(scan_id, websocket)
                    await manager.send_personal_message(
                        json.dumps({'type': 'subscribed', 'scan_id': scan_id}),
                        websocket
                    )
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# API Endpoints

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics"""
    db = get_db().get_session()
    try:
        total_scans = db.query(Scan).count()
        completed_scans = db.query(Scan).filter(Scan.status == 'completed').count()
        running_scans = db.query(Scan).filter(Scan.status == 'running').count()
        total_vulnerabilities = db.query(Vulnerability).count()
        critical_vulns = db.query(Vulnerability).filter(Vulnerability.severity == 'critical').count()
        high_vulns = db.query(Vulnerability).filter(Vulnerability.severity == 'high').count()
        total_targets = db.query(Target).count()
        
        return {
            'scans': {
                'total': total_scans,
                'completed': completed_scans,
                'running': running_scans,
                'pending': db.query(Scan).filter(Scan.status == 'pending').count(),
                'failed': db.query(Scan).filter(Scan.status == 'failed').count()
            },
            'vulnerabilities': {
                'total': total_vulnerabilities,
                'critical': critical_vulns,
                'high': high_vulns,
                'medium': db.query(Vulnerability).filter(Vulnerability.severity == 'medium').count(),
                'low': db.query(Vulnerability).filter(Vulnerability.severity == 'low').count()
            },
            'targets': {
                'total': total_targets,
                'active': db.query(Target).filter(Target.status == 'active').count()
            }
        }
    finally:
        db.close()


@app.get("/api/scans")
async def list_scans(limit: int = 50, offset: int = 0, status: Optional[str] = None):
    """List scans"""
    db = get_db().get_session()
    try:
        query = db.query(Scan)
        if status:
            query = query.filter(Scan.status == status)
        query = query.order_by(Scan.created_at.desc()).limit(limit).offset(offset)
        
        scans = []
        for scan in query.all():
            scans.append({
                'id': scan.id,
                'scan_id': scan.scan_id,
                'name': scan.name,
                'scan_type': scan.scan_type,
                'region': scan.region,
                'status': scan.status,
                'plugin_name': scan.plugin_name,
                'progress': scan.progress,
                'created_at': scan.created_at.isoformat() if scan.created_at else None,
                'started_at': scan.started_at.isoformat() if scan.started_at else None,
                'completed_at': scan.completed_at.isoformat() if scan.completed_at else None,
                'error_message': scan.error_message
            })
        
        return {'scans': scans, 'total': db.query(Scan).count()}
    finally:
        db.close()


@app.post("/api/scans")
async def create_scan(scan_config: Dict, background_tasks: BackgroundTasks):
    """Create and start a new scan"""
    db = get_db().get_session()
    try:
        plugin_name = scan_config.get('plugin')
        if not plugin_name:
            raise HTTPException(status_code=400, detail="Plugin name is required")
        
        plugin_manager = get_plugin_manager()
        plugin = plugin_manager.get_plugin(plugin_name)
        if not plugin:
            raise HTTPException(status_code=404, detail=f"Plugin '{plugin_name}' not found")
        
        if not plugin.enabled:
            raise HTTPException(status_code=400, detail=f"Plugin '{plugin_name}' is disabled")
        
        # Validate config
        is_valid, error = plugin.validate_config(scan_config)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid config: {error}")
        
        # Create scan record
        scan_id = str(uuid.uuid4())
        scan_name = scan_config.get('name', f"{plugin_name} scan")
        
        scan = Scan(
            scan_id=scan_id,
            name=scan_name,
            scan_type=scan_config.get('scan_type', plugin_name),
            region=scan_config.get('region'),
            status='pending',
            plugin_name=plugin_name,
            config=scan_config,
            progress=0.0
        )
        db.add(scan)
        db.commit()
        
        # Start scan in background
        scan_config['scan_id'] = scan_id
        background_tasks.add_task(run_scan_task, scan_id, plugin_name, scan_config)
        
        logger.info(f"Started scan {scan_id} with plugin {plugin_name}")
        
        return {
            'scan_id': scan_id,
            'status': 'pending',
            'message': 'Scan started',
            'name': scan_name
        }
    finally:
        db.close()


async def run_scan_task(scan_id: str, plugin_name: str, scan_config: Dict):
    """Background task to run scan"""
    db = get_db().get_session()
    plugin_manager = get_plugin_manager()
    plugin = plugin_manager.get_plugin(plugin_name)
    
    if not plugin:
        logger.error(f"Plugin {plugin_name} not found for scan {scan_id}")
        scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
        if scan:
            scan.status = 'failed'
            scan.error_message = f"Plugin {plugin_name} not found"
            db.commit()
        db.close()
        return
    
    try:
        # Update scan status
        scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
        if not scan:
            return
        
        scan.status = 'running'
        scan.started_at = datetime.utcnow()
        db.commit()
        
        # Create progress callback
        async def progress_cb(progress: ScanProgress):
            await progress_callback(scan_id, progress)
        
        # Run scan
        results = await plugin.scan(scan_config, progress_cb)
        
        # Save results
        for result_data in results.get('results', []):
            scan_result = ScanResult(
                scan_id=scan.id,
                result_type=results.get('scan_type', plugin_name),
                target_url=result_data.get('url'),
                target_ip=result_data.get('ip'),
                target_port=result_data.get('port'),
                success=result_data.get('success', False),
                data=result_data,
                screenshot_path=result_data.get('screenshot_path')
            )
            db.add(scan_result)
        
        # Save vulnerabilities and trigger webhooks
        for vuln_data in results.get('vulnerabilities', []):
            vulnerability = Vulnerability(
                scan_id=scan.id,
                title=vuln_data.get('title', 'Unknown'),
                description=vuln_data.get('description', ''),
                severity=vuln_data.get('severity', 'info'),
                vulnerability_type=vuln_data.get('vulnerability_type'),
                url=vuln_data.get('url'),
                ip=vuln_data.get('ip'),
                port=vuln_data.get('port'),
                exploitability=vuln_data.get('exploitability'),
                profit_potential=vuln_data.get('profit_potential'),
                technical_details=vuln_data.get('technical_details'),
                proof_of_concept=vuln_data.get('proof_of_concept'),
                mitigation=vuln_data.get('mitigation')
            )
            db.add(vulnerability)
            db.flush()  # Flush to get the ID
            
            # Trigger vulnerability found webhook (async, don't wait)
            try:
                import httpx
                asyncio.create_task(trigger_webhook_async(
                    '/api/webhooks/vulnerability-found',
                    {
                        'scan_id': scan_id,
                        'vulnerability': {
                            'id': vulnerability.id,
                            'title': vulnerability.title,
                            'severity': vulnerability.severity,
                            'url': vulnerability.url
                        }
                    }
                ))
            except Exception as e:
                logger.warning(f"Failed to trigger vulnerability webhook: {e}")
        
        scan.status = 'completed'
        scan.completed_at = datetime.utcnow()
        scan.progress = 1.0
        db.commit()
        
        # Trigger scan completed webhook (async, don't wait)
        try:
            asyncio.create_task(trigger_webhook_async(
                '/api/webhooks/scan-completed',
                {
                    'scan_id': scan_id,
                    'status': 'completed',
                    'results': {
                        'total_results': len(results.get('results', [])),
                        'total_vulnerabilities': len(results.get('vulnerabilities', []))
                    }
                }
            ))
        except Exception as e:
            logger.warning(f"Failed to trigger scan completed webhook: {e}")
        
    except Exception as e:
        logger.error(f"Error running scan {scan_id}: {e}")
        scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
        if scan:
            scan.status = 'failed'
            scan.error_message = str(e)
            db.commit()
    finally:
        db.close()


@app.get("/api/scans/{scan_id}/export")
async def export_scan(scan_id: str, format: str = "json"):
    """Export scan results - MUST be before /api/scans/{scan_id}"""
    db = get_db().get_session()
    try:
        scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        # Get results and vulnerabilities (scan_id in ScanResult is FK to Scan.id, not scan_id UUID)
        results = db.query(ScanResult).filter(ScanResult.scan_id == scan.id).all()
        vulnerabilities = db.query(Vulnerability).filter(Vulnerability.scan_id == scan.scan_id).all()
        
        export_data = {
            'scan_id': scan.scan_id,
            'name': scan.name,
            'scan_type': scan.scan_type,
            'status': scan.status,
            'created_at': scan.created_at.isoformat() if scan.created_at else None,
            'completed_at': scan.completed_at.isoformat() if scan.completed_at else None,
            'results': [r.data for r in results] if results else [],
            'vulnerabilities': [{
                'title': v.title,
                'description': v.description,
                'severity': v.severity,
                'vulnerability_type': v.vulnerability_type,
                'url': v.url,
                'ip': v.ip,
                'port': v.port
            } for v in vulnerabilities]
        }
        
        if format == "json":
            from fastapi.responses import JSONResponse
            return JSONResponse(content=export_data)
        else:
            raise HTTPException(status_code=400, detail=f"Format {format} not supported")
    finally:
        db.close()


@app.get("/api/scans/{scan_id}")
async def get_scan(scan_id: str):
    """Get scan details"""
    db = get_db().get_session()
    try:
        scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        # Get results
        results = db.query(ScanResult).filter(ScanResult.scan_id == scan.id).all()
        result_list = []
        for result in results:
            result_list.append({
                'id': result.id,
                'result_type': result.result_type,
                'target_url': result.target_url,
                'target_ip': result.target_ip,
                'target_port': result.target_port,
                'success': result.success,
                'data': result.data,
                'screenshot_path': result.screenshot_path,
                'timestamp': result.timestamp.isoformat() if result.timestamp else None
            })
        
        # Get vulnerabilities
        vulnerabilities = db.query(Vulnerability).filter(Vulnerability.scan_id == scan.id).all()
        vuln_list = []
        for vuln in vulnerabilities:
            vuln_list.append({
                'id': vuln.id,
                'title': vuln.title,
                'description': vuln.description,
                'severity': vuln.severity,
                'vulnerability_type': vuln.vulnerability_type,
                'url': vuln.url,
                'ip': vuln.ip,
                'port': vuln.port,
                'exploitability': vuln.exploitability,
                'profit_potential': vuln.profit_potential,
                'technical_details': vuln.technical_details,
                'proof_of_concept': vuln.proof_of_concept,
                'mitigation': vuln.mitigation,
                'discovered_at': vuln.discovered_at.isoformat() if vuln.discovered_at else None
            })
        
        return {
            'scan_id': scan.scan_id,
            'name': scan.name,
            'scan_type': scan.scan_type,
            'region': scan.region,
            'status': scan.status,
            'plugin_name': scan.plugin_name,
            'progress': scan.progress,
            'created_at': scan.created_at.isoformat() if scan.created_at else None,
            'started_at': scan.started_at.isoformat() if scan.started_at else None,
            'completed_at': scan.completed_at.isoformat() if scan.completed_at else None,
            'error_message': scan.error_message,
            'results': result_list,
            'vulnerabilities': vuln_list
        }
    finally:
        db.close()


@app.delete("/api/scans/{scan_id}")
async def cancel_scan(scan_id: str):
    """Cancel a running scan"""
    db = get_db().get_session()
    try:
        scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        if scan.status == 'running':
            # Try to stop via plugin
            plugin_manager = get_plugin_manager()
            plugin = plugin_manager.get_plugin(scan.plugin_name)
            if plugin:
                await plugin.stop_scan(scan_id)
            
            scan.status = 'cancelled'
            db.commit()
        
        return {'status': 'cancelled', 'scan_id': scan_id}
    finally:
        db.close()


@app.get("/api/plugins")
async def list_plugins():
    """List all plugins"""
    plugin_manager = get_plugin_manager()
    plugins = plugin_manager.list_plugins()
    return {'plugins': plugins}


@app.get("/api/plugins/{plugin_name}")
async def get_plugin_info(plugin_name: str):
    """Get plugin information"""
    plugin_manager = get_plugin_manager()
    info = plugin_manager.get_plugin_info(plugin_name)
    if not info:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return info


@app.post("/api/plugins/{plugin_name}/enable")
async def enable_plugin(plugin_name: str):
    """Enable a plugin"""
    plugin_manager = get_plugin_manager()
    if plugin_manager.enable_plugin(plugin_name):
        return {'status': 'enabled', 'plugin': plugin_name}
    raise HTTPException(status_code=404, detail="Plugin not found")


@app.post("/api/plugins/{plugin_name}/disable")
async def disable_plugin(plugin_name: str):
    """Disable a plugin"""
    plugin_manager = get_plugin_manager()
    if plugin_manager.disable_plugin(plugin_name):
        return {'status': 'disabled', 'plugin': plugin_name}
    raise HTTPException(status_code=404, detail="Plugin not found")


@app.get("/api/targets")
async def list_targets(status: Optional[str] = None):
    """List targets"""
    db = get_db().get_session()
    try:
        query = db.query(Target)
        if status:
            query = query.filter(Target.status == status)
        targets = query.order_by(Target.priority.desc(), Target.created_at.desc()).all()
        target_list = []
        for target in targets:
            target_list.append({
                'id': target.id,
                'name': target.name,
                'url': target.url,
                'ip': target.ip,
                'region': target.region,
                'country_code': target.country_code,
                'tags': target.tags,
                'priority': target.priority,
                'status': target.status,
                'notes': target.notes,
                'last_scan_at': target.last_scan_at.isoformat() if target.last_scan_at else None,
                'created_at': target.created_at.isoformat() if target.created_at else None
            })
        return {'targets': target_list}
    finally:
        db.close()


@app.post("/api/targets")
async def create_target(target_data: Dict):
    """Create a new target"""
    db = get_db().get_session()
    try:
        # Validate URL
        url = target_data.get('url', '').strip()
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        # Check if target already exists
        existing = db.query(Target).filter(Target.url == url).first()
        if existing:
            raise HTTPException(status_code=400, detail="Target with this URL already exists")
        
        target = Target(
            name=target_data.get('name', url),
            url=url,
            ip=target_data.get('ip'),
            region=target_data.get('region'),
            country_code=target_data.get('country_code'),
            tags=target_data.get('tags', []),
            priority=target_data.get('priority', 5),
            status=target_data.get('status', 'pending'),
            notes=target_data.get('notes')
        )
        db.add(target)
        db.commit()
        
        # Trigger target discovered webhook (async, don't wait)
        try:
            asyncio.create_task(trigger_webhook_async(
                '/api/webhooks/target-discovered',
                {
                    'target': {
                        'id': target.id,
                        'name': target.name,
                        'url': target.url,
                        'region': target.region,
                        'priority': target.priority
                    },
                    'source': 'manual'
                }
            ))
        except Exception as e:
            logger.warning(f"Failed to trigger target discovered webhook: {e}")
        
        return {'id': target.id, 'status': 'created', 'target': {
            'id': target.id,
            'name': target.name,
            'url': target.url,
            'status': target.status
        }}
    finally:
        db.close()


@app.get("/api/targets/{target_id}")
async def get_target(target_id: int):
    """Get target details"""
    db = get_db().get_session()
    try:
        target = db.query(Target).filter(Target.id == target_id).first()
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        return {
            'id': target.id,
            'name': target.name,
            'url': target.url,
            'ip': target.ip,
            'region': target.region,
            'country_code': target.country_code,
            'tags': target.tags,
            'priority': target.priority,
            'status': target.status,
            'notes': target.notes,
            'last_scan_at': target.last_scan_at.isoformat() if target.last_scan_at else None,
            'created_at': target.created_at.isoformat() if target.created_at else None
        }
    finally:
        db.close()


@app.put("/api/targets/{target_id}")
async def update_target(target_id: int, target_data: Dict):
    """Update a target"""
    db = get_db().get_session()
    try:
        target = db.query(Target).filter(Target.id == target_id).first()
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        # Update fields
        if 'name' in target_data:
            target.name = target_data['name']
        if 'url' in target_data:
            target.url = target_data['url']
        if 'region' in target_data:
            target.region = target_data['region']
        if 'country_code' in target_data:
            target.country_code = target_data['country_code']
        if 'tags' in target_data:
            target.tags = target_data['tags']
        if 'priority' in target_data:
            target.priority = target_data['priority']
        if 'status' in target_data:
            target.status = target_data['status']
        if 'notes' in target_data:
            target.notes = target_data['notes']
        
        db.commit()
        return {'status': 'updated', 'target_id': target_id}
    finally:
        db.close()


@app.delete("/api/targets/{target_id}")
async def delete_target(target_id: int):
    """Delete a target"""
    db = get_db().get_session()
    try:
        target = db.query(Target).filter(Target.id == target_id).first()
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        db.delete(target)
        db.commit()
        return {'status': 'deleted', 'target_id': target_id}
    finally:
        db.close()


@app.post("/api/targets/{target_id}/scan")
async def scan_target(target_id: int, scan_config: Optional[Dict] = None, background_tasks: BackgroundTasks = None):
    """Start a scan for a specific target"""
    db = get_db().get_session()
    try:
        target = db.query(Target).filter(Target.id == target_id).first()
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")
        
        # Determine plugin based on target or config
        plugin_name = scan_config.get('plugin', 'browser') if scan_config else 'browser'
        
        # Create scan config
        scan_data = {
            'plugin': plugin_name,
            'name': f"Scan: {target.name or target.url}",
            'url': target.url,
            'scan_type': scan_config.get('scan_type', 'signup') if scan_config else 'signup'
        }
        
        # Create scan using existing logic
        plugin_manager = get_plugin_manager()
        plugin = plugin_manager.get_plugin(plugin_name)
        if not plugin:
            raise HTTPException(status_code=404, detail=f"Plugin '{plugin_name}' not found")
        
        if not plugin.enabled:
            raise HTTPException(status_code=400, detail=f"Plugin '{plugin_name}' is disabled")
        
        # Validate config
        is_valid, error = plugin.validate_config(scan_data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid config: {error}")
        
        # Create scan record
        scan_id = str(uuid.uuid4())
        scan = Scan(
            scan_id=scan_id,
            name=scan_data['name'],
            scan_type=scan_data.get('scan_type', plugin_name),
            region=target.region,
            status='pending',
            plugin_name=plugin_name,
            config=scan_data,
            progress=0.0
        )
        db.add(scan)
        db.commit()
        
        # Start scan in background
        scan_data['scan_id'] = scan_id
        if background_tasks:
            background_tasks.add_task(run_scan_task, scan_id, plugin_name, scan_data)
        
        # Update target's last_scan_at
        target.last_scan_at = datetime.utcnow()
        db.commit()
        
        return {
            'scan_id': scan_id,
            'status': 'pending',
            'message': 'Scan started',
            'name': scan_data['name']
        }
    finally:
        db.close()


@app.post("/api/quick-scan")
async def quick_scan(request: Request, background_tasks: BackgroundTasks):
    """Quick scan endpoint - useful for browser extension integration"""
    data = await request.json()
    url = data.get('url') or request.query_params.get('url')
    
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")
    
    # Create a temporary target and scan it
    db = get_db().get_session()
    try:
        # Check if target exists
        existing_target = db.query(Target).filter(Target.url == url).first()
        
        if existing_target:
            target_id = existing_target.id
        else:
            # Create temporary target
            target = Target(
                url=url,
                name=url,
                status='active',
                priority=5
            )
            db.add(target)
            db.commit()
            target_id = target.id
        
        # Start scan
        scan_config = {'plugin': 'browser', 'scan_type': 'signup'}
        result = await scan_target(target_id, scan_config, background_tasks)
        
        return {
            'success': True,
            'scan_id': result['scan_id'],
            'target_id': target_id,
            'message': 'Quick scan started'
        }
    finally:
        db.close()


@app.get("/api/vulnerabilities")
async def list_vulnerabilities(limit: int = 50, severity: Optional[str] = None):
    """List vulnerabilities"""
    db = get_db().get_session()
    try:
        query = db.query(Vulnerability)
        if severity:
            query = query.filter(Vulnerability.severity == severity)
        query = query.order_by(Vulnerability.discovered_at.desc()).limit(limit)
        
        vulnerabilities = []
        for vuln in query.all():
            vulnerabilities.append({
                'id': vuln.id,
                'title': vuln.title,
                'description': vuln.description,
                'severity': vuln.severity,
                'vulnerability_type': vuln.vulnerability_type,
                'url': vuln.url,
                'ip': vuln.ip,
                'port': vuln.port,
                'exploitability': vuln.exploitability,
                'profit_potential': vuln.profit_potential,
                'discovered_at': vuln.discovered_at.isoformat() if vuln.discovered_at else None
            })
        
        return {'vulnerabilities': vulnerabilities}
    finally:
        db.close()


@app.post("/api/terminal/execute")
async def execute_terminal_command(request: Request):
    """Execute terminal command"""
    data = await request.json()
    command = data.get('command', '')
    args = data.get('args', [])
    
    # Basic command routing
    parts = command.split(' ')
    cmd = parts[0].lower() if parts else ''
    
    # For now, return a simple response
    # In the future, this could execute actual shell commands (with proper security)
    return {
        "success": False,
        "error": "Command execution via API not yet implemented. Use terminal UI commands.",
        "output": ""
    }


# Browser control endpoints
_browser_instances: Dict[str, any] = {}  # Store browser instances by ID

@app.post("/api/browser/start")
async def start_browser():
    """Start a browser instance"""
    try:
        plugin_manager = get_plugin_manager()
        browser_plugin = plugin_manager.get_plugin('browser')
        
        if not browser_plugin:
            raise HTTPException(status_code=404, detail="Browser plugin not found")
        
        # Create a browser instance ID
        instance_id = str(uuid.uuid4())
        
        # Initialize browser scanner
        from tools.browser_scanner import BrowserScanner
        scanner = BrowserScanner(headless=True, timeout=30000)
        await scanner.start()
        
        _browser_instances[instance_id] = scanner
        
        return {
            "success": True,
            "message": f"Browser started with instance ID: {instance_id}",
            "instance_id": instance_id
        }
    except Exception as e:
        logger.error(f"Error starting browser: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/browser/stop")
async def stop_browser(request: Request = None):
    """Stop a browser instance"""
    try:
        data = {}
        if request and hasattr(request, 'body'):
            try:
                body = await request.body()
                if body:
                    import json
                    data = json.loads(body)
            except:
                pass
        instance_id = data.get('instance_id')
        
        if instance_id and instance_id in _browser_instances:
            scanner = _browser_instances[instance_id]
            await scanner.stop()
            del _browser_instances[instance_id]
            return {"success": True, "message": "Browser stopped"}
        elif len(_browser_instances) > 0:
            # Stop all instances
            for scanner in _browser_instances.values():
                await scanner.stop()
            _browser_instances.clear()
            return {"success": True, "message": "All browser instances stopped"}
        else:
            return {"success": False, "message": "No browser instances running"}
    except Exception as e:
        logger.error(f"Error stopping browser: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/browser/status")
async def browser_status():
    """Get browser status"""
    plugin_manager = get_plugin_manager()
    browser_plugin = plugin_manager.get_plugin('browser')
    
    plugin_status = {}
    if browser_plugin:
        plugin_status = browser_plugin.get_browser_status()
    
    return {
        "success": True,
        "running": len(_browser_instances) > 0 or plugin_status.get('active_instances', 0) > 0,
        "api_instances": len(_browser_instances),
        "api_instance_ids": list(_browser_instances.keys()),
        "plugin_instances": plugin_status.get('active_instances', 0),
        "plugin_instance_ids": plugin_status.get('instance_ids', []),
        "plugin_enabled": plugin_status.get('enabled', False)
    }


# Webhook endpoints for Node-RED automation
@app.post("/api/webhooks/vulnerability-found")
async def webhook_vulnerability_found(request: Request):
    """
    Webhook endpoint for vulnerability found events
    Triggered when a vulnerability is discovered during scanning
    """
    try:
        data = await request.json()
        vulnerability = data.get('vulnerability', {})
        scan_id = data.get('scan_id')
        
        logger.info(f"Webhook: Vulnerability found - {vulnerability.get('title', 'Unknown')} (Scan: {scan_id})")
        
        # Broadcast to WebSocket connections
        await manager.broadcast(json.dumps({
            'type': 'vulnerability_found',
            'scan_id': scan_id,
            'vulnerability': vulnerability
        }))
        
        return {
            "success": True,
            "message": "Vulnerability webhook processed",
            "vulnerability_id": vulnerability.get('id')
        }
    except Exception as e:
        logger.error(f"Error processing vulnerability webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/webhooks/scan-completed")
async def webhook_scan_completed(request: Request):
    """
    Webhook endpoint for scan completed events
    Triggered when a scan finishes (success or failure)
    """
    try:
        data = await request.json()
        scan_id = data.get('scan_id')
        status = data.get('status')
        results = data.get('results', {})
        
        logger.info(f"Webhook: Scan completed - {scan_id} (Status: {status})")
        
        # Broadcast to WebSocket connections
        await manager.broadcast(json.dumps({
            'type': 'scan_completed',
            'scan_id': scan_id,
            'status': status,
            'results_summary': {
                'total_results': results.get('total_results', 0),
                'total_vulnerabilities': results.get('total_vulnerabilities', 0)
            }
        }))
        
        return {
            "success": True,
            "message": "Scan completed webhook processed",
            "scan_id": scan_id
        }
    except Exception as e:
        logger.error(f"Error processing scan completed webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/webhooks/target-discovered")
async def webhook_target_discovered(request: Request):
    """
    Webhook endpoint for target discovered events
    Triggered when a new target is discovered during region/target discovery
    """
    try:
        data = await request.json()
        target = data.get('target', {})
        source = data.get('source', 'unknown')
        
        logger.info(f"Webhook: Target discovered - {target.get('url', 'Unknown')} (Source: {source})")
        
        # Broadcast to WebSocket connections
        await manager.broadcast(json.dumps({
            'type': 'target_discovered',
            'target': target,
            'source': source
        }))
        
        return {
            "success": True,
            "message": "Target discovered webhook processed",
            "target_url": target.get('url')
        }
    except Exception as e:
        logger.error(f"Error processing target discovered webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/node-red/flows")
async def list_node_red_flows():
    """
    List available Node-RED automation flows
    Returns metadata about configured flows
    """
    flows_info = {
        "flows": [
            {
                "id": "vulnerability-alert",
                "name": "Vulnerability Alert Automation",
                "description": "Automates alerts when vulnerabilities are found",
                "trigger": "webhook:/api/webhooks/vulnerability-found",
                "enabled": True
            },
            {
                "id": "scan-orchestration",
                "name": "Scan Orchestration",
                "description": "Orchestrates scan execution and monitoring",
                "trigger": "scheduled or manual",
                "enabled": True
            },
            {
                "id": "target-discovery",
                "name": "Target Discovery Pipeline",
                "description": "Automates target discovery and validation",
                "trigger": "scheduled (daily)",
                "enabled": True
            },
            {
                "id": "continuous-monitoring",
                "name": "Continuous Monitoring",
                "description": "Real-time monitoring and alerting",
                "trigger": "websocket events",
                "enabled": True
            }
        ],
        "webhook_endpoints": [
            "/api/webhooks/vulnerability-found",
            "/api/webhooks/scan-completed",
            "/api/webhooks/target-discovered"
        ]
    }
    return flows_info


@app.get("/api/docs")
async def api_docs():
    """API documentation endpoint"""
    return {
        "endpoints": {
            "GET /api/health": "Health check",
            "GET /api/stats": "Dashboard statistics",
            "GET /api/scans": "List scans (query params: limit, offset, status)",
            "POST /api/scans": "Create new scan (body: plugin, name, scan_type, ...)",
            "GET /api/scans/{scan_id}": "Get scan details",
            "DELETE /api/scans/{scan_id}": "Cancel scan",
            "GET /api/plugins": "List all plugins",
            "GET /api/plugins/{plugin_name}": "Get plugin info",
            "POST /api/plugins/{plugin_name}/enable": "Enable plugin",
            "POST /api/plugins/{plugin_name}/disable": "Disable plugin",
            "GET /api/vulnerabilities": "List vulnerabilities (query params: limit, severity)",
            "GET /api/targets": "List targets",
            "POST /api/targets": "Create target",
            "POST /api/terminal/execute": "Execute terminal command",
            "POST /api/browser/start": "Start browser instance",
            "POST /api/browser/stop": "Stop browser instance",
            "POST /api/browser/status": "Get browser status",
            "WebSocket /ws": "Real-time updates (send: {type: 'subscribe', scan_id: '...'})"
        },
        "example_scan": {
            "shodan": {
                "plugin": "shodan",
                "name": "My Shodan Scan",
                "query": "casino country:VN",
                "limit": 100
            },
            "browser": {
                "plugin": "browser",
                "name": "Browser Test",
                "url": "https://example.com",
                "scan_type": "signup"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

