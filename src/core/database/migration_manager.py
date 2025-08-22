#!/usr/bin/env python3
"""
Database Migration and Backup Management System
Handles schema evolution, data migration, and backup/restore operations
"""

import asyncio
import json
import os
import shutil
import subprocess
import tempfile
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import hashlib
import gzip
import tarfile

from .agent_metadata_db import AsyncAgentMetadataDB, DatabaseConfig, create_database_manager


# ========== MIGRATION DATA STRUCTURES ==========

@dataclass
class MigrationScript:
    """Database migration script metadata"""
    version: str
    name: str
    description: str
    up_script: str
    down_script: Optional[str]
    checksum: str
    created_at: datetime
    dependencies: List[str]
    
    def calculate_checksum(self) -> str:
        """Calculate script checksum for integrity verification"""
        content = self.up_script + (self.down_script or "")
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass
class MigrationStatus:
    """Migration execution status"""
    version: str
    status: str  # 'pending', 'running', 'completed', 'failed', 'rolled_back'
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    execution_log: List[str]


@dataclass
class BackupInfo:
    """Backup metadata"""
    backup_id: str
    backup_type: str  # 'full', 'incremental', 'schema_only', 'data_only'
    file_path: str
    size_bytes: int
    created_at: datetime
    database_version: str
    schema_version: str
    compressed: bool
    checksum: str
    metadata: Dict[str, Any]


# ========== MIGRATION MANAGER ==========

class MigrationManager:
    """Manages database schema migrations and versioning"""
    
    def __init__(self, db: AsyncAgentMetadataDB, migrations_dir: str):
        self.db = db
        self.migrations_dir = Path(migrations_dir)
        self.logger = logging.getLogger(__name__)
        
        # Ensure migrations directory exists
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        
        # Migration tracking table
        self.migration_table = "schema_migrations"
    
    async def initialize_migration_tracking(self):
        """Initialize migration tracking table"""
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.migration_table} (
            version VARCHAR(50) PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            checksum VARCHAR(64) NOT NULL,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            applied_by VARCHAR(100) DEFAULT CURRENT_USER,
            execution_time_ms INTEGER,
            status VARCHAR(20) DEFAULT 'completed'
        )
        """
        
        async with self.db.get_connection() as conn:
            await conn.execute(query)
        
        self.logger.info("Migration tracking initialized")
    
    def create_migration(self, 
                        name: str,
                        description: str,
                        up_script: str,
                        down_script: str = None) -> MigrationScript:
        """Create a new migration script"""
        
        # Generate version number based on timestamp
        version = datetime.now().strftime("%Y%m%d%H%M%S")
        
        migration = MigrationScript(
            version=version,
            name=name,
            description=description,
            up_script=up_script,
            down_script=down_script,
            checksum="",  # Will be calculated
            created_at=datetime.now(),
            dependencies=[]
        )
        
        migration.checksum = migration.calculate_checksum()
        
        # Save migration files
        self._save_migration_files(migration)
        
        return migration
    
    def _save_migration_files(self, migration: MigrationScript):
        """Save migration scripts to files"""
        
        # Create migration directory
        migration_dir = self.migrations_dir / f"{migration.version}_{migration.name}"
        migration_dir.mkdir(exist_ok=True)
        
        # Save up script
        up_file = migration_dir / "up.sql"
        up_file.write_text(migration.up_script)
        
        # Save down script if provided
        if migration.down_script:
            down_file = migration_dir / "down.sql"
            down_file.write_text(migration.down_script)
        
        # Save metadata
        metadata_file = migration_dir / "metadata.json"
        metadata = {
            "version": migration.version,
            "name": migration.name,
            "description": migration.description,
            "checksum": migration.checksum,
            "created_at": migration.created_at.isoformat(),
            "dependencies": migration.dependencies
        }
        metadata_file.write_text(json.dumps(metadata, indent=2))
        
        self.logger.info(f"Migration {migration.version} saved to {migration_dir}")
    
    def load_migrations(self) -> List[MigrationScript]:
        """Load all migration scripts from disk"""
        
        migrations = []
        
        for migration_dir in sorted(self.migrations_dir.iterdir()):
            if migration_dir.is_dir() and migration_dir.name.count('_') >= 1:
                try:
                    migration = self._load_migration_from_dir(migration_dir)
                    migrations.append(migration)
                except Exception as e:
                    self.logger.error(f"Failed to load migration from {migration_dir}: {e}")
        
        return sorted(migrations, key=lambda m: m.version)
    
    def _load_migration_from_dir(self, migration_dir: Path) -> MigrationScript:
        """Load migration from directory"""
        
        # Load metadata
        metadata_file = migration_dir / "metadata.json"
        if not metadata_file.exists():
            raise ValueError(f"No metadata.json found in {migration_dir}")
        
        metadata = json.loads(metadata_file.read_text())
        
        # Load scripts
        up_file = migration_dir / "up.sql"
        if not up_file.exists():
            raise ValueError(f"No up.sql found in {migration_dir}")
        
        up_script = up_file.read_text()
        
        down_file = migration_dir / "down.sql"
        down_script = down_file.read_text() if down_file.exists() else None
        
        return MigrationScript(
            version=metadata["version"],
            name=metadata["name"],
            description=metadata["description"],
            up_script=up_script,
            down_script=down_script,
            checksum=metadata["checksum"],
            created_at=datetime.fromisoformat(metadata["created_at"]),
            dependencies=metadata.get("dependencies", [])
        )
    
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        
        query = f"SELECT version FROM {self.migration_table} WHERE status = 'completed' ORDER BY version"
        
        async with self.db.get_connection() as conn:
            rows = await conn.fetch(query)
        
        return [row['version'] for row in rows]
    
    async def get_pending_migrations(self) -> List[MigrationScript]:
        """Get list of pending migrations"""
        
        all_migrations = self.load_migrations()
        applied_versions = await self.get_applied_migrations()
        
        return [m for m in all_migrations if m.version not in applied_versions]
    
    async def apply_migration(self, migration: MigrationScript) -> MigrationStatus:
        """Apply a single migration"""
        
        status = MigrationStatus(
            version=migration.version,
            status='running',
            started_at=datetime.now(),
            completed_at=None,
            error_message=None,
            execution_log=[]
        )
        
        try:
            # Record migration start
            await self._record_migration_start(migration)
            
            # Execute migration script
            status.execution_log.append(f"Starting migration {migration.version}")
            
            async with self.db.get_connection() as conn:
                # Execute in transaction
                async with conn.transaction():
                    await conn.execute(migration.up_script)
            
            status.execution_log.append("Migration script executed successfully")
            
            # Record successful completion
            await self._record_migration_completion(migration, True)
            
            status.status = 'completed'
            status.completed_at = datetime.now()
            
            self.logger.info(f"Migration {migration.version} applied successfully")
            
        except Exception as e:
            error_msg = str(e)
            status.status = 'failed'
            status.error_message = error_msg
            status.execution_log.append(f"Error: {error_msg}")
            
            # Record failure
            await self._record_migration_completion(migration, False, error_msg)
            
            self.logger.error(f"Migration {migration.version} failed: {error_msg}")
        
        return status
    
    async def rollback_migration(self, version: str) -> MigrationStatus:
        """Rollback a migration"""
        
        # Load migration
        migrations = self.load_migrations()
        migration = next((m for m in migrations if m.version == version), None)
        
        if not migration:
            raise ValueError(f"Migration {version} not found")
        
        if not migration.down_script:
            raise ValueError(f"Migration {version} has no rollback script")
        
        status = MigrationStatus(
            version=version,
            status='running',
            started_at=datetime.now(),
            completed_at=None,
            error_message=None,
            execution_log=[]
        )
        
        try:
            status.execution_log.append(f"Starting rollback of migration {version}")
            
            async with self.db.get_connection() as conn:
                # Execute rollback script in transaction
                async with conn.transaction():
                    await conn.execute(migration.down_script)
            
            # Remove from migration tracking
            await self._remove_migration_record(version)
            
            status.status = 'rolled_back'
            status.completed_at = datetime.now()
            status.execution_log.append("Rollback completed successfully")
            
            self.logger.info(f"Migration {version} rolled back successfully")
            
        except Exception as e:
            error_msg = str(e)
            status.status = 'failed'
            status.error_message = error_msg
            status.execution_log.append(f"Rollback error: {error_msg}")
            
            self.logger.error(f"Rollback of migration {version} failed: {error_msg}")
        
        return status
    
    async def apply_all_pending(self) -> List[MigrationStatus]:
        """Apply all pending migrations"""
        
        pending = await self.get_pending_migrations()
        results = []
        
        self.logger.info(f"Applying {len(pending)} pending migrations")
        
        for migration in pending:
            status = await self.apply_migration(migration)
            results.append(status)
            
            # Stop on first failure
            if status.status == 'failed':
                self.logger.error(f"Migration failed, stopping at {migration.version}")
                break
        
        return results
    
    async def _record_migration_start(self, migration: MigrationScript):
        """Record migration start in tracking table"""
        
        query = f"""
        INSERT INTO {self.migration_table} (
            version, name, description, checksum, status
        ) VALUES ($1, $2, $3, $4, 'running')
        ON CONFLICT (version) DO UPDATE SET
            status = 'running',
            applied_at = NOW()
        """
        
        async with self.db.get_connection() as conn:
            await conn.execute(query, 
                             migration.version,
                             migration.name, 
                             migration.description,
                             migration.checksum)
    
    async def _record_migration_completion(self, 
                                         migration: MigrationScript,
                                         success: bool,
                                         error_message: str = None):
        """Record migration completion"""
        
        status = 'completed' if success else 'failed'
        
        query = f"""
        UPDATE {self.migration_table} 
        SET 
            status = $1,
            applied_at = NOW(),
            execution_time_ms = EXTRACT(EPOCH FROM (NOW() - applied_at)) * 1000
        WHERE version = $2
        """
        
        async with self.db.get_connection() as conn:
            await conn.execute(query, status, migration.version)
    
    async def _remove_migration_record(self, version: str):
        """Remove migration record (for rollbacks)"""
        
        query = f"DELETE FROM {self.migration_table} WHERE version = $1"
        
        async with self.db.get_connection() as conn:
            await conn.execute(query, version)


# ========== BACKUP MANAGER ==========

class BackupManager:
    """Manages database backups and restore operations"""
    
    def __init__(self, db_config: DatabaseConfig, backup_dir: str):
        self.db_config = db_config
        self.backup_dir = Path(backup_dir)
        self.logger = logging.getLogger(__name__)
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_full_backup(self, 
                               compress: bool = True,
                               include_data: bool = True) -> BackupInfo:
        """Create a full database backup"""
        
        backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_type = "full" if include_data else "schema_only"
        
        # Determine file extension
        ext = ".sql.gz" if compress else ".sql"
        backup_file = self.backup_dir / f"backup_{backup_id}_{backup_type}{ext}"
        
        try:
            # Build pg_dump command
            cmd = [
                "pg_dump",
                f"--host={self.db_config.host}",
                f"--port={self.db_config.port}",
                f"--username={self.db_config.username}",
                f"--dbname={self.db_config.database}",
                "--verbose",
                "--no-password"
            ]
            
            if not include_data:
                cmd.append("--schema-only")
            
            # Set environment for password
            env = os.environ.copy()
            if self.db_config.password:
                env["PGPASSWORD"] = self.db_config.password
            
            # Execute backup
            self.logger.info(f"Starting {backup_type} backup to {backup_file}")
            
            if compress:
                # Pipe through gzip
                with open(backup_file, 'wb') as f:
                    dump_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env)
                    gzip_process = subprocess.Popen(['gzip'], stdin=dump_process.stdout, stdout=f)
                    dump_process.stdout.close()
                    gzip_process.wait()
                    dump_process.wait()
                    
                    if dump_process.returncode != 0:
                        raise subprocess.CalledProcessError(dump_process.returncode, cmd)
            else:
                # Direct output
                with open(backup_file, 'w') as f:
                    result = subprocess.run(cmd, stdout=f, env=env, check=True)
            
            # Get file info
            file_size = backup_file.stat().st_size
            
            # Calculate checksum
            checksum = self._calculate_file_checksum(backup_file)
            
            # Get database version info
            db_version, schema_version = await self._get_version_info()
            
            backup_info = BackupInfo(
                backup_id=backup_id,
                backup_type=backup_type,
                file_path=str(backup_file),
                size_bytes=file_size,
                created_at=datetime.now(),
                database_version=db_version,
                schema_version=schema_version,
                compressed=compress,
                checksum=checksum,
                metadata={
                    "host": self.db_config.host,
                    "database": self.db_config.database,
                    "include_data": include_data
                }
            )
            
            # Save backup metadata
            self._save_backup_metadata(backup_info)
            
            self.logger.info(f"Backup completed: {backup_file} ({file_size} bytes)")
            
            return backup_info
            
        except Exception as e:
            # Clean up failed backup file
            if backup_file.exists():
                backup_file.unlink()
            raise
    
    async def create_incremental_backup(self, base_backup_id: str) -> BackupInfo:
        """Create an incremental backup (simplified - would need WAL archiving in production)"""
        
        # For simplicity, this creates a timestamp-based backup
        # In production, this would use PostgreSQL WAL archiving
        
        backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Query for changes since base backup
        base_backup = self.get_backup_info(base_backup_id)
        if not base_backup:
            raise ValueError(f"Base backup {base_backup_id} not found")
        
        backup_file = self.backup_dir / f"incremental_{backup_id}_from_{base_backup_id}.sql.gz"
        
        # Create backup of data modified since base backup
        query = f"""
        -- This is a simplified incremental backup
        -- In production, use WAL archiving for true incremental backups
        
        COPY (
            SELECT 'execution_history' as table_name, to_json(eh.*) as data
            FROM execution_history eh
            WHERE eh.started_at >= '{base_backup.created_at.isoformat()}'
            
            UNION ALL
            
            SELECT 'agent_audit_log' as table_name, to_json(al.*) as data
            FROM agent_audit_log al  
            WHERE al.created_at >= '{base_backup.created_at.isoformat()}'
        ) TO STDOUT WITH (FORMAT CSV, HEADER)
        """
        
        # Execute incremental backup
        cmd = [
            "psql",
            f"--host={self.db_config.host}",
            f"--port={self.db_config.port}",
            f"--username={self.db_config.username}",
            f"--dbname={self.db_config.database}",
            "--no-password",
            "-c", query
        ]
        
        env = os.environ.copy()
        if self.db_config.password:
            env["PGPASSWORD"] = self.db_config.password
        
        with open(backup_file, 'wb') as f:
            psql_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env)
            gzip_process = subprocess.Popen(['gzip'], stdin=psql_process.stdout, stdout=f)
            psql_process.stdout.close()
            gzip_process.wait()
            psql_process.wait()
        
        file_size = backup_file.stat().st_size
        checksum = self._calculate_file_checksum(backup_file)
        db_version, schema_version = await self._get_version_info()
        
        backup_info = BackupInfo(
            backup_id=backup_id,
            backup_type="incremental",
            file_path=str(backup_file),
            size_bytes=file_size,
            created_at=datetime.now(),
            database_version=db_version,
            schema_version=schema_version,
            compressed=True,
            checksum=checksum,
            metadata={
                "base_backup_id": base_backup_id,
                "base_backup_date": base_backup.created_at.isoformat()
            }
        )
        
        self._save_backup_metadata(backup_info)
        
        return backup_info
    
    def restore_backup(self, backup_id: str, target_database: str = None) -> bool:
        """Restore from backup"""
        
        backup_info = self.get_backup_info(backup_id)
        if not backup_info:
            raise ValueError(f"Backup {backup_id} not found")
        
        backup_file = Path(backup_info.file_path)
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        # Verify checksum
        if self._calculate_file_checksum(backup_file) != backup_info.checksum:
            raise ValueError("Backup file checksum mismatch - file may be corrupted")
        
        target_db = target_database or self.db_config.database
        
        try:
            self.logger.info(f"Restoring backup {backup_id} to database {target_db}")
            
            if backup_info.compressed:
                # Restore from compressed backup
                cmd = [
                    "gunzip", "-c", str(backup_file)
                ]
                restore_cmd = [
                    "psql",
                    f"--host={self.db_config.host}",
                    f"--port={self.db_config.port}",
                    f"--username={self.db_config.username}",
                    f"--dbname={target_db}",
                    "--no-password"
                ]
                
                env = os.environ.copy()
                if self.db_config.password:
                    env["PGPASSWORD"] = self.db_config.password
                
                # Pipe gunzip output to psql
                gunzip_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                psql_process = subprocess.Popen(restore_cmd, stdin=gunzip_process.stdout, env=env)
                gunzip_process.stdout.close()
                
                psql_process.wait()
                gunzip_process.wait()
                
                if psql_process.returncode != 0:
                    raise subprocess.CalledProcessError(psql_process.returncode, restore_cmd)
            else:
                # Restore from uncompressed backup
                cmd = [
                    "psql",
                    f"--host={self.db_config.host}",
                    f"--port={self.db_config.port}",
                    f"--username={self.db_config.username}",
                    f"--dbname={target_db}",
                    "--no-password",
                    "-f", str(backup_file)
                ]
                
                env = os.environ.copy()
                if self.db_config.password:
                    env["PGPASSWORD"] = self.db_config.password
                
                subprocess.run(cmd, env=env, check=True)
            
            self.logger.info(f"Backup {backup_id} restored successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore backup {backup_id}: {e}")
            raise
    
    def list_backups(self) -> List[BackupInfo]:
        """List all available backups"""
        
        backups = []
        metadata_files = list(self.backup_dir.glob("backup_*.json"))
        
        for metadata_file in sorted(metadata_files):
            try:
                backup_info = self._load_backup_metadata(metadata_file)
                backups.append(backup_info)
            except Exception as e:
                self.logger.warning(f"Failed to load backup metadata from {metadata_file}: {e}")
        
        return sorted(backups, key=lambda b: b.created_at, reverse=True)
    
    def get_backup_info(self, backup_id: str) -> Optional[BackupInfo]:
        """Get backup information by ID"""
        
        metadata_file = self.backup_dir / f"backup_{backup_id}.json"
        if not metadata_file.exists():
            return None
        
        return self._load_backup_metadata(metadata_file)
    
    def cleanup_old_backups(self, keep_days: int = 30, keep_count: int = 10):
        """Clean up old backup files"""
        
        backups = self.list_backups()
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        # Keep recent backups and a minimum count
        to_delete = []
        for i, backup in enumerate(backups):
            if i >= keep_count and backup.created_at < cutoff_date:
                to_delete.append(backup)
        
        for backup in to_delete:
            try:
                # Delete backup file
                backup_file = Path(backup.file_path)
                if backup_file.exists():
                    backup_file.unlink()
                
                # Delete metadata
                metadata_file = self.backup_dir / f"backup_{backup.backup_id}.json"
                if metadata_file.exists():
                    metadata_file.unlink()
                
                self.logger.info(f"Deleted old backup {backup.backup_id}")
                
            except Exception as e:
                self.logger.error(f"Failed to delete backup {backup.backup_id}: {e}")
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    async def _get_version_info(self) -> Tuple[str, str]:
        """Get database and schema version information"""
        
        db = create_database_manager(async_mode=True)
        await db.initialize()
        
        try:
            async with db.get_connection() as conn:
                # Get PostgreSQL version
                db_version_result = await conn.fetchval("SELECT version()")
                db_version = db_version_result.split()[1] if db_version_result else "unknown"
                
                # Get schema version
                try:
                    schema_version = await conn.fetchval(
                        "SELECT version FROM schema_versions ORDER BY applied_at DESC LIMIT 1"
                    )
                except:
                    schema_version = "unknown"
                
                return db_version, schema_version or "unknown"
        finally:
            await db.close()
    
    def _save_backup_metadata(self, backup_info: BackupInfo):
        """Save backup metadata to JSON file"""
        
        metadata_file = self.backup_dir / f"backup_{backup_info.backup_id}.json"
        metadata = {
            "backup_id": backup_info.backup_id,
            "backup_type": backup_info.backup_type,
            "file_path": backup_info.file_path,
            "size_bytes": backup_info.size_bytes,
            "created_at": backup_info.created_at.isoformat(),
            "database_version": backup_info.database_version,
            "schema_version": backup_info.schema_version,
            "compressed": backup_info.compressed,
            "checksum": backup_info.checksum,
            "metadata": backup_info.metadata
        }
        
        metadata_file.write_text(json.dumps(metadata, indent=2))
    
    def _load_backup_metadata(self, metadata_file: Path) -> BackupInfo:
        """Load backup metadata from JSON file"""
        
        metadata = json.loads(metadata_file.read_text())
        
        return BackupInfo(
            backup_id=metadata["backup_id"],
            backup_type=metadata["backup_type"],
            file_path=metadata["file_path"],
            size_bytes=metadata["size_bytes"],
            created_at=datetime.fromisoformat(metadata["created_at"]),
            database_version=metadata["database_version"],
            schema_version=metadata["schema_version"],
            compressed=metadata["compressed"],
            checksum=metadata["checksum"],
            metadata=metadata["metadata"]
        )


# ========== FACTORY FUNCTIONS ==========

async def create_migration_manager(migrations_dir: str = None) -> MigrationManager:
    """Create and initialize migration manager"""
    
    if migrations_dir is None:
        migrations_dir = str(Path.home() / ".claude" / "migrations")
    
    db = create_database_manager(async_mode=True)
    await db.initialize()
    
    manager = MigrationManager(db, migrations_dir)
    await manager.initialize_migration_tracking()
    
    return manager


def create_backup_manager(backup_dir: str = None) -> BackupManager:
    """Create backup manager"""
    
    if backup_dir is None:
        backup_dir = str(Path.home() / ".claude" / "backups")
    
    config = DatabaseConfig.from_env()
    return BackupManager(config, backup_dir)


# ========== EXAMPLE USAGE ==========

async def example_migration_and_backup():
    """Example usage of migration and backup systems"""
    
    # Migration example
    migration_manager = await create_migration_manager()
    
    try:
        # Create a sample migration
        sample_migration = migration_manager.create_migration(
            name="add_user_preferences",
            description="Add user preferences table",
            up_script="""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id VARCHAR(100) NOT NULL,
                preferences JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            CREATE INDEX idx_user_preferences_user ON user_preferences(user_id);
            """,
            down_script="""
            DROP TABLE IF EXISTS user_preferences;
            """
        )
        
        print(f"Created migration: {sample_migration.version}")
        
        # Check pending migrations
        pending = await migration_manager.get_pending_migrations()
        print(f"Pending migrations: {len(pending)}")
        
        # Apply migrations (commented out to avoid actual changes)
        # results = await migration_manager.apply_all_pending()
        # print(f"Applied {len(results)} migrations")
        
    finally:
        await migration_manager.db.close()
    
    # Backup example
    backup_manager = create_backup_manager()
    
    try:
        # Create full backup
        backup_info = await backup_manager.create_full_backup(compress=True)
        print(f"Created backup: {backup_info.backup_id}")
        print(f"Backup size: {backup_info.size_bytes} bytes")
        
        # List backups
        backups = backup_manager.list_backups()
        print(f"Total backups: {len(backups)}")
        
        # Cleanup old backups (dry run)
        print("Would clean up old backups")
        
    except Exception as e:
        print(f"Backup example failed: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example_migration_and_backup())