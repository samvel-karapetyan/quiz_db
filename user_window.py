import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List
from database import Database
from styles import StyleManager

class UserWindow:
    def __init__(self, db: Database, user: Dict, on_logout: callable = None):
        self.db = db
        self.user = user
        self.on_logout = on_logout
        self.current_quiz = None
        self.current_question_index = 0
        self.user_responses = {}
        
        self.window = tk.Tk()
        self.window.title(f"Quiz System - User Panel ({user['username']})")
        self.window.geometry("900x700")
        self.window.configure(bg='#f5f5f5')
        
        self.style_manager = StyleManager(self.window)
        self.create_widgets()
        self.load_quizzes()
    
    def create_widgets(self) -> None:
        header_frame = tk.Frame(self.window, bg='#34495e', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = ttk.Label(header_frame, text=f"Welcome, {self.user['username']}!", style='Title.TLabel')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        logout_button = ttk.Button(header_frame, text="🚪 Sign Out", 
                                  command=self.sign_out, style='Warning.TButton')
        logout_button.pack(side=tk.RIGHT, padx=20, pady=10)
        
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        quiz_list_frame = ttk.LabelFrame(left_frame, text="Available Quizzes", padding="10")
        quiz_list_frame.pack(fill=tk.BOTH, expand=True)
        
        list_frame = ttk.Frame(quiz_list_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.quiz_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                       font=('Arial', 10), bg='white', fg='#2c3e50',
                                       selectbackground='#3498db')
        self.quiz_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.quiz_listbox.yview)
        
        ttk.Button(quiz_list_frame, text="Start Quiz", command=self.start_quiz, 
                  style='Primary.TButton').pack(pady=(15, 0), fill=tk.X)
        
        scores_frame = ttk.LabelFrame(left_frame, text="My Scores", padding="10")
        scores_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        scores_list_frame = ttk.Frame(scores_frame)
        scores_list_frame.pack(fill=tk.BOTH, expand=True)
        
        score_scrollbar = ttk.Scrollbar(scores_list_frame)
        score_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.scores_listbox = tk.Listbox(scores_list_frame, yscrollcommand=score_scrollbar.set, 
                                         height=10, font=('Arial', 9),
                                         bg='white', fg='#2c3e50', selectbackground='#27ae60')
        self.scores_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        score_scrollbar.config(command=self.scores_listbox.yview)
        
        self.quiz_frame = ttk.LabelFrame(right_frame, text="Quiz", padding="20")
        self.quiz_frame.pack(fill=tk.BOTH, expand=True)
        
        self.quiz_title_label = ttk.Label(self.quiz_frame, text="Select a quiz to start", 
                                         font=('Arial', 14, 'bold'), foreground='#34495e')
        self.quiz_title_label.pack(pady=(0, 15))
        
        self.question_label = ttk.Label(self.quiz_frame, text="", wraplength=550, 
                                       font=('Arial', 11), foreground='#2c3e50')
        self.question_label.pack(anchor=tk.W, pady=(0, 15))
        
        self.options_frame = ttk.Frame(self.quiz_frame)
        self.options_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.option_vars = {}
        
        nav_frame = ttk.Frame(self.quiz_frame)
        nav_frame.pack(fill=tk.X)
        
        self.prev_button = ttk.Button(nav_frame, text="< Previous", command=self.prev_question, 
                                     state=tk.DISABLED, style='Primary.TButton')
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = ttk.Button(nav_frame, text="Next >", command=self.next_question, 
                                     style='Primary.TButton')
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        self.submit_button = ttk.Button(nav_frame, text="Submit Quiz", command=self.submit_quiz, 
                                       state=tk.DISABLED, style='Success.TButton')
        self.submit_button.pack(side=tk.RIGHT, padx=5)
        
        self.progress_label = ttk.Label(self.quiz_frame, text="", font=('Arial', 10, 'bold'),
                                       foreground='#7f8c8d')
        self.progress_label.pack(pady=(15, 0))
    
    def load_quizzes(self) -> None:
        self.quiz_listbox.delete(0, tk.END)
        quizzes = self.db.get_all_quizzes()
        for quiz in quizzes:
            self.quiz_listbox.insert(tk.END, f"{quiz['title']}")
        
        scores = self.db.get_user_scores(self.user["id"])
        self.scores_listbox.delete(0, tk.END)
        if scores:
            for score in scores:
                percentage = (score["score"] / score["total_points"] * 100) if score["total_points"] > 0 else 0
                grade = "[OK]" if percentage >= 80 else "[OK]" if percentage >= 60 else "[!]"
                self.scores_listbox.insert(tk.END, 
                    f"{grade} {score['quiz_title']}: {score['score']}/{score['total_points']} ({percentage:.1f}%)")
        else:
            self.scores_listbox.insert(tk.END, "No scores yet. Take a quiz to see your results here!")
    
    def start_quiz(self) -> None:
        selection = self.quiz_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a quiz to start")
            return
        
        quiz_title = self.quiz_listbox.get(selection[0])
        quizzes = self.db.get_all_quizzes()
        selected_quiz = next((q for q in quizzes if q["title"] == quiz_title), None)
        
        if not selected_quiz:
            return
        
        quiz = self.db.get_quiz_with_questions(selected_quiz["id"])
        if not quiz or not quiz["questions"]:
            messagebox.showerror("Error", "This quiz has no questions")
            return
        
        self.current_quiz = quiz
        self.current_question_index = 0
        self.user_responses = {}
        self.option_vars = {}
        
        for question in quiz["questions"]:
            self.user_responses[question["id"]] = []
        
        self.display_question()
    
    def display_question(self) -> None:
        if not self.current_quiz:
            return
        
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        self.option_vars = {}
        
        question = self.current_quiz["questions"][self.current_question_index]
        self.quiz_title_label.config(text=self.current_quiz["title"])
        self.question_label.config(text=f"Q{self.current_question_index + 1}: {question['question_text']}")
        
        is_multiple = question["question_type"] == "multiple_choice"
        
        for opt in question["options"]:
            if is_multiple:
                var = tk.BooleanVar()
                if opt["id"] in self.user_responses[question["id"]]:
                    var.set(True)
            else:
                var = tk.IntVar(value=0)
                if opt["id"] in self.user_responses[question["id"]]:
                    var.set(opt["id"])
            
            self.option_vars[opt["id"]] = var
            
            if is_multiple:
                checkbox = ttk.Checkbutton(
                    self.options_frame,
                    text=opt["option_text"],
                    variable=var,
                    command=lambda oid=opt["id"]: self.save_response(question["id"], oid, is_multiple)
                )
                checkbox.pack(anchor=tk.W, pady=8, padx=10)
            else:
                radio = ttk.Radiobutton(
                    self.options_frame,
                    text=opt["option_text"],
                    variable=var,
                    value=opt["id"],
                    command=lambda oid=opt["id"]: self.save_response(question["id"], oid, is_multiple)
                )
                radio.pack(anchor=tk.W, pady=8, padx=10)
        
        self.prev_button.config(state=tk.NORMAL if self.current_question_index > 0 else tk.DISABLED)
        
        total_questions = len(self.current_quiz["questions"])
        is_last = self.current_question_index == total_questions - 1
        self.next_button.config(state=tk.DISABLED if is_last else tk.NORMAL)
        self.submit_button.config(state=tk.NORMAL if is_last else tk.DISABLED)
        
        self.progress_label.config(text=f"Question {self.current_question_index + 1} of {total_questions}")
    
    def save_response(self, question_id: int, option_id: int, is_multiple: bool) -> None:
        if is_multiple:
            if option_id in self.user_responses[question_id]:
                self.user_responses[question_id].remove(option_id)
            else:
                self.user_responses[question_id].append(option_id)
        else:
            self.user_responses[question_id] = [option_id]
    
    def prev_question(self) -> None:
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.display_question()
    
    def next_question(self) -> None:
        if self.current_question_index < len(self.current_quiz["questions"]) - 1:
            self.current_question_index += 1
            self.display_question()
    
    def submit_quiz(self) -> None:
        if not self.current_quiz:
            return
        
        if not messagebox.askyesno("Confirm Submission", "Are you sure you want to submit the quiz?\nYou cannot change your answers after submission."):
            return
        
        try:
            all_responses = []
            for question_id, selected_options in self.user_responses.items():
                for option_id in selected_options:
                    all_responses.append((question_id, option_id))
            
            if all_responses:
                self.db.save_all_responses(self.user["id"], all_responses)
            
            score, total_points = self.db.calculate_score(self.user["id"], self.current_quiz["id"])
            self.db.save_score(self.user["id"], self.current_quiz["id"], score, total_points)
            
            percentage = (score / total_points * 100) if total_points > 0 else 0
            messagebox.showinfo(
                "Quiz Completed!",
                f"Your Results:\n\n"
                f"Score: {score}/{total_points} points\n"
                f"Percentage: {percentage:.1f}%\n\n"
                f"Correct answers: {score}\n"
                f"Total points: {total_points}"
            )
            
            self.load_quizzes()
            self.current_quiz = None
            self.current_question_index = 0
            self.user_responses = {}
            self.quiz_title_label.config(text="Select a quiz to start")
            self.question_label.config(text="")
            for widget in self.options_frame.winfo_children():
                widget.destroy()
            self.progress_label.config(text="")
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.NORMAL)
            self.submit_button.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit quiz: {str(e)}")
    
    def sign_out(self) -> None:
        if messagebox.askyesno("Sign Out", "Are you sure you want to sign out?"):
            self.window.destroy()
            if self.on_logout:
                self.on_logout()
    
    def run(self) -> None:
        self.window.mainloop()
