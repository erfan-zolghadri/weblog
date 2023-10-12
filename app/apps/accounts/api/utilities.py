from threading import Thread


class EmailThread(Thread):
    """
    Send email to client in a thread separate from Django thread.
    """

    def __init__(self, message):
        Thread.__init__(self)
        self.message = message

    def run(self):
        self.message.send()
