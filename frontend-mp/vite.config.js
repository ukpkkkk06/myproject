import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import path from 'node:path'

export default defineConfig({
  plugins: [uni()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'), // 确保指向 src
    },
  },
  build: {
    // 禁用 sourcemap 减少体积和潜在问题
    sourcemap: false,
    // 确保正确的代码分割
    minify: 'terser',
    target: 'es2015'
  },
  define: {
    // 禁用 process.env 相关的 node 环境检测
    'process.env': {}
  }
})
