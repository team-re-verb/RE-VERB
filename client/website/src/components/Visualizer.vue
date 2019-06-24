<template>
  <div>
    <div id="waveform"></div>
    <button @click="waveform.play()">play</button>
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
        waveColor: "red",
        progressColor: "#ba4300",
        plugins: [
          WaveSurfer.cursor.create(),
          WaveSurfer.regions.create()
        ]
      });

    this.waveform.load("record.wav")//this.waveform.loadBlob(localStorage.audiofile);

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
