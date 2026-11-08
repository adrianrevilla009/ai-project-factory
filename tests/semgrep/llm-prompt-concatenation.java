class A {
  void a(ChatClient.ChatClientRequestSpec c, String userText) {
    // ruleid: llm-prompt-string-concatenation
    c.user("Summarize: " + userText);
    // ok: llm-prompt-string-concatenation
    c.user(u -> u.text("Summarize: {t}").param("t", userText));
  }
}
