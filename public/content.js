// funções suplementares para quando falhar algo e necessitar forçar renderização
function scroll_page(){
  for(let y = 0; y < 10; y++){
    window.scrollTo(0, y*100)
  }
  setTimeout( () => window.scrollTo(0,0), 1000)
}


//controlador do player
function pause_video(){
  let video = document.querySelector('video')
    if(video.paused){
      video.play()
    }else{
      video.pause()
    }
}

function change_video(url){
  window.location.href = url
}

function next(){
  document.querySelector('.ytp-next-button').click()
}





// criar lista de recomendados
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
          if(thumb != ''){
            thumbs.push(thumb)
          }
        }catch(erro){
          console.log(`erro ao pegar a thumb, indentificador do erro --> ${erro}`)
    }
  }
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
    catch (erro){
      console.log('erro ao pegar titulo e link, indentificador do erro -->', erro)
    }
  }
  return {titles, links};
}

function data_sorted(){
  let filtred_links = get_filtred_links();
  let parents = create_parents(filtred_links)
  let thumbs = get_thumbs(filtred_links, parents);
  let {titles, links} = get_titles_and_links(filtred_links, parents)

  // Ordena as listas pelo tamanho para evitar overflow de índice, garantindo que thumbs, titles e links tenham o mesmo tamanho mínimo
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
  return {thumbs, titles, links, listas};
}

function get_recommendation(){
  const my_promise = new Promise ((resolve) => {

    setTimeout(() => {
      let recommendations = []
      let {thumbs, titles, links, listas} = data_sorted()
      for(let i = 0; i < listas[0].length; i++){
        recommendations[i] = {'titulo': titles[i], 'link': links[i], 'thumb': thumbs[i]}
      }
      resolve(recommendations)
    }, 1000)
  })
  return my_promise
}

//controlador de som da extensao
function change_volume(new_volume){
  try{
    const video = document.getElementsByTagName('video')
    if(video.length > 0){
      video[0].volume = new_volume/100
    }else{
      console.log('a tag video não existe no momento que a função change_volume foi chamada')
    }
  }catch (erro){
    console.error('erro na função change_volume, ao tentar mudar o volume do video ou o aria-valuenow, identificado do erro:', erro)
  }
}

function get_volume(){
  const video = document.getElementsByTagName('video')
  if(video.length > 0){
    const current_volume = video[0].volume
    return current_volume*100;
  }
  return undefined
}



let waiting_user_input = true;
chrome.storage.local.get('volume', (data) => {
  waiting_user_input = false;
  if(data.volume !== undefined){
    const tag_video = document.querySelector('video')
    volume_updater = setInterval(() => {tag_video.volume = data.volume/100},50)
  }
})

const observer = new MutationObserver((mutations) => {
  for (const mutation of mutations) {
    for (const node of mutation.addedNodes) {
      if (node.nodeType === 1) {
        const video = node.tagName === 'VIDEO' ? node : node.querySelector?.('video');
        if (video) {
          setTimeout(() => {
            clearInterval(volume_updater)
            waiting_user_input = true;
          }, 500)
        }
      }
    }
  }
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

const video = document.querySelector('video');
video.addEventListener('volumechange', () => {
	if(waiting_user_input){
	    chrome.storage.local.set({'volume': Math.round(video.volume*100)})
      console.log(video.volume*100)
	}
  })


// command listener
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if(message.action == "emit_recommendations"){
    if(message.should_scroll){
      scroll_page()
    }
    get_recommendation().then((resolved_recommendations)=> {
      let data_recommendations = resolved_recommendations;
      if(data_recommendations.length > 0){
        sendResponse({ status: "recommendations emited", recommendations: data_recommendations})
      }else{
        sendResponse({status: "void_list", recommendations: data_recommendations})
      }
    })
    return true
  }

  if(message.action == "change_video"){
    change_video(message.url)
    sendResponse({status: "video trocado com sucesso"})
    return
  }

  if(message.action == "next"){
    next()
    sendResponse({status: "proximo video sendo chamado"})
    return
  }

  if(message.action == "pause"){
    pause_video();
    sendResponse({status: "pausado/despausado com sucesso"});
    return
  }

  if(message.action == "get_volume"){
    let current_volume = get_volume()
    if(current_volume !== undefined){
      sendResponse({status: "volume pego", volume: current_volume})
      return
    }else{
      sendResponse({status: "o volume não pode ser pego pois a tag video não foi encontrado pela função get_volume"})
      return
    }
  }

  if(message.action == "change_volume"){
    change_volume(message.volume)
    sendResponse({status: "volume mudado"})
    return;
  }

  return
})