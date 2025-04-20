const your_ipv4_ip = '192.168.5.102';

setInterval(() => {
    fetch(`http://${your_ipv4_ip}:5000/change_video`)
      .then(res => res.json())
      .then(data => {
        if (data.executar_algo) {
          chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
            const tab = tabs[0];
            if (tab && tab.url.includes("youtube.com")) {
              chrome.tabs.sendMessage(tab.id, {
                action: 'change_video',
                url: data.url
              }, (res) => {
                if (chrome.runtime.lastError) {
                  console.error("Erro ao enviar mensagem:", chrome.runtime.lastError.message);
                } else {
                  console.log('ok, enviando');
                  fetch(`http://${your_ipv4_ip}/changed`);
                }
              });
            } else {
              console.warn("Nenhuma aba do YouTube ativa encontrada.");
            }
          });
        }
      })
      .catch(err => console.error('Erro ao verificar tarefas:', err));
}, 5000);
