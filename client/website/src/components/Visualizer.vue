<template>
  <div id="container">
    <div id="waveform"></div>
    <div class="button" @click="waveform.play()"><img src="../assets/play.svg" alt="play"></div>
  </div>
</template>


<script>
export default {
  name: "visualizer",

  mounted(){
    /*let ws = document.createElement('script')
    ws.setAttribute('src', 'https://unpkg.com/wavesurfer.js')
    document.head.appendChild(ws)*/

    this.waveform = WaveSurfer.create({
        container: "#waveform",
        waveColor: "black",
        progressColor: "dark grey",
        plugins: [
          WaveSurfer.cursor.create(),
          WaveSurfer.regions.create()
        ]
      });

    this.waveform.loadBlob(this.$store.getters.audiofile)//this.waveform.loadBlob(localStorage.audiofile);

    let timeStamps = JSON.parse(localStorage.results)
    
    Object.values(timeStamps).forEach((speaker)=>{
      let speakerColor = randomColor(100)
      
      speaker.forEach(utterance => {
        this.waveform.addRegion({
          start: utterance[0]/1000,
          end: utterance[1]/1000,
          drag: false,
          resize: false,
          color: speakerColor
        })
      });
    })

    function randomColor(brightness){
      function randomChannel(brightness){
        var r = 255-brightness;
        var n = 0|((Math.random() * r) + brightness);
        var s = n.toString(16);
        return (s.length==1) ? '0'+s : s;
      }
    return '#' + '80' + randomChannel(brightness) + randomChannel(brightness) + randomChannel(brightness);
    }
  }
};
</script>

<style scoped>
#container > div {
  margin-top: 10px;
}
.button {
  background-image: linear-gradient(to bottom right, red, orange);
  margin-left:auto;
  margin-right:auto;
  border-radius:50px;
  height: 60px;
  width: 60px;
  display:flex;
  justify-content: center;
  align-items: center;
  
}
.button > * {
position: relative;
padding-left: 4px;
height: 40px;
width: 40px;
}
</style>