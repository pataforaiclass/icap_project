const App = {
  data() {
    return {
      // 所有活動資料
      attractions: [],
      // 所有主題分類
      topics: [],
      // 查詢關鍵字
      keyword: '',
      // 查詢主題分類
      targetTopic: '',
      // 每頁顯示筆數
      // 1 為特殊需求：一頁只顯示一筆
      pageSize: 9,
      // 目前頁碼
      currentPage: 1,
      // API 載入狀態
      loading: false
    }
  },
  computed: {
    // 查詢後的資料
    filteredAttractions() {
      const keyword = this.keyword.trim().toLowerCase()
      const targetTopic = this.targetTopic.trim().toLowerCase()

      return this.attractions.filter(item => {

        // 關鍵字搜尋
        const matchKeyword =
          !keyword ||
          item.title.toLowerCase().includes(keyword) ||
          item.content.toLowerCase().includes(keyword)

        // Topic 搜尋
        const matchTopic =
          !targetTopic ||
          item.topics.some(topic =>
            topic.toLowerCase() === targetTopic
          )

        // 兩個條件都符合才保留
        return matchKeyword && matchTopic
      })
    },
    // 總頁數
    totalPages() {
      return Math.ceil(
        this.filteredAttractions.length / this.pageSize
      )
    },
    // 目前頁面的資料
    paginatedAttractions() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.filteredAttractions.slice(start, end)
    },
    // 分頁頁碼
    pageNumbers() {
      const total = this.totalPages
      const current = this.currentPage

      if (total <= 7) {
        return Array.from(
          { length: total },
          (_, index) => index + 1
        )
      }

      const pages = []

      // 前面幾頁
      if (current <= 4) {
        pages.push(1, 2, 3, 4, 5)
        pages.push('...')
        pages.push(total)
        return pages
      }

      // 後面幾頁
      if (current >= total - 3) {
        pages.push(1)
        pages.push('...')
        pages.push(
          total - 4,
          total - 3,
          total - 2,
          total - 1,
          total
        )
        return pages
      }

      // 中間位置
      pages.push(1)
      pages.push('...')
      pages.push(
        current - 1,
        current,
        current + 1
      )
      pages.push('...')
      pages.push(total)
      return pages
    }
  },
  methods: {
    // 取得活動資料
    async getAttractions() {
      this.loading = true

      try {
        const response = await axios.get('/api/attr')
        this.attractions = response.data.attractions
        console.log('活動資料：', this.attractions)

        this.attractions.forEach(attr => {
          attr.topics.forEach(topic => {
            if (!this.topics.includes(topic)) this.topics.push(topic);
          });
        });
      } catch (error) {
        console.error('========== API ERROR ==========')

        // Axios 錯誤訊息
        console.error('message:', error.message)

        // HTTP Status，例如 500
        console.error('status:', error.response?.status)

        // Flask 回傳的內容
        console.error('response data:', error.response?.data)

        // Response headers
        console.error('response headers:', error.response?.headers)

        // Axios request 設定
        console.error('request config:', error.config)

        console.error('================================')
      } finally {
        this.loading = false
      }
    },
    // 查詢活動
    searchAttractions() {
      // 查詢條件改變後回到第一頁
      this.currentPage = 1
    },
    // 清除查詢
    clearSearch() {
      this.keyword = ''
      this.targetTopic = ''
      this.currentPage = 1
    },
    // 切換頁碼
    changePage(page) {
      // ... 不可以點
      if (page === '...') {
        return
      }
      // 防止超出頁碼範圍
      if (page < 1 || page > this.totalPages) {
        return
      }
      this.currentPage = page
      // 回到列表上方
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      })
    },
    // 每頁筆數改變
    changePageSize() {
      // 改變每頁數量後回到第一頁
      this.currentPage = 1
    }
  },
  watch: {
    // 搜尋文字變化
    keyword() {
      this.currentPage = 1
    },
    // 每頁筆數變化
    pageSize() {
      this.currentPage = 1
    }
  },
  mounted() {
    this.getAttractions()
  }
}
Vue.createApp(App).mount('#app')
