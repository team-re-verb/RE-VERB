<template>
  <div id="home">
    <div class=logo>
      <img id=logo alt="Vue logo" src="./assets/REverb_logo.png">
      <img id=text alt="Vue logo text" src="./assets/REverb_text.png">
    </div>
    <recorder/>
  </div>
</template>

<script>
import Recorder from './components/Recorder.vue'

export default {
  name: 'home',
  components: {
    Recorder
  }
}
</script>

<style>
#home {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

.logo {
  align-items: center;
}
.logo #text{
  width: 50%;
  height: 50%;

}

.logo #logo{
  width: 25%;
  height: 25%;
}
</style>
