class A {
  void a(DynamoDbClient client, DynamoDbTable<X> table) {
    // ruleid: dynamodb-scan-forbidden
    client.scan(req);
    // ruleid: dynamodb-scan-forbidden
    table.scan();
    // ok: dynamodb-scan-forbidden
    client.query(req);
  }
}
