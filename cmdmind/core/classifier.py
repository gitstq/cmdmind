"""
Command Classifier Module
Intelligent command categorization and tagging
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CategoryRule:
    """Rule for categorizing commands"""
    name: str
    patterns: List[str]
    keywords: List[str]
    description: str


class CommandClassifier:
    """Classifies shell commands into categories"""
    
    # Predefined category rules
    CATEGORY_RULES: Dict[str, CategoryRule] = {
        "git": CategoryRule(
            name="git",
            patterns=[r"^git\s", r"^git$", r"^\w+@.*\.git"],
            keywords=["git", "clone", "commit", "push", "pull", "branch", "merge", "rebase", "stash", "checkout"],
            description="Git version control commands"
        ),
        "docker": CategoryRule(
            name="docker",
            patterns=[r"^docker\s", r"^docker-compose\s", r"^docker\s+$"],
            keywords=["docker", "container", "image", "volume", "network", "compose", "dockerfile"],
            description="Docker container commands"
        ),
        "npm": CategoryRule(
            name="npm",
            patterns=[r"^npm\s", r"^yarn\s", r"^pnpm\s", r"^npx\s"],
            keywords=["npm", "yarn", "pnpm", "npx", "install", "package", "node"],
            description="Node.js package manager commands"
        ),
        "pip": CategoryRule(
            name="pip",
            patterns=[r"^pip\s", r"^pip3\s", r"^poetry\s", r"^pipenv\s", r"^uv\s"],
            keywords=["pip", "pip3", "poetry", "pipenv", "uv", "install", "requirement"],
            description="Python package manager commands"
        ),
        "cargo": CategoryRule(
            name="cargo",
            patterns=[r"^cargo\s", r"^rustc\s"],
            keywords=["cargo", "rustc", "rustup", "crate"],
            description="Rust package manager commands"
        ),
        "go": CategoryRule(
            name="go",
            patterns=[r"^go\s", r"^gofmt\s"],
            keywords=["go", "gofmt", "go mod", "go build", "go run"],
            description="Go language commands"
        ),
        "make": CategoryRule(
            name="make",
            patterns=[r"^make\s", r"^make$"],
            keywords=["make", "makefile", "cmake"],
            description="Build automation commands"
        ),
        "ssh": CategoryRule(
            name="ssh",
            patterns=[r"^ssh\s", r"^scp\s", r"^rsync\s", r"^sftp\s"],
            keywords=["ssh", "scp", "rsync", "sftp", "remote", "server"],
            description="Remote connection commands"
        ),
        "file": CategoryRule(
            name="file",
            patterns=[
                r"^ls\s", r"^ls$", r"^cd\s", r"^cd$",
                r"^cp\s", r"^mv\s", r"^rm\s", r"^mkdir\s",
                r"^touch\s", r"^cat\s", r"^find\s", r"^grep\s",
                r"^chmod\s", r"^chown\s", r"^ln\s",
            ],
            keywords=["ls", "cd", "cp", "mv", "rm", "mkdir", "touch", "cat", "find", "grep", "chmod"],
            description="File system operations"
        ),
        "process": CategoryRule(
            name="process",
            patterns=[
                r"^ps\s", r"^ps$", r"^kill\s", r"^killall\s",
                r"^top\s", r"^top$", r"^htop\s", r"^htop$",
                r"^pgrep\s", r"^pkill\s", r"^nice\s", r"^renice\s",
            ],
            keywords=["ps", "kill", "top", "htop", "process", "pid"],
            description="Process management commands"
        ),
        "network": CategoryRule(
            name="network",
            patterns=[
                r"^ping\s", r"^curl\s", r"^wget\s", r"^netstat\s",
                r"^ifconfig\s", r"^ip\s", r"^nc\s", r"^telnet\s",
                r"^nslookup\s", r"^dig\s", r"^traceroute\s",
            ],
            keywords=["ping", "curl", "wget", "netstat", "network", "port", "ip"],
            description="Network utilities"
        ),
        "system": CategoryRule(
            name="system",
            patterns=[
                r"^sudo\s", r"^systemctl\s", r"^service\s",
                r"^journalctl\s", r"^dmesg\s", r"^uname\s",
            ],
            keywords=["sudo", "systemctl", "service", "system", "root"],
            description="System administration commands"
        ),
        "python": CategoryRule(
            name="python",
            patterns=[r"^python\s", r"^python3\s", r"^python$", r"^python3$"],
            keywords=["python", "python3", "py", "script"],
            description="Python interpreter commands"
        ),
        "editor": CategoryRule(
            name="editor",
            patterns=[r"^vim\s", r"^vim$", r"^nano\s", r"^nano$", r"^code\s", r"^nvim\s"],
            keywords=["vim", "nano", "code", "nvim", "editor"],
            description="Text editor commands"
        ),
        "database": CategoryRule(
            name="database",
            patterns=[
                r"^mysql\s", r"^psql\s", r"^sqlite3\s",
                r"^mongo\s", r"^redis-cli\s", r"^pg_dump\s",
            ],
            keywords=["mysql", "psql", "sqlite", "mongo", "redis", "database", "sql"],
            description="Database commands"
        ),
        "archive": CategoryRule(
            name="archive",
            patterns=[
                r"^tar\s", r"^zip\s", r"^unzip\s", r"^gzip\s",
                r"^gunzip\s", r"^xz\s", r"^7z\s",
            ],
            keywords=["tar", "zip", "unzip", "gzip", "archive", "compress"],
            description="Archive and compression commands"
        ),
    }
    
    def __init__(self):
        self._compiled_patterns: Dict[str, List[re.Pattern]] = {}
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for performance"""
        for category, rule in self.CATEGORY_RULES.items():
            self._compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) 
                for pattern in rule.patterns
            ]
    
    def classify(self, command: str) -> Tuple[str, float]:
        """
        Classify a command into a category.
        Returns (category, confidence) tuple.
        """
        command_lower = command.lower().strip()
        
        if not command_lower:
            return ("general", 0.0)
        
        # Check pattern matches first (highest confidence)
        for category, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(command_lower):
                    return (category, 0.95)
        
        # Check keyword matches
        scores: Dict[str, float] = {}
        words = set(re.findall(r'\w+', command_lower))
        
        for category, rule in self.CATEGORY_RULES.items():
            keyword_matches = sum(1 for kw in rule.keywords if kw in command_lower)
            if keyword_matches > 0:
                scores[category] = min(0.8, keyword_matches * 0.2)
        
        if scores:
            best_category = max(scores, key=scores.get)
            return (best_category, scores[best_category])
        
        return ("general", 0.0)
    
    def extract_tags(self, command: str) -> List[str]:
        """Extract relevant tags from a command"""
        tags = []
        command_lower = command.lower()
        
        # Extract flags/options
        flags = re.findall(r'-{1,2}[\w-]+', command)
        tags.extend(flags[:5])  # Limit to 5 flags
        
        # Extract file extensions
        extensions = re.findall(r'\.(\w+)(?:\s|$)', command)
        for ext in extensions:
            if ext in ['py', 'js', 'ts', 'go', 'rs', 'java', 'cpp', 'c', 'rb', 'php']:
                tags.append(f"lang:{ext}")
            elif ext in ['json', 'yaml', 'yml', 'toml', 'xml', 'ini']:
                tags.append(f"config:{ext}")
            elif ext in ['txt', 'md', 'rst', 'log']:
                tags.append(f"text:{ext}")
        
        # Extract URLs
        if 'http' in command_lower or 'www.' in command_lower:
            tags.append("network:url")
        
        # Extract paths
        if '/' in command or '\\' in command:
            tags.append("has:path")
        
        return list(set(tags))
    
    def suggest_description(self, command: str, category: str) -> str:
        """Generate a suggested description for a command"""
        parts = command.split()
        if not parts:
            return ""
        
        cmd_name = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        if category in self.CATEGORY_RULES:
            rule = self.CATEGORY_RULES[category]
            base_desc = f"{rule.description.split('.')[0]}"
            
            if args:
                return f"{base_desc}: {' '.join(args[:3])}"
            return base_desc
        
        return f"Execute {cmd_name}" + (f" with {' '.join(args[:2])}" if args else "")
    
    def get_all_categories(self) -> List[str]:
        """Get list of all available categories"""
        return list(self.CATEGORY_RULES.keys()) + ["general"]
    
    def get_category_info(self, category: str) -> Optional[CategoryRule]:
        """Get information about a specific category"""
        return self.CATEGORY_RULES.get(category)
