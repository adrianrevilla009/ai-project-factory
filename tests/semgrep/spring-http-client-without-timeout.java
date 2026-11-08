class A {
  void a() {
    // ruleid: spring-http-client-without-timeout
    new RestTemplate();
    // ruleid: spring-http-client-without-timeout
    java.net.http.HttpClient.newHttpClient();
    // ok: spring-http-client-without-timeout
    new RestTemplateBuilder();
  }
}
