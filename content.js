let shouldCollectRecommended = false;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "change_video") {
    console.log("Mensagem recebida:", message);
    shouldCollectRecommended = true;
    sendResponse({ status: "ok" });
    window.location.href = message.url;
  }
  return true;
});


chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "collect_recommendations") {
    setTimeout(() => {
      const links = [...document.querySelectorAll("a.yt-lockup-metadata-view-model-wiz__title")];
      const recommended = links.map((link, i) => ({
        url: link.href,
        titulo: link.ariaLabel
      }));
      console.log("Vídeos recomendados:", recommended);
      sendResponse({ status: "ok", data: recommended });
    }, 2000);

    return true;
  }
});
