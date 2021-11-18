import logging

# Configure logging
logger = logging.getLogger(__name__)

class ReportBuilder:
    def __init__(self):
        self.msg = ""
        self.msgs = []

    def addline(self, text, nonewline=False):
        if nonewline == False:
            text = text + "\n"
        if (len(self.msg) + len(text)) > 4000:
            self.finalizemessage()
        self.msg += text

    def finalizemessage(self):
        self.msgs.append(self.msg)
        self.msg = ""

    def addemptyline(self):
        self.addline('\n',nonewline=True)

    def create_report(self):
        self.finalizemessage()
        return self.msgs
