const App = {
  data() {
    return {
      current_type: "",
      title: "",
      editor: null,
      content: "",
      postalCode: "",
      city: "",
      district: "",
      address: "",
      tip: "",
      facilities: "",
      topic: [""],
      image: [],
      titleInvalid: false,
      contentInvalid: false,
      postalCodeInvalid: false
    }
  },
  methods: {
    initEditor() {
      const vm = this;
      ClassicEditor
        .create(document.querySelector('#editor'), {
          toolbar: [
            'heading',
            '|',
            'bold',
            'italic',
            'link',
            'bulletedList',
            'numberedList',
            '|',
            'undo',
            'redo'
          ]
        })
        .then(editor => {
          vm.editor = editor
          vm.content = editor.getData()

          editor.model.document.on('change:data', () => {
            vm.content = editor.getData();
            vm.contentWatch();
          })
        })
        .catch(error => {
          console.error(error)
        })
    },
    getContent() {
      console.log(this.content)
    },
    addTopic() {
      const vm = this;
      vm.topic.push("")
    },
    deleteTopic(index) {
      const vm = this;
      if (vm.topic.length <= 1) {
        vm.topic[0] = "";
        return
      }
      vm.topic.splice(index, 1)
    },
    handleFileChange(attractions) {
      this.image = Array.from(attractions.target.files);
      console.log(this.image);
    },
    titleWatch() {
      const vm = this;
      vm.titleInvalid = (!vm.title || vm.title.trim().length === 0);
    },
    contentWatch() {
      const vm = this;
      vm.contentInvalid = (!vm.content || vm.content.trim().length === 0);
    },
    postalCodeWatch() {
      const vm = this;
      const postalCodeRegex = /^(\d{3}|\d{5}|\d{6})?$/;
      vm.postalCodeInvalid = !postalCodeRegex.test(vm.postalCode);
    },
    storeData() {
      const vm = this;
      const formData = new FormData();
      let noRq = false;


      if (!vm.title || vm.title.trim().length === 0) {
        vm.titleInvalid = true;
        noRq = true;
      }
      if (!vm.content || vm.content.trim().length === 0) {
        vm.contentInvalid = true;
        noRq = true;
      }
      const postalCodeRegex = /^(\d{3}|\d{5}|\d{6})?$/;
      if (!postalCodeRegex.test(vm.postalCode)) {
        vm.postalCodeInvalid = true;
        noRq = true;
      }
      if (noRq) {
        Swal.fire({
          title: "有必要欄位尚未填寫，或欄位填寫錯誤！",
          icon: "warning"
        });
        return;
      }

      formData.append("title", vm.title);
      formData.append("content", vm.content);
      formData.append("postalCode", vm.postalCode);
      formData.append("city", vm.city);
      formData.append("district", vm.district);
      formData.append("address", vm.address);
      formData.append("tip", vm.tip);
      formData.append("facilities", vm.facilities);
      formData.append("topic", JSON.stringify(vm.topic));

      vm.image.forEach(file => {
        formData.append("image", file);
      });

      // console.log(formData);

      axios.post("/admin/api/attractions", formData)
        .then(response => {
          console.log(response.data);
          Swal.fire({
            icon: "success",
            title: "新增成功",
            confirmButtonText: "確定"
          }).then((result) => {
            if (result.isConfirmed) {
              window.location.href = "/admin/attractions";
            }
          });
        })
        .catch(error => {
          console.log("ERROR");
          console.log("HTTP Status:", error.response?.status);
          console.log("Response Data:", error.response?.data);
          console.log("Error Detail:", error.response?.data?.detail);
        });
    }
  },
  computed: {
    //
  },
  mounted() {
    const vm = this;
    vm.current_type = document.getElementById("app").dataset.currentPage;
    vm.initEditor();
  }
}
Vue.createApp(App).mount("#app");