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
    // 忽略 uni-app 框架内部的文件系统错误
    const ignoreErrors = [
      'saaa_config',           // uni-app 框架内部配置文件
      'miniprogramLog',        // 小程序日志文件
      'wxfile://usr',          // 微信文件系统路径
      'not node js file system' // 非 Node.js 文件系统错误
    ]
    
    if (err && typeof err === 'string') {
      for (const pattern of ignoreErrors) {
        if (err.indexOf(pattern) > -1) {
          return true // 阻止错误继续传播
        }
      }
    }
  }
}
</script>

<style>
/*每个页面公共css */
</style>
