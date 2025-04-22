const your_ipv4_ip = '192.168.5.102';
var get_reccomendation = true
setInterval(() => {
    fetch(`http://${your_ipv4_ip}:5000/change_video`)
      .then(res => res.json())
      .then(data => {
        if (data.executar_algo) {
          chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
            const tab = tabs[0];
            if (tab && tab.url.includes("youtube.com")) {
              chrome.tabs.sendMessage(tab.id, {
                action: "change_video",
                url: data.url
              }, (res) => {
                if (chrome.runtime.lastError) {
                  console.error("Erro ao enviar mensagem:", chrome.runtime.lastError.message);
                } else {
                  console.log('ok, enviando');
                  fetch(`http://${your_ipv4_ip}:5000/changed`);

                  // Depois de redirecionar, enviar mensagem para pegar as recomendações
                  // Espere o content.js coletar as recomendações antes de enviar
                  setTimeout(() => {
                    chrome.tabs.sendMessage(tab.id, {
                      action: "collect_recommendations"
                    }, (response) => {
                      if (chrome.runtime.lastError) {
                        console.error("Erro ao enviar mensagem:", chrome.runtime.lastError.message);
                      } else {
                        data_json = {}
                        for (let i = 0; i < response.data.length; i++){
                          data_json[`video${i+1}`] = response.data[i]['url']
                        }
                        fetch('http://192.168.5.102:5000/reccomendations', {method: "POST",
                          headers: {
                            "Content-Type": "application/json"
                          },
                          body: JSON.stringify(data_json)
                        })
                        console.log("Recomendações recebidas do content script:", data_json);
                      }
                    });
                  }, 4000); // Espera 4 segundos para garantir que as recomendações foram carregadas
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

function onload_get_reccomendation(){
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
      const tab = tabs[0]
      if (tab && tab.url.includes('youtube.com')){
        chrome.tabs.sendMessage(tab.id, {action: 'collect_recommendations'}, (response) => {
          if (response.status === 'ok' && response.data){
            if (get_reccomendation){
              get_reccomendation = false
              console.log(response.data)
              data_json = {}
              for (let i = 0; i < response.data.length; i++){
                data_json[response.data[i]['titulo']] = {url: response.data[i]['url'], thumb: ''}
                console.log(data_json)
              }
              fetch('http://192.168.5.102:5000/reccomendations', {method: "POST",
                headers: {
                "Content-Type": "application/json"},
                body: JSON.stringify(data_json)
              })
          }
          }
        })
      }else{
        console.warn('nn foi identificada nhm guia do youtube')
      }
      if(!get_reccomendation){
        console.log('isso deve ser mostrado apenas uma vez')
      }
    })
}

chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
  if (changeInfo.status == 'complete') {
    if(tab.url.includes('youtube.com')){
      get_reccomendation = true
    }
   }
});

var get_reccomendation_interval =  setInterval(onload_get_reccomendation , 4000)