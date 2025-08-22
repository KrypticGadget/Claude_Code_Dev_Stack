#!/usr/bin/env python3
"""
Agent Metadata Database System
Comprehensive database architecture for agent management, performance tracking, and analytics

This module provides:
- High-performance database layer with async/sync interfaces
- Intelligent agent selection and recommendation engine  
- Real-time performance monitoring and health tracking
- Database migration and backup management
- Optimized queries for dashboard and analytics

Components:
- agent_metadata_db: Core database interface and ORM models
- agent_selector: Intelligent agent recommendation engine
- performance_monitor: Real-time monitoring and health checks  
- migration_manager: Schema evolution and backup/restore

Usage:
    from core.database import (
        create_database_manager,
        create_agent_selector, 
        create_performance_monitor,
        create_migration_manager,
        create_backup_manager
    )
"""

from .agent_metadata_db import (
    # Main classes
    AsyncAgentMetadataDB,
    AgentMetadataDB,
    DatabaseConfig,
    
    # Data models
    Agent,
    ExecutionRecord,
    AgentRecommendation,
    
    # Enums
    AgentTier,
    AgentStatus, 
    ExecutionStatus,
    CommunicationType,
    
    # Factory
    create_database_manager
)

from .agent_selector import (
    # Main classes
    AgentSelectionEngine,
    KeywordExtractor,
    
    # Data models
    SelectionContext,
    AgentScore,
    
    # Factory
    create_agent_selector
)

from .performance_monitor import (
    # Main classes  
    PerformanceMonitor,
    MetricsCollector,
    DashboardQueries,
    
    # Data models
    PerformanceMetric,
    AgentHealthStatus,
    SystemHealthReport,
    PerformanceTrend,
    
    # Factory
    create_performance_monitor
)

from .migration_manager import (
    # Main classes
    MigrationManager,
    BackupManager,
    
    # Data models
    MigrationScript,
    MigrationStatus,
    BackupInfo,
    
    # Factory functions
    create_migration_manager,
    create_backup_manager
)

# Version info
__version__ = "1.0.0"
__author__ = "Claude Code Agent System"

# Export all public APIs
__all__ = [
    # Database core
    "AsyncAgentMetadataDB",
    "AgentMetadataDB", 
    "DatabaseConfig",
    "create_database_manager",
    
    # Data models
    "Agent",
    "ExecutionRecord", 
    "AgentRecommendation",
    "SelectionContext",
    "AgentScore",
    "PerformanceMetric",
    "AgentHealthStatus",
    "SystemHealthReport",
    "PerformanceTrend",
    "MigrationScript",
    "MigrationStatus",
    "BackupInfo",
    
    # Enums
    "AgentTier",
    "AgentStatus",
    "ExecutionStatus", 
    "CommunicationType",
    
    # Main systems
    "AgentSelectionEngine",
    "KeywordExtractor",
    "PerformanceMonitor",
    "MetricsCollector",
    "DashboardQueries",
    "MigrationManager",
    "BackupManager",
    
    # Factory functions
    "create_agent_selector",
    "create_performance_monitor", 
    "create_migration_manager",
    "create_backup_manager"
]