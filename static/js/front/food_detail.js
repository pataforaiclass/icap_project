const { createApp, nextTick } = Vue;

createApp({
  data() {
    return {
      // 活動資料
      food: null,
      // 輪播目前圖片
      currentSlide: 0,
      // 載入狀態
      loading: true,
      // 錯誤訊息
      error: null,
      // GLightbox 實例
      lightbox: null
    };
  },
  mounted() {
    this.getFood();
  },
  methods: {
    // 取得活動資料
    async getFood() {
      try {
        this.loading = true;
        /*
         * 這裡先取得目前網址的 foodId
         * 例如： /food/15
         * 就會取得： 15
         */
        const path = window.location.pathname;
        const foodId = path.split('/').filter(Boolean).pop();
        const response = await axios.get(
          `/api/food/${foodId}`
        );
        this.food = response.data.food;
        this.currentSlide = 0;
        setTimeout(() => {
          // console.log(
          //   'Lightbox 元素:',
          //   document.querySelectorAll('.event-lightbox').length
          // );
          this.initLightbox();
        }, 0);
      } catch (error) {
        console.error(error);
        this.error = '活動資料取得失敗。';
      } finally {
        this.loading = false;
      }
    },
    /* 初始化 GLightbox */
    initLightbox() {
      /* 如果之前已經初始化過，先銷毀 */
      if (this.lightbox) {
        this.lightbox.destroy();
        this.lightbox = null;
      }
      /* 如果沒有圖片，就不初始化 */
      if (
        !this.food ||
        !this.food.images ||
        this.food.images.length === 0
      ) {
        return;
      }
      /* 建立 GLightbox */
      this.lightbox = GLightbox({
        selector: '.food-lightbox',
        /* 顯示圖片標題 */
        title: 'data-title',
        /* 啟用鍵盤操作 */
        keyboardNavigation: true,
        /* 點擊背景關閉 */
        closeOnOutsideClick: true
      });
    },
    // 取得圖片網址
    getImageUrl(image) {
      return `/static/image/food/${image}`;
    },
    // 顯示指定圖片
    showSlide(index) {
      if (
        !this.food ||
        !this.food.images ||
        this.food.images.length === 0
      ) {
        return;
      }
      this.currentSlide = index;
    },
    // 上一張 / 下一張
    changeSlide(direction) {
      if (
        !this.food ||
        !this.food.images ||
        this.food.images.length === 0
      ) {
        return;
      }
      const total = this.food.images.length;
      this.currentSlide += direction;
      /* 最後一張 → 第一張 */
      if (this.currentSlide >= total) {
        this.currentSlide = 0;
      }
      /* 第一張 → 最後一張 */
      if (this.currentSlide < 0) {
        this.currentSlide = total - 1;
      }
    }
  },
  beforeUnmount() {
    // 清除 GLightbox
    if (this.lightbox) {
      this.lightbox.destroy();
      this.lightbox = null;
    }
  }
}).mount('#foodDetailApp');