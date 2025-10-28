# 真机调试错误修复说明

## 问题描述

真机调试时出现以下错误：
```
Error: not node js file system!path:/saaa_config.json
error occurs:no such file or directory, access 'wxfile://usr/miniprogramLog/log2'
```

## 问题原因

1. **saaa_config.json**: uni-app 框架内部配置文件，在真机环境下路径不存在
2. **miniprogramLog**: 微信小程序日志系统文件，真机环境下访问权限不同
3. **文件系统差异**: 开发工具使用模拟的文件系统，真机使用微信的 wxfile:// 协议

## 解决方案

### 1. ✅ 全局错误处理 (App.vue)

在 `src/App.vue` 中添加了全局错误拦截：

```javascript
onError: function (err) {
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
```

### 2. ✅ 优化小程序配置 (manifest.json)

添加了以下配置：

```json
{
  "mp-weixin": {
    "setting": {
      "uploadWithSourceMap": false,  // 禁用 sourcemap 上传
      "babelSetting": {
        "ignore": [],
        "disablePlugins": [],
        "outputPath": ""
      }
    },
    "lazyCodeLoading": "requiredComponents"  // 按需加载
    // 注意：不要添加 useExtendedLib 配置，会导致真机调试报错
  }
}
```

**重要提示**：
- ❌ 不要使用 `useExtendedLib` 配置（会导致错误码 80058）
- ✅ 使用 `lazyCodeLoading` 优化加载性能

### 3. ✅ 创建项目配置文件 (project.config.json)

创建了完整的微信小程序项目配置，包括：
- 禁用不必要的检查和功能
- 优化构建和上传设置
- 配置代码压缩选项

## 使用方法

### 重新构建项目

```bash
cd frontend-mp
npm run dev:mp-weixin
```

### 真机调试步骤

1. 使用微信开发者工具打开 `frontend-mp/dist/dev/mp-weixin` 目录
2. 点击"预览"或"真机调试"
3. 使用手机微信扫码

### 预期效果

- ✅ 错误信息不再显示在控制台
- ✅ 小程序在真机上正常运行
- ✅ 不影响业务功能

## 注意事项

⚠️ **这些错误是框架层面的非致命错误，不影响实际功能**

- 错误来源于 uni-app 框架内部
- 在开发工具和真机环境之间的文件系统差异导致
- 通过全局错误处理可以安全忽略

## 如果问题仍然存在

1. **清理缓存重新编译**
   ```bash
   rm -rf node_modules dist
   npm install
   npm run dev:mp-weixin
   ```

2. **检查微信开发者工具设置**
   - 确保"不校验合法域名"已勾选
   - 确保基础库版本 >= 2.0.0

3. **检查手机微信版本**
   - 建议使用最新版本微信

## 常见问题

### Q1: 错误码 80058 - extendedlib=weui value is invalid

**原因**: `useExtendedLib` 配置值不正确

**解决**: 从 `manifest.json` 中移除 `useExtendedLib` 配置项

```json
// ❌ 错误配置
"useExtendedLib": {
  "weui": false
}

// ✅ 正确做法：完全移除该配置
```

### Q2: 仍然看到 saaa_config.json 错误

**解决**: 
1. 确保修改了 `src/App.vue` 的 `onError` 方法
2. 重新编译项目 `npm run dev:mp-weixin`
3. 在微信开发者工具中重新打开项目

## 相关文件

- `src/App.vue` - 全局错误处理
- `src/manifest.json` - 小程序配置
- `src/project.config.json` - 项目配置
- `vite.config.js` - 构建配置
