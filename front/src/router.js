import Vue from 'vue'
import Router from 'vue-router'
import FuturesControl from './views/FuturesControl.vue'
import StockControl from './views/StockControl.vue'
import MultiPeriod from './views/MultiPeriod.vue'
import KlineBig from './views/KlineBig.vue'

Vue.use(Router)

export default new Router({
    base: process.env.BASE_URL,
    mode:'history',
    routes: [
        {
            path: '/',
            redirect: '/futures-control'
        },
        {
            path: '/futures-control',
            name: 'futures-control',
            component: FuturesControl
        },
        {
            path: '/stock-control',
            name: 'stock-control',
            component: StockControl
        },
        {
            path: '/multi-period',
            name: 'multi-period',
            component: MultiPeriod
        },
        {
            path: '/kline-big',
            name: 'kline-big',
            component: KlineBig
        },
    ]
})
