<template>
  <div id="home">
    <div class=logo>
      <img id=logo alt="Vue logo" src="./assets/REverb_logo.png">
      <h1>Analysis results</h1>
    </div>
    <Visualizer/>
  </div>
</template>

<script>
import Visualizer from './components/Visualizer';

export default {
  name: 'analyze',
  components: {
      Visualizer
  }
}
</script>