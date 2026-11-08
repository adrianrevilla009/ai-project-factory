class A {
  // ruleid: jpa-enumerated-ordinal
  @Enumerated(EnumType.ORDINAL)
  Status s;
  // ok: jpa-enumerated-ordinal
  @Enumerated(EnumType.STRING)
  Status t;
}
