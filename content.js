let recommendations = []


function get_recommendation(){
  const my_promise = new Promise ((resolve) => {
    setTimeout(() => {
      const current_video = window.location.search.split('v=')[1].split('&')[0]
      let thumbs = []
      let titles = []
      let links = []
      const element = document.querySelectorAll("a");
      let filtred_link = Array.from(element).filter(link => link.href.includes('watch'))
      filtred_link = filtred_link.filter(link => {
        const link_video = link.href.split('v=')[1].split('&')[0]
        return current_video != link_video;
      })
      let parents = []
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
      let listas = [thumbs, links, titles]
      for(let j = 0; j< listas.length; j++){
      for(let i = 0; i < listas.length - 1; i++){
        if(listas[i].length > listas[i+1].length){
          let antigo = listas[i];
          let novo = listas[i+1];
          listas[i] = novo
          listas[i+1] = antigo
        }
      }}
      for(let i = 0; i < listas[0].length; i++){
        recommendations[i] = {'titulo': titles[i], 'link': links[i], 'thumb': thumbs[i]}
      }
      console.log(recommendations)
      resolve(recommendations)
    }, 5000)
  })
  return my_promise
}


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
