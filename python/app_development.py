
import psutil

class LogMemoryUsage:
    """
    Can be used to log the memory use in the terminal
    """
    def __init__(self):

        self.log_memory_usage()

    def log_memory_usage(self):

        memory_usage = self.get_memory_usage()
        self.print_memory_usage(memory_usage)

    def get_memory_usage(self):

        process = psutil.Process()
        mem_info = process.memory_info()
        
        # Resident Set Size (RAM used)
        return mem_info.rss

    def print_memory_usage(self, memory_usage):
        # Display memory usage in terminal
        print(f"Current RAM Usage: {memory_usage / (1024 ** 2):.2f} MB")

        


        