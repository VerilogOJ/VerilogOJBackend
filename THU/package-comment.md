# 原项目使用包的简介

## 框架和插件

- `Vue2` 前端框架
    - https://vuejs.org/
- `vuex` Vue全局的中心化状态管理
    - https://vuex.vuejs.org/
    - 官方推荐迁移至[Pinia](https://pinia.vuejs.org/)
- `vuex-persistedstate` 在页面刷新时保持状态
    - 已经死了 可以选择移除依赖或者找一个新的包
    - 代码中只有`main.js`里面一处用到了这个包 看一下保存了什么state吧 应该不会是登陆token什么的吧 可能不是很重要
    - https://www.npmjs.com/package/vuex-persistedstate
- `vue-router` 官方路由
    - https://router.vuejs.org/
- `webpack-cli`
    - https://webpack.js.org/api/cli/
- `axios` 发起和接收HTTP请求
    - https://axios-http.com/
- `vue-resource` 和`axios`一样
    - https://www.npmjs.com/package/vue-resource
- `js-cookie` 方便管理Cookie
    - https://www.npmjs.com/package/js-cookie
    - 但是看了一下项目中好像也没有用到这个包啊
- `html-webpack-plugin` simplifies creation of HTML files to serve your bundles
    - 不是很懂做的是什么
    - https://www.npmjs.com/package/html-webpack-plugin

## 网页元素

- `CodeMirror` 网页代码编辑器  
    - https://codemirror.net/
- `vue-codemirror` 和`CodeMirror`一样 应该是专门对Vue优化过的
- `vue-clipboard2` 
- `@toast-ui/vue-editor` 文本编辑器 看起来支持Markdown
    - https://ui.toast.com/
- `element-ui`
    - Vue2 https://element.eleme.io/#/en-US
    - Vue3 https://element-plus.org/en-US/

## 语言

- `core-js` JS的核心库 可以更方便的写js
    - https://www.npmjs.com/package/core-js
- `markdown-it` Markdown解析器
    - https://www.npmjs.com/package/markdown-it
- `luxon` 在JS中管理时间和日期
    - https://www.npmjs.com/package/luxon
- `moment` JS时间管理格式化
    - 和luxon重复
    - https://momentjs.com/
- `vue-datetime` 日期选择窗
    - https://www.npmjs.com/package/vue-datetime
- `weekstart` 获取当地一周开始的时间
    - https://gamtiq.github.io/weekstart/

## Verilog

- `wavedrom` 波形的图形生成
    - https://github.com/wavedrom/wavedrom
