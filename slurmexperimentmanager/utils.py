import os

def check_lock():
    if os.path.isfile("status.done"):
        print("Not running ", __file__, " becuase done lock file exits")
        return False

    if os.path.isfile("status.running"):
        print("Not running ", __file__, " becuase done running file exits")
        return False

    return True

def create_lock(state):
    open(f"status.{state}", 'a').close()

def remove_lock():
    os.remove("status.running")

def start():
    create_lock()

def stop():
    create_lock()

class LockedProcess():
    def __enter__(self):
        if not check_lock():
            exit()
        create_lock("running")

    def __exit__(self, type, value, traceback):
        remove_lock()
        if traceback is None:
            create_lock("done")
        else:
            create_lock("failed")