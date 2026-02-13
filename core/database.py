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
        
        # Viral content table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS viral_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                content_type TEXT NOT NULL,
                url TEXT UNIQUE,
                caption TEXT,
                hashtags TEXT,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                sound_name TEXT,
                posted_at TEXT,
                scraped_at TEXT NOT NULL,
                is_viral BOOLEAN DEFAULT 0,
                niche TEXT,
                simulated BOOLEAN DEFAULT 0
            )
        ''')
        
        # Trending topics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trending_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                platform TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                engagement_score REAL DEFAULT 0.0,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                is_trending BOOLEAN DEFAULT 1,
                niche TEXT
            )
        ''')
        
        # Trending hashtags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trending_hashtags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hashtag TEXT NOT NULL,
                platform TEXT NOT NULL,
                usage_count INTEGER DEFAULT 1,
                avg_engagement_rate REAL DEFAULT 0.0,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                is_trending BOOLEAN DEFAULT 1,
                UNIQUE(hashtag, platform)
            )
        ''')
        
        # Content insights table (AI analysis of viral patterns)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT NOT NULL,
                platform TEXT,
                niche TEXT,
                pattern_description TEXT,
                confidence_score REAL DEFAULT 0.0,
                recommendation TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Video generations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_generations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE NOT NULL,
                provider TEXT NOT NULL,
                prompt TEXT,
                cost_usd REAL DEFAULT 0.0,
                duration_seconds INTEGER,
                status TEXT NOT NULL,
                video_url TEXT,
                thumbnail_url TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                instagram_post_id TEXT,
                views INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                trend_id TEXT,
                error_message TEXT
            )
        ''')
        
        # Provider performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS provider_performance (
                provider TEXT PRIMARY KEY,
                total_videos INTEGER DEFAULT 0,
                successful_videos INTEGER DEFAULT 0,
                failed_videos INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                avg_cost_usd REAL DEFAULT 0.0,
                avg_generation_time_seconds REAL DEFAULT 0.0,
                total_spent_usd REAL DEFAULT 0.0,
                last_used TEXT,
                updated_at TEXT NOT NULL
            )
        ''')
        
        self.conn.commit()
        logger.info("✅ Database tables created/verified (including viral content and video generation tables)")
    
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
    
    # Viral content operations
    def save_viral_content(self, content: Dict) -> bool:
        """Save viral content to database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO viral_content 
                (platform, content_type, url, caption, hashtags, likes, comments, shares, views,
                 engagement_rate, sound_name, posted_at, scraped_at, is_viral, niche, simulated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                content.get('platform'),
                content.get('type'),
                content.get('url'),
                content.get('caption'),
                json.dumps(content.get('hashtags', [])),
                content.get('likes', 0),
                content.get('comments', 0),
                content.get('shares', 0),
                content.get('views', 0),
                content.get('engagement_rate', 0.0),
                content.get('sound_name'),
                content.get('posted_at'),
                content.get('scraped_at'),
                content.get('is_viral', False),
                content.get('niche'),
                content.get('simulated', False)
            ))
            self.conn.commit()
            
            # Update trending hashtags
            if content.get('hashtags'):
                self._update_trending_hashtags(
                    content['hashtags'],
                    content['platform'],
                    content.get('engagement_rate', 0.0)
                )
            
            return True
        except Exception as e:
            logger.error(f"Failed to save viral content: {e}")
            return False
    
    def save_viral_content_batch(self, contents: List[Dict]) -> int:
        """Save multiple viral content items"""
        saved_count = 0
        for content in contents:
            if self.save_viral_content(content):
                saved_count += 1
        return saved_count
    
    def get_viral_content(
        self,
        platform: Optional[str] = None,
        niche: Optional[str] = None,
        min_engagement: float = 0.0,
        limit: int = 50
    ) -> List[Dict]:
        """Get viral content with filters"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM viral_content WHERE 1=1"
        params = []
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        
        if niche:
            query += " AND niche = ?"
            params.append(niche)
        
        if min_engagement > 0:
            query += " AND engagement_rate >= ?"
            params.append(min_engagement)
        
        query += " ORDER BY engagement_rate DESC, scraped_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            content = dict(row)
            content['hashtags'] = json.loads(content['hashtags']) if content['hashtags'] else []
            results.append(content)
        
        return results
    
    def get_top_viral_content(self, platform: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Get top performing viral content"""
        return self.get_viral_content(platform=platform, min_engagement=5.0, limit=limit)
    
    # Trending hashtags operations
    def _update_trending_hashtags(self, hashtags: List[str], platform: str, engagement_rate: float):
        """Update trending hashtags"""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        for hashtag in hashtags:
            hashtag = hashtag.lower().strip('#')
            
            # Check if exists
            cursor.execute('''
                SELECT usage_count, avg_engagement_rate FROM trending_hashtags
                WHERE hashtag = ? AND platform = ?
            ''', (hashtag, platform))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing
                new_count = result[0] + 1
                new_avg = (result[1] * result[0] + engagement_rate) / new_count
                
                cursor.execute('''
                    UPDATE trending_hashtags
                    SET usage_count = ?, avg_engagement_rate = ?, last_seen = ?, is_trending = 1
                    WHERE hashtag = ? AND platform = ?
                ''', (new_count, new_avg, now, hashtag, platform))
            else:
                # Insert new
                cursor.execute('''
                    INSERT INTO trending_hashtags
                    (hashtag, platform, usage_count, avg_engagement_rate, first_seen, last_seen)
                    VALUES (?, ?, 1, ?, ?, ?)
                ''', (hashtag, platform, engagement_rate, now, now))
        
        self.conn.commit()
    
    def get_trending_hashtags(
        self,
        platform: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """Get trending hashtags"""
        cursor = self.conn.cursor()
        
        if platform:
            cursor.execute('''
                SELECT * FROM trending_hashtags
                WHERE platform = ? AND is_trending = 1
                ORDER BY usage_count DESC, avg_engagement_rate DESC
                LIMIT ?
            ''', (platform, limit))
        else:
            cursor.execute('''
                SELECT * FROM trending_hashtags
                WHERE is_trending = 1
                ORDER BY usage_count DESC, avg_engagement_rate DESC
                LIMIT ?
            ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # Content insights operations
    def save_content_insight(self, insight: Dict) -> bool:
        """Save AI-generated content insight"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO content_insights
                (insight_type, platform, niche, pattern_description, confidence_score, recommendation, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                insight.get('type'),
                insight.get('platform'),
                insight.get('niche'),
                insight.get('pattern'),
                insight.get('confidence', 0.0),
                insight.get('recommendation'),
                datetime.now().isoformat()
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save content insight: {e}")
            return False
    
    def get_content_insights(
        self,
        platform: Optional[str] = None,
        niche: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Get content insights"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM content_insights WHERE 1=1"
        params = []
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        
        if niche:
            query += " AND niche = ?"
            params.append(niche)
        
        query += " ORDER BY confidence_score DESC, created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    # Analytics for viral content
    def get_viral_content_stats(self, days: int = 7) -> Dict:
        """Get viral content statistics"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                platform,
                COUNT(*) as total_content,
                AVG(engagement_rate) as avg_engagement,
                SUM(likes) as total_likes,
                SUM(views) as total_views
            FROM viral_content
            WHERE scraped_at >= date('now', '-' || ? || ' days')
            GROUP BY platform
        ''', (days,))
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = {
                'total_content': row[1],
                'avg_engagement': round(row[2], 2) if row[2] else 0,
                'total_likes': row[3],
                'total_views': row[4]
            }
        
        return stats
    
    # Video generation operations
    def add_video_generation(self, video_data: Dict) -> bool:
        """Save video generation to database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO video_generations (
                    job_id, provider, prompt, cost_usd, duration_seconds,
                    status, video_url, thumbnail_url, created_at, trend_id, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_data.get("job_id"),
                video_data.get("provider", ""),
                video_data.get("prompt"),
                video_data.get("cost_usd", 0.0),
                video_data.get("duration_seconds", 0),
                video_data.get("status", "queued"),
                video_data.get("video_url", ""),
                video_data.get("thumbnail_url", ""),
                video_data.get("created_at"),
                video_data.get("trend_id", ""),
                video_data.get("error_message", "")
            ))
            self.conn.commit()
            logger.info(f"✅ Video generation saved: {video_data.get('job_id')}")
            return True
        except Exception as e:
            logger.exception(f"Failed to save video generation: {e}")
            return False
    
    def update_video_generation(self, job_id: str, updates: Dict) -> bool:
        """Update video generation status"""
        try:
            cursor = self.conn.cursor()
            
            # Build update query dynamically
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            query = f"UPDATE video_generations SET {set_clause} WHERE job_id = ?"
            
            params = list(updates.values()) + [job_id]
            cursor.execute(query, params)
            self.conn.commit()
            
            logger.info(f"✅ Video generation updated: {job_id}")
            return True
        except Exception as e:
            logger.exception(f"Failed to update video generation: {e}")
            return False
    
    def get_video_generation(self, job_id: str) -> Optional[Dict]:
        """Get video generation by job_id"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM video_generations WHERE job_id = ?', (job_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_video_generations(
        self,
        provider: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get video generations with filters"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM video_generations WHERE 1=1"
        params = []
        
        if provider:
            query += " AND provider = ?"
            params.append(provider)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def update_provider_performance(self, provider: str, video_data: Dict):
        """Update provider performance metrics"""
        try:
            cursor = self.conn.cursor()
            
            # Get current stats
            cursor.execute('SELECT * FROM provider_performance WHERE provider = ?', (provider,))
            row = cursor.fetchone()
            
            if row:
                # Update existing record
                current = dict(row)
                total_videos = current['total_videos'] + 1
                successful = current['successful_videos'] + (1 if video_data.get('status') == 'completed' else 0)
                failed = current['failed_videos'] + (1 if video_data.get('status') == 'failed' else 0)
                success_rate = (successful / total_videos) * 100 if total_videos > 0 else 0
                
                # Calculate new averages
                cost = video_data.get('cost_usd', 0.0)
                total_spent = current['total_spent_usd'] + cost
                avg_cost = total_spent / total_videos if total_videos > 0 else 0
                
                cursor.execute('''
                    UPDATE provider_performance SET
                        total_videos = ?,
                        successful_videos = ?,
                        failed_videos = ?,
                        success_rate = ?,
                        avg_cost_usd = ?,
                        total_spent_usd = ?,
                        last_used = ?,
                        updated_at = ?
                    WHERE provider = ?
                ''', (
                    total_videos, successful, failed, success_rate,
                    avg_cost, total_spent,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    provider
                ))
            else:
                # Insert new record
                success_rate = 100.0 if video_data.get('status') == 'completed' else 0.0
                cursor.execute('''
                    INSERT INTO provider_performance (
                        provider, total_videos, successful_videos, failed_videos,
                        success_rate, avg_cost_usd, total_spent_usd, last_used, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    provider, 1,
                    1 if video_data.get('status') == 'completed' else 0,
                    1 if video_data.get('status') == 'failed' else 0,
                    success_rate,
                    video_data.get('cost_usd', 0.0),
                    video_data.get('cost_usd', 0.0),
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
            
            self.conn.commit()
            logger.info(f"✅ Provider performance updated: {provider}")
        except Exception as e:
            logger.exception(f"Failed to update provider performance: {e}")
    
    def get_provider_performance(self, provider: Optional[str] = None) -> Dict:
        """Get provider performance metrics"""
        cursor = self.conn.cursor()
        
        if provider:
            cursor.execute('SELECT * FROM provider_performance WHERE provider = ?', (provider,))
            row = cursor.fetchone()
            return dict(row) if row else {}
        else:
            cursor.execute('SELECT * FROM provider_performance ORDER BY success_rate DESC')
            return {row['provider']: dict(row) for row in cursor.fetchall()}
    
    def get_video_analytics(self, days: int = 30) -> Dict:
        """Get video generation analytics"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_videos,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(cost_usd) as total_cost,
                AVG(cost_usd) as avg_cost,
                AVG(duration_seconds) as avg_duration,
                AVG(engagement_rate) as avg_engagement
            FROM video_generations
            WHERE created_at >= date('now', '-' || ? || ' days')
        ''', (days,))
        
        row = cursor.fetchone()
        
        if row:
            return {
                'total_videos': row[0] or 0,
                'completed': row[1] or 0,
                'failed': row[2] or 0,
                'total_cost': round(row[3] or 0.0, 2),
                'avg_cost': round(row[4] or 0.0, 2),
                'avg_duration': round(row[5] or 0.0, 1),
                'avg_engagement': round(row[6] or 0.0, 3)
            }
        return {}
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
