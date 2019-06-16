import socket
import time
import threading


def connHandler(conn, addr):
    print("accepted connection from", addr)
    print("conn is: ", conn)

    data = conn.recv(10000)
    print("received: ", data)
    print("sleeping now")
    time.sleep(1)
    response = str.encode("Thanks for the request\n") + data

    print("sending response")
    conn.sendall(response)
    print("closing connection")
    conn.close()


def poolMonitor(pool):
    while True:
        print("thread pool monitor is running. Threads in pool: ", len(pool))
        for t in pool:
            t.join(0.2)
            if(not t.isAlive()):
                print("Thread :", t.ident, " finished.")
                pool.remove(t)
                print(pool)
        time.sleep(2)


def main():
    try:
        pool = list()
        max_threads = 5
        monitor = threading.Thread(
            name="pool monitor", target=poolMonitor, args=(pool, ), daemon=True)
        monitor.start()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 1231))
        sock.listen(10)
        print("starting event loop")
        while True:
            if(len(pool) < max_threads):
                print("waiting for new connections: ")
                conn, addr = sock.accept()
                t = threading.Thread(target=connHandler,
                                     args=(conn, addr,), daemon=True)
                t.start()
                id = t.ident
                # we should -lock- to avoid race conditions :shrug:
                pool.append(t)
            else:
                print("max pool size reached. Next accept when a thread is done.")
                time.sleep(1)
    finally:
        monitor.join()
        for t in pool:
            t.join(0.1)
        sock.close()


if __name__ == '__main__':
    print('Starting simple server')
    main()
