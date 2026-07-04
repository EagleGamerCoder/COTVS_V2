class BotContext:
    def __init__(self, db, log_error, verifyView):
        self.db = db
        self.log_error = log_error
        self.VerifyView = verifyView