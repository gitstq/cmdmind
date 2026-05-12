"""
Command Searcher Module
Semantic and fuzzy search for command history
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from rapidfuzz import fuzz, process

from cmdmind.core.database import Command, CommandDatabase


@dataclass
class SearchResult:
    """Represents a search result with relevance score"""
    command: Command
    score: float
    match_type: str  # 'exact', 'fuzzy', 'semantic', 'category'


class CommandSearcher:
    """Advanced search engine for command history"""
    
    # Semantic keyword mappings for natural language queries
    SEMANTIC_MAPPINGS = {
        # Actions
        "delete": ["rm", "del", "remove", "unlink", "rmdir"],
        "copy": ["cp", "copy", "rsync", "scp"],
        "move": ["mv", "move", "rename"],
        "list": ["ls", "dir", "find", "locate", "tree"],
        "search": ["grep", "find", "rg", "ag", "ack", "search"],
        "install": ["install", "add", "npm install", "pip install", "apt install"],
        "update": ["update", "upgrade", "npm update", "pip install --upgrade"],
        "remove": ["uninstall", "remove", "npm uninstall", "pip uninstall", "apt remove"],
        "run": ["run", "execute", "python", "node", "bash", "sh"],
        "build": ["build", "make", "compile", "gcc", "cargo build"],
        "test": ["test", "pytest", "jest", "npm test", "cargo test"],
        "deploy": ["deploy", "publish", "release", "push"],
        "commit": ["commit", "git commit"],
        "push": ["push", "git push", "upload"],
        "pull": ["pull", "git pull", "download", "fetch"],
        "clone": ["clone", "git clone", "copy"],
        
        # Targets
        "file": ["file", "touch", "cat", "vim", "nano", "rm", "cp", "mv"],
        "folder": ["mkdir", "rmdir", "cd", "ls"],
        "process": ["ps", "kill", "top", "htop", "pgrep"],
        "network": ["ping", "curl", "wget", "netstat", "ifconfig"],
        "docker": ["docker", "container", "image", "docker-compose"],
        "git": ["git", "branch", "commit", "push", "pull", "merge"],
        "database": ["mysql", "psql", "mongo", "redis", "sqlite"],
        
        # Modifiers
        "recursive": ["-r", "-R", "--recursive", "recursively"],
        "force": ["-f", "--force", "forcefully"],
        "verbose": ["-v", "--verbose", "verbose"],
        "quiet": ["-q", "--quiet", "silent"],
        "all": ["-a", "--all", "all"],
        "help": ["-h", "--help", "help"],
    }
    
    def __init__(self, db: CommandDatabase):
        self.db = db
    
    def search(
        self, 
        query: str, 
        limit: int = 20,
        category: Optional[str] = None,
        favorites_only: bool = False
    ) -> List[SearchResult]:
        """
        Perform a comprehensive search across command history.
        Combines exact, fuzzy, and semantic matching.
        """
        results: Dict[int, SearchResult] = {}
        query_lower = query.lower().strip()
        
        # Get base command set
        if favorites_only:
            commands = self.db.get_favorites()
        elif category:
            commands = self.db.get_by_category(category)
        else:
            commands = self.db.get_recent_commands(limit=500)
        
        if not commands:
            return []
        
        # 1. Exact substring match
        for cmd in commands:
            if query_lower in cmd.command.lower():
                score = self._calculate_exact_score(query_lower, cmd.command.lower())
                if cmd.id not in results or results[cmd.id].score < score:
                    results[cmd.id] = SearchResult(cmd, score, "exact")
        
        # 2. Fuzzy match
        command_texts = {cmd.id: cmd.command for cmd in commands}
        fuzzy_results = process.extract(
            query_lower,
            command_texts,
            scorer=fuzz.partial_ratio,
            limit=limit * 2
        )
        
        for cmd_id, score, _ in fuzzy_results:
            if score >= 60:  # Threshold for fuzzy match
                cmd = next((c for c in commands if c.id == cmd_id), None)
                if cmd:
                    adjusted_score = (score / 100) * 0.85  # Scale fuzzy scores
                    if cmd_id not in results or results[cmd_id].score < adjusted_score:
                        results[cmd_id] = SearchResult(cmd, adjusted_score, "fuzzy")
        
        # 3. Semantic match
        semantic_commands = self._semantic_search(query_lower, commands)
        for cmd, score in semantic_commands:
            if cmd.id not in results or results[cmd.id].score < score:
                results[cmd.id] = SearchResult(cmd, score, "semantic")
        
        # Sort by score and return top results
        sorted_results = sorted(results.values(), key=lambda r: r.score, reverse=True)
        return sorted_results[:limit]
    
    def _calculate_exact_score(self, query: str, command: str) -> float:
        """Calculate score for exact matches"""
        # Exact match gets highest score
        if query == command:
            return 1.0
        
        # Prefix match
        if command.startswith(query):
            return 0.95
        
        # Word boundary match
        if re.search(rf'\b{re.escape(query)}\b', command):
            return 0.9
        
        # Substring match - score based on position and length ratio
        pos = command.find(query)
        length_ratio = len(query) / len(command)
        position_bonus = 1 - (pos / len(command))
        
        return 0.7 + (length_ratio * 0.2) + (position_bonus * 0.1)
    
    def _semantic_search(self, query: str, commands: List[Command]) -> List[Tuple[Command, float]]:
        """Perform semantic search based on keyword mappings"""
        results = []
        query_words = set(query.split())
        
        # Find matching semantic categories
        matched_commands = set()
        for word in query_words:
            if word in self.SEMANTIC_MAPPINGS:
                for pattern in self.SEMANTIC_MAPPINGS[word]:
                    for cmd in commands:
                        if pattern.lower() in cmd.command.lower():
                            matched_commands.add(cmd)
        
        # Score matched commands
        for cmd in matched_commands:
            score = 0.6  # Base semantic score
            # Boost if multiple semantic matches
            match_count = sum(
                1 for word in query_words
                if word in self.SEMANTIC_MAPPINGS
                and any(p.lower() in cmd.command.lower() for p in self.SEMANTIC_MAPPINGS[word])
            )
            score += min(0.2, match_count * 0.05)
            results.append((cmd, score))
        
        return results
    
    def search_by_time(
        self, 
        days: int = 7,
        limit: int = 100
    ) -> List[Command]:
        """Search commands from a specific time range"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = self.db.get_recent_commands(limit=500)
        return [cmd for cmd in recent if cmd.timestamp >= cutoff][:limit]
    
    def search_by_pattern(
        self, 
        pattern: str,
        limit: int = 50
    ) -> List[Command]:
        """Search commands matching a regex pattern"""
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            commands = self.db.get_recent_commands(limit=500)
            return [cmd for cmd in commands if regex.search(cmd.command)][:limit]
        except re.error:
            return []
    
    def get_similar_commands(
        self, 
        command: Command,
        limit: int = 10
    ) -> List[Tuple[Command, float]]:
        """Find similar commands based on structure"""
        commands = self.db.get_recent_commands(limit=200)
        results = []
        
        for cmd in commands:
            if cmd.id == command.id:
                continue
            
            # Calculate structural similarity
            score = fuzz.ratio(command.command, cmd.command) / 100
            
            # Boost if same category
            if cmd.category == command.category:
                score += 0.1
            
            if score >= 0.5:
                results.append((cmd, score))
        
        return sorted(results, key=lambda x: x[1], reverse=True)[:limit]
    
    def get_command_suggestions(self, partial: str, limit: int = 10) -> List[str]:
        """Get command suggestions based on partial input"""
        commands = self.db.get_recent_commands(limit=200)
        command_set = {cmd.command for cmd in commands}
        
        suggestions = []
        partial_lower = partial.lower()
        
        for cmd_text in command_set:
            if cmd_text.lower().startswith(partial_lower):
                suggestions.append(cmd_text)
        
        # Sort by use count if available
        cmd_use_counts = {cmd.command: cmd.use_count for cmd in commands}
        suggestions.sort(key=lambda x: cmd_use_counts.get(x, 0), reverse=True)
        
        return suggestions[:limit]
