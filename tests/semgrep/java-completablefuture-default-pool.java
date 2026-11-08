class A {
  void a() {
    // ruleid: java-completablefuture-default-pool
    CompletableFuture.supplyAsync(() -> 1);
    // ruleid: java-completablefuture-default-pool
    CompletableFuture.runAsync(() -> {});
    // ok: java-completablefuture-default-pool
    CompletableFuture.supplyAsync(() -> 1, executor);
  }
}
