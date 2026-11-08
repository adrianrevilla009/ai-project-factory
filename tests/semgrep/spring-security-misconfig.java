class A {
  void a(HttpSecurity http, CorsConfiguration c, CorsRegistration r, JwtParser p, String t) throws Exception {
    // ruleid: spring-csrf-disabled-globally
    http.csrf(x -> x.disable());
    // ruleid: spring-cors-wildcard-with-credentials
    c.addAllowedOrigin("*");
    // ruleid: spring-jwt-none-or-unverified-parse
    JWT.decode(t);
    // ok: spring-csrf-disabled-globally
    http.csrf(Customizer.withDefaults());
    // ok: spring-cors-wildcard-with-credentials
    c.addAllowedOrigin("https://app.example.com");
    // ok: spring-jwt-none-or-unverified-parse
    p.parseSignedClaims(t);
  }
}
