import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import hashlib

class Database:
    def __init__(self, db_path: str = "quiz.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.isolation_level = "IMMEDIATE"
        return conn
    
    def init_database(self) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                question_type TEXT NOT NULL CHECK(question_type IN ('single_choice', 'multiple_choice')),
                points INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                option_text TEXT NOT NULL,
                is_correct INTEGER NOT NULL CHECK(is_correct IN (0, 1)),
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                selected_option_id INTEGER NOT NULL,
                response_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (question_id) REFERENCES questions(id),
                FOREIGN KEY (selected_option_id) REFERENCES options(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                quiz_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                total_points INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        admin_password_hash = hashlib.sha256('admin'.encode()).hexdigest()
        
        if admin_count == 0:
            cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES ('admin', ?, 'admin')
            """, (admin_password_hash,))
        else:
            cursor.execute("""
                UPDATE users 
                SET password = ? 
                WHERE username = 'admin' AND (password = 'admin' OR LENGTH(password) != 64)
            """, (admin_password_hash,))
        
        conn.commit()
        conn.close()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, role FROM users
            WHERE username = ? AND password = ?
        """, (username, password))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {"id": result[0], "username": result[1], "role": result[2]}
        return None
    
    def create_user(self, username: str, password: str, role: str = "user") -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            """, (username, password, role))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            raise ValueError("Username already exists")
    
    def create_quiz(self, title: str, description: str, created_by: int) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO quizzes (title, description, created_by)
                VALUES (?, ?, ?)
            """, (title, description, created_by))
            conn.commit()
            quiz_id = cursor.lastrowid
            conn.close()
            return quiz_id
        except Exception as e:
            conn.rollback()
            conn.close()
            raise
    
    def update_quiz(self, quiz_id: int, title: str, description: str) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE quizzes
                SET title = ?, description = ?
                WHERE id = ?
            """, (title, description, quiz_id))
            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise
    
    def add_question(self, quiz_id: int, question_text: str, question_type: str, points: int = 1) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO questions (quiz_id, question_text, question_type, points)
                VALUES (?, ?, ?, ?)
            """, (quiz_id, question_text, question_type, points))
            conn.commit()
            question_id = cursor.lastrowid
            conn.close()
            return question_id
        except Exception as e:
            conn.rollback()
            conn.close()
            raise
    
    def update_question(self, question_id: int, question_text: str, question_type: str, points: int) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE questions
                SET question_text = ?, question_type = ?, points = ?
                WHERE id = ?
            """, (question_text, question_type, points, question_id))
            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise
    
    def add_option(self, question_id: int, option_text: str, is_correct: int) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO options (question_id, option_text, is_correct)
                VALUES (?, ?, ?)
            """, (question_id, option_text, is_correct))
            conn.commit()
            option_id = cursor.lastrowid
            conn.close()
            return option_id
        except Exception as e:
            conn.rollback()
            conn.close()
            raise
    
    def save_question_with_options(self, quiz_id: int, question_id: Optional[int], question_text: str, 
                                   question_type: str, points: int, options: List[Dict]) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if question_id:
                cursor.execute("""
                    UPDATE questions
                    SET question_text = ?, question_type = ?, points = ?
                    WHERE id = ?
                """, (question_text, question_type, points, question_id))
                cursor.execute("DELETE FROM options WHERE question_id = ?", (question_id,))
            else:
                cursor.execute("""
                    INSERT INTO questions (quiz_id, question_text, question_type, points)
                    VALUES (?, ?, ?, ?)
                """, (quiz_id, question_text, question_type, points))
                question_id = cursor.lastrowid
            
            for opt in options:
                cursor.execute("""
                    INSERT INTO options (question_id, option_text, is_correct)
                    VALUES (?, ?, ?)
                """, (question_id, opt["text"], 1 if opt["is_correct"] else 0))
            
            conn.commit()
            conn.close()
            return question_id
        except Exception as e:
            conn.rollback()
            conn.close()
            raise
    
    def get_all_quizzes(self) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, description, created_at
            FROM quizzes
            ORDER BY title ASC
        """)
        quizzes = []
        for row in cursor.fetchall():
            quizzes.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "created_at": row[3]
            })
        conn.close()
        return quizzes
    
    def get_quiz_with_questions(self, quiz_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, description
            FROM quizzes WHERE id = ?
        """, (quiz_id,))
        quiz_row = cursor.fetchone()
        if not quiz_row:
            conn.close()
            return None
        
        quiz = {
            "id": quiz_row[0],
            "title": quiz_row[1],
            "description": quiz_row[2],
            "questions": []
        }
        
        cursor.execute("""
            SELECT id, question_text, question_type, points
            FROM questions WHERE quiz_id = ?
            ORDER BY id
        """, (quiz_id,))
        
        for q_row in cursor.fetchall():
            question = {
                "id": q_row[0],
                "question_text": q_row[1],
                "question_type": q_row[2],
                "points": q_row[3],
                "options": []
            }
            
            cursor.execute("""
                SELECT id, option_text, is_correct
                FROM options WHERE question_id = ?
                ORDER BY id
            """, (question["id"],))
            
            for opt_row in cursor.fetchall():
                question["options"].append({
                    "id": opt_row[0],
                    "option_text": opt_row[1],
                    "is_correct": bool(opt_row[2])
                })
            
            quiz["questions"].append(question)
        
        conn.close()
        return quiz
    
    def save_response(self, user_id: int, question_id: int, selected_option_id: int) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO responses (user_id, question_id, selected_option_id)
                VALUES (?, ?, ?)
            """, (user_id, question_id, selected_option_id))
            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise
    
    def save_all_responses(self, user_id: int, responses: List[Tuple[int, int]]) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            for question_id, selected_option_id in responses:
                cursor.execute("""
                    INSERT INTO responses (user_id, question_id, selected_option_id)
                    VALUES (?, ?, ?)
                """, (user_id, question_id, selected_option_id))
            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise
    
    def calculate_score(self, user_id: int, quiz_id: int) -> Tuple[int, int]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT q.id, q.question_type, q.points
            FROM questions q
            WHERE q.quiz_id = ?
        """, (quiz_id,))
        
        questions = cursor.fetchall()
        total_points = sum(q[2] for q in questions)
        earned_points = 0
        
        for question_id, question_type, points in questions:
            cursor.execute("""
                SELECT o.id, o.is_correct
                FROM options o
                WHERE o.question_id = ?
            """, (question_id,))
            options = cursor.fetchall()
            
            cursor.execute("""
                SELECT selected_option_id
                FROM responses
                WHERE user_id = ? AND question_id = ?
            """, (user_id, question_id))
            user_responses = [r[0] for r in cursor.fetchall()]
            
            if question_type == "single_choice":
                correct_option = next((opt[0] for opt in options if opt[1] == 1), None)
                if correct_option and correct_option in user_responses:
                    earned_points += points
            else:
                correct_options = {opt[0] for opt in options if opt[1] == 1}
                user_selected = set(user_responses)
                if correct_options and user_selected == correct_options:
                    earned_points += points
        
        conn.close()
        return earned_points, total_points
    
    def save_score(self, user_id: int, quiz_id: int, score: int, total_points: int) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO scores (user_id, quiz_id, score, total_points)
                VALUES (?, ?, ?, ?)
            """, (user_id, quiz_id, score, total_points))
            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise
    
    def delete_quiz(self, quiz_id: int) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise
    
    def delete_question(self, question_id: int) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            conn.rollback()
            conn.close()
            raise
    
    def create_demo_quizzes(self, admin_id: int) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            demo_quizzes = [
                {
                    "title": "Demo: Python Basics",
                    "description": "Test your knowledge of Python programming fundamentals",
                    "questions": [
                        {
                            "text": "What is the correct way to create a list in Python?",
                            "type": "single_choice",
                            "points": 1,
                            "options": [
                                {"text": "list = []", "correct": True},
                                {"text": "list = {}", "correct": False},
                                {"text": "list = ()", "correct": False},
                                {"text": "list = None", "correct": False}
                            ]
                        },
                        {
                            "text": "Which of the following are Python data types?",
                            "type": "multiple_choice",
                            "points": 2,
                            "options": [
                                {"text": "int", "correct": True},
                                {"text": "str", "correct": True},
                                {"text": "float", "correct": True},
                                {"text": "char", "correct": False}
                            ]
                        },
                        {
                            "text": "What does the 'len()' function do?",
                            "type": "single_choice",
                            "points": 1,
                            "options": [
                                {"text": "Returns the length of an object", "correct": True},
                                {"text": "Returns the maximum value", "correct": False},
                                {"text": "Returns the minimum value", "correct": False},
                                {"text": "Converts to lowercase", "correct": False}
                            ]
                        },
                        {
                            "text": "How do you define a function in Python?",
                            "type": "single_choice",
                            "points": 1,
                            "options": [
                                {"text": "def function_name():", "correct": True},
                                {"text": "function function_name():", "correct": False},
                                {"text": "define function_name():", "correct": False},
                                {"text": "func function_name():", "correct": False}
                            ]
                        },
                        {
                            "text": "Which methods can be used to add elements to a list?",
                            "type": "multiple_choice",
                            "points": 2,
                            "options": [
                                {"text": "append()", "correct": True},
                                {"text": "insert()", "correct": True},
                                {"text": "extend()", "correct": True},
                                {"text": "add()", "correct": False}
                            ]
                        }
                    ]
                },
                {
                    "title": "Demo: SQL Fundamentals",
                    "description": "Basic SQL knowledge quiz covering queries, transactions, and database concepts",
                    "questions": [
                        {
                            "text": "What does SQL stand for?",
                            "type": "single_choice",
                            "points": 1,
                            "options": [
                                {"text": "Structured Query Language", "correct": True},
                                {"text": "Simple Query Language", "correct": False},
                                {"text": "Standard Query Language", "correct": False},
                                {"text": "System Query Language", "correct": False}
                            ]
                        },
                        {
                            "text": "Which SQL statements are used for data manipulation?",
                            "type": "multiple_choice",
                            "points": 2,
                            "options": [
                                {"text": "SELECT", "correct": True},
                                {"text": "INSERT", "correct": True},
                                {"text": "UPDATE", "correct": True},
                                {"text": "CREATE", "correct": False}
                            ]
                        },
                        {
                            "text": "What is a transaction in SQL?",
                            "type": "single_choice",
                            "points": 2,
                            "options": [
                                {"text": "A sequence of operations executed as a single unit", "correct": True},
                                {"text": "A database table", "correct": False},
                                {"text": "A SQL function", "correct": False},
                                {"text": "A data type", "correct": False}
                            ]
                        },
                        {
                            "text": "What is the purpose of the PRIMARY KEY constraint?",
                            "type": "single_choice",
                            "points": 1,
                            "options": [
                                {"text": "Uniquely identifies each row in a table", "correct": True},
                                {"text": "Links two tables together", "correct": False},
                                {"text": "Prevents NULL values", "correct": False},
                                {"text": "Sorts data automatically", "correct": False}
                            ]
                        },
                        {
                            "text": "Which SQL commands are used for transaction control?",
                            "type": "multiple_choice",
                            "points": 2,
                            "options": [
                                {"text": "COMMIT", "correct": True},
                                {"text": "ROLLBACK", "correct": True},
                                {"text": "BEGIN TRANSACTION", "correct": True},
                                {"text": "EXECUTE", "correct": False}
                            ]
                        }
                    ]
                },
                {
                    "title": "Demo: General Knowledge",
                    "description": "A fun general knowledge quiz covering various topics",
                    "questions": [
                        {
                            "text": "What is the capital of France?",
                            "type": "single_choice",
                            "points": 1,
                            "options": [
                                {"text": "Paris", "correct": True},
                                {"text": "London", "correct": False},
                                {"text": "Berlin", "correct": False},
                                {"text": "Madrid", "correct": False}
                            ]
                        },
                        {
                            "text": "Which of these are programming languages?",
                            "type": "multiple_choice",
                            "points": 2,
                            "options": [
                                {"text": "Python", "correct": True},
                                {"text": "Java", "correct": True},
                                {"text": "HTML", "correct": False},
                                {"text": "CSS", "correct": False}
                            ]
                        },
                        {
                            "text": "What is 2 + 2?",
                            "type": "single_choice",
                            "points": 1,
                            "options": [
                                {"text": "4", "correct": True},
                                {"text": "3", "correct": False},
                                {"text": "5", "correct": False},
                                {"text": "6", "correct": False}
                            ]
                        },
                        {
                            "text": "Which planets are in our solar system?",
                            "type": "multiple_choice",
                            "points": 2,
                            "options": [
                                {"text": "Earth", "correct": True},
                                {"text": "Mars", "correct": True},
                                {"text": "Jupiter", "correct": True},
                                {"text": "Pluto", "correct": False}
                            ]
                        }
                    ]
                },
                {
                    "title": "Demo: Web Development",
                    "description": "Quiz about web development technologies and concepts",
                    "questions": [
                        {
                            "text": "What does HTML stand for?",
                            "type": "single_choice",
                            "points": 1,
                            "options": [
                                {"text": "HyperText Markup Language", "correct": True},
                                {"text": "High Tech Modern Language", "correct": False},
                                {"text": "Home Tool Markup Language", "correct": False},
                                {"text": "Hyperlink Text Markup Language", "correct": False}
                            ]
                        },
                        {
                            "text": "Which of these are HTTP methods?",
                            "type": "multiple_choice",
                            "points": 2,
                            "options": [
                                {"text": "GET", "correct": True},
                                {"text": "POST", "correct": True},
                                {"text": "PUT", "correct": True},
                                {"text": "FETCH", "correct": False}
                            ]
                        },
                        {
                            "text": "What is CSS used for?",
                            "type": "single_choice",
                            "points": 1,
                            "options": [
                                {"text": "Styling web pages", "correct": True},
                                {"text": "Creating databases", "correct": False},
                                {"text": "Writing server code", "correct": False},
                                {"text": "Managing files", "correct": False}
                            ]
                        },
                        {
                            "text": "Which technologies are used for frontend development?",
                            "type": "multiple_choice",
                            "points": 2,
                            "options": [
                                {"text": "JavaScript", "correct": True},
                                {"text": "React", "correct": True},
                                {"text": "CSS", "correct": True},
                                {"text": "MySQL", "correct": False}
                            ]
                        }
                    ]
                }
            ]
            
            created_count = 0
            for quiz_data in demo_quizzes:
                cursor.execute("SELECT id FROM quizzes WHERE title = ?", (quiz_data["title"],))
                existing = cursor.fetchone()
                
                if existing:
                    continue
                
                cursor.execute("""
                    INSERT INTO quizzes (title, description, created_by)
                    VALUES (?, ?, ?)
                """, (quiz_data["title"], quiz_data["description"], admin_id))
                quiz_id = cursor.lastrowid
                created_count += 1
                
                for q_data in quiz_data["questions"]:
                    cursor.execute("""
                        INSERT INTO questions (quiz_id, question_text, question_type, points)
                        VALUES (?, ?, ?, ?)
                    """, (quiz_id, q_data["text"], q_data["type"], q_data["points"]))
                    question_id = cursor.lastrowid
                    
                    for opt_data in q_data["options"]:
                        cursor.execute("""
                            INSERT INTO options (question_id, option_text, is_correct)
                            VALUES (?, ?, ?)
                        """, (question_id, opt_data["text"], 1 if opt_data["correct"] else 0))
            
            conn.commit()
            conn.close()
            return created_count
        except Exception as e:
            conn.rollback()
            conn.close()
            raise
    
    def get_user_scores(self, user_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, q.title, s.score, s.total_points, s.completed_at
            FROM scores s
            JOIN quizzes q ON s.quiz_id = q.id
            WHERE s.user_id = ?
            ORDER BY s.completed_at DESC
        """, (user_id,))
        scores = []
        for row in cursor.fetchall():
            scores.append({
                "id": row[0],
                "quiz_title": row[1],
                "score": row[2],
                "total_points": row[3],
                "completed_at": row[4]
            })
        conn.close()
        return scores

