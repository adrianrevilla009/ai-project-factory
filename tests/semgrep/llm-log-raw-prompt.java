class A {
  void a(String prompt) {
    // ruleid: llm-log-raw-prompt
    log.info("sending {}", prompt);
    // ok: llm-log-raw-prompt
    log.info("sending prompt of {} chars", prompt.length());
  }
}
