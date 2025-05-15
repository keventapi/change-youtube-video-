let recommendations = []
let get_volume = true;

function scroll_page(){
  for(let y = 0; y < 10; y++){
    window.scrollTo(0, y*100)
  }
  get_thumbs();

  setTimeout( () => window.scrollTo(0,0), 1000)
}
scroll_page()

function pause(){
  video = document.querySelector('video')
    if(video.paused){
      video.play()
    }else{
      video.pause()
    }
}

function change_video(url){
  window.location.href = url
}

//temporario
function get_filtred_links(){
  const current_video = window.location.search.split('v=')[1].split('&')[0]
  const element = document.querySelectorAll("a");
  let filtred_link = Array.from(element).filter(link => link.href.includes('watch'))
  filtred_link = filtred_link.filter(link => {
    const link_video = link.href.split('v=')[1].split('&')[0]
    return current_video != link_video;
  })
  return filtred_link;
}


function create_parents(filtred_link){
  let parents = []
  for(let i = 0; i < filtred_link.length; i++){
    parents[i] = filtred_link[i].parentElement;
  }
  return parents;
}


function get_thumbs(filtred_link, parents){
  let thumbs = []
  for(let i = 0; i < filtred_link.length; i++){
        let thumb_element = parents[i].querySelector('img');
        try{
          let thumb = thumb_element.src
          console.log(thumb)
          if(thumb != ''){
            thumbs.push(thumb)
          }
        }catch(erro){
          console.log(`erro ao pegar a thumb, indentificador do erro --> ${erro}`)
    }
  }
  console.log(thumbs)
  return thumbs;
}

function get_titles_and_links(filtred_link, parents){
  let titles = []
  let links = []
  for(let i = 0; i < filtred_link.length; i++){
    try{
      let title_element = parents[i].querySelectorAll('span')[0];
      let title = title_element.title;
      if(title != ''){
        titles.push(title)
        links.push(filtred_link[i].href)
      }
    }
    catch{
      console.log('\n')
    }
  }
  return {titles, links};
}

function data_sorted(){
  let filtred_links = get_filtred_links();
  let parents = create_parents(filtred_links)
  let thumbs = get_thumbs(filtred_links, parents);
  let {titles, links} = get_titles_and_links(filtred_links, parents)
  let listas = [thumbs, links, titles]
  for(let j = 0; j< listas.length; j++){
    for(let i = 0; i < listas.length - 1; i++){
      if(listas[i].length > listas[i+1].length){
        let antigo = listas[i];
        let novo = listas[i+1];
        listas[i] = novo
        listas[i+1] = antigo
      }
    }
  }
  return listas;
}

// ---------------------------


function get_recommendation(){
  const my_promise = new Promise ((resolve) => {

    setTimeout(() => {

      let recommendations = []
      let listas = data_sorted()
      for(let i = 0; i < listas[0].length; i++){
        recommendations[i] = {'titulo': titles[i], 'link': links[i], 'thumb': thumbs[i]}
      }
      resolve(recommendations)
    }, 5000)
  })
  return my_promise
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if(message.action == "emit_recommendations"){
    get_recommendation().then((resolved_recommendations)=> {
      let data_recommendations = resolved_recommendations;
      if(data_recommendations.length > 0){
        socket.emit('post_recommendations', {recommendations: data_recommendations})
        sendResponse({status: "ok"})
      }else{
        sendResponse({status: "void_list"})
      }
    })
  }
  if(message.action == "scroll_page"){

  }
  return true;
})

const ip = "192.168.5.102"
const socket = io(`https://${ip}:5000`, { transports: ["websocket"] });

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
  pause();
})


/*
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {

  if (message.action === "change_video") {
    console.log("Mensagem recebida:", message);
    sendResponse({ status: "ok" });
    window.location.href = message.url;
    return true;
  }
  


  if (message.action === "collect_recommendations") {
      get_recommendation().then((resolved_recommendations)=> {
        recommendations = resolved_recommendations;
        console.log(recommendations);
        sendResponse({ status: "ok", data: recommendations});
      })
      return true;
  }


  if(message.action == "pause"){
    video = document.querySelector('video')
    if(video.paused){
      video.play()
    }else{
      video.pause()
    }
    sendResponse({status: "ok"});
  }


  if(message.action == "next"){
    document.querySelector('.ytp-next-button').click()
    sendResponse({status: "ok"})
    return true;
  }

  if(message.action == "get_volume"){
    volume_element = document.getElementsByClassName('ytp-volume-panel')[0];
    current_volume = volume_element.getAttribute('aria-valuenow');
    console.log(current_volume)
    sendResponse({status: "ok", volume: current_volume})
    return true;
  }
});
*/