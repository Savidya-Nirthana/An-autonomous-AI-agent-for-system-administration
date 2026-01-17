import psycopg2
from psycopg2 import pool
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.connection_pool = None
        self.init_pool()
    
    def init_pool(self):
        """Initialize PostgreSQL connection pool"""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'admin_mind'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres')
            )
        except Exception as e:
            raise Exception(f"Database connection failed: {e}")
    
    def get_connection(self):
        """Get connection from pool"""
        return self.connection_pool.getconn()
    
    def release_connection(self, conn):
        """Release connection back to pool"""
        self.connection_pool.putconn(conn)
    
    def init_tables(self):
        """Initialize database tables"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            
            # Create sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id VARCHAR(100) PRIMARY KEY,
                    username VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise Exception(f"Table creation failed: {e}")
        finally:
            cursor.close()
            self.release_connection(conn)
    
    def create_user(self, username, password):
        """Create a new user with hashed password"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash.decode('utf-8'))
            )
            
            conn.commit()
            return True
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            return False
        except Exception as e:
            conn.rollback()
            raise Exception(f"User creation failed: {e}")
        finally:
            cursor.close()
            self.release_connection(conn)
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT password_hash FROM users WHERE username = %s",
                (username,)
            )
            
            result = cursor.fetchone()
            
            if result:
                password_hash = result[0]
                if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                    # Update last login
                    cursor.execute(
                        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = %s",
                        (username,)
                    )
                    conn.commit()
                    return True
            
            return False
        except Exception as e:
            raise Exception(f"User verification failed: {e}")
        finally:
            cursor.close()
            self.release_connection(conn)
    
    def close_all(self):
        """Close all connections"""
        if self.connection_pool:
            self.connection_pool.closeall()