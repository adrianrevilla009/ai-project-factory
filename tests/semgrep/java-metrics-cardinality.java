class A {
  void a(Counter.Builder b, String id) {
    // ruleid: java-metric-tag-high-cardinality
    b.tag("userId", id);
    // ok: java-metric-tag-high-cardinality
    b.tag("outcome", "ok");
  }
}
