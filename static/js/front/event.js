const App = {
  data() {
    return {
      // 所有活動資料
      event: [],
      // 查詢關鍵字
      keyword: '',
      // 排序分類
      sortType: 'newest',
      // 每頁顯示筆數
      // 1 為特殊需求：一頁只顯示一筆
      pageSize: 9,
      // 目前頁碼
      currentPage: 1,
      // API 載入狀態
      loading: false,
      // 區域順序
      districtOrder: ['中區', '東區', '南區', '西區', '北區', '北屯區', '西屯區', '南屯區', '太平區', '大里區', '霧峰區', '烏日區', '豐原區', '后里區', '石岡區', '東勢區', '和平區', '新社區', '潭子區', '大雅區', '神岡區', '大肚區', '沙鹿區', '龍井區', '梧棲區', '清水區', '大甲區', '外埔區', '大安區']
    }
  },
  computed: {
    // 查詢後的資料
    filteredEvents() {
      const keyword = this.keyword.trim().toLowerCase()

      // 先搜尋
      let result = this.event

      if (keyword) {
        result = this.event.filter(item => {
          return item.title.toLowerCase().includes(keyword) ||
            item.content.toLowerCase().includes(keyword)
        })
      }

      // 再排序
      result = [...result]

      switch (this.sortType) {
        case 'newest':
          result.sort((a, b) => {
            return new Date(b.id) - new Date(a.id)
          })
          break

        case 'oldest':
          result.sort((a, b) => {
            return new Date(a.id) - new Date(b.id)
          })
          break

        case 'titleAsc':
          result.sort((a, b) => {
            return a.title.localeCompare(b.title, 'zh-Hant')
          })
          break

        case 'titleDesc':
          result.sort((a, b) => {
            return b.title.localeCompare(a.title, 'zh-Hant')
          })
          break

        case 'district':
          result.sort((a, b) => {
            const indexA = this.districtOrder.indexOf(a.district)
            const indexB = this.districtOrder.indexOf(b.district)
            // 空值排最後
            if (!a.district && !b.district) {
              return 0
            }
            if (!a.district) {
              return 1
            }
            if (!b.district) {
              return -1
            }
            // 不在 districtOrder 中的資料也排最後
            if (indexA === -1 && indexB === -1) {
              return 0
            }
            if (indexA === -1) {
              return 1
            }
            if (indexB === -1) {
              return -1
            }
            return indexA - indexB
          })
          break
      }

      return result
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
    // 改變排序
    changeSort() {
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
