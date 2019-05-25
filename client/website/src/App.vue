<template>
  <div id="app">
    <img id="logo" alt="Vue logo" src="./assets/logo.png">
    <recorder/>
  </div>
</template>

<script>
import Recorder from './components/Recorder.vue'

export default {
  name: 'app',
  components: {
    Recorder
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

#logo {
  width: 50%;
  height: 50%;
}
</style>
