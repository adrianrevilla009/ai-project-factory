class A {
  void a() {
    // ruleid: dynamodb-put-without-condition
    var r = PutItemRequest.builder().tableName("t").item(m).build();
  }
  void b() {
    // ok: dynamodb-put-without-condition
    var r = PutItemRequest.builder().tableName("t").item(m).conditionExpression("attribute_not_exists(pk)").build();
  }
}
