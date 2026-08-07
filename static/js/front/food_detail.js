const { createApp } = Vue;

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
      error: null
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
      } catch (error) {
        console.error(error);
        this.error = '活動資料取得失敗。';
      } finally {
        this.loading = false;
      }
    },
    // 取得圖片網址
    getImageUrl(image) {
      return `/static/image/food/${image}`;
    },
    // 顯示指定圖片
    showSlide(index) {
      this.currentSlide = index;
    },
    // 上一張 / 下一張
    changeSlide(direction) {
      const total = this.food.images.length;
      this.currentSlide += direction;
      // 超過最後一張 → 第一張
      if (this.currentSlide >= total) {
        this.currentSlide = 0;
      }
      // 小於第一張 → 最後一張
      if (this.currentSlide < 0) {
        this.currentSlide = total - 1;
      }
    }
  }
}).mount('#foodDetailApp');