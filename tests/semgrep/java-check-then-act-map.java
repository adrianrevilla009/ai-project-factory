import java.util.Map;
class A {
  void a(Map<String, String> m, String k) {
    // ruleid: java-check-then-act-map
    if (!m.containsKey(k)) {
      m.put(k, "v");
    }
  }
  void b(Map<String, String> m, String k) {
    // ok: java-check-then-act-map
    m.computeIfAbsent(k, x -> "v");
  }
}
