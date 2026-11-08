import java.math.BigDecimal;
class A {
  // ruleid: java-money-as-double
  double totalPrice;
  // ok: java-money-as-double
  BigDecimal okPrice;
  void a(double d, String s, Optional<String> o, java.util.Map<String, String> m) {
    // ruleid: java-bigdecimal-double-ctor
    new BigDecimal(0.1);
    // ruleid: java-bigdecimal-double-ctor
    new BigDecimal(d);
    // ok: java-bigdecimal-double-ctor
    new BigDecimal("0.1");
    // ruleid: java-legacy-date-api
    new SimpleDateFormat("yyyy");
    // ok: java-legacy-date-api
    DateTimeFormatter.ofPattern("yyyy");
    // ok: java-catch-throwable-or-swallow
    try { run(); } catch (IOException e) { log(e); }
    // ruleid: java-default-charset-string
    s.getBytes();
    // ok: java-default-charset-string
    s.getBytes(StandardCharsets.UTF_8);
    // ruleid: java-catch-throwable-or-swallow
    try {
      run();
    } catch (Throwable t) {
      log(t);
    }
    // ruleid: java-optional-get
    o.get();
    // ok: java-optional-get
    m.get("k");
    // ok: java-optional-get
    o.orElseThrow();
  }
}
