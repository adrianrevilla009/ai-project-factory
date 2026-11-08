class A {
  void a() {
    // ruleid: dynamodb-endpoint-override-in-main-code
    DynamoDbClient c = DynamoDbClient.builder().endpointOverride(URI.create("http://localhost:8000")).build();
  }
  void b() {
    // ok: dynamodb-endpoint-override-in-main-code
    DynamoDbClient c = DynamoDbClient.builder().region(Region.EU_WEST_1).build();
  }
}
