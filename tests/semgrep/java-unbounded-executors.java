class A {
  void a() {
    // ruleid: java-unbounded-executors
    Executors.newCachedThreadPool();
    // ruleid: java-unbounded-executors
    new Thread(() -> {});
    // ok: java-unbounded-executors
    Executors.newVirtualThreadPerTaskExecutor();
  }
}
