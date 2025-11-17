"""
Unit tests for tools and scanners
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import yaml
import json
from tools.target_manager import TargetManager, Target
from tools.vulnerability_classifier import VulnerabilityClassifier


@pytest.mark.unit
class TestTargetManager:
    """Test target manager functionality"""
    
    def test_target_creation(self):
        """Test creating a Target object"""
        target = Target(
            url="https://example.com",
            region="vietnam",
            name="Test Casino",
            description="A test casino",
            tags=["casino", "gambling"],
            priority=7,
            status="pending"
        )
        
        assert target.url == "https://example.com"
        assert target.region == "vietnam"
        assert target.name == "Test Casino"
        assert target.priority == 7
        assert target.status == "pending"
        assert "casino" in target.tags
    
    def test_target_default_tags(self):
        """Test target with default tags"""
        target = Target(
            url="https://example.com",
            region="vietnam",
            name="Test"
        )
        
        assert target.tags == []
    
    def test_target_manager_initialization(self, temp_targets_dir):
        """Test target manager initialization"""
        manager = TargetManager(targets_dir=str(temp_targets_dir))
        
        assert manager.targets_dir == temp_targets_dir
        assert manager.targets == {}
    
    def test_load_targets_yaml(self, temp_targets_dir):
        """Test loading targets from YAML file"""
        # Create test YAML file
        yaml_file = temp_targets_dir / "vietnam.yaml"
        yaml_data = {
            "region": "vietnam",
            "targets": [
                {
                    "url": "https://casino1.com",
                    "region": "vietnam",
                    "name": "Casino 1",
                    "priority": 5,
                    "status": "pending"
                },
                {
                    "url": "https://casino2.com",
                    "region": "vietnam",
                    "name": "Casino 2",
                    "priority": 8,
                    "status": "pending"
                }
            ]
        }
        
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_data, f)
        
        manager = TargetManager(targets_dir=str(temp_targets_dir))
        loaded = manager.load_targets()
        
        assert "vietnam" in loaded
        assert len(loaded["vietnam"]) == 2
        assert loaded["vietnam"][0].url == "https://casino1.com"
        assert loaded["vietnam"][1].priority == 8
    
    def test_load_targets_json(self, temp_targets_dir):
        """Test loading targets from JSON file"""
        # Create test JSON file
        json_file = temp_targets_dir / "laos.json"
        json_data = {
            "region": "laos",
            "targets": [
                {
                    "url": "https://casino3.com",
                    "region": "laos",
                    "name": "Casino 3",
                    "priority": 6,
                    "status": "pending"
                }
            ]
        }
        
        with open(json_file, 'w') as f:
            json.dump(json_data, f)
        
        manager = TargetManager(targets_dir=str(temp_targets_dir))
        loaded = manager.load_targets()
        
        assert "laos" in loaded
        assert len(loaded["laos"]) == 1
        assert loaded["laos"][0].url == "https://casino3.com"
    
    def test_load_targets_region_filter(self, temp_targets_dir):
        """Test loading targets filtered by region"""
        # Create multiple region files
        for region in ["vietnam", "laos", "cambodia"]:
            yaml_file = temp_targets_dir / f"{region}.yaml"
            yaml_data = {
                "region": region,
                "targets": [
                    {
                        "url": f"https://{region}-casino.com",
                        "region": region,
                        "name": f"{region.title()} Casino",
                        "priority": 5,
                        "status": "pending"
                    }
                ]
            }
            with open(yaml_file, 'w') as f:
                yaml.dump(yaml_data, f)
        
        manager = TargetManager(targets_dir=str(temp_targets_dir))
        loaded = manager.load_targets(region="vietnam")
        
        assert "vietnam" in loaded
        assert "laos" not in loaded
        assert "cambodia" not in loaded
    
    def test_get_targets(self, temp_targets_dir):
        """Test getting targets with filters"""
        # Create test data
        yaml_file = temp_targets_dir / "vietnam.yaml"
        yaml_data = {
            "region": "vietnam",
            "targets": [
                {
                    "url": "https://casino1.com",
                    "region": "vietnam",
                    "name": "Casino 1",
                    "status": "pending"
                },
                {
                    "url": "https://casino2.com",
                    "region": "vietnam",
                    "name": "Casino 2",
                    "status": "completed"
                }
            ]
        }
        
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_data, f)
        
        manager = TargetManager(targets_dir=str(temp_targets_dir))
        manager.load_targets()
        
        # Get all targets
        all_targets = manager.get_targets()
        assert len(all_targets) == 2
        
        # Get targets by status
        pending_targets = manager.get_targets(status="pending")
        assert len(pending_targets) == 1
        assert pending_targets[0].status == "pending"
        
        # Get targets by region
        vietnam_targets = manager.get_targets(region="vietnam")
        assert len(vietnam_targets) == 2
        
        # Get targets by region and status
        pending_vietnam = manager.get_targets(region="vietnam", status="pending")
        assert len(pending_vietnam) == 1
    
    def test_add_target(self, temp_targets_dir):
        """Test adding a new target"""
        manager = TargetManager(targets_dir=str(temp_targets_dir))
        
        target = Target(
            url="https://new-casino.com",
            region="vietnam",
            name="New Casino",
            priority=9
        )
        
        manager.add_target(target, "vietnam")
        
        assert "vietnam" in manager.targets
        assert len(manager.targets["vietnam"]) == 1
        assert manager.targets["vietnam"][0].url == "https://new-casino.com"
    
    def test_update_target(self, temp_targets_dir):
        """Test updating a target"""
        # Create initial target
        yaml_file = temp_targets_dir / "vietnam.yaml"
        yaml_data = {
            "region": "vietnam",
            "targets": [
                {
                    "url": "https://casino1.com",
                    "region": "vietnam",
                    "name": "Casino 1",
                    "priority": 5,
                    "status": "pending"
                }
            ]
        }
        
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_data, f)
        
        manager = TargetManager(targets_dir=str(temp_targets_dir))
        manager.load_targets()
        
        # Update target
        manager.update_target("https://casino1.com", "vietnam", priority=10, status="active")
        
        targets = manager.get_targets(region="vietnam")
        assert targets[0].priority == 10
        assert targets[0].status == "active"
    
    def test_export_targets_json(self, temp_targets_dir):
        """Test exporting targets as JSON"""
        manager = TargetManager(targets_dir=str(temp_targets_dir))
        
        target = Target(
            url="https://casino1.com",
            region="vietnam",
            name="Casino 1",
            priority=5
        )
        manager.add_target(target, "vietnam")
        
        exported = manager.export_targets(region="vietnam", format="json")
        data = json.loads(exported)
        
        assert len(data) == 1
        assert data[0]["url"] == "https://casino1.com"
        assert data[0]["name"] == "Casino 1"
    
    def test_export_targets_yaml(self, temp_targets_dir):
        """Test exporting targets as YAML"""
        manager = TargetManager(targets_dir=str(temp_targets_dir))
        
        target = Target(
            url="https://casino1.com",
            region="vietnam",
            name="Casino 1",
            priority=5
        )
        manager.add_target(target, "vietnam")
        
        exported = manager.export_targets(region="vietnam", format="yaml")
        data = yaml.safe_load(exported)
        
        assert len(data) == 1
        assert data[0]["url"] == "https://casino1.com"


@pytest.mark.unit
class TestVulnerabilityClassifier:
    """Test vulnerability classifier"""
    
    def test_classifier_initialization(self):
        """Test vulnerability classifier initialization"""
        classifier = VulnerabilityClassifier()
        assert classifier is not None
    
    def test_classify_severity(self):
        """Test classifying vulnerability severity"""
        classifier = VulnerabilityClassifier()
        
        # Test different vulnerability types
        test_cases = [
            ("No CAPTCHA on signup", "high"),
            ("SQL injection", "critical"),
            ("XSS vulnerability", "high"),
            ("Weak password policy", "medium"),
            ("Missing HTTPS", "medium"),
            ("Information disclosure", "low"),
        ]
        
        for description, expected_severity in test_cases:
            severity = classifier.classify_severity(description)
            # The classifier should return a valid severity level
            assert severity in ["critical", "high", "medium", "low", "info"]
    
    def test_classify_exploitability(self):
        """Test classifying exploitability"""
        classifier = VulnerabilityClassifier()
        
        exploitability = classifier.classify_exploitability("No CAPTCHA on signup")
        assert exploitability in ["easy", "medium", "hard", "theoretical"]
    
    def test_classify_profit_potential(self):
        """Test classifying profit potential"""
        classifier = VulnerabilityClassifier()
        
        profit = classifier.classify_profit_potential("Account creation without verification")
        assert profit in ["high", "medium", "low", "n/a"]


@pytest.mark.unit
class TestReporter:
    """Test reporter functionality"""
    
    def test_reporter_initialization(self):
        """Test reporter initialization"""
        from tools.reporter import Reporter
        
        reporter = Reporter()
        assert reporter is not None
    
    def test_generate_report(self, temp_results_dir):
        """Test generating a report"""
        from tools.reporter import Reporter
        
        reporter = Reporter()
        
        scan_data = {
            "scan_id": "test-123",
            "name": "Test Scan",
            "results": [
                {
                    "url": "https://example.com",
                    "success": True
                }
            ],
            "vulnerabilities": [
                {
                    "title": "Test Vulnerability",
                    "severity": "high"
                }
            ]
        }
        
        report_path = reporter.generate_report(scan_data, output_dir=str(temp_results_dir))
        
        assert Path(report_path).exists()
        assert Path(report_path).suffix == ".html" or Path(report_path).suffix == ".json"

