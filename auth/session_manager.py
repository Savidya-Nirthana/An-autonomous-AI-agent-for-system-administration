import redis
import uuid
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class SessionManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
        self.session_timeout = int(os.getenv('SESSION_TIMEOUT', 3600))  # Default 1 hour
    
    def create_session(self, username):
        """Create a new session for user"""
        session_id = f"{username}-{uuid.uuid4().hex[:8]}"
        
        session_data = {
            'username': username,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        
        # Store session in Redis with expiration
        self.redis_client.setex(
            f"session:{session_id}",
            self.session_timeout,
            json.dumps(session_data)
        )
        
        return session_id
    
    def get_session(self, session_id):
        """Get session data"""
        session_key = f"session:{session_id}"
        session_data = self.redis_client.get(session_key)
        
        if session_data:
            # Update last activity and refresh TTL
            data = json.loads(session_data)
            data['last_activity'] = datetime.now().isoformat()
            self.redis_client.setex(
                session_key,
                self.session_timeout,
                json.dumps(data)
            )
            return data
        
        return None
    
    def validate_session(self, session_id):
        """Check if session is valid"""
        return self.redis_client.exists(f"session:{session_id}") > 0
    
    def destroy_session(self, session_id):
        """Destroy session and clear all related data"""
        try:
            # Delete session
            self.redis_client.delete(f"session:{session_id}")
            
            # Delete chat memory for this session
            self.redis_client.delete(f"chat:{session_id}")
            
            # Delete any other session-related keys
            pattern = f"*:{session_id}"
            for key in self.redis_client.scan_iter(match=pattern):
                self.redis_client.delete(key)
            
            return True
        except Exception as e:
            raise Exception(f"Session destruction failed: {e}")
    
    def get_active_sessions(self, username):
        """Get all active sessions for a user"""
        sessions = []
        for key in self.redis_client.scan_iter(match=f"session:{username}-*"):
            session_data = self.redis_client.get(key)
            if session_data:
                sessions.append({
                    'session_id': key.replace('session:', ''),
                    'data': json.loads(session_data)
                })
        return sessions
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions (Redis handles this automatically with TTL)"""
        pass
    
    def get_session_ttl(self, session_id):
        """Get remaining time for session"""
        ttl = self.redis_client.ttl(f"session:{session_id}")
        return ttl if ttl > 0 else 0