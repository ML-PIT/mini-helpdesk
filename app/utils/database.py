import os
from urllib.parse import urlparse
from pymongo import MongoClient
from sqlalchemy import create_engine, text
from flask import current_app

class DatabaseManager:
    """Database abstraction layer supporting SQLite, MySQL, and MongoDB"""
    
    def __init__(self, app=None):
        self.app = app
        self.mongo_client = None
        self.mongo_db = None
        
    def init_app(self, app):
        """Initialize database connections"""
        self.app = app
        
        # Initialize SQL database (SQLite/MySQL)
        self._init_sql_database()
        
        # Initialize MongoDB if configured
        mongo_uri = app.config.get('MONGO_URI')
        if mongo_uri:
            self._init_mongo_database(mongo_uri)
    
    def _init_sql_database(self):
        """Initialize SQL database connection"""
        database_url = self.app.config.get('SQLALCHEMY_DATABASE_URI')
        parsed = urlparse(database_url)
        
        if parsed.scheme.startswith('sqlite'):
            self._setup_sqlite()
        elif parsed.scheme.startswith('mysql'):
            self._setup_mysql()
    
    def _init_mongo_database(self, mongo_uri):
        """Initialize MongoDB connection"""
        try:
            self.mongo_client = MongoClient(mongo_uri)
            db_name = urlparse(mongo_uri).path.lstrip('/')
            self.mongo_db = self.mongo_client[db_name or 'helpdesk_db']
            
            # Test connection
            self.mongo_client.admin.command('ping')
            current_app.logger.info("MongoDB connection established")
            
        except Exception as e:
            current_app.logger.error(f"MongoDB connection failed: {e}")
            self.mongo_client = None
            self.mongo_db = None
    
    def _setup_sqlite(self):
        """Configure SQLite specific settings"""
        from app import db
        
        # Enable foreign keys for SQLite
        @db.event.listens_for(db.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    
    def _setup_mysql(self):
        """Configure MySQL specific settings"""
        # MySQL configuration is handled by SQLAlchemy
        current_app.logger.info("MySQL database configured")
    
    def get_mongo_collection(self, collection_name):
        """Get MongoDB collection"""
        if self.mongo_db is None:
            raise RuntimeError("MongoDB not initialized")
        return self.mongo_db[collection_name]
    
    def is_mongo_available(self):
        """Check if MongoDB is available"""
        return self.mongo_db is not None

class SearchManager:
    """Full-text search abstraction for different database backends"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def search_tickets(self, query, user_role=None, user_id=None, limit=50):
        """Search tickets with full-text search"""
        from app.models.ticket import Ticket
        from app import db
        
        # Base query with access control
        base_query = Ticket.query
        
        if user_role == 'customer':
            base_query = base_query.filter_by(created_by=user_id)
        
        # Different search strategies based on database
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        
        if 'sqlite' in database_url.lower():
            return self._sqlite_search(base_query, query, limit)
        elif 'mysql' in database_url.lower():
            return self._mysql_search(base_query, query, limit)
        else:
            # Fallback to basic LIKE search
            return self._basic_search(base_query, query, limit)
    
    def _sqlite_search(self, base_query, query, limit):
        """SQLite FTS search"""
        search_term = f"%{query}%"
        return base_query.filter(
            db.or_(
                Ticket.title.like(search_term),
                Ticket.description.like(search_term),
                Ticket.ticket_number.like(search_term)
            )
        ).limit(limit).all()
    
    def _mysql_search(self, base_query, query, limit):
        """MySQL fulltext search"""
        from app import db
        
        # Use MySQL FULLTEXT search if available
        try:
            return base_query.filter(
                db.text("MATCH(title, description) AGAINST(:query IN BOOLEAN MODE)")
            ).params(query=f"+{query}*").limit(limit).all()
        except:
            # Fallback to LIKE search
            return self._basic_search(base_query, query, limit)
    
    def _basic_search(self, base_query, query, limit):
        """Basic LIKE search as fallback"""
        from app import db
        search_term = f"%{query}%"
        return base_query.filter(
            db.or_(
                Ticket.title.like(search_term),
                Ticket.description.like(search_term),
                Ticket.ticket_number.like(search_term)
            )
        ).limit(limit).all()
    
    def search_knowledge_articles(self, query, is_public=True, limit=20):
        """Search knowledge base articles"""
        from app.models.knowledge import KnowledgeArticle
        from app import db
        
        base_query = KnowledgeArticle.query.filter_by(is_published=True)
        
        if is_public:
            base_query = base_query.filter_by(is_public=True)
        
        search_term = f"%{query}%"
        return base_query.filter(
            db.or_(
                KnowledgeArticle.title.like(search_term),
                KnowledgeArticle.content.like(search_term),
                KnowledgeArticle.summary.like(search_term),
                KnowledgeArticle.tags.like(search_term)
            )
        ).order_by(KnowledgeArticle.view_count.desc()).limit(limit).all()

class BackupManager:
    """Database backup utilities"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def create_backup(self, backup_path=None):
        """Create database backup"""
        if backup_path is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"backups/helpdesk_backup_{timestamp}"
        
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        
        if 'sqlite' in database_url.lower():
            return self._backup_sqlite(backup_path)
        elif 'mysql' in database_url.lower():
            return self._backup_mysql(backup_path)
        
        raise NotImplementedError("Backup not supported for this database type")
    
    def _backup_sqlite(self, backup_path):
        """Backup SQLite database"""
        import shutil
        from urllib.parse import urlparse
        
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        db_path = urlparse(database_url).path
        
        # Remove leading slash if present
        if db_path.startswith('/'):
            db_path = db_path[1:]
        
        # Ensure backup directory exists
        os.makedirs(os.path.dirname(backup_path + '.db'), exist_ok=True)
        
        # Copy database file
        shutil.copy2(db_path, backup_path + '.db')
        
        current_app.logger.info(f"SQLite backup created: {backup_path}.db")
        return backup_path + '.db'
    
    def _backup_mysql(self, backup_path):
        """Backup MySQL database"""
        import subprocess
        from urllib.parse import urlparse
        
        database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        parsed = urlparse(database_url)
        
        # Ensure backup directory exists
        os.makedirs(os.path.dirname(backup_path + '.sql'), exist_ok=True)
        
        # Create mysqldump command
        cmd = [
            'mysqldump',
            '-h', parsed.hostname or 'localhost',
            '-P', str(parsed.port or 3306),
            '-u', parsed.username,
            f'-p{parsed.password}',
            parsed.path.lstrip('/'),
        ]
        
        # Run mysqldump
        with open(backup_path + '.sql', 'w') as backup_file:
            result = subprocess.run(cmd, stdout=backup_file, stderr=subprocess.PIPE)
        
        if result.returncode == 0:
            current_app.logger.info(f"MySQL backup created: {backup_path}.sql")
            return backup_path + '.sql'
        else:
            error_msg = result.stderr.decode()
            current_app.logger.error(f"MySQL backup failed: {error_msg}")
            raise RuntimeError(f"MySQL backup failed: {error_msg}")

# Initialize database manager
db_manager = DatabaseManager()
search_manager = None
backup_manager = None

def init_database_utils(app):
    """Initialize database utilities"""
    global search_manager, backup_manager
    
    db_manager.init_app(app)
    search_manager = SearchManager(db_manager)
    backup_manager = BackupManager(db_manager)
    
    return db_manager, search_manager, backup_manager