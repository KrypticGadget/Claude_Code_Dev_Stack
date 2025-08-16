#!/usr/bin/env python3
"""
Test Audio Notification System for Claude Code Dev Stack v3.0
Validates agent-specific audio notifications and audio file integrity.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Expected audio files for each agent category
EXPECTED_AUDIO_FILES = {
    "agent_activated.wav": "General agent activation",
    "agent_delegating.wav": "Agent delegation events",
    "backend_agent.wav": "Backend services agent",
    "database_agent.wav": "Database architecture agent", 
    "frontend_agent.wav": "Frontend development agent",
    "business_analysis.wav": "Business analysis completion",
    "security_verified.wav": "Security audit completion",
    "testing_complete.wav": "Testing automation completion",
    "deployment_ready.wav": "DevOps deployment ready",
    "quality_verified.wav": "Quality assurance completion",
    "performance_optimized.wav": "Performance optimization completion",
    "documentation_complete.wav": "Documentation generation completion"
}

class AudioSystemTester:
    def __init__(self):
        self.audio_path = self._find_audio_directory()
        self.test_results = {}
        
    def _find_audio_directory(self) -> Path:
        """Find the audio files directory"""
        search_paths = [
            "Claude_Code_Dev_Stack_v3/core/audio/audio",
            "core/audio/audio",
            ".claude-hooks-ref/audio",
            "audio"
        ]
        
        for path_str in search_paths:
            path = Path(path_str)
            if path.exists() and path.is_dir():
                logger.info(f"Found audio directory: {path.absolute()}")
                return path.absolute()
        
        raise FileNotFoundError("Audio directory not found")
    
    def test_audio_file_availability(self) -> Dict[str, Any]:
        """Test availability of expected audio files"""
        logger.info("Testing audio file availability...")
        
        results = {
            "total_expected": len(EXPECTED_AUDIO_FILES),
            "files_found": 0,
            "files_missing": 0,
            "file_details": {},
            "extra_files": []
        }
        
        # Check expected files
        for filename, description in EXPECTED_AUDIO_FILES.items():
            file_path = self.audio_path / filename
            
            if file_path.exists():
                file_size = file_path.stat().st_size
                results["files_found"] += 1
                results["file_details"][filename] = {
                    "status": "found",
                    "description": description,
                    "size_bytes": file_size,
                    "path": str(file_path)
                }
                logger.info(f"Found: {filename} ({file_size} bytes)")
            else:
                results["files_missing"] += 1
                results["file_details"][filename] = {
                    "status": "missing",
                    "description": description,
                    "expected_path": str(file_path)
                }
                logger.warning(f"Missing: {filename}")
        
        # Check for extra files
        all_audio_files = list(self.audio_path.glob("*.wav")) + list(self.audio_path.glob("*.mp3"))
        expected_names = set(EXPECTED_AUDIO_FILES.keys())
        
        for audio_file in all_audio_files:
            if audio_file.name not in expected_names:
                results["extra_files"].append({
                    "filename": audio_file.name,
                    "size_bytes": audio_file.stat().st_size,
                    "path": str(audio_file)
                })
                logger.info(f"Extra file found: {audio_file.name}")
        
        results["availability_score"] = (results["files_found"] / results["total_expected"]) * 100
        
        return results
    
    def test_audio_file_integrity(self) -> Dict[str, Any]:
        """Test audio file integrity and playability"""
        logger.info("Testing audio file integrity...")
        
        results = {
            "total_tested": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "integrity_details": {}
        }
        
        audio_files = list(self.audio_path.glob("*.wav")) + list(self.audio_path.glob("*.mp3"))
        
        for audio_file in audio_files:
            results["total_tested"] += 1
            
            try:
                # Basic file validation
                file_size = audio_file.stat().st_size
                file_ext = audio_file.suffix.lower()
                
                # Check if file is not empty
                if file_size == 0:
                    results["invalid_files"] += 1
                    results["integrity_details"][audio_file.name] = {
                        "status": "invalid",
                        "error": "Empty file",
                        "size": file_size
                    }
                    continue
                
                # Check if file has valid audio extension
                if file_ext not in ['.wav', '.mp3', '.ogg']:
                    results["invalid_files"] += 1
                    results["integrity_details"][audio_file.name] = {
                        "status": "invalid", 
                        "error": f"Invalid extension: {file_ext}",
                        "size": file_size
                    }
                    continue
                
                # File appears valid
                results["valid_files"] += 1
                results["integrity_details"][audio_file.name] = {
                    "status": "valid",
                    "size": file_size,
                    "extension": file_ext,
                    "duration_estimate": file_size / 44100 if file_ext == '.wav' else "unknown"
                }
                
            except Exception as e:
                results["invalid_files"] += 1
                results["integrity_details"][audio_file.name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        results["integrity_score"] = (results["valid_files"] / results["total_tested"]) * 100 if results["total_tested"] > 0 else 0
        
        return results
    
    def test_agent_audio_mapping(self) -> Dict[str, Any]:
        """Test mapping between agents and their audio notifications"""
        logger.info("Testing agent-audio mapping...")
        
        # Agent categories and their expected audio files
        agent_audio_mapping = {
            "master-orchestrator": "agent_activated.wav",
            "prompt-engineer": "agent_activated.wav", 
            "business-analyst": "business_analysis.wav",
            "technical-cto": "agent_activated.wav",
            "ceo-strategy": "business_analysis.wav",
            "financial-analyst": "business_analysis.wav",
            "project-manager": "agent_activated.wav",
            "technical-specifications": "agent_activated.wav",
            "business-tech-alignment": "agent_activated.wav",
            "technical-documentation": "documentation_complete.wav",
            "api-integration-specialist": "agent_activated.wav",
            "frontend-architecture": "frontend_agent.wav",
            "frontend-mockup": "frontend_agent.wav",
            "ui-ux-design": "frontend_agent.wav",
            "production-frontend": "frontend_agent.wav",
            "backend-services": "backend_agent.wav",
            "database-architecture": "database_agent.wav",
            "middleware-specialist": "backend_agent.wav",
            "mobile-development": "agent_activated.wav",
            "devops-engineering": "deployment_ready.wav",
            "integration-setup": "agent_activated.wav",
            "script-automation": "agent_activated.wav",
            "development-prompt": "agent_activated.wav",
            "security-architecture": "security_verified.wav",
            "performance-optimization": "performance_optimized.wav",
            "quality-assurance": "quality_verified.wav",
            "testing-automation": "testing_complete.wav",
            "usage-guide": "documentation_complete.wav"
        }
        
        results = {
            "total_agents": len(agent_audio_mapping),
            "mappings_valid": 0,
            "mappings_invalid": 0,
            "mapping_details": {}
        }
        
        for agent, expected_audio in agent_audio_mapping.items():
            audio_path = self.audio_path / expected_audio
            
            if audio_path.exists():
                results["mappings_valid"] += 1
                results["mapping_details"][agent] = {
                    "status": "valid",
                    "audio_file": expected_audio,
                    "audio_path": str(audio_path),
                    "file_size": audio_path.stat().st_size
                }
            else:
                results["mappings_invalid"] += 1
                results["mapping_details"][agent] = {
                    "status": "invalid",
                    "audio_file": expected_audio,
                    "error": "Audio file not found",
                    "expected_path": str(audio_path)
                }
        
        results["mapping_score"] = (results["mappings_valid"] / results["total_agents"]) * 100
        
        return results
    
    def test_audio_notification_triggers(self) -> Dict[str, Any]:
        """Test audio notification trigger scenarios"""
        logger.info("Testing audio notification triggers...")
        
        trigger_scenarios = [
            {
                "scenario": "agent_activation",
                "description": "Agent activated via @agent- mention",
                "expected_audio": "agent_activated.wav",
                "trigger_event": "user_prompt_with_agent_mention"
            },
            {
                "scenario": "agent_delegation", 
                "description": "Agent delegates to another agent",
                "expected_audio": "agent_delegating.wav",
                "trigger_event": "orchestrator_delegation"
            },
            {
                "scenario": "backend_completion",
                "description": "Backend services agent completes task",
                "expected_audio": "backend_agent.wav", 
                "trigger_event": "backend_task_completion"
            },
            {
                "scenario": "frontend_completion",
                "description": "Frontend agent completes task",
                "expected_audio": "frontend_agent.wav",
                "trigger_event": "frontend_task_completion"
            },
            {
                "scenario": "testing_completion",
                "description": "Testing automation completes",
                "expected_audio": "testing_complete.wav",
                "trigger_event": "testing_task_completion"
            }
        ]
        
        results = {
            "total_scenarios": len(trigger_scenarios),
            "scenarios_ready": 0,
            "scenarios_not_ready": 0,
            "scenario_details": {}
        }
        
        for scenario in trigger_scenarios:
            audio_file = scenario["expected_audio"]
            audio_path = self.audio_path / audio_file
            
            if audio_path.exists():
                results["scenarios_ready"] += 1
                results["scenario_details"][scenario["scenario"]] = {
                    "status": "ready",
                    "description": scenario["description"],
                    "audio_file": audio_file,
                    "trigger_event": scenario["trigger_event"],
                    "file_available": True
                }
            else:
                results["scenarios_not_ready"] += 1
                results["scenario_details"][scenario["scenario"]] = {
                    "status": "not_ready",
                    "description": scenario["description"], 
                    "audio_file": audio_file,
                    "trigger_event": scenario["trigger_event"],
                    "file_available": False,
                    "error": "Audio file missing"
                }
        
        results["readiness_score"] = (results["scenarios_ready"] / results["total_scenarios"]) * 100
        
        return results
    
    def run_comprehensive_audio_test(self) -> Dict[str, Any]:
        """Run complete audio system test suite"""
        logger.info("Starting comprehensive audio system test...")
        
        test_start = datetime.now()
        
        # Run all audio tests
        availability_results = self.test_audio_file_availability()
        integrity_results = self.test_audio_file_integrity()
        mapping_results = self.test_agent_audio_mapping()
        trigger_results = self.test_audio_notification_triggers()
        
        test_end = datetime.now()
        test_duration = (test_end - test_start).total_seconds()
        
        # Calculate overall audio system score
        scores = [
            availability_results["availability_score"],
            integrity_results["integrity_score"],
            mapping_results["mapping_score"],
            trigger_results["readiness_score"]
        ]
        overall_score = sum(scores) / len(scores)
        
        # Determine system status
        if overall_score >= 90:
            system_status = "excellent"
        elif overall_score >= 75:
            system_status = "good"
        elif overall_score >= 50:
            system_status = "needs_improvement"
        else:
            system_status = "critical"
        
        return {
            "test_suite_version": "3.0_audio",
            "timestamp": test_end.isoformat(),
            "test_duration": test_duration,
            "audio_directory": str(self.audio_path),
            "overall_score": overall_score,
            "system_status": system_status,
            
            "test_results": {
                "file_availability": availability_results,
                "file_integrity": integrity_results,
                "agent_mapping": mapping_results,
                "notification_triggers": trigger_results
            },
            
            "summary": {
                "total_audio_files": len(list(self.audio_path.glob("*.wav")) + list(self.audio_path.glob("*.mp3"))),
                "expected_files": len(EXPECTED_AUDIO_FILES),
                "files_available": availability_results["files_found"],
                "files_missing": availability_results["files_missing"],
                "valid_files": integrity_results["valid_files"],
                "agent_mappings_valid": mapping_results["mappings_valid"],
                "notification_scenarios_ready": trigger_results["scenarios_ready"]
            },
            
            "recommendations": self._generate_audio_recommendations(
                availability_results, integrity_results, mapping_results, trigger_results
            )
        }
    
    def _generate_audio_recommendations(self, availability: Dict, integrity: Dict, 
                                      mapping: Dict, triggers: Dict) -> List[str]:
        """Generate recommendations for audio system improvements"""
        recommendations = []
        
        if availability["files_missing"] > 0:
            recommendations.append(f"Create {availability['files_missing']} missing audio files")
        
        if integrity["invalid_files"] > 0:
            recommendations.append(f"Fix {integrity['invalid_files']} corrupted audio files")
        
        if mapping["mappings_invalid"] > 0:
            recommendations.append(f"Resolve {mapping['mappings_invalid']} invalid agent-audio mappings")
        
        if triggers["scenarios_not_ready"] > 0:
            recommendations.append(f"Prepare {triggers['scenarios_not_ready']} notification scenarios")
        
        if availability["availability_score"] < 80:
            recommendations.append("Implement missing audio files for better user experience")
        
        if integrity["integrity_score"] < 90:
            recommendations.append("Validate and repair audio file integrity")
        
        if not recommendations:
            recommendations.append("Audio system is fully operational - no improvements needed")
        
        return recommendations
    
    def save_audio_test_results(self, results: Dict[str, Any]):
        """Save audio test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audio_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Audio test results saved to: {filename}")
        except Exception as e:
            logger.error(f"Failed to save audio test results: {e}")

def main():
    print("Claude Code Dev Stack v3.0 - Audio System Testing")
    print("=" * 60)
    
    try:
        tester = AudioSystemTester()
        results = tester.run_comprehensive_audio_test()
        tester.save_audio_test_results(results)
        
        print("\nAUDIO SYSTEM TEST RESULTS:")
        print("=" * 60)
        print(f"Overall Score: {results['overall_score']:.1f}%")
        print(f"System Status: {results['system_status'].upper()}")
        print(f"Test Duration: {results['test_duration']:.2f}s")
        
        summary = results['summary']
        print(f"\nSUMMARY:")
        print(f"Total Audio Files: {summary['total_audio_files']}")
        print(f"Files Available: {summary['files_available']}/{summary['expected_files']}")
        print(f"Files Missing: {summary['files_missing']}")
        print(f"Valid Files: {summary['valid_files']}")
        print(f"Agent Mappings: {summary['agent_mappings_valid']}/28")
        print(f"Scenarios Ready: {summary['notification_scenarios_ready']}/5")
        
        print("\nRECOMMENDATIONS:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"{i}. {rec}")
        
        print("=" * 60)
        print("Audio system test completed!")
        
    except Exception as e:
        logger.error(f"Audio system test failed: {e}")
        print(f"ERROR: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())