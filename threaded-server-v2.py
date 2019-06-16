import socket
import time
import uuid
import threading


def connHandler(conn, addr):
    print("accepted connection from", addr)
    # add timeout to avoid draining by slow clients
    data = conn.recv(10000)
    # print("received: ", data)

    response = b"Thanks for the request\n" + data
    conn.sendall(response)
    # print("closing connection")
    conn.close()


def addJob(queue, handler, *handlerArgs):
    queue.append((handler, *handlerArgs))


def dispatchJobs(queue, registry):
    name = threading.currentThread().name
    prefix = '[{}] '.format(name)
    time.sleep(10)

    while True:
        if(len(queue) > 0):
            id = uuid.uuid4()
            handler, *handlerArgs = queue.pop()
            t = threading.Thread(target=handler, args=(
                *handlerArgs,), daemon=True)
            registry[id] = t
            t.start()
        else:
            # print(prefix, "nothing to dispatch.")
            if(len(registry) >= threading.active_count() - 1):
                print(prefix, "cleaning up.")
                joinFinishThreads(registry)
            else:
                # print(prefix, "sleeping.")
                time.sleep(0.2)


def joinFinishThreads(registry):
    finished = []
    for _id, t in registry.items():
        t.join(0.2)
        if(not t.isAlive()):
            print("Thread :", t.ident, " finished.")
            finished.append(_id)
    for _id in finished:
        del registry[_id]


def cleanup(registry, sock):
    joinFinishThreads(registry)
    sock.close()


def main():
    try:
        registry = dict()
        taskQueue = []
        max_threads = 2  # small for testing
        dispatcher = threading.Thread(name="dispatch thread", target=dispatchJobs, args=(
            taskQueue, registry,), daemon=True)
        dispatcher.start()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.bind(("127.0.0.1", 1234))
        sock.listen(2)
        print("starting event loop")
        while True:
            if(len(registry) < max_threads):
                print("waiting for new connections: ")
                conn, addr = sock.accept()
                addJob(taskQueue, connHandler, conn, addr)
            else:
                print("max threads reached. Next accept when a thread is done.")
                time.sleep(1)
    except KeyboardInterrupt:
        print("keyboard interrupt caught")
    except:
        print("unknown exception caught")
    finally:
        cleanup(registry, sock)


if __name__ == '__main__':
    print('Starting simple server')
    main()
