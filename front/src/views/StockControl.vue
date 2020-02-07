<template>
    <div class="stock-control-main">
        <MyHeader></MyHeader>
        <el-table
            v-loading="loading"
            :data="signalList"
            size="mini"
            :stripe="true"
            :border="true"
        >
            <el-table-column
                prop="code"
                label="代码"
                width="180"
            >
                <template slot-scope="scope">
                    <el-link type="primary" :underline="false" @click="jumpToKline(scope.row.code,scope.row.period)">
                        {{scope.row.code}}
                    </el-link>
                </template>
            </el-table-column>
            <el-table-column
                prop="period"
                label="周期"
                width="180"
                :filters="[{ text: '5m', value: '5m' }, { text: '15m', value: '15m' },{ text: '30m', value: '30m' }]"
                :filter-method="filterPeriod"
                filter-placement="bottom-end"
            >
            </el-table-column>
            <el-table-column
                prop="fire_time"
                label="时间">
            </el-table-column>
            <el-table-column
                prop="price"
                label="价格">
            </el-table-column>
            <el-table-column
                prop="remark"
                label="备注">
            </el-table-column>
            <el-table-column
                prop="tags"
                label="标签"
                :filters="[{ text: '双盘', value: '双盘' }, { text: '完备', value: '完备' }]"
                :filter-method="filterTags"
                filter-placement="bottom-end"
            >
            </el-table-column>
        </el-table>
    </div>
</template>

<script>
    // @ is an alias to /src
    import {userApi} from '../api/UserApi'
    // import {mapGetters, mapMutations} from 'vuex'
    // let moment = require('moment')
    import echarts from 'echarts/lib/echarts'
    import CommonTool from "../tool/CommonTool";
    import MyHeader from "./MyHeader";

    export default {
        name: 'stock-control',
        components: {
            "MyHeader": MyHeader
        },
        data() {
            return {
                loading: true,
                signalList: [],
                periodList: ['3m', '5m', '15m', '30m', '60m'],
                beichiList: {}
            }
        },
        mounted() {
            const page = this.getParams('page') || '1';
            this.getSignalList(page)
        },
        beforeDestroy() {

        },
        methods: {
            jumpToControl(type) {
                if (type === "futures") {
                    this.$router.replace("/futures-control")
                } else {
                    this.$router.replace("/stock-control")
                }
            },
            filterTags(value, row) {
                return row.tags === value;
            },
            filterPeriod(value, row) {
                return row.period === value;
            },
            getSignalList(page) {
                userApi.getStockSignalList(page).then(res => {
                    this.signalList = res
                    this.loading = false
                }).catch((error) => {
                    this.loading = false
                    console.log("获取股票信号列表失败:", error)
                })
            },
            jumpToKline(symbol, period) {
                // 总控页面不关闭，开启新页面
                let routeUrl = this.$router.resolve({
                    path: '/kline-big',
                    query: {
                        symbol: symbol,
                        period: period,
                        endDate: CommonTool.dateFormat("yyyy-MM-dd")
                    }
                });
                window.open(routeUrl.href, '_blank');
            },
            getParams(name) {
                let res = ''
                let categoryStr = window.location.href.split('?')[1] || ''
                if (categoryStr.length > 1) {
                    let arr = categoryStr.split('&')
                    for (let i = 0, len = arr.length; i < len; i++) {
                        let pair = arr[i]
                        let key = pair.split('=')[0]
                        let value = pair.split('=')[1]

                        if (key === name) {
                            res = value
                            console.log('coinName', res)
                            break
                        }
                    }
                }
                return res
            }
        }
    }
</script>
<style lang="stylus" scoped>
    @import "../style/stock-control.styl";
</style>