from database import Database
from auth_window import AuthWindow
from admin_window import AdminWindow
from user_window import UserWindow

def main():
    db = Database("quiz.db")
    
    def show_login():
        auth_window = AuthWindow(db, on_auth_success)
        auth_window.run()
    
    def on_auth_success(user):
        if user["role"] == "admin":
            admin_window = AdminWindow(db, user, on_logout=show_login)
            admin_window.run()
        else:
            user_window = UserWindow(db, user, on_logout=show_login)
            user_window.run()
    
    show_login()

if __name__ == "__main__":
    main()

