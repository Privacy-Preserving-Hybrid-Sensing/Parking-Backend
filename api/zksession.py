'''
The session implementation is not safe since it will have IDOR vulnerability to the user_id as unique value.
For the sake of simplicity in defining this MVP, this is a known issue and left intentionally like this.
Further improvement might be needed in the next implementation by the one continuing this research.
Improvements available:
    - better search algorithm in ZKSessionManager
    - resolve IDOR vulnerability
'''
class ZKSessionManager():
    sessions = set()

    @classmethod
    def get_all_sessions(self):
        return self.sessions

    @classmethod
    def get_session(self, user_id):
        session = None
        for s in self.sessions:
            if s.user_id == user_id:
                session = s
                break
        return session

    @classmethod
    def remove_session(self, user_id):
        self.sessions.pop(self.get_session(user_id))
        return
    
    @classmethod
    def reset_session(self, user_id):
        s = self.get_session(user_id)
        s.eligible_to_claim_credit = False
        s.credential_verified = False
        s.q_verified = False
        s.credit_claimed = False
        return

    @classmethod
    def add_session(self, user_id):
        exists = self.get_session(user_id)
        if exists:
            self.remove_session(user_id)
        self.sessions.add(ZKSession(user_id))
        return

class ZKSession:
    def __init__(self, user_uuid):
        self.user_id = user_uuid
        self.eligible_to_claim_credit = False
        self.credential_verified = False
        self.q_verified = False
        self.credit_claimed = False