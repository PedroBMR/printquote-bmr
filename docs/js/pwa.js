/**
 * Lógica de PWA do PrintQuote by BMR (versão web):
 *  1. Botão "Instalar app" — captura o beforeinstallprompt e oferece a
 *     instalação num botão próprio no cabeçalho.
 *  2. Aviso de atualização — quando o service worker instala uma versão
 *     nova dos arquivos, mostra um banner "Atualizar" que recarrega.
 *
 * Sem dependências. No iOS (Safari) não há beforeinstallprompt — o usuário
 * instala por "Compartilhar > Adicionar à Tela de Início"; o botão só
 * aparece nos navegadores que suportam o prompt (Android/desktop Chromium).
 */
(function () {
  const installBtn = document.getElementById("installBtn");
  const updateBanner = document.getElementById("updateBanner");
  const updateReloadBtn = document.getElementById("updateReloadBtn");

  // ---------------------------------------------------------------------
  // 1. Botão "Instalar app"
  // ---------------------------------------------------------------------
  let deferredPrompt = null;
  const isStandalone =
    window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;

  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (installBtn && !isStandalone) installBtn.style.display = "inline-flex";
  });

  if (installBtn) {
    installBtn.addEventListener("click", async () => {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      await deferredPrompt.userChoice;
      deferredPrompt = null;
      installBtn.style.display = "none";
    });
  }

  window.addEventListener("appinstalled", () => {
    deferredPrompt = null;
    if (installBtn) installBtn.style.display = "none";
  });

  // ---------------------------------------------------------------------
  // 2. Service worker + aviso de atualização
  // ---------------------------------------------------------------------
  if (!("serviceWorker" in navigator)) return;

  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("sw.js")
      .then((reg) => {
        reg.addEventListener("updatefound", () => {
          const nw = reg.installing;
          if (!nw) return;
          nw.addEventListener("statechange", () => {
            // Só é "atualização" se já havia um SW controlando a página
            // (senão é a primeira instalação, que não merece aviso).
            if (nw.state === "installed" && navigator.serviceWorker.controller) {
              if (updateBanner) updateBanner.classList.add("show");
            }
          });
        });
      })
      .catch((err) => console.warn("Service worker não registrado:", err));
  });

  if (updateReloadBtn) {
    updateReloadBtn.addEventListener("click", () => location.reload());
  }
})();
