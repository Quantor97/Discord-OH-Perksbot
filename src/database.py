import sqlite3
import settings
import os

logger = settings.logging.getLogger("database")

class Database:
    def __init__(self, db_name=settings.db_dir+'/perks.db'):
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
            # Create perks table if it doesn't exist
            self.c.execute('''CREATE TABLE IF NOT EXISTS perks (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              name TEXT UNIQUE,
                              type TEXT,
                              specialization TEXT,
                              specialization_effects TEXT
                              )''')
            
            # Create user_perks table if it doesn't exist
            self.c.execute('''CREATE TABLE IF NOT EXISTS user_perks (
                              user_id INTEGER,
                              user_name TEXT,
                              perk_id INTEGER,
                              FOREIGN KEY (perk_id) REFERENCES perks(id)
                              )''')
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error creating tables: {e}")

    def add_user_perks(self, user_id, user_name, perk_names):
        try:
            # Add perks for a user
            with self.conn:
                for perk_name in perk_names:
                    self.c.execute("SELECT id FROM perks WHERE name = ?", (perk_name,))
                    perk_id = self.c.fetchone()
                    if perk_id:
                        self.c.execute("INSERT INTO user_perks (user_id, user_name, perk_id) VALUES (?, ?, ?)", (user_id, user_name, perk_id[0]))
            logger.info(f"Added perks for user {user_id} ({user_name}).")
        except Exception as e:
            logger.error(f"Error adding user perks: {e}")

    def update_user_perks(self, user_id, user_name, perk_names):
        try:
            # Update perks for a user
            with self.conn:
                self.c.execute("DELETE FROM user_perks WHERE user_id = ?", (user_id,))
                self.add_user_perks(user_id, user_name, perk_names)
            logger.info(f"Updated perks for user {user_id} ({user_name}).")
        except Exception as e:
            logger.error(f"Error updating user perks: {e}")

    def user_has_perks(self, user_id):
        try:
            # Check if a user has perks
            self.c.execute("SELECT 1 FROM user_perks WHERE user_id = ?", (user_id,))
            return self.c.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking if user has perks: {e}")
            return False

    def get_users_with_perk(self, perk_name):
        try:
            # Get users who have a specific perk
            like_perk_name = f"%{perk_name}%"
            self.c.execute("SELECT id, name FROM perks WHERE name LIKE ?", (like_perk_name,))
            perks = self.c.fetchall()
            if not perks:
                return []
            
            output = []
            for perk in perks:
                self.c.execute("SELECT user_name FROM user_perks WHERE perk_id = ?", (perk[0],))
                user_namens = self.c.fetchall()

                if not user_namens:
                    continue
                
                output.append({"id": perk[0], "name": perk[1], "users": [user_name[0] for user_name in user_namens]})

            return output
        except Exception as e:
            logger.error(f"Error getting users with perk \"{perk_name}\": {e}")
            return []

    def get_users_with_perk_type(self, perk_type):
        try:
            self.c.execute('''
                SELECT up.user_name, p.name
                FROM user_perks up
                JOIN perks p ON up.perk_id = p.id
                WHERE p.type = ?
            ''', (perk_type,))
            users_with_perks = {}
            for row in self.c.fetchall():
                user, perk = row
                if user not in users_with_perks:
                    users_with_perks[user] = []
                users_with_perks[user].append(perk)
            return users_with_perks
        except Exception as e:
            logger.error(f"Error getting users with perk type {perk_type}: {e}")
            return {}

    def get_users_with_perk_specialization(self, perk_specialization):
        try:
            self.c.execute('''
                SELECT up.user_name, p.name
                FROM user_perks up
                JOIN perks p ON up.perk_id = p.id
                WHERE p.specialization = ?
            ''', (perk_specialization,))
            users_with_perks = {}
            for row in self.c.fetchall():
                user, perk = row
                if user not in users_with_perks:
                    users_with_perks[user] = []
                users_with_perks[user].append(perk)
            return users_with_perks
        except Exception as e:
            logger.error(f"Error getting users with perk specialization {perk_specialization}: {e}")
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

    def update_perks(self, perks):
        try:
            # Update the list of perks
            with self.conn:
                self.c.execute("DELETE FROM perks")
                for perk in perks:
                    self.c.execute("INSERT INTO perks (name, type, specialization, specialization_effects) VALUES (?, ?, ?, ?)",
                                   (perk['Name'], perk['Type'], perk['Specialization'], perk['Specialization Effects']))
                self.conn.commit()
            logger.info("Perks list updated.")
        except Exception as e:
            logger.error(f"Error updating perks list: {e}")

    def get_perks(self):
        try:
            # Get the list of perks
            self.c.execute("SELECT name FROM perks")
            return [row[0] for row in self.c.fetchall()]
        except Exception as e:
            logger.error(f"Error getting perks list: {e}")
            return []
        
    def get_perk_info(self, perk_id):
        try:
            self.c.execute("SELECT name, type, specialization, specialization_effects FROM perks WHERE id = ?", (perk_id,))
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
            logger.error(f"Error getting perk info for perk_id {perk_id}: {e}")
            return None

    def get_user_perks(self, user_id):
        try:
            self.c.execute('''
                SELECT p.name
                FROM perks p
                JOIN user_perks up ON p.id = up.perk_id
                WHERE up.user_id = ?
            ''', (user_id,))
            return [row[0] for row in self.c.fetchall()]
        except Exception as e:
            logger.error(f"Error getting user perks: {e}")
            return []

    def get_all_users_with_perks(self):
        try:
            self.c.execute('''
                SELECT up.user_name, p.name
                FROM user_perks up
                JOIN perks p ON up.perk_id = p.id
            ''')
            users_with_perks = {}
            for row in self.c.fetchall():
                user, perk = row
                if user not in users_with_perks:
                    users_with_perks[user] = []
                users_with_perks[user].append(perk)
            return users_with_perks
        except Exception as e:
            logger.error(f"Error getting all users with perks: {e}")
            return {}
        
    def clear_user_perks(self, user_id):
        try:
            with self.conn:
                self.c.execute("DELETE FROM user_perks WHERE user_id = ?", (user_id,))
            logger.info(f"Cleared perks for user {user_id}.")
        except Exception as e:
            logger.error(f"Error clearing user perks: {e}")
            return False