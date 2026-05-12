"""
Command Analyzer Module
Statistical analysis and insights for command history
"""

from collections import Counter
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TimeDistribution:
    """Command distribution over time"""
    hour: int
    count: int
    percentage: float


@dataclass 
class CategoryStats:
    """Statistics for a command category"""
    category: str
    count: int
    percentage: float
    avg_length: float
    success_rate: float


class CommandAnalyzer:
    """Analyzes command history for patterns and insights"""
    
    def __init__(self, db):
        self.db = db
    
    def get_overview(self) -> Dict[str, Any]:
        """Get comprehensive overview of command history"""
        stats = self.db.get_statistics()
        commands = self.db.get_recent_commands(limit=1000)
        
        if not commands:
            return {
                "total_commands": 0,
                "categories": {},
                "time_distribution": [],
                "insights": ["No commands recorded yet. Start using your terminal!"]
            }
        
        return {
            "total_commands": stats["total_commands"],
            "categories": self._analyze_categories(commands),
            "time_distribution": self._analyze_time_distribution(commands),
            "daily_trend": self._analyze_daily_trend(commands),
            "top_commands": self._get_top_commands(commands, 10),
            "insights": self._generate_insights(commands),
        }
    
    def _analyze_categories(self, commands: List) -> Dict[str, CategoryStats]:
        """Analyze command distribution by category"""
        category_data: Dict[str, Dict] = {}
        total = len(commands)
        
        for cmd in commands:
            cat = cmd.category
            if cat not in category_data:
                category_data[cat] = {
                    "count": 0,
                    "total_length": 0,
                    "success_count": 0,
                }
            
            category_data[cat]["count"] += 1
            category_data[cat]["total_length"] += len(cmd.command)
            if cmd.exit_code == 0:
                category_data[cat]["success_count"] += 1
        
        result = {}
        for cat, data in category_data.items():
            result[cat] = CategoryStats(
                category=cat,
                count=data["count"],
                percentage=round(data["count"] / total * 100, 1),
                avg_length=round(data["total_length"] / data["count"], 1),
                success_rate=round(data["success_count"] / data["count"] * 100, 1)
            )
        
        return result
    
    def _analyze_time_distribution(self, commands: List) -> List[TimeDistribution]:
        """Analyze when commands are executed"""
        hour_counts = Counter()
        total = len(commands)
        
        for cmd in commands:
            if cmd.timestamp:
                hour_counts[cmd.timestamp.hour] += 1
        
        distribution = []
        for hour in range(24):
            count = hour_counts.get(hour, 0)
            distribution.append(TimeDistribution(
                hour=hour,
                count=count,
                percentage=round(count / total * 100, 1) if total > 0 else 0
            ))
        
        return distribution
    
    def _analyze_daily_trend(self, commands: List) -> Dict[str, int]:
        """Analyze daily command trend"""
        daily_counts = Counter()
        
        for cmd in commands:
            if cmd.timestamp:
                date_str = cmd.timestamp.strftime("%Y-%m-%d")
                daily_counts[date_str] += 1
        
        # Return last 7 days
        result = {}
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            result[date] = daily_counts.get(date, 0)
        
        return dict(reversed(list(result.items())))
    
    def _get_top_commands(self, commands: List, limit: int) -> List[Tuple[str, int]]:
        """Get most frequently used commands"""
        command_counts = Counter(cmd.command for cmd in commands)
        return command_counts.most_common(limit)
    
    def _generate_insights(self, commands: List) -> List[str]:
        """Generate actionable insights from command history"""
        insights = []
        
        if not commands:
            return ["No commands to analyze yet."]
        
        # Time-based insights
        hour_dist = self._analyze_time_distribution(commands)
        peak_hours = sorted(hour_dist, key=lambda x: x.count, reverse=True)[:3]
        
        if peak_hours[0].count > 0:
            peak_hour = peak_hours[0].hour
            insights.append(
                f"🕐 Most productive hour: {peak_hour:02d}:00 - {peak_hour+1:02d}:00 "
                f"({peak_hours[0].count} commands)"
            )
        
        # Category insights
        categories = self._analyze_categories(commands)
        top_category = max(categories.values(), key=lambda x: x.count)
        insights.append(
            f"📁 Most used category: {top_category.category} "
            f"({top_category.count} commands, {top_category.percentage}%)"
        )
        
        # Efficiency insights
        failed_commands = [cmd for cmd in commands if cmd.exit_code != 0]
        if failed_commands:
            failure_rate = len(failed_commands) / len(commands) * 100
            if failure_rate > 10:
                insights.append(
                    f"⚠️ High failure rate: {failure_rate:.1f}% of commands failed. "
                    f"Consider reviewing common error patterns."
                )
        
        # Command length insight
        avg_length = sum(len(cmd.command) for cmd in commands) / len(commands)
        if avg_length > 50:
            insights.append(
                f"📏 Average command length: {avg_length:.0f} chars. "
                f"Consider creating aliases for long commands."
            )
        
        # Favorite usage
        favorites = [cmd for cmd in commands if cmd.favorite]
        if favorites:
            insights.append(
                f"⭐ {len(favorites)} favorite commands saved for quick access."
            )
        
        return insights
    
    def get_productivity_score(self) -> Dict[str, Any]:
        """Calculate productivity metrics"""
        commands = self.db.get_recent_commands(limit=500)
        
        if not commands:
            return {"score": 0, "level": "Beginner", "tips": []}
        
        # Calculate various metrics
        unique_commands = len(set(cmd.command for cmd in commands))
        total_commands = len(commands)
        success_rate = sum(1 for cmd in commands if cmd.exit_code == 0) / total_commands
        
        # Categories used
        categories_used = len(set(cmd.category for cmd in commands))
        
        # Calculate score (0-100)
        score = 0
        
        # Volume score (max 30 points)
        score += min(30, total_commands / 10)
        
        # Diversity score (max 25 points)
        diversity = unique_commands / total_commands if total_commands > 0 else 0
        score += diversity * 25
        
        # Success rate score (max 25 points)
        score += success_rate * 25
        
        # Category breadth score (max 20 points)
        score += min(20, categories_used * 2)
        
        score = min(100, round(score))
        
        # Determine level
        if score >= 80:
            level = "Expert"
        elif score >= 60:
            level = "Advanced"
        elif score >= 40:
            level = "Intermediate"
        else:
            level = "Beginner"
        
        # Generate tips
        tips = []
        if success_rate < 0.8:
            tips.append("Focus on understanding command errors to improve success rate")
        if diversity < 0.3:
            tips.append("Explore more diverse commands to expand your toolkit")
        if categories_used < 5:
            tips.append("Try commands from different categories to become more versatile")
        
        return {
            "score": score,
            "level": level,
            "metrics": {
                "total_commands": total_commands,
                "unique_commands": unique_commands,
                "success_rate": round(success_rate * 100, 1),
                "categories_used": categories_used,
            },
            "tips": tips
        }
    
    def export_report(self, format: str = "text") -> str:
        """Export analysis report"""
        overview = self.get_overview()
        productivity = self.get_productivity_score()
        
        if format == "json":
            import json
            return json.dumps({
                "overview": overview,
                "productivity": productivity
            }, indent=2, default=str)
        
        # Text format
        lines = [
            "=" * 50,
            "CmdMind Analysis Report",
            "=" * 50,
            "",
            f"Total Commands: {overview['total_commands']}",
            f"Productivity Score: {productivity['score']} ({productivity['level']})",
            "",
            "Category Distribution:",
        ]
        
        for cat, stats in sorted(overview['categories'].items(), 
                                 key=lambda x: x[1].count, reverse=True):
            lines.append(f"  {cat}: {stats.count} ({stats.percentage}%)")
        
        lines.extend([
            "",
            "Top Commands:",
        ])
        
        for cmd, count in overview['top_commands'][:5]:
            lines.append(f"  {cmd[:40]}... ({count}x)")
        
        lines.extend([
            "",
            "Insights:",
        ])
        
        for insight in overview['insights']:
            lines.append(f"  {insight}")
        
        return "\n".join(lines)
