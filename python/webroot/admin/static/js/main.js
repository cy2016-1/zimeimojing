const Foo = {
    template: '<div>这里是Foo模块内容</div>'
}
const Bar = {
    template: '<div>bar的内容</div>'
}

const baseURL = "../"

Vue.component('head-com', function(resolve, reject) {
    axios.get("./pages/test.html").then(function(res) {
        resolve({
            template: res.data
        })
    });
});

var getRouter;

function routerGo(getRouter) {
    getRouter = filterAsyncRouter(getRouter) // 过滤路由
    console.log(getRouter)
    router.addRoutes(getRouter) // 动态添加路由
        // global.antRouter = getRouter // 将路由数据传递给全局变量，做侧边栏菜单渲染工作
        // next({...to, replace: true })
}

// 遍历后台传来的路由字符串，转换为组件对象
function filterAsyncRouter(asyncRouterMap) {
    const accessedRouters = asyncRouterMap.filter(route => {
        // if (route.component) {
        //     if (route.component === 'Layout') { // Layout组件特殊处理
        //         route.component = Layout
        //     } else {
        //         route.component = _import(route.component)
        //     }
        // }
        if (route.children && route.children.length) {
            route.children = filterAsyncRouter(route.children)
        }
        return true
    })
    return accessedRouters
}

const routes = [{
    path: '/foo'
}, {
    path: '/bar'
}]

const router = new VueRouter({
    routes // (缩写) 相当于 routes: routes
})

// 获取远程路由表
var menu_url = baseURL + 'api/admin.py?get=menu'
axios.get(menu_url).then(res => {
    getRouter = res.data // 后台拿到路由
    console.log(getRouter)

    // saveObjArr('router', getRouter) // 存储路由到localStorage
    routerGo(getRouter) // 执行路由跳转方法
})

new Vue({
    el: '#app',
    data: function() {
        return {
            visible: false,
            isCollapse: false
        }
    },
    watch: {
        // 如果路由有变化，会再次执行该方法
        '$route': 'fetchData'
    },
    methods: {
        fetchData() {
            console.log('这里执行了')
            console.log(this.$route.fullPath)
        },
        handleOpen(key, keyPath) {
            console.log(key, keyPath);
        },
        handleClose(key, keyPath) {
            console.log(key, keyPath);
        }
    },
    computed: {
        routes() {
            console.log("这里", getRouter)
            return getRouter
        }
    },
    router: router
})