import Vue from 'vue'
import axios from 'axios'
import Home from './Home.vue'
import Analyze from './Analyze.vue';

Vue.config.productionTip = false
Vue.prototype.$http = axios

const NotFound = {
  template: '<p>Page not found</p>'
}

const routes = {
  '/': Home,
  '/analyze': Analyze
}

new Vue({
  el: '#app',
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