import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
import Home from './Home.vue'
import Analyze from './Analyze.vue';

Vue.config.productionTip = false
Vue.prototype.$http = axios

Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    audiofile: undefined,
    showAnalyze: false
  },
  mutations:{
    change(state, audiofile) {
      state.audiofile = audiofile
    },
    toggle(state){
      state.showAnalyze = !state.showAnalyze
    }
  },
  getters: {
    audiofile: state => state.audiofile,
    showAnalyze: state => state.showAnalyze
  }
})

const NotFound = {
  template: '<p>Page not found</p>'
}

const routes = {
  '/': Home,
  '/analyze': Analyze
}

new Vue({
  el: '#app',
  store,
  data: {
    currentRoute: window.location.pathname
  },
  computed: {
    ViewComponent() {
      return routes[this.currentRoute] || NotFound
    }
  },
  render(h) {
    return h(this.ViewComponent)
  }
})