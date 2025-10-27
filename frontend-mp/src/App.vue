<script>
export default {
  onLaunch: function () {
    console.log('App Launch')
    // 禁用后台获取数据功能，避免隐私权限报错
    if (typeof wx !== 'undefined' && wx.getBackgroundFetchData) {
      // 不调用后台获取数据相关API
    }
  },
  onShow: function () {
    console.log('App Show')
  },
  onHide: function () {
    console.log('App Hide')
  },
  // 全局错误处理
  onError: function (err) {
    console.error('App Error:', err)
    // 忽略 saaa_config.json 相关的报错（uni-app框架内部问题）
    if (err && err.indexOf && err.indexOf('saaa_config') > -1) {
      return true // 阻止错误继续传播
    }
  }
}
</script>

<style>
/*每个页面公共css */
</style>
