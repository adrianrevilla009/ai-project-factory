class A {
  // ruleid: spring-autowired-field-injection
  @Autowired
  Service s;
  // ok: spring-autowired-field-injection
  final Service t;
  A(Service t) { this.t = t; }
}
