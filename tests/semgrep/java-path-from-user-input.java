class A {
  void a(HttpServletRequest req, File base, MultipartFile f) {
    // ruleid: java-path-traversal-resolve-request-param
    new java.io.File(base, req.getParameter("n"));
    // ruleid: java-path-traversal-resolve-request-param
    f.getOriginalFilename();
    // ok: java-path-traversal-resolve-request-param
    base.toPath().resolve("fixed.txt");
  }
}
