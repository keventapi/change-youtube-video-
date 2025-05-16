import { io } from "socket.io-client"

let MAX_ATTEMPTS = {};

function attempt_emit_recommendations(tabId, scroll=false){
  MAX_ATTEMPTS[tabId] += 1;
  chrome.tabs.sendMessage(tabId, {
        action: "emit_recommendations",
        should_scroll: scroll
      }, (res) => {
        if (chrome.runtime.lastError) {
          console.error("Erro ao enviar recomendações para o servidor:", chrome.runtime.lastError.message);
        }else {
          if(res.status == 'void_list'){
            if(MAX_ATTEMPTS[tabId] <= 3){
              setTimeout(() => {
                if(MAX_ATTEMPTS[tabId] == 2){
                  attempt_emit_recommendations(tabId, true)
                }else{
                  attempt_emit_recommendations(tabId)
                }
              }, 1000)
            }else{
              MAX_ATTEMPTS[tabId] = 0;
            }
         }else{
          socket.emit('post_recommendations', {recommendations: res.recommendations})
        }
      }
    }
  )
}


chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
  if (changeInfo.status === 'complete') {
    MAX_ATTEMPTS[tabId] = 0;
    if (tab.url.includes('youtube.com/watch?v')) {
      attempt_emit_recommendations(tabId);
    }
  }
});

function change_video(video_url){
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
    const tab = tabs[0]
    if (tab && tab.url.includes('youtube.com/watch?v')){
      chrome.tabs.sendMessage(tab.id, {action: "change_video", url: video_url})
    }
  })
}

function nex_video(){
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
    const tab = tabs[0]
    if (tab && tab.url.includes('youtube.com/watch?v')){
      chrome.tabs.sendMessage(tab.id, {action: "change_video", url: video_url}, (res) => {
        if(chrome.runtime.lastError){
          console.log('erro ao ir para proximo video indentificador do erro -->', chrome.runtime.lastError)
        }else{
          socket.emit('reset')
        }
      })
    }
  })
}

const ip = "192.168.5.102"
const socket = io(`http://${ip}:5000`, { transports: ["websocket"] });

socket.on('connect', () => {
  console.log('Conectado ao WebSocket');
});

socket.on('connect_error', (err) => {
  console.error('Erro de conexão:', err);
});

socket.on('disconnect', () => {
  console.log('Desconectado do WebSocket');
});

socket.on('emit_pause', () =>{
  console.log('evento de pausa foi escutado');
})

socket.on('change_video', (data) => {
  change_video(data.url);
})

socket.on('next', (data) => {
  nex_video();
})

/*const your_ipv4_ip = '192.168.5.102';
var should_get_recommendations = true;
var get_volume = true;
importScripts('min/socket.io.min.js')
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
      fetch(`http://${your_ipv4_ip}:5000/reset_data`);
      collect_recommendations()
    }
  });
}

function next(data, tab){
  chrome.tabs.sendMessage(tab.id, {action: "next"}, (res) => {
    if(chrome.runtime.lastError){
      console.log('erro ao executar proximo video', chrome.runtime.lastError.message)
    }else{
      fetch(`http://${your_ipv4_ip}:5000/reset_data`)
      collect_recommendations()
    }
  })
}

function pause(data, tab){
  chrome.tabs.sendMessage(tab.id, {action: "pause"}, (res) => {
    if(chrome.runtime.lastError){
      console.log("erro ao tentar pausar ou despausar o video", chrome.runtime.lastError.message)
    }else{
      fetch(`http://${your_ipv4_ip}:5000/reset_data`).then((response) => response.json()).then((data) => {
        console.log(data);
      })
    }
  })
}

function onload_should_get_recommendations(){
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
      const tab = tabs[0]
      if (tab && tab.url.includes('youtube.com/watch?v')){
        chrome.tabs.sendMessage(tab.id, {action: 'collect_recommendations'}, (response) => {
          if (response.status === 'ok' && response.data){

            data_json = {}
            for (let i = 0; i < response.data.length; i++){
              data_json[response.data[i]['titulo']] = {"url": response.data[i]['link'], "thumb": response.data[i]['thumb']}
            }

            fetch(`http://${your_ipv4_ip}:5000/get_data`).then((res) => res.json()).then((data) => {
              if (should_get_recommendations 
                || Object.keys(data.recommendations).length === 0 
                || JSON.stringify(data_json) != JSON.stringify(data.recommendations)){

                  should_get_recommendations = false
                  console.log(response.data)
                  
                  fetch(`http://${your_ipv4_ip}:5000/post_recommendations`, {method: "POST",
                    headers: {
                    "Content-Type": "application/json"},
                    body: JSON.stringify(data_json)

                })
            }

            })
            onload_get_volume();
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
          fetch(`http://${your_ipv4_ip}:5000/post_volume`, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({'volume': response.volume}) } )
          get_volume = false;
          }
      })
    }
  })
}

chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
  if (changeInfo.status == 'complete') {
    if(tab.url.includes('youtube.com/watch?v')){
      should_get_recommendations = true
    }
   }
});

function collect_recommendations(){
  setTimeout(() => {
    should_get_recommendations = true;
    get_volume = true;
    onload_should_get_recommendations();
  }, 5000)
}

var should_get_recommendations_interval =  setInterval(onload_should_get_recommendations , 4000)*/