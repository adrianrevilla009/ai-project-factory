// ruleid: frontend-token-in-web-storage
localStorage.setItem("access_token", t);
// ruleid: frontend-token-in-web-storage
sessionStorage.setItem("jwt", t);
// ok: frontend-token-in-web-storage
document.title = "x";
