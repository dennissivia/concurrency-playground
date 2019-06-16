# concurrency-playground

Implement concurrency primitives from scratch

## Simple threads

## Thread pools

![Thread pool](/docs/images/thread-pool.png)

## TODO list

Some more things I want to implement

* [x] Basic threaded networking server
  * [x] Ensure a fixed max number of threads
* [x] Thread pools
  * [x] Implement basic thread pool
  * [ ] Detect dead worker
* [ ] Check if underlaying datastructures are thread-safe
* [ ] Make tasks cancellable to handle slow clients
* [ ] Implement back pressure / throttling
* [ ] Work different promitives
  * [x] Locks
  * [ ] Semaphores
  * [ ] Barriers
  * [ ] Cyclic Barriers
  * [ ] Condition objects
  * [ ] IVar / Future
  * [ ] MVar
  * [ ] TVar (STM)
  * [ ] Cancellation
* Implement different schedulers
  * [x] FIFO
  * [ ] (Job) priority scheduling
  * [ ] (shortest) remaining time first
* [ ] High level abstractions
  * [ ] Promise
* [ ] Actors
* [ ] Actor Pool
* [ ] Channel
