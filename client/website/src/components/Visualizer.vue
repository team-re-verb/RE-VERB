<template>
  <div id="waveform"></div>
</template>


<script>
import WaveSurfer from 'wavesurfer.js'

export default {
  name: "visualizer",
  mounted(){
    this.waveform = WaveSurfer.create({
        container: "#waveform",
        waveColor: "violet",
        progressColor: "purple",
      });
    this.waveform.load("record.wav")//this.waveform.loadBlob(localStorage.audiofile);

    this.waveform.on('ready', function () {
    this.waveform.play();
    });
  }
};
</script>