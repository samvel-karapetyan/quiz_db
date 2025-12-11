# Quiz Construction System

A comprehensive quiz management system built with Python, Tkinter, and SQLite. Features role-based access control, SQL transactions for data integrity, and a modern GUI interface.

## Data Model

### E/R Model

The system consists of the following entities:

- **User**: Represents system users (administrators and regular users)
  - Attributes: id, username, password, role

- **Quiz**: Represents a quiz created by an administrator
  - Attributes: id, title, description, created_by, created_at

- **Question**: Represents a question within a quiz
  - Attributes: id, quiz_id, question_text, question_type, points

- **Option**: Represents an answer option for a question
  - Attributes: id, question_id, option_text, is_correct

- **Response**: Represents a user's answer to a question
  - Attributes: id, user_id, question_id, selected_option_id, response_time

- **Score**: Represents a user's score for a completed quiz
  - Attributes: id, user_id, quiz_id, score, total_points, completed_at

### Relational Model (3NF)

The database is normalized to **Third Normal Form (3NF)**:

1. **First Normal Form (1NF)**: All attributes are atomic
2. **Second Normal Form (2NF)**: All non-key attributes are fully functionally dependent on the primary key
3. **Third Normal Form (3NF)**: No transitive dependencies exist

**Tables:**

1. `users` (id PK, username UNIQUE, password, role)
2. `quizzes` (id PK, title, description, created_by FK→users.id, created_at)
3. `questions` (id PK, quiz_id FK→quizzes.id, question_text, question_type, points)
4. `options` (id PK, question_id FK→questions.id, option_text, is_correct)
5. `responses` (id PK, user_id FK→users.id, question_id FK→questions.id, selected_option_id FK→options.id, response_time)
6. `scores` (id PK, user_id FK→users.id, quiz_id FK→quizzes.id, score, total_points, completed_at)

**Referential Integrity:**
- Foreign keys enforce relationships between tables
- CASCADE deletes maintain consistency (deleting a quiz automatically deletes its questions and options)
- CHECK constraints validate data types and values

## SQL Transactions

The system uses SQL transactions extensively to ensure data integrity:

- **Atomic Operations**: Question creation with options, quiz responses saving, and demo quiz creation are all atomic
- **Rollback on Errors**: All write operations use try/except blocks with rollback on failure
- **Data Consistency**: Transactions ensure that related data is saved together or not at all

Key transaction methods:
- `save_question_with_options()`: Atomically saves question and all its options
- `save_all_responses()`: Atomically saves all user responses for a quiz
- `create_demo_quizzes()`: Creates complete demo quizzes with all questions and options in one transaction

## Installation and Usage

### Requirements

- Python 3.7+
- tkinter (usually included with Python)
- SQLite3 (included with Python)

### Running the Application

```bash
python main.py
```

### Default Credentials

- **Admin**: username: `admin`, password: `admin`
- Regular users can register through the login window

### Features

**Administrator Features:**
- Create, edit, and delete quizzes
- Add questions to quizzes (single choice or multiple choice)
- Add answer options for each question with correct/incorrect marking
- Set points per question
- Create demo quizzes with sample data
- View all quizzes sorted alphabetically
- Sign out to switch accounts

**User Features:**
- View available quizzes
- Take quizzes with question navigation
- Submit quizzes and receive immediate scores
- View score history with percentage grades
- Sign out to switch accounts

## Project Structure

```
quiz_inqnuruyn/
├── main.py              # Application entry point and routing
├── database.py          # Database layer with SQL operations and transactions
├── auth_window.py       # Authentication UI (login/register)
├── admin_window.py      # Admin panel for quiz management
├── user_window.py       # User panel for taking quizzes
├── styles.py            # UI styling and theme management
├── quiz.db              # SQLite database file (created automatically)
└── README.md            # This file
```

## Architecture

The application follows a layered architecture:

1. **UI Layer**: Tkinter windows for user interaction
2. **Business Logic Layer**: Window classes handle UI logic and user interactions
3. **Data Access Layer**: Database class manages all SQL operations
4. **Database Layer**: SQLite database with normalized schema

## Score Calculation

- **Single Choice Questions**: User must select the one correct option to earn points
- **Multiple Choice Questions**: User must select exactly all correct options (no more, no less) to earn points
- Final score is the sum of points earned across all questions

