import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, List, Optional, Callable
from database import Database
from styles import StyleManager

class AdminWindow:
    def __init__(self, db: Database, user: Dict, on_logout: callable = None):
        self.db = db
        self.user = user
        self.on_logout = on_logout
        self.current_quiz_id = None
        self.current_questions = []
        self.is_editing = False
        
        self.window = tk.Tk()
        self.window.title(f"Quiz System - Admin Panel ({user['username']})")
        self.window.geometry("1100x750")
        self.window.configure(bg='#f5f5f5')
        
        self.style_manager = StyleManager(self.window)
        self.create_widgets()
        self.load_quizzes()
    
    def create_widgets(self) -> None:
        header_frame = tk.Frame(self.window, bg='#34495e', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = ttk.Label(header_frame, text="Quiz Administration Panel", style='Title.TLabel')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        demo_button = ttk.Button(button_frame, text="Create Demo Quizzes", 
                                command=self.create_demo_quizzes, style='Info.TButton')
        demo_button.pack(side=tk.LEFT, padx=5)
        
        logout_button = ttk.Button(button_frame, text="Sign Out", 
                                  command=self.sign_out, style='Warning.TButton')
        logout_button.pack(side=tk.LEFT, padx=5)
        
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        left_frame = ttk.LabelFrame(main_frame, text="Quiz List", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.quiz_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                       font=('Arial', 10), selectmode=tk.SINGLE,
                                       bg='white', fg='#2c3e50', selectbackground='#3498db')
        self.quiz_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.quiz_listbox.bind("<<ListboxSelect>>", self.on_quiz_select)
        scrollbar.config(command=self.quiz_listbox.yview)
        
        quiz_buttons = ttk.Frame(left_frame)
        quiz_buttons.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(quiz_buttons, text="New Quiz", command=self.new_quiz, 
                  style='Success.TButton').pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        ttk.Button(quiz_buttons, text="Delete Quiz", command=self.delete_quiz, 
                  style='Danger.TButton').pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        
        help_label = ttk.Label(left_frame, 
                              text="💡 Click on a quiz to edit it",
                              font=('Arial', 8),
                              foreground='#888888')
        help_label.pack(pady=(5, 0))
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        quiz_edit_frame = ttk.LabelFrame(right_frame, text="Quiz Details", padding="15")
        quiz_edit_frame.pack(fill=tk.BOTH, expand=True)
        
        instruction_label = ttk.Label(quiz_edit_frame, 
                                     text="📝 To create a quiz: 1) Click 'New Quiz' → 2) Enter title & description → 3) Click 'Save Quiz' → 4) Add questions",
                                     font=('Arial', 9),
                                     foreground='#666666',
                                     wraplength=500)
        instruction_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        self.title_entry = ttk.Entry(quiz_edit_frame, width=45, font=('Arial', 10))
        self.title_entry.grid(row=1, column=1, pady=8, padx=10, sticky=tk.EW)
        
        ttk.Label(quiz_edit_frame, text="Description:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.NW, pady=8)
        self.description_text = scrolledtext.ScrolledText(quiz_edit_frame, width=45, height=6, 
                                                          font=('Arial', 10), wrap=tk.WORD)
        self.description_text.grid(row=2, column=1, pady=8, padx=10, sticky=tk.EW)
        
        quiz_edit_frame.columnconfigure(1, weight=1)
        
        save_cancel_frame = ttk.Frame(quiz_edit_frame)
        save_cancel_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        ttk.Button(save_cancel_frame, text="Save Quiz", command=self.save_quiz, 
                  style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(save_cancel_frame, text="Cancel", command=self.cancel_edit, 
                  style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        
        questions_frame = ttk.LabelFrame(right_frame, text="Questions", padding="15")
        questions_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        questions_list_frame = ttk.Frame(questions_frame)
        questions_list_frame.pack(fill=tk.BOTH, expand=True)
        
        q_scrollbar = ttk.Scrollbar(questions_list_frame)
        q_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.questions_listbox = tk.Listbox(questions_list_frame, yscrollcommand=q_scrollbar.set, 
                                           height=10, font=('Arial', 9),
                                           bg='white', fg='#2c3e50', selectbackground='#3498db')
        self.questions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.questions_listbox.bind("<<ListboxSelect>>", self.on_question_select)
        q_scrollbar.config(command=self.questions_listbox.yview)
        
        question_help = ttk.Label(questions_frame, 
                                 text="💡 After saving a quiz, click 'Add Question' to add questions with multiple choice answers",
                                 font=('Arial', 9),
                                 foreground='#666666',
                                 wraplength=500)
        question_help.pack(pady=(0, 10))
        
        question_buttons = ttk.Frame(questions_frame)
        question_buttons.pack(fill=tk.X, pady=(0, 0))
        
        ttk.Button(question_buttons, text="Add Question", command=self.add_question, 
                  style='Success.TButton').pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        ttk.Button(question_buttons, text="Edit Question", command=self.edit_question, 
                  style='Primary.TButton').pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        ttk.Button(question_buttons, text="Delete", command=self.delete_question, 
                  style='Danger.TButton').pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
    
    def load_quizzes(self) -> None:
        self.quiz_listbox.delete(0, tk.END)
        quizzes = self.db.get_all_quizzes()
        for quiz in quizzes:
            self.quiz_listbox.insert(tk.END, f"{quiz['id']}: {quiz['title']}")
    
    def on_quiz_select(self, event: tk.Event) -> None:
        selection = self.quiz_listbox.curselection()
        if not selection:
            return
        
        selected_text = self.quiz_listbox.get(selection[0])
        quiz_id = int(selected_text.split(":")[0])
        
        quiz = self.db.get_quiz_with_questions(quiz_id)
        if quiz:
            self.current_quiz_id = quiz_id
            self.is_editing = True
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, quiz["title"])
            self.description_text.delete(1.0, tk.END)
            self.description_text.insert(1.0, quiz.get("description", ""))
            self.load_questions(quiz["questions"])
    
    def load_questions(self, questions: List[Dict]) -> None:
        self.current_questions = questions
        self.questions_listbox.delete(0, tk.END)
        for i, q in enumerate(questions):
            q_type = "SC" if q['question_type'] == 'single_choice' else "MC"
            preview = q['question_text'][:60] + "..." if len(q['question_text']) > 60 else q['question_text']
            self.questions_listbox.insert(tk.END, f"Q{i+1} [{q_type}] ({q['points']}pts): {preview}")
    
    def new_quiz(self) -> None:
        self.current_quiz_id = None
        self.is_editing = False
        self.title_entry.delete(0, tk.END)
        self.description_text.delete(1.0, tk.END)
        self.questions_listbox.delete(0, tk.END)
        self.current_questions = []
        self.quiz_listbox.selection_clear(0, tk.END)
    
    def cancel_edit(self) -> None:
        self.new_quiz()
    
    def save_quiz(self) -> None:
        title = self.title_entry.get().strip()
        description = self.description_text.get(1.0, tk.END).strip()
        
        if not title:
            messagebox.showerror("Error", "Quiz title is required")
            return
        
        try:
            if self.current_quiz_id and self.is_editing:
                self.db.update_quiz(self.current_quiz_id, title, description)
                messagebox.showinfo("Success", "Quiz updated successfully!")
            else:
                quiz_id = self.db.create_quiz(title, description, self.user["id"])
                self.current_quiz_id = quiz_id
                self.is_editing = True
                messagebox.showinfo("Success", "Quiz created successfully!")
            
            self.load_quizzes()
            if self.current_quiz_id:
                quiz = self.db.get_quiz_with_questions(self.current_quiz_id)
                if quiz:
                    self.load_questions(quiz["questions"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save quiz: {str(e)}")
    
    def delete_quiz(self) -> None:
        selection = self.quiz_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a quiz to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this quiz?\nAll questions and responses will be deleted."):
            return
        
        selected_text = self.quiz_listbox.get(selection[0])
        quiz_id = int(selected_text.split(":")[0])
        
        try:
            self.db.delete_quiz(quiz_id)
            messagebox.showinfo("Success", "Quiz deleted successfully!")
            self.load_quizzes()
            self.new_quiz()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete quiz: {str(e)}")
    
    def create_demo_quizzes(self) -> None:
        if not messagebox.askyesno("Create Demo Quizzes", 
                                   "This will create demo quizzes with sample questions.\n"
                                   "Only missing demo quizzes will be created.\n\nProceed?"):
            return
        
        try:
            created_count = self.db.create_demo_quizzes(self.user["id"])
            if created_count > 0:
                messagebox.showinfo("Success", f"Created {created_count} demo quiz(es) successfully!")
            else:
                messagebox.showinfo("Info", "All demo quizzes already exist.")
            self.load_quizzes()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create demo quizzes: {str(e)}")
    
    def add_question(self) -> None:
        if not self.current_quiz_id:
            messagebox.showwarning("Warning", "Please create or select a quiz first")
            return
        
        QuestionDialog(self.window, self.db, self.current_quiz_id, None, self.on_question_saved)
    
    def edit_question(self) -> None:
        selection = self.questions_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a question to edit")
            return
        
        question = self.current_questions[selection[0]]
        QuestionDialog(self.window, self.db, self.current_quiz_id, question, self.on_question_saved)
    
    def delete_question(self) -> None:
        selection = self.questions_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a question to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this question?"):
            return
        
        question = self.current_questions[selection[0]]
        try:
            self.db.delete_question(question["id"])
            messagebox.showinfo("Success", "Question deleted successfully!")
            quiz = self.db.get_quiz_with_questions(self.current_quiz_id)
            if quiz:
                self.load_questions(quiz["questions"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete question: {str(e)}")
    
    def on_question_saved(self) -> None:
        if self.current_quiz_id:
            quiz = self.db.get_quiz_with_questions(self.current_quiz_id)
            if quiz:
                self.load_questions(quiz["questions"])
    
    def on_question_select(self, event: tk.Event) -> None:
        pass
    
    def sign_out(self) -> None:
        if messagebox.askyesno("Sign Out", "Are you sure you want to sign out?"):
            self.window.destroy()
            if self.on_logout:
                self.on_logout()
    
    def run(self) -> None:
        self.window.mainloop()

class QuestionDialog:
    def __init__(self, parent: tk.Tk, db: Database, quiz_id: int, question: Optional[Dict], callback: Callable):
        self.db = db
        self.quiz_id = quiz_id
        self.question = question
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Question" if question else "Add Question")
        self.dialog.geometry("650x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg='#f5f5f5')
        
        self.create_widgets()
        
        if question:
            self.dialog.after_idle(self.load_question_data)
    
    def create_widgets(self) -> None:
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Question Text:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.question_text = scrolledtext.ScrolledText(main_frame, width=70, height=5, font=('Arial', 10), wrap=tk.WORD)
        self.question_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        type_frame = ttk.Frame(main_frame)
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(type_frame, text="Type:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 15))
        self.question_type = tk.StringVar(value="single_choice")
        ttk.Radiobutton(type_frame, text="Single Choice", variable=self.question_type, 
                       value="single_choice").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="Multiple Choice", variable=self.question_type, 
                       value="multiple_choice").pack(side=tk.LEFT, padx=10)
        
        points_frame = ttk.Frame(main_frame)
        points_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(points_frame, text="Points:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 15))
        self.points_var = tk.IntVar(value=1)
        ttk.Spinbox(points_frame, from_=1, to=10, textvariable=self.points_var, 
                   width=10, font=('Arial', 10)).pack(side=tk.LEFT)
        
        ttk.Label(main_frame, text="Answer Options:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.BOTH, expand=True)
        
        options_list_frame = ttk.Frame(options_frame)
        options_list_frame.pack(fill=tk.BOTH, expand=True)
        
        opt_scrollbar = ttk.Scrollbar(options_list_frame)
        opt_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.options_listbox = tk.Listbox(options_list_frame, yscrollcommand=opt_scrollbar.set, 
                                         height=8, font=('Arial', 9),
                                         bg='white', fg='#2c3e50', selectbackground='#3498db')
        self.options_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        opt_scrollbar.config(command=self.options_listbox.yview)
        
        self.options_data = []
        
        opt_buttons = ttk.Frame(options_frame)
        opt_buttons.pack(fill=tk.X, pady=(10, 0))
        
        style_mgr = StyleManager(self.dialog)
        ttk.Button(opt_buttons, text="Add Option", command=self.add_option, 
                  style='Success.TButton').pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        ttk.Button(opt_buttons, text="Edit Option", command=self.edit_option, 
                  style='Primary.TButton').pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        ttk.Button(opt_buttons, text="Delete", command=self.delete_option, 
                  style='Danger.TButton').pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(button_frame, text="Save Question", command=self.save_question, 
                  style='Success.TButton').pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy, 
                  style='Danger.TButton').pack(side=tk.RIGHT, padx=5)
    
    def load_question_data(self) -> None:
        if not self.question:
            return
        
        self.question_text.delete(1.0, tk.END)
        question_text = self.question.get("question_text", "")
        if question_text:
            self.question_text.insert(1.0, question_text)
        
        question_type = self.question.get("question_type", "single_choice")
        self.question_type.set(question_type)
        
        points = self.question.get("points", 1)
        self.points_var.set(points)
        
        self.options_data = []
        options = self.question.get("options", [])
        for opt in options:
            self.options_data.append({
                "id": opt.get("id"),
                "text": opt.get("option_text", ""),
                "is_correct": bool(opt.get("is_correct", False))
            })
        
        self.refresh_options_list()
    
    def refresh_options_list(self) -> None:
        self.options_listbox.delete(0, tk.END)
        for opt in self.options_data:
            marker = "[X]" if opt["is_correct"] else "[ ]"
            preview = opt['text'][:50] + "..." if len(opt['text']) > 50 else opt['text']
            self.options_listbox.insert(tk.END, f"[{marker}] {preview}")
    
    def add_option(self) -> None:
        OptionDialog(self.dialog, None, self.on_option_saved)
    
    def edit_option(self) -> None:
        selection = self.options_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an option to edit", parent=self.dialog)
            return
        
        option = self.options_data[selection[0]]
        OptionDialog(self.dialog, option, self.on_option_saved)
    
    def delete_option(self) -> None:
        selection = self.options_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an option to delete", parent=self.dialog)
            return
        
        del self.options_data[selection[0]]
        self.refresh_options_list()
    
    def on_option_saved(self, option_data: Dict) -> None:
        if "id" in option_data:
            for i, opt in enumerate(self.options_data):
                if opt.get("id") == option_data["id"]:
                    self.options_data[i] = option_data
                    break
        else:
            self.options_data.append(option_data)
        self.refresh_options_list()
    
    def save_question(self) -> None:
        question_text = self.question_text.get(1.0, tk.END).strip()
        if not question_text:
            messagebox.showerror("Error", "Question text is required", parent=self.dialog)
            return
        
        if len(self.options_data) < 2:
            messagebox.showerror("Error", "At least 2 options are required", parent=self.dialog)
            return
        
        correct_count = sum(1 for opt in self.options_data if opt["is_correct"])
        if correct_count == 0:
            messagebox.showerror("Error", "At least one correct option is required", parent=self.dialog)
            return
        
        q_type = self.question_type.get()
        if q_type == "single_choice" and correct_count > 1:
            messagebox.showerror("Error", "Single choice questions can have only one correct answer", parent=self.dialog)
            return
        
        try:
            question_id = None
            if self.question:
                question_id = self.question["id"]
            
            self.db.save_question_with_options(
                self.quiz_id, question_id, question_text, 
                q_type, self.points_var.get(), self.options_data
            )
            messagebox.showinfo("Success", "Question saved successfully!", parent=self.dialog)
            self.dialog.destroy()
            self.callback()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save question: {str(e)}", parent=self.dialog)

class OptionDialog:
    def __init__(self, parent: tk.Tk, option: Optional[Dict], callback: Callable):
        self.option = option
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Option" if option else "Add Option")
        self.dialog.geometry("450x220")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg='#f5f5f5')
        
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Option Text:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.option_text = scrolledtext.ScrolledText(main_frame, width=50, height=4, 
                                                     font=('Arial', 10), wrap=tk.WORD)
        self.option_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        is_correct_value = option.get("is_correct", False) if option else False
        self.is_correct = tk.BooleanVar(value=is_correct_value)
        ttk.Checkbutton(main_frame, text="Correct Answer", variable=self.is_correct).pack(anchor=tk.W, pady=(0, 15))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        style_mgr = StyleManager(self.dialog)
        ttk.Button(button_frame, text="Save", command=self.save, 
                  style='Success.TButton').pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy, 
                  style='Danger.TButton').pack(side=tk.RIGHT, padx=5)
        
        if option:
            option_text_value = option.get("text", "")
            if option_text_value:
                self.option_text.insert(1.0, option_text_value)
    
    def save(self) -> None:
        text = self.option_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showerror("Error", "Option text is required", parent=self.dialog)
            return
        
        option_data = {
            "text": text,
            "is_correct": self.is_correct.get()
        }
        
        if self.option and "id" in self.option:
            option_data["id"] = self.option["id"]
        
        self.dialog.destroy()
        self.callback(option_data)
