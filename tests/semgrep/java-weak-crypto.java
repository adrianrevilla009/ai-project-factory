class A {
  void a() throws Exception {
    // ruleid: java-weak-crypto-algorithm
    MessageDigest.getInstance("MD5");
    // ruleid: java-weak-crypto-algorithm
    Cipher.getInstance("AES/ECB/PKCS5Padding");
    // ruleid: java-weak-crypto-algorithm
    new java.util.Random();
    // ok: java-weak-crypto-algorithm
    MessageDigest.getInstance("SHA-256");
  }
}
