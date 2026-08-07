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
      phone1: "",
      phone2: "",
      facilities: "",
      topic: [""],
      image: [],
      titleInvalid: false,
      contentInvalid: false,
      postalCodeInvalid: false,
      phone1Invalid: false,
      phone2Invalid: false
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
    handleFileChange(food) {
      this.image = Array.from(food.target.files);
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
    phone1Watch() {
      const vm = this;
      const phoneRegex = /^(?:$|(?:0[2-8]-?\d{7,8}|0\d{2}-?\d{6,8}|\(0[2-8]\)\d{7,8}|\(0\d{2}\)\d{6,8}|09\d{2}-?\d{3}-?\d{3}))$/;
      vm.phone1Invalid = !phoneRegex.test(vm.phone1);
    },
    phone2Watch() {
      const vm = this;
      const phoneRegex = /^(?:$|(?:0[2-8]-?\d{7,8}|0\d{2}-?\d{6,8}|\(0[2-8]\)\d{7,8}|\(0\d{2}\)\d{6,8}|09\d{2}-?\d{3}-?\d{3}))$/;
      vm.phone2Invalid = !phoneRegex.test(vm.phone2);
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
      const phoneRegex = /^(?:$|(?:0[2-8]-?\d{7,8}|0\d{2}-?\d{6,8}|\(0[2-8]\)\d{7,8}|\(0\d{2}\)\d{6,8}|09\d{2}-?\d{3}-?\d{3}))$/;
      if (!phoneRegex.test(vm.phone1)) {
        vm.phone1Invalid = true;
        noRq = true;
      }
      if (!phoneRegex.test(vm.phone2)) {
        vm.phone2Invalid = true;
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
      formData.append("phone1", vm.phone1);
      formData.append("phone2", vm.phone2);
      formData.append("facilities", vm.facilities);
      formData.append("topic", JSON.stringify(vm.topic));

      vm.image.forEach(file => {
        formData.append("image", file);
      });

      // console.log(formData);

      axios.post("/admin/api/food", formData)
        .then(response => {
          console.log(response.data);
          Swal.fire({
            icon: "success",
            title: "新增成功",
            confirmButtonText: "確定"
          }).then((result) => {
            if (result.isConfirmed) {
              window.location.href = "/admin/food";
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