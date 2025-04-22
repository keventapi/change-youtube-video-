console.log("content.js carregado");

let shouldCollectRecommended = false;

// Escutando mensagens do background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "change_video") {
    console.log("Mensagem recebida:", message);
    shouldCollectRecommended = true;

    // Redirecionar a página após a coleta das recomendações
    // Não vamos redirecionar até a coleta estar completa
    sendResponse({ status: "ok" });
    
    // Aqui, você faz o redirecionamento da página após a resposta ser enviada
    window.location.href = message.url;
  }
  return true; // Necessário para permitir a resposta assíncrona
});


chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "collect_recommendations") {
    // Espera um pouco para o DOM carregar os vídeos recomendados
    setTimeout(() => {
      const links = [...document.querySelectorAll("a.yt-lockup-metadata-view-model-wiz__title")];
      const recommended = links.map((link, i) => ({
        url: link.href,
        titulo: link.ariaLabel
      }));

      console.log("Vídeos recomendados:", recommended);

      // Envia os dados de volta como resposta
      sendResponse({ status: "ok", data: recommended });
    }, 2000);

    return true; // sinaliza que o sendResponse vai ser chamado de forma assíncrona
  }

  // o outro if do change_video continua aqui
});
