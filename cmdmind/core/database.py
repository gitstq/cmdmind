"""
Command Database Module
SQLite-based persistent storage for command history
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from contextlib import contextmanager


@dataclass
class Command:
    """Represents a single command entry"""
    id: Optional[int] = None
    command: str = ""
    shell: str = "bash"
    exit_code: int = 0
    cwd: str = ""
    timestamp: datetime = None
    tags: List[str] = None
    category: str = "general"
    description: str = ""
    favorite: bool = False
    use_count: int = 1
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat() if self.timestamp else None
        data['tags'] = json.dumps(self.tags) if self.tags else "[]"
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Command":
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if isinstance(data.get('tags'), str):
            data['tags'] = json.loads(data['tags'])
        return cls(**data)


class CommandDatabase:
    """SQLite database manager for command history"""
    
    SCHEMA_VERSION = 1
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            # Default to user's home directory
            db_path = Path.home() / ".cmdmind" / "commands.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Commands table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    shell TEXT DEFAULT 'bash',
                    exit_code INTEGER DEFAULT 0,
                    cwd TEXT DEFAULT '',
                    timestamp TEXT NOT NULL,
                    tags TEXT DEFAULT '[]',
                    category TEXT DEFAULT 'general',
                    description TEXT DEFAULT '',
                    favorite INTEGER DEFAULT 0,
                    use_count INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Indexes for fast queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_commands_timestamp 
                ON commands(timestamp DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_commands_category 
                ON commands(category)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_commands_favorite 
                ON commands(favorite)
            """)
            
            # Full-text search virtual table
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS commands_fts 
                USING fts5(command, description, content='commands', content_rowid='id')
            """)
            
            # Triggers to keep FTS in sync
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS commands_ai AFTER INSERT ON commands BEGIN
                    INSERT INTO commands_fts(rowid, command, description)
                    VALUES (new.id, new.command, new.description);
                END
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS commands_ad AFTER DELETE ON commands BEGIN
                    INSERT INTO commands_fts(commands_fts, rowid, command, description)
                    VALUES('delete', old.id, old.command, old.description);
                END
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS commands_au AFTER UPDATE ON commands BEGIN
                    INSERT INTO commands_fts(commands_fts, rowid, command, description)
                    VALUES('delete', old.id, old.command, old.description);
                    INSERT INTO commands_fts(rowid, command, description)
                    VALUES (new.id, new.command, new.description);
                END
            """)
            
            # Metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            
            # Set schema version
            cursor.execute("""
                INSERT OR REPLACE INTO metadata (key, value) 
                VALUES ('schema_version', ?)
            """, (str(self.SCHEMA_VERSION),))
            
            conn.commit()
    
    def add_command(self, command: Command) -> int:
        """Add a new command to the database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            data = command.to_dict()
            
            cursor.execute("""
                INSERT INTO commands (
                    command, shell, exit_code, cwd, timestamp, tags, 
                    category, description, favorite, use_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['command'], data['shell'], data['exit_code'],
                data['cwd'], data['timestamp'], data['tags'],
                data['category'], data['description'], 
                int(data['favorite']), data['use_count']
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_command(self, command_id: int) -> Optional[Command]:
        """Get a command by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM commands WHERE id = ?", (command_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_command(row)
            return None
    
    def update_command(self, command: Command) -> bool:
        """Update an existing command"""
        if command.id is None:
            return False
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            data = command.to_dict()
            
            cursor.execute("""
                UPDATE commands SET
                    command = ?, shell = ?, exit_code = ?, cwd = ?,
                    tags = ?, category = ?, description = ?, 
                    favorite = ?, use_count = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                data['command'], data['shell'], data['exit_code'],
                data['cwd'], data['tags'], data['category'],
                data['description'], int(data['favorite']), 
                data['use_count'], command.id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_command(self, command_id: int) -> bool:
        """Delete a command by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM commands WHERE id = ?", (command_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_recent_commands(self, limit: int = 100) -> List[Command]:
        """Get most recent commands"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM commands 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            return [self._row_to_command(row) for row in cursor.fetchall()]
    
    def get_favorites(self) -> List[Command]:
        """Get all favorite commands"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM commands 
                WHERE favorite = 1 
                ORDER BY use_count DESC, timestamp DESC
            """)
            
            return [self._row_to_command(row) for row in cursor.fetchall()]
    
    def get_by_category(self, category: str) -> List[Command]:
        """Get commands by category"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM commands 
                WHERE category = ? 
                ORDER BY timestamp DESC
            """, (category,))
            
            return [self._row_to_command(row) for row in cursor.fetchall()]
    
    def search_commands(self, query: str, limit: int = 50) -> List[Command]:
        """Full-text search for commands"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.* FROM commands c
                JOIN commands_fts fts ON c.id = fts.rowid
                WHERE commands_fts MATCH ?
                ORDER BY c.timestamp DESC
                LIMIT ?
            """, (query, limit))
            
            return [self._row_to_command(row) for row in cursor.fetchall()]
    
    def increment_use_count(self, command_id: int) -> bool:
        """Increment the use count for a command"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE commands 
                SET use_count = use_count + 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (command_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total commands
            cursor.execute("SELECT COUNT(*) FROM commands")
            total = cursor.fetchone()[0]
            
            # Commands by category
            cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM commands 
                GROUP BY category 
                ORDER BY count DESC
            """)
            by_category = dict(cursor.fetchall())
            
            # Most used commands
            cursor.execute("""
                SELECT command, use_count 
                FROM commands 
                ORDER BY use_count DESC 
                LIMIT 10
            """)
            most_used = cursor.fetchall()
            
            # Recent activity (last 7 days)
            cursor.execute("""
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM commands
                WHERE timestamp >= DATE('now', '-7 days')
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            """)
            recent_activity = dict(cursor.fetchall())
            
            return {
                "total_commands": total,
                "by_category": by_category,
                "most_used": [(row[0], row[1]) for row in most_used],
                "recent_activity": recent_activity,
            }
    
    def _row_to_command(self, row: sqlite3.Row) -> Command:
        """Convert a database row to a Command object"""
        return Command(
            id=row['id'],
            command=row['command'],
            shell=row['shell'],
            exit_code=row['exit_code'],
            cwd=row['cwd'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            tags=json.loads(row['tags']),
            category=row['category'],
            description=row['description'],
            favorite=bool(row['favorite']),
            use_count=row['use_count'],
        )
    
    def clear_all(self) -> int:
        """Clear all commands from the database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM commands")
            conn.commit()
            return cursor.rowcount
