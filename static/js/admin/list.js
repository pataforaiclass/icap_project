const App = {
  data() {
    return {
      current_type: "",
      dataList: []
    }
  },
  methods: {
    get_list() {
      const vm = this;
      axios
        .get('/admin/api/' + vm.current_type)
        .then(function (response) {
          // console.log(response);
          vm.dataList = response.data;
          // console.log(vm.dataList);
        })
        .catch(function (error) {
          console.log(error);
        })
        .finally(function () {
          // always executed
        });
    },
    gotoAdd() {
      const vm = this;
      window.location.href = "/admin/" + vm.current_type + "/add";
    },
    async deleteSelected() {
      const currentData = this.dataList[this.current_type];

      if (!currentData || currentData.length === 0) {
        return;
      }

      const selectedData = currentData.filter(item => item.checked);

      if (selectedData.length === 0) {
        Swal.fire({
          icon: "warning",
          title: "尚未選擇資料",
          text: "請至少選擇一筆資料"
        });

        return;
      }

      const result = await Swal.fire({
        icon: "warning",
        title: "確定要刪除嗎？",
        text: `即將刪除 ${selectedData.length} 筆資料`,
        showCancelButton: true,
        confirmButtonText: "確定刪除",
        cancelButtonText: "取消"
      });

      if (!result.isConfirmed) {
        return;
      }

      try {
        await Promise.all(
          selectedData.map(item => {
            return axios.delete(
              `/admin/api/${this.current_type}/${item.id}`
            );
          })
        );

        // 從目前類型的資料中移除已刪除的資料
        this.dataList[this.current_type] =
          currentData.filter(item => !item.checked);

        Swal.fire({
          icon: "success",
          title: "刪除成功",
          text: `已刪除 ${selectedData.length} 筆資料`
        });

      } catch (error) {
        console.error("刪除失敗：", error);
        console.log("status:", error.response?.status);
        console.log("data:", error.response?.data);

        Swal.fire({
          icon: "error",
          title: "刪除失敗",
          text: "刪除資料時發生錯誤"
        });
      }
    }
  },
  computed: {
    allChecked: {
      get() {
        const currentData = this.dataList[this.current_type];

        if (!currentData || currentData.length === 0) {
          return false;
        }

        return currentData.every(item => item.checked);
      },

      set(value) {
        const currentData = this.dataList[this.current_type];

        if (!currentData) {
          return;
        }

        currentData.forEach(item => {
          item.checked = value;
        });
      }
    }
  },
  mounted() {
    const vm = this;
    vm.current_type = document.getElementById("app").dataset.currentPage;

    vm.get_list();
  }
}
Vue.createApp(App).mount("#app");