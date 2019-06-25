<template>
  <div id="recorder">
    <h1>Start recording your conversation!</h1>
    <p>{{ response }}</p>
    <div id="container">
      
      <template v-if="this.isRecording">
        <img class="button" alt="stop button" @click="stopRecord" src="../assets/stop.svg">
      </template>
      
      <template v-else>
        <div v-if="this.showAnalysisButton" @click="$store.commit('toggle')" class="button" id="analyze">
          Analyze results
        </div>
        <img class="button" alt="rec button" @click="startRecord" src="../assets/button.svg">
      </template>
    
    </div>
  </div>
</template>

<script>
import Recorderx, {ENCODE_TYPE} from 'recorderx'


export default {
    name: 'recorder',
    
    data() {
        return { response: '', rc: new Recorderx(), isRecording: false , showAnalysisButton: false} 
    },

    methods: {
      async startRecord() {
        try {
          this.response = "Recording...";
          await this.rc.start()
          this.isRecording = true;
        }
        catch(e) {
          this.response = e
          this.rc.clear();
        }        
      },

      async stopRecord() {
        this.rc.pause()
        this.response = 'Finished recording'
        this.isRecording = false;
        this.showAnalysisButton = false;

        const audiofile = this.rc.getRecord({
          encodeTo: ENCODE_TYPE.WAV
        })
        this.rc.clear();

        let data = new FormData()
        data.append('file', audiofile)
        // push to vuex
        this.$store.commit('change', audiofile)

        this.response = 'sending data'
        try {
          let server_response = await fetch('http://localhost:1337/upload', {
            method: 'POST',
            body: data
          })

          let result = await server_response.text()
          
          if(result == "ERROR"){
            this.response = `Could not process file. 
        Make sure that the file is uncorrupted, in the right format
        or does not contain empty recording`
          }
          else{
            this.response = result
            this.showAnalysisButton = true;

            localStorage.results = this.response
            
          }
        }
        catch(e) {
          this.response = e
        }
      }    
    }
}

</script>

<style>
#recorder {
  font-family:Arial, Helvetica, sans-serif;
}
#recorder > *{
  margin-top: 2vw;
  margin-bottom: 2vw;
}
.button {
  cursor: pointer;
}
.container{
  align-items: center;
}
#analyze{
  background-image: linear-gradient(to bottom right, red, orange);
  width: 180px;
  height: 50px;
  border-radius: 50px;
  margin-right:auto;
  margin-left:auto;
  display:flex;
  justify-content: center;
  align-items: center;
  color: white;
  font-weight: bold;
  font-size: 18.5px;
}
</style>
