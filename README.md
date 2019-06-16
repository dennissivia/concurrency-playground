# concurrency-playground

Implement concurrency primitives from scratch

## Simple threads

## Thread pools

![Thread pool](/docs/images/thread-pool.png)

## TODO list

Some more things I want to implement

* [x] Basic threaded networking server
* [x] Ensure a fixed max number of threads
* [x] Implement simple thread pool
* [ ] Check if underlaying datastructures are thread-safe
* [ ] Make tasks cancellable to handle slow clients
* [ ] Implement back pressure
* [ ] Work different promitives
  * [x] Locks
  * [ ] Semaphores
  * [ ] Barriers
  * [ ] Condition objects
* Implement different schedulers
  * [x] FIFO
  * [ ] (Job) priority scheduling
  * [ ] (shortest) remaining time first
