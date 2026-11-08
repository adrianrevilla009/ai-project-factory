class A {
  void a(InputStream in, ObjectMapper m) throws Exception {
    // ruleid: java-object-input-stream-untrusted
    new ObjectInputStream(in);
    // ruleid: java-object-input-stream-untrusted
    m.enableDefaultTyping();
    // ok: java-object-input-stream-untrusted
    new ByteArrayInputStream(new byte[0]);
  }
}
