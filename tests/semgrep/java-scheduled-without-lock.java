class A {
  // ruleid: java-scheduled-without-lock
  @Scheduled(fixedRate = 1000)
  void bad() {}

  // ok: java-scheduled-without-lock
  @SchedulerLock(name = "x")
  @Scheduled(fixedRate = 1000)
  void good() {}
}
