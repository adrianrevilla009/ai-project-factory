class A {
  void a() throws Exception {
    // ruleid: xml-document-builder-without-xxe-hardening
    DocumentBuilderFactory f = DocumentBuilderFactory.newInstance();
    f.newDocumentBuilder();
  }
  void b() throws Exception {
    // ok: xml-document-builder-without-xxe-hardening
    DocumentBuilderFactory f = DocumentBuilderFactory.newInstance();
    f.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
  }
}
