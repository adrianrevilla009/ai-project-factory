class A {
  // ruleid: jpa-toone-without-lazy
  @ManyToOne
  Customer c;
  // ruleid: jpa-toone-without-lazy
  @OneToOne(fetch = FetchType.EAGER)
  Profile p;
  // ok: jpa-toone-without-lazy
  @ManyToOne(fetch = FetchType.LAZY)
  Customer ok;
}
