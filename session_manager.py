class SessionManager:
    def __init__(self):
        self.sessions = {}

    def get_session(self, user_id):
        if user_id not in self.sessions:
            self.sessions[user_id] = {"last_results": None, "page": 0}
        return self.sessions[user_id]


session_manager = SessionManager()