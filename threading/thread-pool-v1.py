
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


def serverHandler(taskQueue, stopFlag):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.bind(("127.0.0.1", 1238))
        sock.listen(0)
        log("starting event loop")
        while True:
            if stopFlag:
                break
            if(capacity()):
                log("waiting for new connections: ")
                conn, addr = sock.accept()
                addJob(taskQueue, connHandler, conn, addr)
            else:
                log("No free capacity. Rejecing connections.")
                time.sleep(1)
    finally:
        sock.close()


# should return false if all tasks are idle and the backlog is growing too big
def capacity():
    return True


def connHandler(conn, addr):
    log("accepted connection from", addr)
    # add timeout to avoid draining by slow clients
    data = conn.recv(10000)

    response = b"Thanks for the request\n" + data
    conn.sendall(response)
    conn.close()
    log("done")

    # dummy result until we have something more useful
    return True


def registerWorker(_id, idleQueue, busyQueue):
    idleQueue.remove(_id)
    busyQueue.append(_id)


def unregisterWorker(_id, idleQueue, busyQueue):
    idleQueue.append(_id)
    busyQueue.remove(_id)


def threadHandler(threadPool, idleQueue, busyQueue, taskQueue, outputQueue, stopFlag, lock):
    try:
        _id = threading.currentThread().ident
        while True:
            if stopFlag:
                break
            else:
                if(len(taskQueue) > 0):
                    if(lock.acquire(1)):
                        # see: "double checked locking"
                        if(len(taskQueue) > 0):
                            registerWorker(_id, idleQueue, busyQueue)
                            task = taskQueue.pop()
                            handler, *args = task

                            lock.release()
                            result = handler(*args)

                            lock.acquire()
                            output = "Got result: " + str(result) + " from worker: " + str(_id)
                            outputQueue.append(output)
                            unregisterWorker(_id, idleQueue, busyQueue)
                            lock.release()
                        # the else and the 2 release() calls are required to first release the lock and then call the handler
                        else:
                            lock.release()
    finally:
        lock.release()


def initPool(threadPool, maxThreads, idleQueue, busyQueue, taskQueue, outputQueue, stopFlag, lock):
    for n in range(maxThreads):
        t = threading.Thread(target=threadHandler, args=(
            threadPool, idleQueue, busyQueue, taskQueue, outputQueue, stopFlag, lock, ), daemon=True)
        t.start()
        _id = t.ident
        threadPool[_id] = t
        idleQueue.append(_id)


def runJobs(threadPool, maxThreads, taskQueue, outputQueue, stopFlag, lock):
    try:
        idleQueue = []
        busyQueue = []
        initPool(threadPool, maxThreads, idleQueue,
                 busyQueue, taskQueue, outputQueue, stopFlag, lock)

        while True:
            if stopFlag:
                joinFinishThreads(threadPool, 1)
                break
            else:
                time.sleep(0.2)
    finally:
        joinFinishThreads(threadPool, None)


def joinFinishThreads(threadPool, joinTimeout=0.2):
    finished = []
    for _id, t in threadPool.items():
        t.join(joinTimeout)
        if(not t.isAlive()):
            log("Thread :", t.ident, " finished.")
            finished.append(_id)
    for _id in finished:
        del threadPool[_id]


def main():
    try:
        threadPool = dict()
        taskQueue = []
        outputQueue = []
        maxThreads = 8  # small for testing

        stopExecutor = False
        executor = threading.Thread(name="executor thread", target=runJobs, args=(
            threadPool, maxThreads, taskQueue, outputQueue, stopExecutor, threading.Lock()), daemon=True)
        executor.start()

        stopServer = False
        server = threading.Thread(name="network server", target=serverHandler, args=(
            taskQueue, stopServer), daemon=True)
        server.start()
        while True:
            if(len(outputQueue) > 0):
                output = outputQueue.pop()
                print("main: ", output)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("keyboard interrupt caught")
    except:
        print("unknown exception caught")
    finally:
        stopExecutor = True
        stopServer = True
        print("waiting for context threads to finish")
        executor.join(1)
        server.join(1)


if __name__ == '__main__':
    print('Starting simple server')
    main()
