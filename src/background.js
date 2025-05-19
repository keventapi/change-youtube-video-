import { io } from "socket.io-client"

// TODO: Refatorar usando padrão when_on_youtube(callback) para evitar repetição e isolar lógica de verificação de URL do YouTube

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

function next_video(){
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
    const tab = tabs[0]
    if (tab && tab.url.includes('youtube.com/watch?v')){
      chrome.tabs.sendMessage(tab.id, {action: "next"}, (res) => {
        if(chrome.runtime.lastError){
          console.log('erro ao ir para proximo video indentificador do erro -->', chrome.runtime.lastError)
        }else{
          socket.emit('reset')
        }
      })
    }
  })
}


function pause_video(){
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
    const tab = tabs[0]
    if (tab && tab.url.includes('youtube.com/watch?v')){
      chrome.tabs.sendMessage(tab.id, {action: "pause"}, (res) => {
        if(chrome.runtime.lastError){
          console.log('erro ao pausar o video indentificador do erro -->', chrome.runtime.lastError)
        }else{
          socket.emit('reset')
        }
      })
    }
  })
}

function get_volume(){
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
    const tab = tabs[0]
    if (tab && tab.url.includes('youtube.com/watch?v')){
      chrome.tabs.sendMessage(tab.id, {action: "get_volume"}, (res) => {
        if(chrome.runtime.lastError){
          console.log('erro ao pegar o volume indentificador do erro -->', chrome.runtime.lastError)
        }else{
          if(res.volume){
            socket.emit('recive_volume', {volume: res.volume})
            chrome.storage.local.set({volume: res.volume})
          }else{
            console.log('o volume retornou undefined, o scrapping esta com problema')
          }
        }
      })
    }
  })
}

function change_volume(new_volume){
  chrome.storage.local.set({'volume': new_volume})
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
    const tab = tabs[0]
    if (tab && tab.url.includes('youtube.com/watch?v')){
      chrome.tabs.sendMessage(tab.id, {action: "change_volume", volume: new_volume}, (res) => {
        if(chrome.runtime.lastError){
          console.log('erro ao mudar o volume indentificador do erro -->', chrome.runtime.lastError)
        }
      })
    }
  })
}

// websocket listener
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
  pause_video();
})

socket.on('change_video', (data) => {
  change_video(data.url);
})

socket.on('send_next', (data) => {
  console.log(data)
  next_video();
})

socket.on('get_volume', () => {
  get_volume()
})

socket.on('change_volume', (data) => {
  change_volume(data['volume'])
})


//listener do chrome
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if(message.action == "update_volume"){
    chrome.storage.local.set({volume: message.new_volume})
    sendResponse({status: "volume atualizado com sucesso"})
  }
})