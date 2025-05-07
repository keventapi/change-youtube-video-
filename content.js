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

function get_recommendation(){
  setTimeout(() => {
    const current_video = window.location.search.split('v=')[1].split('&')[0]
    let recommendetions = []
    let thumbs = []
    let titles = []
    let links = []
    const element = document.querySelectorAll("a");
    let filtred_link = Array.from(element).filter(link => link.href.includes('watch'))
    filtred_link = filtred_link.filter(link => {
      const link_video = link.href.split('v=')[1].split('&')[0]
      return current_video != link_video;
    })
    parents = []
    for(let i = 0; i < filtred_link.length; i++){
      if(i > 1){ //pula os dois primeiros a força pois o resultado pego nn é o esperado
        parents[i] = filtred_link[i].parentElement;
        if((i)%2 === 0 || i === 0){
          let thumb_element = parents[i].querySelectorAll('img')[0];
          try{
            let thumb = thumb_element.src
            if(thumb != ''){
              thumbs.push(thumb)
            }
          }catch{
            console.log('\n')
          }
        }else{
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
      }
    }
    listas = [thumbs, links, titles]
    for(let j = 0; j< listas.length; j++){
    for(let i = 0; i < listas.length - 1; i++){
      if(listas[i].length > listas[i+1].length){
        let antigo = listas[i];
        let novo = listas[i+1];
        listas[i] = novo
        listas[i+1] = antigo
      }
    }}
    console.log(listas)
    for(let i = 0; i < listas[0].length; i++){
      recommendetions[i] = {'titulo': titles[i], 'link': links[i], 'thumb': thumbs[i]}
    }
    return recommendetions;
  }, 10000)
}


chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "collect_recommendations") {
      recommendetions = get_recommendation()
      sendResponse({ status: "ok", data: recommendetions });
      return true;
  }


  if(message.action == "pause"){
    video = document.querySelector('video')
    if(video.paused){
      video.play()
    }else{
      video.pause()
    }
    sendResponse({action: "ok"});
  }


  if(message.action == "next"){
    document.querySelector('.ytp-next-button').click()
    sendResponse({status: "ok"})
    return true;
  }
  return true;
});
