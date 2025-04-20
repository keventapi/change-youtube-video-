console.log("content.js carregado");

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "change_video") {
    console.log("Mensagem recebida:", message);
    window.location.href = message.url;
    sendResponse({ status: "ok" });
  }
  return true;
});

// Ouvir mudanças na URL da aba para reagir quando a página for carregada
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (tab.url && tab.url.includes("youtube.com")) {
    console.log("Página do YouTube detectada:", tab.url);
  }
});