<template>
  <div>
    <h1>Start recording your conversation!</h1>
    <p>{{ response }}</p>

    <template v-if="this.isRecording">
      <img class="button" alt="stop button" @click="stopRecord" src="../assets/stop.svg">
    </template>
    <img v-else class="button" alt="rec button" @click="startRecord" src="../assets/button.svg">
  </div>
</template>

<script>
import Recorderx, {ENCODE_TYPE} from 'recorderx'


export default {
    name: 'recorder',
    
    data() {
        return { response: '', rc: new Recorderx(), isRecording: false } 
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

        const audiofile = this.rc.getRecord({
          encodeTo: ENCODE_TYPE.WAV
        })
        this.rc.clear();

        let data = new FormData()
        data.append('file', audiofile)

        this.response = 'sending data'
        try {
          let server_response = await fetch('http://localhost:1337/upload', {
            method: 'POST',
            body: data
          })

          this.response = await server_response.text()
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
  align-content: center;
  font-family:sans-serif;
}
.button {
  cursor: pointer;
}
</style>
