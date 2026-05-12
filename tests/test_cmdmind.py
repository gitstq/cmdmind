"""Tests for CmdMind"""

import pytest
from datetime import datetime

from cmdmind.core.database import Command, CommandDatabase
from cmdmind.core.classifier import CommandClassifier
from cmdmind.core.searcher import CommandSearcher


class TestCommand:
    """Tests for Command dataclass"""
    
    def test_command_creation(self):
        """Test creating a command"""
        cmd = Command(
            command="git status",
            shell="bash",
            exit_code=0,
            cwd="/home/user/project"
        )
        
        assert cmd.command == "git status"
        assert cmd.shell == "bash"
        assert cmd.exit_code == 0
        assert cmd.cwd == "/home/user/project"
        assert cmd.category == "general"
        assert cmd.favorite is False
        assert cmd.use_count == 1
    
    def test_command_to_dict(self):
        """Test converting command to dictionary"""
        cmd = Command(command="ls -la", category="file")
        data = cmd.to_dict()
        
        assert data["command"] == "ls -la"
        assert data["category"] == "file"
        assert "timestamp" in data
    
    def test_command_from_dict(self):
        """Test creating command from dictionary"""
        data = {
            "id": 1,
            "command": "npm install",
            "category": "npm",
            "timestamp": "2024-01-15T10:30:00",
            "tags": '["node", "install"]'
        }
        
        cmd = Command.from_dict(data)
        
        assert cmd.id == 1
        assert cmd.command == "npm install"
        assert cmd.category == "npm"
        assert cmd.tags == ["node", "install"]


class TestCommandDatabase:
    """Tests for CommandDatabase"""
    
    @pytest.fixture
    def db(self, tmp_path):
        """Create a temporary database for testing"""
        db_path = tmp_path / "test_commands.db"
        return CommandDatabase(db_path)
    
    def test_add_command(self, db):
        """Test adding a command"""
        cmd = Command(command="echo hello", category="general")
        cmd_id = db.add_command(cmd)
        
        assert cmd_id is not None
        assert cmd_id > 0
    
    def test_get_command(self, db):
        """Test retrieving a command"""
        cmd = Command(command="pwd", category="file")
        cmd_id = db.add_command(cmd)
        
        retrieved = db.get_command(cmd_id)
        
        assert retrieved is not None
        assert retrieved.command == "pwd"
        assert retrieved.category == "file"
    
    def test_update_command(self, db):
        """Test updating a command"""
        cmd = Command(command="ls", category="file")
        cmd_id = db.add_command(cmd)
        
        cmd.id = cmd_id
        cmd.favorite = True
        cmd.use_count = 5
        
        success = db.update_command(cmd)
        assert success is True
        
        updated = db.get_command(cmd_id)
        assert updated.favorite is True
        assert updated.use_count == 5
    
    def test_delete_command(self, db):
        """Test deleting a command"""
        cmd = Command(command="rm test")
        cmd_id = db.add_command(cmd)
        
        success = db.delete_command(cmd_id)
        assert success is True
        
        deleted = db.get_command(cmd_id)
        assert deleted is None
    
    def test_get_recent_commands(self, db):
        """Test getting recent commands"""
        for i in range(10):
            cmd = Command(command=f"command_{i}")
            db.add_command(cmd)
        
        recent = db.get_recent_commands(limit=5)
        
        assert len(recent) == 5
    
    def test_get_favorites(self, db):
        """Test getting favorite commands"""
        cmd1 = Command(command="fav1", favorite=True)
        cmd2 = Command(command="fav2", favorite=False)
        cmd3 = Command(command="fav3", favorite=True)
        
        db.add_command(cmd1)
        db.add_command(cmd2)
        db.add_command(cmd3)
        
        favorites = db.get_favorites()
        
        assert len(favorites) == 2
    
    def test_get_statistics(self, db):
        """Test getting statistics"""
        db.add_command(Command(command="git status", category="git"))
        db.add_command(Command(command="git log", category="git"))
        db.add_command(Command(command="npm install", category="npm"))
        
        stats = db.get_statistics()
        
        assert stats["total_commands"] == 3
        assert "git" in stats["by_category"]
        assert "npm" in stats["by_category"]


class TestCommandClassifier:
    """Tests for CommandClassifier"""
    
    @pytest.fixture
    def classifier(self):
        return CommandClassifier()
    
    def test_classify_git_command(self, classifier):
        """Test classifying git commands"""
        category, confidence = classifier.classify("git status")
        assert category == "git"
        assert confidence > 0.9
    
    def test_classify_docker_command(self, classifier):
        """Test classifying docker commands"""
        category, confidence = classifier.classify("docker ps -a")
        assert category == "docker"
        assert confidence > 0.9
    
    def test_classify_npm_command(self, classifier):
        """Test classifying npm commands"""
        category, confidence = classifier.classify("npm install express")
        assert category == "npm"
        assert confidence > 0.9
    
    def test_classify_file_command(self, classifier):
        """Test classifying file commands"""
        category, confidence = classifier.classify("ls -la /home")
        assert category == "file"
    
    def test_classify_unknown_command(self, classifier):
        """Test classifying unknown commands"""
        category, confidence = classifier.classify("my-custom-tool --option")
        assert category == "general"
    
    def test_extract_tags(self, classifier):
        """Test extracting tags from command"""
        tags = classifier.extract_tags("git commit -m 'message' --amend")
        
        assert "-m" in tags or "--amend" in tags
    
    def test_get_all_categories(self, classifier):
        """Test getting all categories"""
        categories = classifier.get_all_categories()
        
        assert "git" in categories
        assert "docker" in categories
        assert "npm" in categories
        assert "general" in categories


class TestCommandSearcher:
    """Tests for CommandSearcher"""
    
    @pytest.fixture
    def db_with_commands(self, tmp_path):
        """Create database with sample commands"""
        db_path = tmp_path / "test_search.db"
        db = CommandDatabase(db_path)
        
        db.add_command(Command(command="git status", category="git"))
        db.add_command(Command(command="git log --oneline", category="git"))
        db.add_command(Command(command="docker ps", category="docker"))
        db.add_command(Command(command="npm install express", category="npm"))
        db.add_command(Command(command="ls -la", category="file"))
        
        return db
    
    def test_search_exact_match(self, db_with_commands):
        """Test exact match search"""
        searcher = CommandSearcher(db_with_commands)
        results = searcher.search("git")
        
        assert len(results) > 0
        assert any("git" in r.command.command for r in results)
    
    def test_search_fuzzy_match(self, db_with_commands):
        """Test fuzzy match search"""
        searcher = CommandSearcher(db_with_commands)
        results = searcher.search("doker")  # Typo
        
        # Should still find docker
        assert any("docker" in r.command.command for r in results)
    
    def test_search_by_category(self, db_with_commands):
        """Test search with category filter"""
        searcher = CommandSearcher(db_with_commands)
        results = searcher.search("", category="git")
        
        assert all(r.command.category == "git" for r in results)
    
    def test_search_semantic(self, db_with_commands):
        """Test semantic search"""
        searcher = CommandSearcher(db_with_commands)
        results = searcher.search("list files")
        
        # Should find ls command
        assert any("ls" in r.command.command for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
