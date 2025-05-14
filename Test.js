import { io } from "socket.io-client";

const ip = 'localhost';
const socket = io(`https://${ip}:5000`, {
  transports: ["websocket"],
  rejectUnauthorized: false});

const titles = ['Vídeo A'];
const links = ['https://youtube.com/a'];
const thumbs = ['https://img.youtube.com/vi/a/hqdefault.jpg'];
const i = 0;

socket.on('connect', () => {
  console.log('conectado');
  socket.emit('post_recommendations', {
    recommendations: [
      { titulo: titles[i], link: links[i], thumb: thumbs[i] }
    ]
  });
});
socket.on('connect_error', err => console.error('Erro de conexão:', err));
socket.on('disconnect', () => console.log('Desconectado'));

function pause(){
  video = document.querySelector('video')

    if(video.paused){
      video.play()
    }else{
      video.pause()
    }
}

socket.on('emit_pause', () => {
  pause()
})

socket.on("new_recommendations", (data) => {
    console.log(data)
  })

