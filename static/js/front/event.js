const App = {
  data() {
    return {
      // 所有活動資料
      event: [],
      // 查詢關鍵字
      keyword: '',
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
    filteredEvents() {
      const keyword = this.keyword.trim().toLowerCase()

      if (!keyword) {
        return this.event
      }

      return this.event.filter(item => {
        return item.title.toLowerCase().includes(keyword) ||
          item.content.toLowerCase().includes(keyword)
      })
    },
    // 總頁數
    totalPages() {
      return Math.ceil(
        this.filteredEvents.length / this.pageSize
      )
    },
    // 目前頁面的資料
    paginatedEvents() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.filteredEvents.slice(start, end)
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
    async getEvent() {
      this.loading = true

      try {
        const response = await axios.get('/api/event')
        this.event = response.data.event
        // console.log('活動資料：', this.event)
      } catch (error) {
        console.error('取得活動資料失敗：', error)
      } finally {
        this.loading = false
      }
    },
    // 查詢活動
    searchEvent() {
      // 查詢條件改變後回到第一頁
      this.currentPage = 1
    },
    // 清除查詢
    clearSearch() {
      this.keyword = ''
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
    this.getEvent()
  }
}
Vue.createApp(App).mount('#app')
