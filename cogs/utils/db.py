import mysql.connector
from mysql.connector import Error

TABLE_SCHEMAS = {
    'blacklist': """
        CREATE TABLE IF NOT EXISTS blacklist (
            user_id BIGINT PRIMARY KEY,
            reason VARCHAR(255)
        )
    """,
    'warnings': """
        CREATE TABLE IF NOT EXISTS warnings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            server_id BIGINT NOT NULL,
            user_id BIGINT NOT NULL,
            moderator_id BIGINT NOT NULL,
            reason VARCHAR(255) NOT NULL,
            warn_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_server_user (server_id, user_id),
            INDEX idx_user (user_id),
            INDEX idx_server (server_id)
        )
    """,
    'removebg': """
        CREATE TABLE IF NOT EXISTS removebg (
            server_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255)
        )
    """,
    'tiktokdl': """
        CREATE TABLE IF NOT EXISTS tiktokdl (
            server_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255)
        )
    """,
    'youtubedl': """
        CREATE TABLE IF NOT EXISTS youtubedl (
            server_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255)
        )
    """,
    'youtubedlaudio': """
        CREATE TABLE IF NOT EXISTS youtubedlaudio (
            server_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255)
        )
    """,
    'user_favorites': """
        CREATE TABLE IF NOT EXISTS user_favorites (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(255),
            amv_id VARCHAR(255),
            source VARCHAR(255)
        )
    """,
    'user_profiles': """
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id VARCHAR(255) PRIMARY KEY,
            username VARCHAR(255),
            avatar_url VARCHAR(255),
            editing_software VARCHAR(255),
            editing_style VARCHAR(255),
            amvs TEXT,
            youtube_link VARCHAR(255),
            tiktok_link VARCHAR(255),
            instagram_link VARCHAR(255)
        )
    """,
    'user_ratings': """
        CREATE TABLE IF NOT EXISTS user_ratings (
            user_id VARCHAR(255),
            rater_id VARCHAR(255),
            rating FLOAT,
            PRIMARY KEY (user_id, rater_id)
        )
    """,
    'instagramdl': """
        CREATE TABLE IF NOT EXISTS instagramdl (
            server_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255)
        )
    """,
    'animesearch': """
        CREATE TABLE IF NOT EXISTS animesearch (
            server_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255)
        )
    """,
    'disableads_servers': """
        CREATE TABLE IF NOT EXISTS disableads_servers (
            server_id VARCHAR(255) PRIMARY KEY
        )
    """,
    'removebgapi': """
        CREATE TABLE IF NOT EXISTS removebgapi (
            api_key VARCHAR(255) PRIMARY KEY
        )
    """,
    'songsearch': """
        CREATE TABLE IF NOT EXISTS songsearch (
            server_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255)
        )
    """,
    'fontsearch': """
        CREATE TABLE IF NOT EXISTS fontsearch (
            server_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255)
        )
    """,
    'ryujinai': """
        CREATE TABLE IF NOT EXISTS ryujinai (
            server_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255)
        )
    """
}

def create_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(
            host='censored',
            user='censored', 
            password='censored',
            database='censored'
        )
        return connection if connection.is_connected() else None
    except Error as e:
        print(f"Error: {e}")
        return None

def create_table(connection, table_name, schema):
    """Create a table in the database"""
    try:
        cursor = connection.cursor()
        cursor.execute(schema)
        connection.commit()
        cursor.close()
    except Error as e:
        print(f"Error: {e}")

def initialize_database():
    """Initialize all database tables"""
    connection = create_db_connection()
    if connection:
        for table_name, schema in TABLE_SCHEMAS.items():
            create_table(connection, table_name, schema)
        return connection
    return None

async def add_to_blacklist(connection, user_id, reason):
    """Add a user to the blacklist"""
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO blacklist (user_id, reason) VALUES (%s, %s) ON DUPLICATE KEY UPDATE reason = VALUES(reason)",
            (user_id, reason)
        )
        connection.commit()
        cursor.close()
    except Error as e:
        print(f"Error: {e}")

async def remove_from_blacklist(connection, user_id):
    """Remove a user from the blacklist"""
    try:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM blacklist WHERE user_id = %s",
            (user_id,)
        )
        deleted = cursor.rowcount > 0
        connection.commit()
        cursor.close()
        return deleted
    except Error as e:
        print(f"Error removing from blacklist: {e}")
        return False

def get_blacklist(connection):
    """Get all blacklisted users"""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, reason FROM blacklist")
        blacklist = {int(row[0]): row[1] for row in cursor.fetchall()}
        cursor.close()
        return blacklist
    except Error as e:
        print(f"Error: {e}")
        return {}

async def add_warning(connection, server_id, user_id, moderator_id, reason):
    """Add a warning to a user"""
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO warnings (server_id, user_id, moderator_id, reason) VALUES (%s, %s, %s, %s)",
            (server_id, user_id, moderator_id, reason)
        )
        connection.commit()
        warning_id = cursor.lastrowid
        cursor.close()
        return warning_id
    except Error as e:
        print(f"Error adding warning: {e}")
        return None

async def remove_warning(connection, warning_id, server_id, reason):
    """Remove a specific warning"""
    try:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM warnings WHERE id = %s AND server_id = %s",
            (warning_id, server_id)
        )
        deleted = cursor.rowcount > 0
        connection.commit()
        cursor.close()
        return deleted
    except Error as e:
        print(f"Error removing warning: {e}")
        return False

async def get_user_warnings(connection, server_id, user_id):
    """Get all warnings for a user in a specific server"""
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, moderator_id, reason, warn_date FROM warnings WHERE server_id = %s AND user_id = %s ORDER BY warn_date DESC",
            (server_id, user_id)
        )
        warnings = cursor.fetchall()
        cursor.close()
        return warnings
    except Error as e:
        print(f"Error getting warnings: {e}")
        return []

async def get_warning_count(connection, server_id, user_id):
    """Get the total number of warnings for a user in a server"""
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM warnings WHERE server_id = %s AND user_id = %s",
            (server_id, user_id)
        )
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    except Error as e:
        print(f"Error getting warning count: {e}")
        return 0

def get_removebg_channels(connection):
    """Get all remove background channels"""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT server_id, channel_id FROM removebg")
        channels = cursor.fetchall()
        cursor.close()
        return channels
    except Error as e:
        print(f"Error: {e}")
        return [] 