const App = {
  data() {
    return {
      // 所有活動資料
      food: [],
      // 所有主題分類
      topics: [],
      // 查詢關鍵字
      keyword: '',
      // 排序分類
      sortType: 'newest',
      // 查詢主題分類
      targetTopic: '',
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
    filteredFood() {
      const keyword = this.keyword.trim().toLowerCase()
      const targetTopic = this.targetTopic.trim().toLowerCase()

      // 先進行搜尋與 Topic 篩選
      let result = this.food.filter(item => {

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

      // 複製陣列，避免直接修改 this.food
      result = [...result]

      // 排序
      switch (this.sortType) {
        // 最新景點
        case 'newest':
          result.sort((a, b) => {
            return new Date(b.id) - new Date(a.id)
          })
          break
        // 最舊景點
        case 'oldest':
          result.sort((a, b) => {
            return new Date(a.id) - new Date(b.id)
          })
          break
        // 名稱 A-Z
        case 'titleAsc':
          result.sort((a, b) => {
            return a.title.localeCompare(b.title, 'zh-Hant')
          })
          break
        // 名稱 Z-A
        case 'titleDesc':
          result.sort((a, b) => {
            return b.title.localeCompare(a.title, 'zh-Hant')
          })
          break
        // 台中行政區固定順序
        case 'district':
          result.sort((a, b) => {
            const indexA = this.districtOrder.indexOf(a.district)
            const indexB = this.districtOrder.indexOf(b.district)
            // 都是空值
            if (!a.district && !b.district) {
              return 0
            }
            // 空值排最後
            if (!a.district) {
              return 1
            }
            if (!b.district) {
              return -1
            }
            // 不在 districtOrder 的資料排最後
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
        this.filteredFood.length / this.pageSize
      )
    },
    // 目前頁面的資料
    paginatedFood() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.filteredFood.slice(start, end)
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
    async getFood() {
      this.loading = true

      try {
        const response = await axios.get('/api/food')
        this.food = response.data.food
        // console.log('活動資料：', this.food)

        this.food.forEach(food => {
          food.topics.forEach(topic => {
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
    searchFood() {
      // 查詢條件改變後回到第一頁
      this.currentPage = 1
    },
    // 清除查詢
    clearSearch() {
      this.keyword = ''
      this.targetTopic = ''
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
    this.getFood()
  }
}
Vue.createApp(App).mount('#app')
