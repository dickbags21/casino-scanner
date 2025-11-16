"""
Target Manager Module
Manages target definitions and region-specific configurations
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import yaml

logger = logging.getLogger(__name__)


@dataclass
class Target:
    """Represents a target site"""
    url: str
    region: str
    name: str
    description: Optional[str] = None
    tags: List[str] = None
    priority: int = 5  # 1-10, higher is more important
    status: str = "pending"  # pending, active, completed, failed
    notes: str = ""
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class TargetManager:
    """Manages target definitions and operations"""
    
    def __init__(self, targets_dir: str = "targets"):
        """
        Initialize target manager
        
        Args:
            targets_dir: Directory containing target definitions
        """
        self.targets_dir = Path(targets_dir)
        self.targets_dir.mkdir(parents=True, exist_ok=True)
        self.targets: Dict[str, List[Target]] = {}
    
    def load_targets(self, region: str = None) -> Dict[str, List[Target]]:
        """
        Load targets from files
        
        Args:
            region: Optional region filter
            
        Returns:
            Dictionary mapping region to list of targets
        """
        loaded_targets = {}
        
        # Look for YAML and JSON files in targets directory
        for file_path in self.targets_dir.glob("*.yaml"):
            region_name = file_path.stem
            if region and region_name != region:
                continue
            
            try:
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                    targets = []
                    for target_data in data.get('targets', []):
                        target = Target(**target_data)
                        targets.append(target)
                    loaded_targets[region_name] = targets
                    logger.info(f"Loaded {len(targets)} targets from {file_path}")
            except Exception as e:
                logger.error(f"Error loading targets from {file_path}: {e}")
        
        for file_path in self.targets_dir.glob("*.json"):
            region_name = file_path.stem
            if region and region_name != region:
                continue
            
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    targets = []
                    for target_data in data.get('targets', []):
                        target = Target(**target_data)
                        targets.append(target)
                    loaded_targets[region_name] = targets
                    logger.info(f"Loaded {len(targets)} targets from {file_path}")
            except Exception as e:
                logger.error(f"Error loading targets from {file_path}: {e}")
        
        self.targets = loaded_targets
        return loaded_targets
    
    def get_targets(self, region: str = None, status: str = None) -> List[Target]:
        """
        Get targets filtered by region and/or status
        
        Args:
            region: Optional region filter
            status: Optional status filter
            
        Returns:
            List of Target objects
        """
        all_targets = []
        
        for reg, targets in self.targets.items():
            if region and reg != region:
                continue
            
            for target in targets:
                if status and target.status != status:
                    continue
                all_targets.append(target)
        
        return all_targets
    
    def add_target(self, target: Target, region: str):
        """
        Add a new target
        
        Args:
            target: Target object
            region: Region name
        """
        if region not in self.targets:
            self.targets[region] = []
        
        self.targets[region].append(target)
        self.save_targets(region)
    
    def update_target(self, url: str, region: str, **updates):
        """
        Update target properties
        
        Args:
            url: Target URL
            region: Region name
            **updates: Key-value pairs to update
        """
        targets = self.targets.get(region, [])
        for target in targets:
            if target.url == url:
                for key, value in updates.items():
                    if hasattr(target, key):
                        setattr(target, key, value)
                self.save_targets(region)
                return
        
        logger.warning(f"Target {url} not found in region {region}")
    
    def save_targets(self, region: str):
        """
        Save targets to file
        
        Args:
            region: Region name
        """
        if region not in self.targets:
            return
        
        file_path = self.targets_dir / f"{region}.yaml"
        
        targets_data = {
            'region': region,
            'targets': [asdict(target) for target in self.targets[region]]
        }
        
        try:
            with open(file_path, 'w') as f:
                yaml.dump(targets_data, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Saved {len(self.targets[region])} targets to {file_path}")
        except Exception as e:
            logger.error(f"Error saving targets to {file_path}: {e}")
    
    def export_targets(self, region: str = None, format: str = "json") -> str:
        """
        Export targets to string
        
        Args:
            region: Optional region filter
            format: Export format (json or yaml)
            
        Returns:
            Exported targets as string
        """
        targets_to_export = self.get_targets(region=region)
        
        if format == "json":
            return json.dumps([asdict(t) for t in targets_to_export], indent=2)
        else:
            return yaml.dump([asdict(t) for t in targets_to_export], default_flow_style=False)

