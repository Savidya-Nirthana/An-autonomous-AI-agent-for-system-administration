from auth.database import Database
from auth.session_manager import SessionManager

class AuthManager:
    def __init__(self):
        self.db = Database()
        self.session_manager = SessionManager()
    
    def initialize(self):
        """Initialize database tables"""
        self.db.init_tables()
    
    def register_user(self, username, password):
        """Register a new user"""
        return self.db.create_user(username, password)
    
    def login(self, username, password):
        """
        Login user and create session
        Returns: session_id if successful, None if failed
        """
        # Verify credentials
        if self.db.verify_user(username, password):
            # Create session
            session_id = self.session_manager.create_session(username)
            return session_id
        
        return None
    
    def logout(self, session_id):
        """
        Logout user and destroy session
        Clears all session data and chat history
        """
        return self.session_manager.destroy_session(session_id)
    
    def validate_session(self, session_id):
        """Check if session is valid and active"""
        return self.session_manager.validate_session(session_id)
    
    def get_session_info(self, session_id):
        """Get session information"""
        return self.session_manager.get_session(session_id)
    
    def get_session_username(self, session_id):
        """Get username from session"""
        session_data = self.session_manager.get_session(session_id)
        return session_data['username'] if session_data else None
    
    def get_active_sessions(self, username):
        """Get all active sessions for user"""
        return self.session_manager.get_active_sessions(username)
    
    def close(self):
        """Close all connections"""
        self.db.close_all()