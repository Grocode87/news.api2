from timeit import default_timer

class Timer():
    """Simple timer to time parts of uploader script
    """
    def __init__(self):
        self.proc_name = ""
        self.start_time = -1
        self.end_time = -1
        self.going = False
        
    def start(self, proc_name):
        """Set timer name and start it

        Args:
            proc_name (String): timer name
        """
        self.proc_name = proc_name
        self.start_time = default_timer()
        self.going = True
        
    def end(self):
        """End timer and print results
        """
        if self.going:
            self.end_time = default_timer()
            self.going = False
            
            total_time = self.end_time - self.start_time
            print("{} took {} seconds to run".format(self.proc_name, round(total_time, 2)))
        else:
            print("TIMER ERROR: Timer must be started before being stopped")
        
