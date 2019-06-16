import socket
import time
import uuid
import threading


def currentName():
    return threading.currentThread().name


def currentPrefix():
    name = currentName()
    return '[{}] '.format(name)


def log(*messages):
    print(currentPrefix(), *messages)


def addJob(queue, handler, *handlerArgs):
    queue.append((handler, *handlerArgs))


def serverHandler(taskQueue, registry, maxThreads, stopFlag):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.bind(("127.0.0.1", 1234))
        sock.listen(0)
        log("starting event loop")
        while True:
            if stopFlag:
                break
            if(len(registry) < maxThreads):
                log("waiting for new connections: ")
                conn, addr = sock.accept()
                addJob(taskQueue, connHandler, conn, addr)
            else:
                log("max threads reached. Next accept when a thread is done.")
                time.sleep(1)
    finally:
        sock.close()


def connHandler(conn, addr):
    log("accepted connection from", addr)
    # add timeout to avoid draining by slow clients
    data = conn.recv(10000)
    # log("received: ", data)

    response = b"Thanks for the request\n" + data
    conn.sendall(response)
    # log("closing connection")
    conn.close()


def runJobs(queue, registry, stopFlag):
    try:
        time.sleep(5)

        while True:
            if stopFlag:
                break
            if(len(queue) > 0):
                handler, *handlerArgs = queue.pop()
                t = threading.Thread(target=handler, args=(
                    *handlerArgs,), daemon=True)
                _id = uuid.uuid4()
                registry[_id] = t
                t.start()
            else:
                # log("nothing to dispatch.")
                if(len(registry) >= threading.active_count() - 2):
                    log("cleaning up.")
                    joinFinishThreads(registry)
                else:
                    # log("sleeping.")
                    time.sleep(0.2)
    finally:
        joinFinishThreads()


def joinFinishThreads(registry):
    finished = []
    for _id, t in registry.items():
        t.join(0.2)
        if(not t.isAlive()):
            log("Thread :", t.ident, " finished.")
            finished.append(_id)
    for _id in finished:
        del registry[_id]


def main():
    try:
        registry = dict()
        taskQueue = []
        maxThreads = 2  # small for testing

        stopRunner = False
        runner = threading.Thread(name="runner thread", target=runJobs, args=(
            taskQueue, registry, stopRunner, ), daemon=True)
        runner.start()

        stopServer = False
        server = threading.Thread(name="network server", target=serverHandler, args=(
            taskQueue, registry, maxThreads, stopServer), daemon=True)
        server.start()
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("keyboard interrupt caught")
    except:
        print("unknown exception caught")
    finally:
        stopRunner = True
        stopServer = True
        print("waiting for context threads to finish")
        runner.join(1)
        server.join(1)


if __name__ == '__main__':
    print('Starting simple server')
    main()
