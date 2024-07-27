import sqlite3
import settings
import os

logger = settings.logging.getLogger("database")

class Database:
    def __init__(self, db_name=settings.db_dir+"/perks.db"):
        try:
            # Check if the database file exists
            if not os.path.isfile(db_name):
                logger.info(f"Database file {db_name} not found. Creating a new one.")

            # Connect to the SQLite database
            self.conn = sqlite3.connect(db_name)
            self.c = self.conn.cursor()
            self.create_tables()
            logger.info("Database connected and tables created.")
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")

    def create_tables(self):
        try:
            # Create users table
            self.c.execute('''CREATE TABLE IF NOT EXISTS users (
                              user_id INTEGER PRIMARY KEY,
                              user_name TEXT
                              )''')

            # Create user_perks table
            self.c.execute('''CREATE TABLE IF NOT EXISTS user_perks (
                              user_id INTEGER,
                              perk_name TEXT,
                              FOREIGN KEY (user_id) REFERENCES users (user_id),
                              FOREIGN KEY (perk_name) REFERENCES perks (perk_name)
                              )''')

            # Create perks table
            self.c.execute('''CREATE TABLE IF NOT EXISTS perks (
                              perk_name TEXT PRIMARY KEY,
                              type TEXT,
                              specialization TEXT,
                              specialization_effects TEXT
                              )''')
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error creating tables: {e}")

    def add_user(self, user_id, user_name):
        try:
            with self.conn:
                self.c.execute("INSERT OR IGNORE INTO users (user_id, user_name) VALUES (?, ?)", (user_id, user_name))
            logger.info(f"Added user {user_name} with ID {user_id}.")
        except Exception as e:
            logger.error(f"Error adding user: {e}")

    def add_user_perks(self, user_id, perks):
        try:
            with self.conn:
                for perk in perks:
                    self.c.execute("INSERT INTO user_perks (user_id, perk_name) VALUES (?, ?)", (user_id, perk))
            logger.info(f"Added perks for user {user_id}.")
        except Exception as e:
            logger.error(f"Error adding user perks: {e}")

    def update_user_perks(self, user_id, perks):
        try:
            with self.conn:
                self.c.execute("DELETE FROM user_perks WHERE user_id = ?", (user_id,))
                self.add_user_perks(user_id, perks)
            logger.info(f"Updated perks for user {user_id}.")
        except Exception as e:
            logger.error(f"Error updating user perks: {e}")

    def get_user_perks(self, user_id):
        try:
            self.c.execute("SELECT perk_name FROM user_perks WHERE user_id = ?", (user_id,))
            return [row[0] for row in self.c.fetchall()]
        except Exception as e:
            logger.error(f"Error getting user perks: {e}")
            return []

    def user_has_perks(self, user_id):
        try:
            self.c.execute("SELECT 1 FROM user_perks WHERE user_id = ?", (user_id,))
            return self.c.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking if user has perks: {e}")
            return False
    
    def update_perks(self, perks):
        try:
            with self.conn:
                self.c.execute("DELETE FROM perks")
                for perk in perks:
                    self.c.execute("INSERT INTO perks (perk_name, type, specialization, specialization_effects) VALUES (?, ?, ?, ?)",
                                   (perk['Name'], perk['Type'], perk['Specialization'], perk['Specialization Effects']))
            logger.info("Perks updated in the database.")
        except Exception as e:
            logger.error(f"Error updating perks: {e}")

    def get_perks(self):
        try:
            self.c.execute("SELECT perk_name FROM perks")
            return [row[0] for row in self.c.fetchall()]
        except Exception as e:
            logger.error(f"Error getting perks: {e}")
            return []

    def clear_user_perks(self, user_id):
        try:
            # Clear all perks for a user
            with self.conn:
                self.c.execute("DELETE FROM user_perks WHERE user_id = ?", (user_id,))
            logger.info(f"Cleared all perks for user {user_id}.")
        except Exception as e:
            logger.error(f"Error clearing perks for user {user_id}: {e}")

    def get_perk_info(self, perk_name):
        try:
            self.c.execute("SELECT * FROM perks WHERE perk_name = ?", (perk_name,))
            row = self.c.fetchone()
            if row:
                return {
                    "name": row[0],
                    "type": row[1],
                    "specialization": row[2],
                    "specialization_effects": row[3]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting perk info: {e}")
            return None

    def get_users_with_perk(self, perk_name):
        try:
            like_perk = f"%{perk_name}%"
            
            self.c.execute('''
                SELECT users.user_name, group_concat(user_perks.perk_name) as perks 
                FROM users
                JOIN user_perks ON users.user_id = user_perks.user_id
                WHERE user_perks.perk_name like ?
                GROUP BY users.user_name
            ''', (like_perk,))
            return [{"name": row[0], "users": row[1].split(",")} for row in self.c.fetchall()]
        except Exception as e:
            logger.error(f"Error getting users with perk: {e}")
            return []

    def get_users_with_perk_type(self, perk_type):
        try:
            self.c.execute('''
                SELECT users.user_name, group_concat(user_perks.perk_name) as perks 
                FROM users
                JOIN user_perks ON users.user_id = user_perks.user_id
                JOIN perks ON user_perks.perk_name = perks.perk_name
                WHERE perks.type = ?
                GROUP BY users.user_name
            ''', (perk_type,))
            return {row[0]: row[1].split(",") for row in self.c.fetchall()}
        except Exception as e:
            logger.error(f"Error getting users with perk type: {e}")
            return {}

    def get_users_with_perk_specialization(self, specialization):
        try:
            self.c.execute('''
                SELECT users.user_name, group_concat(user_perks.perk_name) as perks 
                FROM users
                JOIN user_perks ON users.user_id = user_perks.user_id
                JOIN perks ON user_perks.perk_name = perks.perk_name
                WHERE perks.specialization = ?
                GROUP BY users.user_name
            ''', (specialization,))
            return {row[0]: row[1].split(",") for row in self.c.fetchall()}
        except Exception as e:
            logger.error(f"Error getting users with perk specialization: {e}")
            return {}

    def get_all_users_with_perks(self):
        try:
            self.c.execute('''
                SELECT users.user_name, group_concat(user_perks.perk_name) as perks 
                FROM users
                JOIN user_perks ON users.user_id = user_perks.user_id
                GROUP BY users.user_name
            ''')
            return {row[0]: row[1].split(",") for row in self.c.fetchall()}
        except Exception as e:
            logger.error(f"Error getting all users with perks: {e}")
            return {}

    def get_perk_types(self):
        try:
            self.c.execute("SELECT DISTINCT type FROM perks")
            return [row[0] for row in self.c.fetchall()]
        except Exception as e:
            logger.error(f"Error getting perk types: {e}")
            return []

    def get_perk_specializations(self):
        try:
            self.c.execute("SELECT DISTINCT specialization FROM perks")
            return [row[0] for row in self.c.fetchall()]
        except Exception as e:
            logger.error(f"Error getting perk specializations: {e}")
            return []
