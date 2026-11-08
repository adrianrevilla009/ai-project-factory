class A {
  void a(EntityManager em, JdbcTemplate jdbc, String n) {
    // ruleid: sql-string-concatenation
    em.createQuery("from U where n = '" + n + "'", U.class);
    // ruleid: sql-string-concatenation
    jdbc.query("select * from u where n = '" + n + "'", mapper);
    // ok: sql-string-concatenation
    em.createQuery("from U where n = :n", U.class);
  }
}
