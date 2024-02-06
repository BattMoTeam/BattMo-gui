from api import server
import multiprocessing


if __name__ == '__main__':
    #multiprocessing.set_start_method("spawn")'
    server.run(host='0.0.0.0', port=8000)