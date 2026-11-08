class A {
  void a(Exception e, String x) {
    // ruleid: java-print-stack-trace
    e.printStackTrace();
    // ok: java-print-stack-trace
    log.error("x", e);
    // ok: java-system-out
    log.info("x");
    // ruleid: java-system-out
    System.out.println("x");
    // ruleid: java-log-string-concat
    log.info("id " + x);
    // ok: java-log-string-concat
    log.info("id {}", x);
  }
}
