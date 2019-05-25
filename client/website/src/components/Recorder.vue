<template>
  <div>
    <h1>Start recording your conversation!</h1>
    <p>{{ response }}</p>

    <template v-if="this.isRecording">
      <p>Recording for: {{ recordTime }} </p>
      <button @click="stopRecord">Stop!</button>
    </template>
    <button v-else @click="startRecord">Record!</button>
  </div>
</template>

<script>
import Recorderx, {ENCODE_TYPE} from 'recorderx'


export default {
    name: 'recorder',
    
    data() {
        return { response: '', rc: new Recorderx(), recordTime: 0, isRecording: false } 
    },

    methods: {
      async startRecord() {
        try {
          await this.rc.start()
          this.isRecording = true;

          setInterval(() => this.recordTime += 1 , 1000)
        }
        catch(e) {
          this.response = e
        }        
      },

      async stopRecord() {
        this.rc.pause()
        this.response = 'Finished recording'
        this.isRecording = false;
        this.recordTime = 0;

        const audiofile = this.rc.getRecord({
          encodeTo: ENCODE_TYPE.WAV
        })

        let data = new FormData()
        data.append('file', audiofile)

        this.response = 'sending data'
        try {
          let response = await fetch('http://localhost:1337/upload', {
            method: 'POST',
            body: data
          })

          this.response = await response.text()
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
}
</style>
