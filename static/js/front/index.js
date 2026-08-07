const App = {
  data() {
    return {
      event: [],
      attr: [],
      food: []
    }
  },
  methods: {
    getData(){
      const vm = this;
      axios.get('/index/data')
        .then(response => {
          console.log(response.data.events);
          vm.event = response.data.events;
          vm.attr = response.data.attractions;
          vm.food = response.data.foods;
        })
        .catch(error => {
          console.log(error);
        });
    }
  },
  mounted() {
    const vm = this;
    vm.getData();
  }
}
Vue.createApp(App).mount("#app");