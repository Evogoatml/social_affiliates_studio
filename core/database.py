"""
Database module for persistent storage using SQLite
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from core.logger import setup_logger

logger = setup_logger(__name__)

class Database:
    """SQLite database handler for the autonomous influencer system"""
    
    def __init__(self, db_path: str = "data/influencer.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Connect to the database"""
        try:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Access columns by name
            logger.info(f"📊 Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()
        
        # Content table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                theme TEXT,
                caption TEXT,
                hashtags TEXT,
                media_prompt TEXT,
                media_data TEXT,
                day_offset INTEGER,
                post_index INTEGER,
                strategy_id TEXT,
                created_at TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                scheduled_time TEXT NOT NULL,
                posted_time TEXT,
                status TEXT DEFAULT 'scheduled',
                platform_post_id TEXT,
                error_message TEXT,
                FOREIGN KEY (content_id) REFERENCES content(id)
            )
        ''')
        
        # Engagement metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS engagement (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
        ''')
        
        # Strategies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategies (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                niche TEXT,
                target_audience TEXT,
                goals TEXT,
                content_plan TEXT,
                platforms TEXT,
                created_at TEXT NOT NULL,
                optimized_at TEXT,
                optimization_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Avatars table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS avatars (
                id TEXT PRIMARY KEY,
                image_path TEXT,
                image_url TEXT,
                prompt TEXT,
                config TEXT,
                placeholder BOOLEAN DEFAULT 0,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Analytics snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_date TEXT NOT NULL,
                total_posts INTEGER,
                total_engagement INTEGER,
                avg_engagement_rate REAL,
                top_platform TEXT,
                insights TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        self.conn.commit()
        logger.info("✅ Database tables created/verified")
    
    # Content operations
    def save_content(self, content: Dict) -> bool:
        """Save content to database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO content 
                (id, type, theme, caption, hashtags, media_prompt, media_data, 
                 day_offset, post_index, strategy_id, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                content.get('id'),
                content.get('type'),
                content.get('theme'),
                content.get('caption'),
                json.dumps(content.get('hashtags', [])),
                content.get('media_prompt'),
                json.dumps(content.get('media')) if content.get('media') else None,
                content.get('day_offset'),
                content.get('post_index'),
                content.get('strategy_id'),
                content.get('created_at'),
                content.get('status', 'pending')
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save content: {e}")
            return False
    
    def get_content(self, content_id: str) -> Optional[Dict]:
        """Get content by ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM content WHERE id = ?', (content_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_pending_content(self, limit: int = 10) -> List[Dict]:
        """Get pending content items"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM content 
            WHERE status = 'pending' 
            ORDER BY created_at 
            LIMIT ?
        ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # Post operations
    def save_post(self, post: Dict) -> int:
        """Save post record"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO posts 
                (content_id, platform, scheduled_time, posted_time, status, platform_post_id, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                post.get('content_id'),
                post.get('platform'),
                post.get('scheduled_time'),
                post.get('posted_time'),
                post.get('status', 'scheduled'),
                post.get('platform_post_id'),
                post.get('error_message')
            ))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to save post: {e}")
            return -1
    
    def update_post_status(self, post_id: int, status: str, posted_time: Optional[str] = None,
                          platform_post_id: Optional[str] = None, error_message: Optional[str] = None):
        """Update post status"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE posts 
                SET status = ?, posted_time = COALESCE(?, posted_time),
                    platform_post_id = COALESCE(?, platform_post_id),
                    error_message = ?
                WHERE id = ?
            ''', (status, posted_time, platform_post_id, error_message, post_id))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update post status: {e}")
            return False
    
    def get_scheduled_posts(self, before_time: Optional[str] = None) -> List[Dict]:
        """Get scheduled posts"""
        cursor = self.conn.cursor()
        
        if before_time:
            cursor.execute('''
                SELECT * FROM posts 
                WHERE status = 'scheduled' AND scheduled_time <= ?
                ORDER BY scheduled_time
            ''', (before_time,))
        else:
            cursor.execute('''
                SELECT * FROM posts 
                WHERE status = 'scheduled'
                ORDER BY scheduled_time
            ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    # Engagement operations
    def save_engagement(self, engagement: Dict) -> bool:
        """Save engagement metrics"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO engagement 
                (post_id, platform, likes, comments, shares, views, engagement_rate, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                engagement.get('post_id'),
                engagement.get('platform'),
                engagement.get('likes', 0),
                engagement.get('comments', 0),
                engagement.get('shares', 0),
                engagement.get('views', 0),
                engagement.get('engagement_rate', 0.0),
                datetime.now().isoformat()
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save engagement: {e}")
            return False
    
    def get_engagement_stats(self, platform: Optional[str] = None, days: int = 7) -> Dict:
        """Get engagement statistics"""
        cursor = self.conn.cursor()
        
        if platform:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_posts,
                    SUM(likes) as total_likes,
                    SUM(comments) as total_comments,
                    SUM(shares) as total_shares,
                    SUM(views) as total_views,
                    AVG(engagement_rate) as avg_engagement_rate
                FROM engagement
                WHERE platform = ? AND updated_at >= date('now', '-' || ? || ' days')
            ''', (platform, days))
        else:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_posts,
                    SUM(likes) as total_likes,
                    SUM(comments) as total_comments,
                    SUM(shares) as total_shares,
                    SUM(views) as total_views,
                    AVG(engagement_rate) as avg_engagement_rate
                FROM engagement
                WHERE updated_at >= date('now', '-' || ? || ' days')
            ''', (days,))
        
        row = cursor.fetchone()
        return dict(row) if row else {}
    
    # Strategy operations
    def save_strategy(self, strategy: Dict) -> bool:
        """Save marketing strategy"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO strategies 
                (id, name, niche, target_audience, goals, content_plan, platforms, 
                 created_at, optimized_at, optimization_count, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                strategy.get('id'),
                strategy.get('name'),
                strategy.get('niche'),
                strategy.get('target_audience'),
                json.dumps(strategy.get('goals', [])),
                json.dumps(strategy.get('content_plan', {})),
                json.dumps(strategy.get('platforms', {})),
                strategy.get('created_at'),
                strategy.get('optimized_at'),
                strategy.get('optimization_count', 0),
                strategy.get('is_active', True)
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save strategy: {e}")
            return False
    
    def get_active_strategy(self) -> Optional[Dict]:
        """Get the active strategy"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM strategies 
            WHERE is_active = 1 
            ORDER BY created_at DESC 
            LIMIT 1
        ''')
        row = cursor.fetchone()
        
        if row:
            strategy = dict(row)
            # Parse JSON fields
            strategy['goals'] = json.loads(strategy['goals']) if strategy['goals'] else []
            strategy['content_plan'] = json.loads(strategy['content_plan']) if strategy['content_plan'] else {}
            strategy['platforms'] = json.loads(strategy['platforms']) if strategy['platforms'] else {}
            return strategy
        return None
    
    # Avatar operations
    def save_avatar(self, avatar: Dict) -> bool:
        """Save avatar data"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO avatars 
                (id, image_path, image_url, prompt, config, placeholder, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                avatar.get('id'),
                avatar.get('image_path'),
                avatar.get('image_url'),
                avatar.get('prompt'),
                json.dumps(avatar.get('config', {})),
                avatar.get('placeholder', False),
                avatar.get('created_at')
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save avatar: {e}")
            return False
    
    def get_avatar(self) -> Optional[Dict]:
        """Get the latest avatar"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM avatars ORDER BY created_at DESC LIMIT 1')
        row = cursor.fetchone()
        
        if row:
            avatar = dict(row)
            avatar['config'] = json.loads(avatar['config']) if avatar['config'] else {}
            return avatar
        return None
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("📊 Database connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
