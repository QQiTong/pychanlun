<template>
    <!--    <div class="main" id="main">-->
    <!--    </div>-->
    <div class="main">
        <!--合约切换区域        -->
        <div class="left">
            <div class="switchContainer">
                <div class="furtureTab">
                    <div class="symbol-title">期货</div>
                    <!--            上期所-->
                    <div class="symbol-list">
                        <a @click="switchSymbol('RB1910.XSGE')" class="bold symbol-item">螺纹RB</a>
                        <a @click="switchSymbol('HC9999.XSGE')" class="symbol-item">热卷HC</a>
                        <a @click="switchSymbol('RU9999.XSGE')" class="symbol-item">橡胶RU</a>
                        <a @click="switchSymbol('NI9999.XSGE')" class="symbol-item">沪镍NI</a>
                        <a @click="switchSymbol('FU9999.XSGE')" class="symbol-item">燃油FU</a>
                        <a @click="switchSymbol('ZN9999.XSGE')" class="symbol-item">沪锌ZN</a>
                        <a @click="switchSymbol('SP9999.XSGE')" class="symbol-item">纸浆SP</a>
                        <!--            郑商所-->
                        <a @click="switchSymbol('MA9999.XZCE')" class="bold symbol-item">甲醇MA</a>
                        <a @click="switchSymbol('SR9999.XZCE')" class="symbol-item">白糖SR</a>
                        <a @click="switchSymbol('AP9999.XZCE')" class="symbol-item">苹果AP</a>
                        <a @click="switchSymbol('CF9999.XZCE')" class="symbol-item">棉花CF</a>
                        <!--            大商所-->
                        <a @click="switchSymbol('J9999.XDCE')" class="bold symbol-item">焦炭J</a>
                        <a @click="switchSymbol('JM9999.XDCE')" class="symbol-item">焦煤JM</a>
                        <a @click="switchSymbol('PP9999.XDCE')" class="symbol-item">聚丙烯PP</a>
                    </div>

                </div>
                <div class="coinTab">
                    <div class="symbol-title">数字货币</div>
                    <div class="symbol-list">
                        <a @click="switchSymbol('XBTUSD')" class="bold symbol-item">BTC</a>
                    </div>

                </div>
                <div class="save-kline" @click="saveKline">保存K线</div>
            </div>
        </div>
        <!--图表显示区域        -->
        <div class="right">
            <div class="echarts">
                <v-chart autoresize ref="myCharts" :manual-update="true"></v-chart>
            </div>
            <div class="loading-anim" v-show="showAnim">
                <div class="loader-inner"></div>
                <div class="loader-inner"></div>
                <div class="loader-inner"></div>
                <div class="loader-inner"></div>
                <div class="loader-inner"></div>
            </div>
        </div>

    </div>
</template>

<script>
    // @ is an alias to /src
    import {userApi} from '../api/UserApi'
    // import {mapGetters, mapMutations} from 'vuex'
    // let moment = require('moment')

    import ECharts from 'vue-echarts'
    import 'echarts/lib/chart/candlestick'
    import 'echarts/lib/chart/line'
    import 'echarts/lib/chart/bar'
    import 'echarts/lib/component/dataZoom'
    import 'echarts/lib/component/toolbox'
    import 'echarts/lib/component/tooltip'
    import 'echarts/lib/component/markPoint'
    import 'echarts/lib/component/markLine'
    import 'echarts/lib/component/markArea'
    import 'echarts/lib/component/legend'
    import 'echarts/lib/component/title'

    export default {
        name: 'home',
        components: {
            'v-chart': ECharts
        },
        data () {
            return {
                // 控制动画和防重复请求
                showAnim: true,
                // myChart: null,
                option: {},
                echartsConfig: {
                    bgColor: '#202529',
                    upColor: 'red',
                    upBorderColor: 'red',
                    downColor: '#14d0cd',
                    downBorderColor: '#14d0cd'
                },
                // 品种
                symbol: 'XBTUSD',
                period: '1min',
                // symbol: "BTC_CQ",
                // period: "1min",
                // symbol: "RB1910.XSGE",
                // period: "1day",
                // 1 重新渲染 2 更新,
                refreshOrUpdate: 1,
                dataTitle: '主标题',
                dataSubTitle: '副标题',
                periodIcons: [
                    require('../assets/img/icon_1min.png'),
                    require('../assets/img/icon_3min.png'),
                    require('../assets/img/icon_5min.png'),
                    require('../assets/img/icon_15min.png'),
                    require('../assets/img/icon_30min.png'),
                    require('../assets/img/icon_1h.png'),
                    require('../assets/img/icon_4h.png'),
                    require('../assets/img/icon_1d.png'),
                    require('../assets/img/icon_1w.png'),
                    require('../assets/img/icon_refresh.svg')
                ],
                //    处理好的echarts数据
                resultData: {},
                // 缩放比例
                zoomStart: 55,
                timer: null,
                savedZoomStart: 0
            }
        },
        mounted () {
            this.getStockData()
            this.timer = setInterval(() => {
                this.refreshOrUpdate = 2
                if (!this.showAnim) {
                    console.log('发出请求---')
                    this.getStockData()
                } else {
                    console.log('拦截重复请求---')
                }
            }, 10 * 1000)

            this.$nextTick(() => {
                console.log('----1', this.$refs.myCharts)
                console.log('----2', this.$refs.myCharts.options)
            })
            // this.$refs.myCharts.options = this.option
            // this.$refs.myCharts.on('datazoom', function (obj) {
            //     //do some thing
            //     //这里通过obj获取信息，设定option之后,重新载入图表
            //     console.log("zoom事件:", obj)
            // });
        },
        beforeDestroy () {
            // if (!this.myChart) {
            //     return;
            // }
            // this.myChart.clear()
            // this.myChart.dispose();
            // this.myChart = null;
        },
        methods: {
            // handleDataZoom(param) {
            //     console.log("item", param)
            //     this.zoomStart = param.batch[0].start
            // },
            saveKline () {
                let requestData = {
                    symbol: this.symbol,
                    period: this.period
                }
                userApi.saveStockData(requestData).then(res => {
                    this.showAnim = false
                    // console.log("结果:", res);

                    this.dataTitle = this.symbol
                    this.dataSubTitle = this.period
                    // todo 判断请求和返回的symbol 是否一致
                    this.draw(res)
                }).catch(() => {
                    this.showAnim = false
                })
            },
            switchSymbol (symbol) {
                this.symbol = symbol
                this.refreshOrUpdate = 1
                this.getStockData()
            },
            getStockData () {
                this.showAnim = true

                // 恢复缩放比例
                // if (JSON.stringify(this.option) !== "{}") {
                //     console.log("恢复zoom", this.savedZoomStart, this.zoomStart)
                //     this.zoomStart = this.savedZoomStart
                // }
                let requestData = {
                    symbol: this.symbol,
                    period: this.period
                }
                userApi.stockData(requestData).then(res => {
                    this.showAnim = false
                    // console.log("结果:", res);

                    this.dataTitle = this.symbol
                    this.dataSubTitle = this.period
                    // todo 判断请求和返回的symbol 是否一致
                    this.draw(res)
                }).catch(() => {
                    this.showAnim = false
                })
            },
            //
            draw (stockJsonData) {
                let resultData = this.splitData(stockJsonData)
                // console.log("当前类型", this.refreshOrUpdate);
                if (this.refreshOrUpdate === 2) {
                    //    更新charts
                    // console.log("更新");
                    let options = this.$refs.myCharts.computedOptions
                    console.log('更新', this.$refs.myCharts, options)

                    options.series[0].data = resultData.values
                    options.series[0].markArea.data = resultData.zsvalues
                    options.series[1].data = resultData.biValues
                    options.series[2].data = resultData.duanValues
                    options.series[3].data = this.calculateMA(resultData, 5)
                    options.series[4].data = this.calculateMA(resultData, 10)
                    options.series[5].data = resultData.macd
                    options.series[6].data = resultData.diff
                    options.series[7].data = resultData.dea

                    options.series[8].data = resultData.macdBigLevel
                    options.series[9].data = resultData.diffBigLevel
                    options.series[10].data = resultData.deaBigLevel

                    options.series[11].data = resultData.volume

                    options.xAxis[0].data = resultData.time
                    options.xAxis[1].data = resultData.time
                    options.xAxis[2].data = resultData.timeBigLevel
                    options.xAxis[3].data = resultData.time
                    this.$refs.myCharts.mergeOptions(options, false)
                } else {
                    console.log('重载')
                    //    重载echarts
                    let option = {
                        animation: false,
                        backgroundColor: this.echartsConfig.bgColor,
                        title: {
                            text: this.dataTitle,
                            subtext: this.dataSubTitle,
                            left: '2%',
                            textStyle: {
                                color: 'white'
                            }
                        },
                        tooltip: { // 提示框
                            trigger: 'axis', // 触发类型：axis坐标轴触发,item
                            axisPointer: { // 坐标轴指示器配置项
                                type: 'cross' // 指示器类型，十字准星
                            },
                        },
                        toolbox: {
                            orient: 'horizontal',
                            itemSize: 16,
                            itemGap: 8,
                            top: 16,
                            right: '1.4%',
                            feature: {
                                myLevel1: {
                                    show: true,
                                    title: '1分钟',
                                    icon: 'image://' + this.periodIcons[0],
                                    onclick: () => {
                                        this.period = '1min'
                                        this.refreshOrUpdate = 1
                                        // console.log("this",this,params);
                                        this.getStockData()
                                    }
                                },
                                myLevel3: {
                                    show: true,
                                    title: '3分钟',
                                    icon: 'image://' + this.periodIcons[1],
                                    onclick: () => {
                                        this.period = '3min'
                                        this.refreshOrUpdate = 1
                                        this.getStockData()
                                    }
                                },
                                myLevel5: {
                                    show: true,
                                    title: '5分钟',
                                    icon: 'image://' + this.periodIcons[2],
                                    onclick: () => {
                                        this.period = '5min'
                                        this.refreshOrUpdate = 1
                                        this.getStockData()
                                    }
                                },
                                myLevel15: {
                                    show: true,
                                    title: '15分钟',
                                    icon: 'image://' + this.periodIcons[3],
                                    onclick: () => {
                                        this.period = '15min'
                                        this.refreshOrUpdate = 1
                                        this.getStockData()
                                    }
                                },
                                myLevel30: {
                                    show: true,
                                    title: '30分钟',
                                    icon: 'image://' + this.periodIcons[4],
                                    onclick: () => {
                                        this.period = '30min'
                                        this.refreshOrUpdate = 1
                                        this.getStockData()
                                    }
                                },
                                myLevel60: {
                                    show: true,
                                    title: '60分钟',
                                    icon: 'image://' + this.periodIcons[5],
                                    onclick: () => {
                                        this.period = '60min'
                                        this.refreshOrUpdate = 1
                                        this.getStockData()
                                    }
                                },
                                myLevel240: {
                                    show: true,
                                    title: '240分钟',
                                    icon: 'image://' + this.periodIcons[6],
                                    onclick: () => {
                                        this.period = '4hour'
                                        this.refreshOrUpdate = 1
                                        this.getStockData()
                                    }
                                },
                                myLevelDay: {
                                    show: true,
                                    title: '日',
                                    icon: 'image://' + this.periodIcons[7],
                                    background: '#555',
                                    onclick: () => {
                                        this.period = '1day'
                                        this.refreshOrUpdate = 1
                                        this.getStockData()
                                    }
                                },
                                myLevelWeek: {
                                    show: true,
                                    title: '周',
                                    icon: 'image://' + this.periodIcons[8],
                                    background: '#555',
                                    onclick: () => {
                                        this.period = '1week'
                                        this.refreshOrUpdate = 1
                                        this.getStockData()
                                    }
                                },
                                myAutoRefresh: {
                                    type: 'jpeg', // png
                                    // name: resultData.info
                                    background: '#555',
                                    icon: 'image://' + this.periodIcons[9],
                                    title: '刷新',
                                    onclick: () => {
                                        this.refreshOrUpdate = 2
                                        this.getStockData()
                                    }
                                },
                                // saveAsImage: {
                                //     type: 'jpeg',//png
                                //     name: dataTitle + '自动画线',
                                //     backgroundColor: '#fff',
                                //     title: '保存图片',
                                //     show: false
                                // },
                            },
                        },
                        color: ['yellow', 'green', 'yellow', 'white', '#999999'],
                        legend: {
                            data: ['笔', '段', 'MA5', 'MA10', '布林中轨'],
                            selected: {
                                '笔': true,
                                '段': true,
                                'MA5': false,
                                'MA10': false,
                                '布林中轨': false
                            },
                            top: 10,
                            textStyle: {
                                color: 'white'
                            }
                        },
                        grid: [
                            {// 直角坐标系
                                left: '3.2%',
                                right: '3.35%',
                                height: '57%',
                                top: 50,
                            },
                            {
                                top: '60%',
                                height: '15%',
                                left: '3.2%',
                                right: '3.35%',
                            },
                            {
                                top: '75%',
                                height: '15%',
                                left: '3.2%',
                                right: '3.35%',
                            },
                            {
                                top: '90%',
                                height: '5%',
                                left: '3.2%',
                                right: '3.35%',
                            }
                        ],
                        xAxis: [
                            {
                                type: 'category',
                                data: resultData.time,
                                scale: true,
                                boundaryGap: false,
                                splitLine: {show: false},
                                splitNumber: 20,
                                min: 'dataMin',
                                max: 'dataMax',
                                axisLine: {onZero: false, lineStyle: {color: '#8392A5'}}
                            },
                            {
                                type: 'category',
                                gridIndex: 1,
                                data: resultData.time,
                                axisTick: {
                                    show: false
                                },
                                axisLabel: {
                                    show: true
                                },
                                axisLine: {lineStyle: {color: '#8392A5'}}

                            },
                            {
                                type: 'category',
                                gridIndex: 2,
                                data: resultData.timeBigLevel,
                                axisTick: {
                                    show: false
                                },
                                axisLabel: {
                                    show: false
                                },
                                axisLine: {lineStyle: {color: '#8392A5'}}
                            },
                            {
                                type: 'category',
                                gridIndex: 3,
                                data: resultData.time,
                                axisTick: {
                                    show: false
                                },
                                axisLabel: {
                                    show: false
                                },
                                axisLine: {lineStyle: {color: '#8392A5'}}
                            }
                        ],
                        yAxis: [
                            {
                                scale: true,
                                splitArea: {
                                    show: false
                                },
                                splitLine: {
                                    lineStyle: {
                                        opacity: 0.3,
                                        type: 'dashed',
                                    }
                                },
                                axisLine: {lineStyle: {color: '#8392A5'}},
                            },
                            // 本级别macd
                            {
                                gridIndex: 1,
                                splitNumber: 2,
                                axisLine: {
                                    onZero: false,
                                    lineStyle: {color: '#8392A5'}
                                },
                                axisTick: {
                                    show: false
                                },
                                splitLine: {
                                    show: false
                                },
                                axisLabel: {
                                    show: true
                                },
                            },
                            // 大级别macd
                            {
                                gridIndex: 2,
                                splitNumber: 2,
                                axisLine: {
                                    onZero: false,
                                    lineStyle: {color: '#8392A5'}
                                },
                                axisTick: {
                                    show: false
                                },
                                splitLine: {
                                    show: false
                                },
                                axisLabel: {
                                    show: true
                                },
                            },
                            // 成交量
                            {
                                gridIndex: 3,
                                splitNumber: 1,
                                axisLine: {
                                    onZero: false,
                                    lineStyle: {color: '#8392A5'}
                                },
                                axisTick: {
                                    show: false
                                },
                                splitLine: {
                                    show: false
                                },
                                axisLabel: {
                                    show: false
                                },
                            },
                        ],
                        dataZoom: [

                            {
                                type: 'inside',
                                xAxisIndex: [0, 0],
                                start: this.zoomStart,
                                end: 100,
                                minSpan: 10,
                            },
                            {
                                type: 'inside',
                                xAxisIndex: [0, 1],
                                start: this.zoomStart,
                                end: 100,
                                minSpan: 10,
                            },
                            {
                                type: 'inside',
                                xAxisIndex: [0, 1],
                                start: this.zoomStart,
                                end: 100,
                                minSpan: 10,
                            },
                            {
                                xAxisIndex: [0, 1, 2, 3],
                                type: 'slider',
                                start: this.zoomStart,
                                end: 100,
                                top: '95%',
                                minSpan: 10,
                                textStyle: {
                                    color: '#8392A5'
                                },
                                dataBackground: {
                                    areaStyle: {
                                        color: '#8392A5'
                                    },
                                    lineStyle: {
                                        opacity: 0.8,
                                        color: '#8392A5'
                                    }
                                },
                                handleStyle: {
                                    color: '#fff',
                                    shadowBlur: 3,
                                    shadowColor: 'rgba(0, 0, 0, 0.6)',
                                    shadowOffsetX: 2,
                                    shadowOffsetY: 2
                                }

                            }
                        ],
                        series: [
                            {
                                name: 'K线图',
                                type: 'candlestick',
                                data: resultData.values,
                                animation: false,
                                itemStyle: {
                                    normal: {
                                        color: this.echartsConfig.upColor,
                                        color0: this.echartsConfig.downColor,
                                        borderColor: this.echartsConfig.upBorderColor,
                                        borderColor0: this.echartsConfig.downBorderColor
                                    }
                                },
                                // markPoint: {
                                //     data: resultData.mmdValues,
                                //     animation: false
                                // },
                                markArea: {
                                    silent: true,
                                    data: resultData.zsvalues,
                                },
                            },
                            {
                                name: '笔',
                                type: 'line',
                                z: 3,
                                data: resultData.biValues,
                                lineStyle: {
                                    normal: {
                                        opacity: 1,
                                        type: 'dashed',
                                        width: 1,
                                        color: 'yellow'
                                    },
                                },
                                symbol: 'none',
                                animation: false
                            },
                            {
                                name: '段',
                                type: 'line',
                                z: 4,
                                data: resultData.duanValues,
                                lineStyle: {
                                    normal: {
                                        opacity: 1,
                                        type: 'solid',
                                        width: 2,
                                        color: 'green'
                                    },
                                },
                                symbol: 'none',
                                animation: false
                            },
                            // {
                            //     name: 'markline',
                            //     type: 'line',
                            //     data: resultData.markLineData,
                            //     smooth: true,
                            //     lineStyle: {
                            //         normal: {
                            //             opacity: 0.25,
                            //             type: 'dashed',
                            //             width: 0.8,
                            //             color: 'blue'
                            //         },
                            //     },
                            //     symbol: 'none',
                            //     animation: false
                            // },
                            {
                                name: 'MA5',
                                type: 'line',
                                data: this.calculateMA(resultData, 5),
                                smooth: true,
                                lineStyle: {
                                    normal: {
                                        opacity: 0.9,
                                        type: 'solid',
                                        width: 1,
                                        color: 'white'
                                    },
                                },
                                symbol: 'none',
                                animation: false
                            },
                            {
                                name: 'MA10',
                                type: 'line',
                                data: this.calculateMA(resultData, 10),
                                smooth: true,
                                lineStyle: {
                                    normal: {
                                        opacity: 0.9,
                                        type: 'solid',
                                        width: 1,
                                        color: 'yellow'
                                    },
                                },
                                symbol: 'none',
                                animation: false
                            },
                            {
                                name: 'MACD',
                                type: 'bar',
                                xAxisIndex: 1,
                                yAxisIndex: 1,
                                data: resultData.macd,
                                barWidth: 1,
                                itemStyle: {
                                    normal: {
                                        color: function (params) {
                                            let colorList
                                            if (params.data >= 0) {
                                                colorList = 'red'
                                            } else {
                                                colorList = '#14d0cd'
                                            }
                                            return colorList
                                        },
                                    }
                                }
                            },
                            {
                                name: 'DIFF',
                                type: 'line',
                                xAxisIndex: 1,
                                yAxisIndex: 1,
                                data: resultData.diff,
                                smooth: true,
                                lineStyle: {
                                    normal: {
                                        opacity: 1,
                                        type: 'solid',
                                        width: 1,
                                        color: 'white'
                                    },
                                },
                                symbol: 'none',
                                animation: false,
                                markPoint: {
                                    data: resultData.bcMACDValues
                                },
                            },
                            {
                                name: 'DEA',
                                type: 'line',
                                xAxisIndex: 1,
                                yAxisIndex: 1,
                                data: resultData.dea,
                                smooth: true,
                                lineStyle: {
                                    normal: {
                                        opacity: 1,
                                        type: 'solid',
                                        width: 1,
                                        color: 'yellow'
                                    },
                                },
                                symbol: 'none',
                                animation: false
                            },
                            // 大级别MACD
                            {
                                name: 'MACD',
                                type: 'bar',
                                xAxisIndex: 2,
                                yAxisIndex: 2,
                                data: resultData.macdBigLevel,
                                barWidth: 1,
                                itemStyle: {
                                    normal: {
                                        color: function (params) {
                                            let colorList
                                            if (params.data >= 0) {
                                                colorList = 'red'
                                            } else {
                                                colorList = '#14d0cd'
                                            }
                                            return colorList
                                        },
                                    }
                                }
                            },
                            {
                                name: 'DIFF',
                                type: 'line',
                                xAxisIndex: 2,
                                yAxisIndex: 2,
                                data: resultData.diffBigLevel,
                                smooth: true,
                                lineStyle: {
                                    normal: {
                                        opacity: 1,
                                        type: 'solid',
                                        width: 1,
                                        color: 'white'
                                    },
                                },
                                symbol: 'none',
                                animation: false,
                                markPoint: {
                                    // data: resultData.bcMACDValues
                                },
                            },
                            {
                                name: 'DEA',
                                type: 'line',
                                xAxisIndex: 2,
                                yAxisIndex: 2,
                                data: resultData.deaBigLevel,
                                smooth: true,
                                lineStyle: {
                                    normal: {
                                        opacity: 1,
                                        type: 'solid',
                                        width: 1,
                                        color: 'yellow'
                                    },
                                },
                                symbol: 'none',
                                animation: false
                            },
                            {
                                name: 'Volume',
                                type: 'bar',
                                xAxisIndex: 3,
                                yAxisIndex: 3,
                                data: resultData.volume,
                                itemStyle: {
                                    normal: {
                                        color: (params) => {
                                            let colorList
                                            if (resultData.values[params.dataIndex][1] > resultData.values[params.dataIndex][0]) {
                                                colorList = 'red'
                                            } else {
                                                colorList = this.echartsConfig.downColor
                                            }
                                            return colorList
                                        },
                                    }
                                }
                            },
                            // {
                            //     name: '布林上轨',
                            //     type: 'line',
                            //     data: resultData.boll_up,
                            //     smooth: true,
                            //     lineStyle: {
                            //         normal: {
                            //             opacity: 0.6,
                            //             type: 'dotted',
                            //             width: 1,
                            //             color: '#444'
                            //         },
                            //     },
                            //     symbol: 'none',
                            //     animation: false
                            // },
                            // {
                            //     name: '布林中轨',
                            //     type: 'line',
                            //     data: resultData.boll_middle,
                            //     smooth: true,
                            //     lineStyle: {
                            //         normal: {
                            //             opacity: 0.5,
                            //             type: 'dotted',
                            //             width: 1,
                            //             color: "#888888"
                            //         },
                            //     },
                            //     symbol: 'none',
                            //     animation: false
                            // },
                            // {
                            //     name: '布林下轨',
                            //     type: 'line',
                            //     data: resultData.boll_bottom,
                            //     smooth: true,
                            //     lineStyle: {
                            //         normal: {
                            //             opacity: 0.6,
                            //             type: 'dotted',
                            //             width: 1,
                            //             color: '#444'
                            //         },
                            //     },
                            //     symbol: 'none',
                            //     animation: false
                            // },
                        ],
                        graphic: [],
                    }
                    this.$refs.myCharts.mergeOptions(option)
                }
            },
            splitData (jsonObj) {
                const stockDate = jsonObj.date
                const stockHigh = jsonObj.high
                const stockLow = jsonObj.low
                const stockOpen = jsonObj.open
                const stockClose = jsonObj.close
                const volumeData = jsonObj.volume
                const bidata = jsonObj.bidata
                const duandata = jsonObj.duandata
                const zsdata = jsonObj.zsdata
                const zsflag = jsonObj.zsflag
                //
                const macddata = jsonObj.macd
                const diffdata = jsonObj.diff
                const deadata = jsonObj.dea

                const macdBigLevel = jsonObj.macdBigLevel
                const diffBigLevel = jsonObj.diffBigLevel
                const deaBigLevel = jsonObj.deaBigLevel

                const dateBigLevel = jsonObj.dateBigLevel
                let values = []
                for (let i = 0; i < stockDate.length; i++) {
                    values.push([stockOpen[i], stockClose[i], stockLow[i], stockHigh[i]])
                }
                let biValues = []
                for (let i = 0; i < bidata.date.length; i++) {
                    biValues.push([bidata.date[i], bidata.data[i]])
                }
                let duanValues = []
                for (let i = 0; i < duandata.date.length; i++) {
                    duanValues.push([duandata.date[i], duandata.data[i]])
                }
                let zsvalues = []
                for (let i = 0; i < zsdata.length; i++) {
                    let value
                    if (zsflag[i] > 0) {
                        value = [
                            {
                                coord: zsdata[i][0],
                                itemStyle: {
                                    color: this.echartsConfig.bgColor,
                                    borderWidth: '2',
                                    borderColor: 'red',
                                    opacity: 1,
                                }
                            },
                            {
                                coord: zsdata[i][1],
                                itemStyle: {
                                    color: 'red',
                                    borderWidth: '1',
                                    borderColor: 'red',
                                    opacity: 0.2,
                                }
                            }
                        ]
                    } else {
                        value = [
                            {
                                coord: zsdata[i][0],
                                itemStyle: {
                                    color: this.echartsConfig.downColor,
                                    borderWidth: '1',
                                    borderColor: this.echartsConfig.downColor,
                                    opacity: 0.2,
                                }
                            },
                            {
                                coord: zsdata[i][1],
                                itemStyle: {
                                    color: this.echartsConfig.downColor,
                                    borderWidth: '1',
                                    borderColor: this.echartsConfig.downColor,
                                    opacity: 0.2,
                                }
                            }
                        ]
                    }
                    zsvalues.push(value)
                }

                // 买卖点
                // let mmdValues = [];
                // for (let i = 0; i < jsonObj.buyData.date.length; i++) {
                //     let value = {
                //         coord: [jsonObj.buyData.date[i], jsonObj.buyData.data[i]],
                //         value: jsonObj.buyData.value[i],
                //         symbolRotate: -180,
                //         symbol: 'pin',
                //         symbolOffset: [0, '0%'],
                //         itemStyle: {
                //             normal: {color: 'red', opacity: '0.9'}
                //         },
                //         label: {
                //             //position: ['-50%','50%'],
                //             position: 'inside',
                //             offset: [0, 10],
                //             textBorderColor: 'red',
                //             textBorderWidth: 3,
                //             color: 'white',
                //             //borderColor: 'blue',
                //             //borderWidth: 1,
                //         },
                //     };
                //     mmdValues.push(value);
                // }
                // for (let i = 0; i < jsonObj.sellData.date.length; i++) {
                //     let value = {
                //         coord: [jsonObj.sellData.date[i], jsonObj.sellData.data[i]],
                //         value: jsonObj.sellData.value[i],
                //
                //         itemStyle: {
                //             normal: {color: 'green', opacity: '0.9'}
                //         }
                //     };
                //     mmdValues.push(value);
                // }
                // let value = {
                //    name: 'lowest value',
                //    type: 'min',
                //    valueDim: 'lowest',
                //    symbolRotate: -90,
                //    symbol: 'pin',
                //    itemStyle: {
                //        normal: {
                //            color: 'white',
                //            opacity: '0.75'
                //        }
                //    },
                //    label: {
                //        position: 'inside',
                //        offset: [8, 2],
                //
                //        //textBorderWidth: 1,
                //        color: 'blue',
                //    },
                // };
                // mmdValues.push(value);
                // let value = {
                //    name: 'highest value',
                //    type: 'max',
                //    valueDim: 'highest',
                //    symbolRotate: -90,
                //    symbol: 'pin',
                //    itemStyle: {
                //        normal: {
                //            color: 'white',
                //            opacity: '0.75'
                //        }
                //    },
                //    label: {
                //        position: 'inside',
                //        offset: [8, 2],
                //        //textBorderColor: 'blue',
                //        //textBorderWidth: 1,
                //        color: 'blue',
                //    },
                // };
                // mmdValues.push(value);

                // for (let i = 0; i < jsonObj.buyBCData.date.length; i++) {
                //     let value = {
                //         coord: [jsonObj.buyBCData.date[i], jsonObj.buyBCData.data[i]],
                //         value: jsonObj.buyBCData.value[i],
                //         symbolRotate: 90,
                //         symbol: 'pin',
                //         itemStyle: {
                //             normal: {color: 'red', opacity: '0.85'}
                //         },
                //         label: {
                //             position: 'inside',
                //             offset: [-5, 2],
                //             textBorderColor: 'red',
                //             textBorderWidth: 2,
                //             color: 'white',
                //         },
                //     };
                //     mmdValues.push(value);
                // }
                // for (let i = 0; i < jsonObj.sellBCData.date.length; i++) {
                //     let value = {
                //         coord: [jsonObj.sellBCData.date[i], jsonObj.sellBCData.data[i]],
                //         value: jsonObj.sellBCData.value[i],
                //         symbolRotate: 90,
                //         symbol: 'pin',
                //         itemStyle: {
                //             normal: {color: 'green', opacity: '0.85'}
                //         },
                //         label: {
                //             position: 'inside',
                //             offset: [-5, 2],
                //             textBorderColor: 'red',
                //             textBorderWidth: 2,
                //             color: 'white',
                //         },
                //     };
                //     mmdValues.push(value);
                // }
                //
                let bcMACDValues = []
                for (let i = 0; i < jsonObj.buyMACDBCData.date.length; i++) {
                    let value = {
                        coord: [jsonObj.buyMACDBCData.date[i], jsonObj.buyMACDBCData.data[i]],
                        value: jsonObj.buyMACDBCData.value[i],
                        symbolRotate: -180,
                        symbol: 'pin',
                        itemStyle: {
                            normal: {color: 'red'}
                        },
                        label: {
                            position: 'inside',
                            offset: [0, 10],
                            textBorderColor: 'red',
                            textBorderWidth: 2,
                            color: 'white',
                        },
                    }
                    bcMACDValues.push(value)
                }
                for (let i = 0; i < jsonObj.sellMACDBCData.date.length; i++) {
                    let value = {
                        coord: [jsonObj.sellMACDBCData.date[i], jsonObj.sellMACDBCData.data[i]],
                        value: jsonObj.sellMACDBCData.value[i],
                        symbolRotate: 0,
                        symbol: 'pin',
                        itemStyle: {
                            normal: {color: 'green'}
                        }
                    }
                    bcMACDValues.push(value)
                }
                return {
                    time: stockDate,
                    values: values,
                    volume: volumeData,
                    biValues: biValues,
                    duanValues: duanValues,
                    zsvalues: zsvalues,
                    zsflag: zsflag,
                    macd: macddata,
                    diff: diffdata,
                    dea: deadata,
                    macdBigLevel: macdBigLevel,
                    diffBigLevel: diffBigLevel,
                    deaBigLevel: deaBigLevel,
                    timeBigLevel: dateBigLevel,
                    // boll_up: boll_up,
                    // boll_middle: boll_middle,
                    // boll_bottom: boll_bottom,
                    // info: info,
                    // isTradeTime: isTradeTime,
                    // basicInfo: basicInfo,
                    // concept: concept,
                    // mmdValues: mmdValues,
                    bcMACDValues: bcMACDValues,
                    // markLineData: markLineData,
                }
            },
            calculateMA (resultData, dayCount) {
                let result = []
                for (let i = 0, len = resultData.values.length; i < len; i++) {
                    if (i < dayCount) {
                        result.push('-')
                        continue
                    }
                    let sum = 0
                    for (let j = 0; j < dayCount; j++) {
                        sum += resultData.values[i - j][1]
                    }
                    result.push((sum / dayCount).toFixed(5))
                }
                return result
            }
        }
    }
</script>
<style lang="stylus">
    @import "../style/main.styl";
</style>
