const App = {
  data() {
    return {
      manager: [],
      statistics: [],
      pieChart: null
    }
  },
  methods: {
    createChart() {
      const vm = this;
      const ctx = document.getElementById('pieChart');

      vm.pieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['年度活動', '熱門景點', '美食巡禮'],
          datasets: [{
            label: '資料筆數',
            data: [vm.statistics.event,vm.statistics.attraction,vm.statistics.food],
            hoverOffset: 4
          }]
        }
      });
    }
  },
  mounted() {
    const vm = this;
    axios.get("/admin/api/index")
      .then(function (res) {
        // console.log(res);
        vm.manager = res.data.manager;
        vm.statistics = res.data.statistics;
        vm.createChart();
      })
      .catch(function (err) {
        console.log(err);
      })
      .finally(function () {
        //
      });
  }
}
Vue.createApp(App).mount("#app");