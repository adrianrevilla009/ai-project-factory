class A {
  boolean a(String signature, String expected) {
    // ruleid: webhook-signature-non-constant-compare
    return signature.equals(expected);
  }
  boolean b(byte[] sig, byte[] expected) {
    // ok: webhook-signature-non-constant-compare
    return MessageDigest.isEqual(sig, expected);
  }
}
