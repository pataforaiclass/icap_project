const NavbarApp = {
  data() {
    return {
      //
    }
  },
  methods: {
    logout() {
      // console.log("out!");
      Swal.fire({
        title: "確定要登出？",
        showCancelButton: true,
        confirmButtonText: "確定",
        cancelButtonText: "取消",
        icon: "question"
      }).then((result) => {
        /* Read more about isConfirmed, isDenied below */
        if (result.isConfirmed) {
          // Swal.fire("已登出！", "", "success");
          window.location.href = "/admin/logout";
        }
      });
    }
  }
}
Vue.createApp(NavbarApp).mount("#navbarApp");