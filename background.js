const your_ipv4_ip = '10.113.1.50';
var get_reccomendation = true

setInterval(() => {
    fetch(`http://${your_ipv4_ip}:5000/get_data`)
      .then(res => res.json())
      .then(data => {
        if (data.executar_algo) {
          chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
            const tab = tabs[0];
            if (tab && tab.url.includes("youtube.com/watch?v")) {
              if(data.function == "change_video"){
                change_video(data, tab);
              }
              if(data.function == "next"){
                next(data, tab);
              }
              if(data.function == "pause"){
                pause(data, tab);
              }
            } else {
              console.warn("Nenhuma aba do YouTube ativa encontrada.");
            }
          }
        );
        }
      })
      .catch(err => console.error('Erro ao verificar tarefas:', err));
}, 5000);

function change_video(data, tab){
  chrome.tabs.sendMessage(tab.id, {
    action: "change_video",
    url: data.url
  }, (res) => {
    if (chrome.runtime.lastError) {
      console.error("Erro ao mudar video por url/recomendação:", chrome.runtime.lastError.message);
    } else {
      fetch(`http://${your_ipv4_ip}:5000/changed`);
      set_reccomendation()
    }
  });
}

function next(data, tab){
  chrome.tabs.sendMessage(tab.id, {action: "next"}, (res) => {
    if(chrome.runtime.lastError){
      console.log('erro ao executar proximo video', chrome.runtime.lastError.message)
    }else{
      fetch(`http://${your_ipv4_ip}:5000/changed`)
      set_reccomendation()
    }
  })
}

function pause(data, tab){
  chrome.tabs.sendMessage(tab.id, {action: "pause"}, (res) => {
    if(crhome.runtime.lastError){
      console.log("erro ao tentar pausar ou despausar o video", chrome.runtime.lastError.message)
    }else{
      fetch(`http://${your_ipv4_ip}:5000/changed`)
    }
  })
}

function onload_get_reccomendation(){
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
      const tab = tabs[0]
      if (tab && tab.url.includes('youtube.com/watch?v')){
        chrome.tabs.sendMessage(tab.id, {action: 'collect_recommendations'}, (response) => {
          if (response.status === 'ok' && response.data){
            if (get_reccomendation){
              get_reccomendation = false
              console.log(response.data)
              data_json = {}
              for (let i = 0; i < response.data.length; i++){
                data_json[response.data[i]['titulo']] = {"url": response.data[i]['link'], "thumb": response.data[i]['thumb']}
              }
              fetch(`http://${your_ipv4_ip}:5000/reccomendations`, {method: "POST",
                headers: {
                "Content-Type": "application/json"},
                body: JSON.stringify(data_json)
              })
          }
          }
        })
      }else{
        console.warn('a guia atual não é do youtube')
      }
    })
}

function onload_get_volume(){
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
    const tab = tabs[0]
    if(tab&& tab.url.includes('youtube.com/watch?v')){
      chrome.tabs.sendMessage(tab.id, {action: 'get_volume'}, (response) => {
        if(response.status == 'ok' && response.volume !== undefined){
          fetch(`http://${your_ipv4_ip}:5000/post_volume`, {method: "POST",
            headers: {"Content-Type": "application/json"}, body: JSON.stringify({'volume': response.volume}) } )
        }
      })
    }
  })
}

chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
  if (changeInfo.status == 'complete') {
    if(tab.url.includes('youtube.com/watch?v')){
      get_reccomendation = true
    }
   }
});

function set_reccomendation(){
  setTimeout(() => {
    get_reccomendation = true;
    onload_get_reccomendation();
    onload_get_volume();
  }, 5000)
}

var get_reccomendation_interval =  setInterval(onload_get_reccomendation , 4000)