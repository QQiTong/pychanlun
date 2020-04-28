// import echarts from 'echarts'
import {futureApi} from '@/api/futureApi'
import {stockApi} from '@/api/stockApi'
import CommonTool from '@/tool/CommonTool'
import KlineHeader from "../KlineHeader"
// import 'echarts/lib/chart/candlestick'
// import 'echarts/lib/chart/line'
// import 'echarts/lib/chart/bar'
// import 'echarts/lib/component/dataZoom'
// import 'echarts/lib/component/toolbox'
// import 'echarts/lib/component/tooltip'
// import 'echarts/lib/component/markPoint'
// import 'echarts/lib/component/markLine'
// import 'echarts/lib/component/markArea'
// import 'echarts/lib/component/legend'
// import 'echarts/lib/component/title'
// import { Button, Select } from 'element-ui'

export default {
    components: {
        'KlineHeader': KlineHeader
    },
    data() {
        return {
            showPeriodList: false,
            // 防重复请求
            requestFlag: true,
            // 控制加载动画是否第一次请求
            firstFlag: [true, true, true, true, true, true, true],
            // 大图
            myChart: null,
            // 多周期图
            myChart1: null,
            myChart3: null,
            myChart5: null,
            myChart15: null,
            myChart30: null,
            myChart60: null,
            myChart240: null,

            echartsConfig: {

                bgColor: '#202529',
                upColor: 'red',
                upBorderColor: 'red',
                downColor: '#14d0cd',
                downBorderColor: '#14d0cd',

                higherUpColor: 'purple',
                higherDownColor: 'green',

                higherHigherUpColor: 'pink',
                higherHigherDownColor: 'blue',

                higherColor: '#14d0cd',
                higherHigherColor: 'green',
                dynamicOpertionColor: 'yellow',
                currentPriceColor: '#FFCDD2',
                macdUpLastValue: Number.MIN_SAFE_INTEGER,
                macdDownLastValue: Number.MAX_SAFE_INTEGER,
                macdUpDarkColor: '#EF5350',
                macdUpLightColor: '#FFCDD2',
                macdDownDarkColor: '#26A69A',
                macdDownLightColor: '#B2DFDB',
                loadingOption: {
                    text: '让子弹飞一会...',
                    maskColor: '#0B0E11',
                    textColor: 'white',
                    color: '#FFCC08'
                },
                // 多周期显示不下,需要配置
                multiPeriodGrid: [{
                    left: '0%',
                    right: '18%',
                    height: '85%',
                    top: 50
                },
                    {
                        left: '0%',
                        right: '18%',
                        top: '82%',
                        height: '20%',
                    },

                ],
                klineBigGrid: [{
                    left: '0%',
                    right: '5%',
                    height: '90%',
                    top: 50
                },
                    {
                        left: '0%',
                        right: '5%',
                        top: '85%',
                        height: '20%',
                    },
                ],
            },
            // 品种
            symbol: 'RB2005',
            period: '',
            // 1 reload 2 update,
            reloadOrUpdate: 'reload',
            dataTitle: '主标题',
            dataSubTitle: '副标题',
            periodIcons: [
                require('../../assets/img/icon_1min.png'),
                require('../../assets/img/icon_3min.png'),
                require('../../assets/img/icon_5min.png'),
                require('../../assets/img/icon_15min.png'),
                require('../../assets/img/icon_30min.png'),
                require('../../assets/img/icon_1h.png'),
                require('../../assets/img/icon_4h.png'),
                require('../../assets/img/icon_1d.png'),
                require('../../assets/img/icon_1w.png'),
                require('../../assets/img/icon_refresh.svg'),
                require('../../assets/img/big-kline.png')
            ],

            futureSymbolList: [],
            futureSymbolMap: {},
            timer: null,
            // 不同期货公司提高的点数不一样 ,华安是在基础上加1%
            marginLevelCompany: 0.01,
            marginPrice: 0, // 每手需要的保证金


            currentMarginRate: null,
            marginLevel: 1,
            // 合约乘数
            contractMultiplier: 1,
            // 账户总额
            account: 0,
            // 期货账户总额
            futureAccount: this.$futureAccount,
            globalFutureAccount: this.$globalFutureAccount,
            // 数字货币账户总额
            digitCoinAccount: this.$digitCoinAccount,
            // 开仓价格
            openPrice: null,
            // 止损价格
            stopPrice: null,
            // 开仓手数
            maxOrderCount: null,
            // 资金使用率
            accountUseRate: null,
            // 最大资金使用率
            maxAccountUseRate: 0.1,
            // 止损系数
            stopRate: 0.01,
            // 数字货币手续费 20倍杠杆 双向 0.05%*2
            digitCoinFee: 0.001,
            // okex 开仓起始杠杆
            digitCoinLevel: this.$digitCoinLevel,
            // 1手需要的保证金
            perOrderMargin: 0,
            // 1手止损金额
            perOrderStopMoney: 0,
            // 1手止损百分比
            perOrderStopRate: 0,
            // 总保证金
            totalOrderMargin: 0,
            // 总止损额
            totalOrderStopMoney: 0,

            // 动态止盈价格(动态止盈部分手数使剩下的止损也不亏钱)
            dynamicWinPrice: null,
            // 动态止盈手数
            dynamicWinCount: 0,
            // end仓位管理计算
            // 结束日期
            endDate: CommonTool.dateFormat('yyyy-MM-dd'),
            // 选中的品种
            selectedSymbol: '',
            // 输入的交割过的期货品种 或者 股票品种
            inputSymbol: '',
            periodList: ['1m', '3m', '5m', '15m', '30m', '60m', '240m'],
            // 是否指显示当前持仓的开平动止
            isPosition: false,
            // 当前品种持仓信息
            currentPosition: null,
            positionStatus: 'holding',
            positionDirection: '',
            dynamicDirectionMap: {'long': '多', 'short': '空', 'close': '平'},
            currentInfo: null,
            // 数字货币 和外盘 将240m 替换成1m
            isShow1Min: false,
            futureConfig: {},
            symbolInfo: null,
            show1MinSymbol: ['BTC'],
            globalFutureSymbol: ['CL', 'GC', 'SI', 'CT', 'ZS', 'ZM', 'ZL', 'NID', 'CP', 'YM', 'CN'],
            //    快速计算开仓手数
            quickCalc: {
                openPrice: 0,
                stopPrice: 0,
                count: 0,
                stopRate: 0,
                perOrderStopMoney: 0
            }
        }
    },
    beforeMount() {
        this.symbol = this.getParams('symbol')
        if (this.show1MinSymbol.indexOf(this.symbol) !== -1) {
            this.isShow1Min = true
        } else {
            this.isShow1Min = false
        }
    },
    mounted() {
        // 不共用symbol对象, symbol是双向绑定的
        this.inputSymbol = JSON.parse(JSON.stringify(this.symbol))
        this.period = this.getParams('period')
        this.isPosition = this.getParams('isPosition')
        this.endDate = this.getParams('endDate')
        if (!this.endDate) {
            const today = new Date();
            this.endDate = CommonTool.parseTime(today.getTime(), '{y}-{m}-{d}')
        }

        if (this.isPosition === 'true') {
            this.positionPeriod = this.getParams('positionPeriod')
            this.positionDirection = this.getParams('positionDirection')
            this.positionStatus = this.getParams('positionStatus')
            this.positionDirection = this.getParams('positionDirection')
            if (this.symbol.indexOf('sz') !== -1 || this.symbol.indexOf('sh') !== -1) {
                this.getStockPosition()
            } else {
                this.getFutruePosition()
            }
        }
        this.initEcharts()
        // 取出本地缓存
        let futureConfig = window.localStorage.getItem('futureConfig')
        // 本地缓存有合约配置数据
        if (futureConfig != null) {
            this.futureConfig = JSON.parse(futureConfig)
            this.requestSymbolData()
        } else {
            // 新设备 直接进入大图页面 先获取合约配置数据

            this.getFutureConfig()
        }

    },
    beforeDestroy() {
        clearTimeout(this.timer)
    },
    methods: {
        quickSwitchDay(type) {
            let tempDate = this.endDate.replace(/-/g, '/')
            let date = new Date(tempDate)
            let preDay = date.getTime() - 3600 * 1000 * 24
            let nextDay = date.getTime() + 3600 * 1000 * 24
            if (type === 'pre') {
                this.endDate = CommonTool.parseTime(preDay, '{y}-{m}-{d}')
            } else {
                this.endDate = CommonTool.parseTime(nextDay, '{y}-{m}-{d}')
            }
            this.submitSymbol(this.symbol)
        },
        getFutruePosition() {
            // let period = 'all'
            // if (this.period !== "") {
            //     period = this.period
            // }
            futureApi.getPosition(this.symbol, this.positionPeriod, this.positionStatus, this.positionDirection).then(res => {
                this.currentPosition = res
                console.log('获取当前品种持仓:', res)
            }).catch((error) => {
                console.log('获取当前品种持仓失败:', error)
            })
        },
        getStockPosition() {
            let period = 'all'
            // if (this.period !== "") {
            //     period = this.period
            // }
            stockApi.getPosition(this.symbol, period, this.positionStatus).then(res => {
                this.currentPosition = res
                console.log('获取当前品种持仓:', res)
            }).catch(() => {
                console.log('获取当前品种持仓失败:', error)
            })
        },
        initEcharts() {
            //  大图只显示选中的k线图
            if (this.period !== '') {
                // this.endDate = this.getParams('endDate')
                this.myChart = this.$echarts.init(document.getElementById('main'))
                this.chartssize(document.getElementById('mainParent'),
                    document.getElementById('main'))
                this.myChart.resize()
                window.addEventListener('resize', () => {
                    this.myChart.resize()
                })
            } else {
                this.myChart3 = this.$echarts.init(document.getElementById('main3'))
                this.myChart5 = this.$echarts.init(document.getElementById('main5'))
                this.myChart15 = this.$echarts.init(document.getElementById('main15'))
                this.myChart30 = this.$echarts.init(document.getElementById('main30'))
                this.myChart60 = this.$echarts.init(document.getElementById('main60'))
                if (this.isShow1Min) {
                    this.myChart1 = this.$echarts.init(document.getElementById('main1'))
                    this.chartssize(document.getElementById('main1Parent'), document.getElementById('main1'))
                    this.myChart1.resize()
                } else {
                    this.myChart240 = this.$echarts.init(document.getElementById('main240'))
                    this.chartssize(document.getElementById('main240Parent'), document.getElementById('main240'))
                    this.myChart240.resize()
                }
                this.chartssize(document.getElementById('main3Parent'), document.getElementById('main3'))
                this.chartssize(document.getElementById('main15Parent'), document.getElementById('main15'))
                this.chartssize(document.getElementById('main60Parent'), document.getElementById('main60'))
                this.chartssize(document.getElementById('main5Parent'), document.getElementById('main5'))
                this.chartssize(document.getElementById('main30Parent'), document.getElementById('main30'))
                this.myChart3.resize()
                this.myChart5.resize()
                this.myChart15.resize()
                this.myChart30.resize()
                this.myChart60.resize()
                window.addEventListener('resize', () => {
                    this.myChart3.resize()
                    this.myChart5.resize()
                    this.myChart15.resize()
                    this.myChart30.resize()
                    this.myChart60.resize()
                    if (this.isShow1Min) {
                        this.myChart1.resize()
                    } else {
                        this.myChart240.resize()
                    }
                })
            }
        },
        // 计算echarts 高度
        chartssize(container, charts) {
            function getStyle(el, name) {
                if (window.getComputedStyle) {
                    return window.getComputedStyle(el, null)
                } else {
                    return el.currentStyle
                }
            }

            let wi = getStyle(container, 'width').width
            let hi = getStyle(container, 'height').height
            charts.style.height = hi
        },
        replaceParamVal(paramName, replaceWith) {
            let oUrl = window.location.href.toString()
            // eslint-disable-next-line no-eval
            let re = eval('/(' + paramName + '=)([^&]*)/gi')
            let nUrl = oUrl.replace(re, paramName + '=' + replaceWith)
            this.location = nUrl
            // window.location.href = nUrl
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
        },
        jumpToMultiPeriod() {
            if (this.isPosition === 'true') {
                this.$router.push({
                    path: '/multi-period',
                    query: {
                        symbol: this.symbol,
                        isPosition: 'true',
                        endDate: this.endDate
                    }
                })
            } else {
                this.$router.push({
                    path: '/multi-period',
                    query: {
                        symbol: this.symbol,
                        endDate: this.endDate
                    }
                })
            }
        },

        jumpToKlineBig(period) {
            if (this.isPosition === 'true') {
                this.$router.push({
                    path: '/kline-big',
                    query: {
                        symbol: this.symbol,
                        period: period,
                        isPosition: 'true',
                        endDate: this.endDate,
                        positionPeriod: this.positionPeriod,
                        positionDirection: this.positionDirection,
                        positionStatus: this.positionStatus,
                    }
                })
            } else {
                this.$router.push({
                    path: '/kline-big',
                    query: {
                        symbol: this.symbol,
                        period: period,
                        endDate: this.endDate
                    }
                })
            }
        },

        jumpToControl(type) {
            console.log('type', type)
            if (type === 'futures') {
                this.$router.replace('/futures-control')
            } else {
                this.$router.replace('/stock-control')
            }
        },
        submitSymbol(val) {
            this.inputSymbol = val
            if (val !== '') {
                this.symbol = this.inputSymbol.indexOf('sz') === -1 && this.inputSymbol.indexOf('sh') ? this.inputSymbol.toUpperCase() : this.inputSymbol
            } else {
                alert('请输入品种')
                return
            }
            this.processMargin()
            // 切换symbol 重置第一次请求标志
            // 一个大图+ 6个小图
            this.firstFlag = [true, true, true, true, true, true, true]
            this.switchSymbol(this.symbol, 'reload')
            // this.replaceParamVal("symbol",this.symbol)
        },
        // 请求数据
        requestSymbolData() {
            let that = this
            this.switchSymbol(this.symbol, 'reload')
            // 开启轮询
            that.timer = setInterval(() => {
                if (that.requestFlag) {
                    that.switchSymbol(that.symbol, 'update')
                } else {
                    // console.log('wait...')
                }
            }, 10000)
        },
        processMargin() {
            // 获取当前品种的合约 保证金率
            if (this.symbol === 'BTC') {
                // BTC
                this.symbolInfo = this.futureConfig[this.symbol]
                this.currentMarginRate = this.symbolInfo.margin_rate
                this.marginLevel = 1 / this.currentMarginRate
                this.contractMultiplier = 1
            } else if (this.symbol.indexOf('sz') !== -1 || this.symbol.indexOf('sh') !== -1) {
                this.currentMarginRate = 1
                this.marginLevel = 1
                this.contractMultiplier = 1

            } else if (this.globalFutureSymbol.indexOf(this.symbol) !== -1) {
                // 外盘
                this.symbolInfo = this.futureConfig[this.symbol]
                this.currentMarginRate = this.symbolInfo.margin_rate
                this.marginLevel = Number((1 / this.currentMarginRate).toFixed(2))
                this.contractMultiplier = this.symbolInfo.contract_multiplier
            } else {
                // 内盘 期货简单代码   RB
                let simpleSymbol = this.symbol.replace(/[0-9]/g, '')
                this.symbolInfo = this.futureConfig[simpleSymbol]
                const margin_rate = this.symbolInfo.margin_rate
                this.currentMarginRate = margin_rate + this.marginLevelCompany
                this.marginLevel = Number((1 / this.currentMarginRate).toFixed(2))
                this.contractMultiplier = this.symbolInfo.contract_multiplier
            }

        },
        getFutureConfig() {
            futureApi.getFutureConfig().then(res => {
                console.log('合约配置信息:', res)
                this.futureConfig = res
                window.localStorage.setItem('symbolConfig', JSON.stringify(this.futureConfig))
                this.processMargin()
                this.requestSymbolData()
            }).catch((error) => {
                this.requestFlag = true
                console.log('获取合约配置失败:', error)
            })
        },
        switchPeriod(period) {
            // 重置加载
            this.firstFlag[0] = true
            this.period = period
            this.switchSymbol(this.symbol, 'reload')
        },
        switchSymbol(symbol, update) {
            this.symbol = symbol
            let that = this
            if (this.period !== '') {
                document.title = `${symbol}-${that.period}`
            } else {
                document.title = symbol
            }
            if (that.timer) {
                clearTimeout(that.timer)
                that.timer = setInterval(() => {
                    if (this.requestFlag) {
                        that.switchSymbol(symbol, 'update')
                    } else {
                    }
                }, 10000)
            }
            const {...query} = that.$route.query
            // 如果是大图，只请求一个周期的数据
            if (this.period !== '') {
                Object.assign(query, {symbol, period: this.period, endDate: this.endDate})
                that.$router.push({query})
                that.sendRequest(symbol, this.period, update)
            } else {
                Object.assign(query, {symbol, endDate: this.endDate})
                that.$router.push({query})
                for (let i = 0; i < 8; i++) {
                    switch (i) {
                        // case 0:
                        //     that.sendRequest(symbol, '1m', update)
                        //     break;
                        case 1:
                            that.sendRequest(symbol, '3m', update)
                            break
                        case 2:
                            that.sendRequest(symbol, '5m', update)
                            break
                        case 3:
                            that.sendRequest(symbol, '15m', update)
                            break
                        case 4:
                            that.sendRequest(symbol, '30m', update)
                            break
                        case 5:
                            that.sendRequest(symbol, '60m', update)
                            break
                        case 6:
                            if (this.isShow1Min) {
                                that.sendRequest(symbol, '1m', update)
                            } else {
                                that.sendRequest(symbol, '240m', update)
                            }
                            break
                        // case 7:
                        //     that.sendRequest(symbol, '1d', update)
                        //     break
                    }
                }
            }
        },
        sendRequest(symbol, period, update) {
            let requestData = {'symbol': symbol, 'period': period, 'endDate': this.endDate}
            this.getStockData(requestData, update)
        },
        getStockData(requestData, update) {
            this.requestFlag = false
            if (this.period !== '') {
                if (this.firstFlag[0] === true) {
                    this.myChart.showLoading(this.echartsConfig.loadingOption)
                }
            } else {
                if (this.firstFlag[1] === true) {
                    this.myChart3.showLoading(this.echartsConfig.loadingOption)
                }
                if (this.firstFlag[2] === true) {
                    this.myChart5.showLoading(this.echartsConfig.loadingOption)
                }
                if (this.firstFlag[3] === true) {
                    this.myChart15.showLoading(this.echartsConfig.loadingOption)
                }
                if (this.firstFlag[4] === true) {
                    this.myChart30.showLoading(this.echartsConfig.loadingOption)
                }
                if (this.firstFlag[5] === true) {
                    this.myChart60.showLoading(this.echartsConfig.loadingOption)
                }
                if (this.isShow1Min) {
                    if (this.firstFlag[6] === true) {
                        this.myChart1.showLoading(this.echartsConfig.loadingOption)
                    }
                } else {
                    if (this.firstFlag[6] === true) {
                        this.myChart240.showLoading(this.echartsConfig.loadingOption)
                    }
                }
            }

            futureApi.stockData(requestData).then(res => {
                // 如果之前请求的symbol 和当前的symbol不一致，直接过滤
                if (res && (res.symbol !== this.symbol || res.endDate !== this.endDate || res.period !== requestData.period)) {
                    console.log('symbol或period结束日期不一致，过滤掉之前的请求')
                    return
                }
                this.requestFlag = true
                if (this.period !== '') {
                    this.myChart.hideLoading()
                    this.firstFlag[0] = false
                } else {
                    if (requestData.period === '3m') {
                        this.myChart3.hideLoading()
                        this.firstFlag[1] = false
                    }
                    if (requestData.period === '5m') {
                        this.myChart5.hideLoading()
                        this.firstFlag[2] = false
                    }
                    if (requestData.period === '15m') {
                        this.myChart15.hideLoading()
                        this.firstFlag[3] = false
                    }
                    if (requestData.period === '30m') {
                        this.myChart30.hideLoading()
                        this.firstFlag[4] = false
                    }
                    if (requestData.period === '60m') {
                        this.myChart60.hideLoading()
                        this.firstFlag[5] = false
                    }
                    if (this.isShow1Min) {
                        if (requestData.period === '1m') {
                            this.myChart1.hideLoading()
                            this.firstFlag[6] = false
                        }
                    } else {
                        if (requestData.period === '240m') {
                            this.myChart240.hideLoading()
                            this.firstFlag[6] = false
                        }
                    }
                }
                // console.log("结果", res)
                this.draw(res, update, requestData.period)
            }).catch(() => {
                this.requestFlag = true
            })
        },

        draw(stockJsonData, update, period) {
            let that = this
            let zoomStart = 55
            const resultData = this.splitData(stockJsonData, period)
            let dataTitle = that.symbol + '  ' + period
            let subText = '杠杆: ' + this.marginLevel + ' 保证金: ' + this.marginPrice + ' 乘数: ' + this.contractMultiplier +
                this.currentInfo
            let currentChart
            // if (period === '1m') {
            //     currentChart = myChart1
            // } else
            //
            if (this.period !== '') {
                currentChart = this.myChart
            } else {
                if (period === '3m') {
                    currentChart = this.myChart3
                } else if (period === '5m') {
                    currentChart = this.myChart5
                } else if (period === '15m') {
                    currentChart = this.myChart15
                } else if (period === '30m') {
                    currentChart = this.myChart30
                } else if (period === '60m') {
                    currentChart = this.myChart60
                } else {
                    if (period === '1m') {
                        currentChart = this.myChart1
                    } else {
                        currentChart = this.myChart240
                    }
                }
            }
            // else if (period === '1d') {
            //     currentChart = myChart1d
            // }
            let option
            if (update === 'update') {
                // console.log('更新', period)
                option = that.refreshOption(currentChart, resultData)
            } else {
                // console.log('重载', period)
                option = {
                    animation: false,
                    backgroundColor: this.echartsConfig.bgColor,
                    title: {
                        text: dataTitle,
                        subtext: subText,
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
                    axisPointer: {
                        link: {xAxisIndex: 'all'},
                    },

                    toolbox: {
                        orient: 'horizontal',
                        itemSize: 25,
                        itemGap: 8,
                        top: 16,
                        right: '3%',
                        feature: {
                            myLevel1: {
                                show: true,
                                title: '放大',
                                icon: 'image://' + this.periodIcons[10],
                                onclick: function () {
                                    that.jumpToKlineBig(period)
                                }
                            },
                            //         myLevel3: {
                            //             show: true,
                            //             title: '3分钟',
                            //             icon: 'image://' + this.periodIcons[1],
                            //             onclick: () => {
                            //                 this.period = '3min'
                            //                 this.reloadOrUpdate = 1
                            //                 this.getStockData()
                            //             }
                            //         },
                            //         myLevel5: {
                            //             show: true,
                            //             title: '5分钟',
                            //             icon: 'image://' + this.periodIcons[2],
                            //             onclick: () => {
                            //                 this.period = '5min'
                            //                 this.reloadOrUpdate = 1
                            //                 this.getStockData()
                            //             }
                            //         },
                            //         myLevel15: {
                            //             show: true,
                            //             title: '15分钟',
                            //             icon: 'image://' + this.periodIcons[3],
                            //             onclick: () => {
                            //                 this.period = '15min'
                            //                 this.reloadOrUpdate = 1
                            //                 this.getStockData()
                            //             }
                            //         },
                            //         myLevel30: {
                            //             show: true,
                            //             title: '30分钟',
                            //             icon: 'image://' + this.periodIcons[4],
                            //             onclick: () => {
                            //                 this.period = '30min'
                            //                 this.reloadOrUpdate = 1
                            //                 this.getStockData()
                            //             }
                            //         },
                            //         myLevel60: {
                            //             show: true,
                            //             title: '60分钟',
                            //             icon: 'image://' + this.periodIcons[5],
                            //             onclick: () => {
                            //                 this.period = '60min'
                            //                 this.reloadOrUpdate = 1
                            //                 this.getStockData()
                            //             }
                            //         },
                            //         myLevel240: {
                            //             show: true,
                            //             title: '240分钟',
                            //             icon: 'image://' + this.periodIcons[6],
                            //             onclick: () => {
                            //                 this.period = '4hour'
                            //                 this.reloadOrUpdate = 1
                            //                 this.getStockData()
                            //             }
                            //         },
                            //         myLevelDay: {
                            //             show: true,
                            //             title: '日',
                            //             icon: 'image://' + this.periodIcons[7],
                            //             background: '#555',
                            //             onclick: () => {
                            //                 this.period = '1day'
                            //                 this.reloadOrUpdate = 1
                            //                 this.getStockData()
                            //             }
                            //         },
                            //         myLevelWeek: {
                            //             show: true,
                            //             title: '周',
                            //             icon: 'image://' + this.periodIcons[8],
                            //             background: '#555',
                            //             onclick: () => {
                            //                 this.period = '1week'
                            //                 this.reloadOrUpdate = 1
                            //                 this.getStockData()
                            //             }
                            //         },
                            //         myAutoRefresh: {
                            //             type: 'jpeg', // png
                            //             // name: resultData.info
                            //             background: '#555',
                            //             icon: 'image://' + this.periodIcons[9],
                            //             title: '刷新',
                            //             onclick: () => {
                            //                 this.reloadOrUpdate = 2
                            //                 this.getStockData()
                            //             }
                            //         },
                            //         // saveAsImage: {
                            //         //     type: 'jpeg',//png
                            //         //     name: dataTitle + '自动画线',
                            //         //     backgroundColor: '#fff',
                            //         //     title: '保存图片',
                            //         //     show: false
                            //         // },
                        },
                    },
                    color: ['yellow', 'green', 'blue', 'white', 'white', 'red' /* 'white', 'white', 'white' */],
                    legend: {
                        data: ['笔', '段', '高级别段', 'MA5', 'MA10', 'MA20', 'MA30', 'MA60', /* '布林上轨', '布林中轨', '布林下轨' */],

                        selected: {
                            '笔': true,
                            '段': true,
                            '高级别段': true,
                            'MA5': false,
                            'MA10': false,
                            'MA20': false,
                            'MA30': false,
                            'MA60': false,
                            // 'markline': true
                        },
                        top: 10,
                        textStyle: {
                            color: 'white'
                        }
                    },
                    grid: [
                        {// 直角坐标系
                            left: '0%',
                            right: '18%',
                            height: '75%',
                            top: 50,
                        },
                        {
                            top: '65%',
                            height: '20%',
                            left: '0%',
                            right: '10%',
                        },
                        // {
                        //     top: '80%',
                        //     height: '15%',
                        //     left: '0%',
                        //     right: '10%',
                        // },
                        // {
                        //     top: '90%',
                        //     height: '5%',
                        //     left: '3.2%',
                        //     right: '3.35%',
                        // }
                    ],
                    xAxis: [
                        {
                            type: 'category',
                            data: resultData.date,
                            scale: true,
                            boundaryGap: false,
                            splitLine: {show: false},
                            splitNumber: 20,
                            min: 'dataMin',
                            max: 'dataMax',
                            axisLabel: {
                                show: true
                            },
                            axisLine: {onZero: true, lineStyle: {color: '#8392A5'}},
                            axisPointer: {
                                label: {
                                    // formatter: function (params) {
                                    //     let seriesValue = (params.seriesData[0] || {}).value;
                                    //     return params.value
                                    //         + (seriesValue != null
                                    //                 ? '\n' + echarts.format.addCommas(seriesValue)
                                    //                 : ''
                                    //         );
                                    // }
                                    show: false
                                }
                            }
                        },
                        // {
                        //     type: 'category',
                        //     gridIndex: 1,
                        //     data: resultData.date,
                        //     axisTick: {
                        //         show: false
                        //     },
                        //     axisLabel: {
                        //         show: true
                        //     },
                        //     axisLine: {lineStyle: {color: '#8392A5'}},
                        //     axisPointer: {
                        //         label: {
                        //             show: false
                        //         }
                        //     }
                        // },
                        // {
                        //     type: 'category',
                        //     gridIndex: 2,
                        //     data: resultData.timeBigLevel,
                        //     axisTick: {
                        //         show: false
                        //     },
                        //     axisLabel: {
                        //         show: false
                        //     },
                        //     // axisLine: {lineStyle: {color: '#8392A5'}}
                        // },
                        // {
                        //     type: 'category',
                        //     gridIndex: 3,
                        //     data: resultData.date,
                        //     axisTick: {
                        //         show: false
                        //     },
                        //     axisLabel: {
                        //         show: false
                        //     },
                        //     axisLine: {lineStyle: {color: '#8392A5'}}
                        // }
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
                                    color: this.echartsConfig.bgColor
                                }
                            },
                            axisLine: {lineStyle: {color: this.echartsConfig.bgColor}},
                        },
                        // {
                        //     gridIndex: 1,
                        //     splitNumber: 2,
                        //     axisTick: {
                        //         show: false
                        //     },
                        //     splitLine: {
                        //         show: false
                        //     },
                        //     axisLabel: {
                        //         show: true
                        //     },
                        //     axisLine: {onZero: true, lineStyle: {color: '#8392A5'}},
                        // },
                        // 成交量
                        // {
                        //     gridIndex: 3,
                        //     splitNumber: 1,
                        //     axisLine: {
                        //         onZero: false
                        //     },
                        //     axisTick: {
                        //         show: false
                        //     },
                        //     splitLine: {
                        //         show: false
                        //     },
                        //     axisLabel: {
                        //         show: false
                        //     },
                        //     axisLine: {lineStyle: {color: '#8392A5'}},
                        // },
                    ],
                    dataZoom: [

                        {
                            type: 'inside',
                            xAxisIndex: [0, 0],
                            start: 55,
                            end: 100,
                            minSpan: 10,
                        },
                        // {
                        //     type: 'inside',
                        //     xAxisIndex: [0, 1],
                        //     start: 55,
                        //     end: 100,
                        //     minSpan: 10,
                        // },
                        // {
                        //     type: 'inside',
                        //     xAxisIndex: [0, 1],
                        //     start: zoomStart,
                        //     end: 100,
                        //     minSpan: 10,
                        // },
                        // {
                        //     xAxisIndex: [0, 1, 2],
                        //     type: 'slider',
                        //     start: zoomStart,
                        //     end: 100,
                        //     top: '95%',
                        //     minSpan: 10,
                        //     textStyle: {
                        //         color: '#8392A5'
                        //     },
                        //     dataBackground: {
                        //         areaStyle: {
                        //             color: '#8392A5'
                        //         },
                        //         lineStyle: {
                        //             opacity: 0.8,
                        //             color: '#8392A5'
                        //         }
                        //     },
                        //     handleStyle: {
                        //         color: '#fff',
                        //         shadowBlur: 3,
                        //         shadowColor: 'rgba(0, 0, 0, 0.6)',
                        //         shadowOffsetX: 2,
                        //         shadowOffsetY: 2
                        //     }
                        //
                        // }
                    ],
                    series: [
                        // index 0
                        {
                            name: 'K线图',
                            type: 'k',
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
                            markPoint: {
                                data: resultData.huilaValues,
                                animation: false
                            },
                            markArea: {
                                silent: true,
                                data: resultData.zsvalues,
                            },
                            markLine: {
                                silent: true,
                                data: resultData.markLineData,
                                symbol: 'circle',
                                symbolSize: 1,
                            }
                        },
                        // index 1
                        {
                            name: '笔',
                            type: 'line',
                            z: 1,
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
                        // index 2
                        {
                            name: '段',
                            type: 'line',
                            z: 1,
                            data: resultData.duanValues,
                            lineStyle: {
                                normal: {
                                    opacity: 1,
                                    type: 'solid',
                                    width: 2,
                                    color: 'green'
                                },
                            },
                            markPoint: {
                                data: resultData.duanPriceValues
                            },
                            symbol: 'none',
                            animation: false
                        },
                        // index 3
                        {
                            name: '高级别段',
                            type: 'line',
                            z: 1,
                            data: resultData.higherDuanValues,
                            lineStyle: {
                                normal: {
                                    opacity: 1,
                                    type: 'solid',
                                    width: 2,
                                    color: 'blue'
                                },
                            },
                            symbol: 'none',
                            animation: false
                        },
                        // index 4
                        // {
                        //     name: 'MACD',
                        //     type: 'bar',
                        //     xAxisIndex: 1,
                        //     yAxisIndex: 1,
                        //     data: resultData.macd,
                        //     barWidth: 2,
                        //     itemStyle: {
                        //         normal: {
                        //             color: function (params) {
                        //                 let colorList
                        //                 if (params.data >= 0) {
                        //                     if (params.data >= that.echartsConfig.macdUpLastValue) {
                        //                         colorList = that.echartsConfig.macdUpDarkColor
                        //                     } else {
                        //                         colorList = that.echartsConfig.macdUpLightColor
                        //                     }
                        //                     that.echartsConfig.macdUpLastValue = params.data
                        //                 } else {
                        //                     if (params.data <= that.echartsConfig.macdDownLastValue) {
                        //                         colorList = that.echartsConfig.macdDownDarkColor
                        //                     } else {
                        //                         colorList = that.echartsConfig.macdDownLightColor
                        //                     }
                        //                     that.echartsConfig.macdDownLastValue = params.data
                        //                 }
                        //                 return colorList
                        //             },
                        //         }
                        //     }
                        // },
                        // index 5

                        // {
                        //     name: 'DIFF',
                        //     type: 'line',
                        //     xAxisIndex: 1,
                        //     yAxisIndex: 1,
                        //     data: resultData.diff,
                        //     smooth: true,
                        //     lineStyle: {
                        //         normal: {
                        //             opacity: 1,
                        //             type: 'solid',
                        //             width: 1,
                        //             color: 'white'
                        //         },
                        //     },
                        //     symbol: 'none',
                        //     animation: false,
                        //     markPoint: {
                        //         data: resultData.bcMACDValues
                        //     },
                        // },
                        // index 6

                        // {
                        //     name: 'DEA',
                        //     type: 'line',
                        //     xAxisIndex: 1,
                        //     yAxisIndex: 1,
                        //     data: resultData.dea,
                        //     smooth: true,
                        //     lineStyle: {
                        //         normal: {
                        //             opacity: 1,
                        //             type: 'solid',
                        //             width: 1,
                        //             color: 'yellow'
                        //         },
                        //     },
                        //     symbol: 'none',
                        //     animation: false,
                        //     // markPoint: {
                        //     //     data: resultData.macdAreaValues
                        //     // },
                        // },
                        // index 4
                        // {
                        //     name: 'MA5',
                        //     type: 'line',
                        //     data: that.calculateMA(resultData, 5),
                        //     smooth: true,
                        //     lineStyle: {
                        //         normal: {
                        //             opacity: 0.9,
                        //             type: 'solid',
                        //             width: 2,
                        //             color: "white"
                        //         },
                        //     },
                        //     symbol: 'none',
                        //     animation: false
                        // },
                        // // //index 5
                        // {
                        //     name: 'MA10',
                        //     type: 'line',
                        //     data: that.calculateMA(resultData, 10),
                        //     smooth: true,
                        //     lineStyle: {
                        //         normal: {
                        //             opacity: 0.9,
                        //             type: 'solid',
                        //             width: 2,
                        //             color: "yellow"
                        //         },
                        //     },
                        //     symbol: 'none',
                        //     animation: false
                        // },
                        // // index 6
                        // {
                        //     name: 'MA20',
                        //     type: 'line',
                        //     data: that.calculateMA(resultData, 20),
                        //     smooth: true,
                        //     lineStyle: {
                        //         normal: {
                        //             opacity: 0.9,
                        //             type: 'solid',
                        //             width: 2,
                        //             color: "green"
                        //         },
                        //     },
                        //     symbol: 'none',
                        //     animation: false
                        // },
                        // // index 7
                        // {
                        //     name: 'MA30',
                        //     type: 'line',
                        //     data: that.calculateMA(resultData, 30),
                        //     smooth: true,
                        //     lineStyle: {
                        //         normal: {
                        //             opacity: 0.9,
                        //             type: 'solid',
                        //             width: 2,
                        //             color: "red"
                        //         },
                        //     },
                        //     symbol: 'none',
                        //     animation: false
                        // },
                        //
                        // // index 8
                        // {
                        //     name: 'MA60',
                        //     type: 'line',
                        //     data: that.calculateMA(resultData, 60),
                        //     smooth: true,
                        //     lineStyle: {
                        //         normal: {
                        //             opacity: 1,
                        //             type: 'solid',
                        //             width: 2,
                        //             color: "purple"
                        //         },
                        //     },
                        //     symbol: 'none',
                        //     animation: false
                        // }
                    ],
                    graphic: [],
                }
            }
            // console.log("option", currentChart, option)
            //  大图隐藏放大按钮
            if (this.period !== '') {
                option.toolbox.feature = {}
                option.grid = this.echartsConfig.klineBigGrid
            } else {
                option.grid = this.echartsConfig.multiPeriodGrid
            }
            currentChart.setOption(option)
        },
        refreshOption(chart, resultData) {
            let option = chart.getOption()
            option.series[0].data = resultData.values
            option.xAxis[0].data = resultData.date
            // option.xAxis[1].data = resultData.date
            option.series[0].markArea.data = resultData.zsvalues
            option.series[0].markLine.data = resultData.markLineData
            option.series[0].markPoint.data = resultData.huilaValues
            option.series[1].data = resultData.biValues
            option.series[2].data = resultData.duanValues
            option.series[2].markPoint.data = resultData.duanPriceValues
            option.series[3].data = resultData.higherDuanValues
            // option.series[4].data = resultData.macd
            // option.series[5].data = resultData.diff
            // option.series[5].markPoint.data = resultData.bcMACDValues

            // option.series[6].data = resultData.dea
            // option.series[6].markPoint.data = resultData.bcMACDValues
            // option.series[4].data = this.calculateMA(resultData, 5);
            // option.series[5].data = this.calculateMA(resultData, 10);
            // option.series[6].data = this.calculateMA(resultData, 20);
            // option.series[7].data = this.calculateMA(resultData, 30);
            // option.series[8].data = this.calculateMA(resultData, 60);
            // option.series[11].data = resultData.volume;
            // console.log('更新的option', option)
            return option
        },
        splitData(jsonObj, period) {
            const stockDate = jsonObj.date
            const stockHigh = jsonObj.high
            const stockLow = jsonObj.low
            const stockOpen = jsonObj.open
            const stockClose = jsonObj.close
            const volumeData = jsonObj.volume

            const bidata = jsonObj.bidata
            const duandata = jsonObj.duandata
            const higherDuanData = jsonObj.higherDuanData

            // console.log('bidata', bidata);
            // console.log('duandata', duandata);

            const zsdata = jsonObj.zsdata
            const zsflag = jsonObj.zsflag

            const duan_zsdata = jsonObj.duan_zsdata
            const duan_zsflag = jsonObj.duan_zsflag

            const higher_duan_zsdata = jsonObj.higher_duan_zsdata
            const higher_duan_zsflag = jsonObj.higher_duan_zsflag

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
            let duanPriceValues = []
            for (let i = 0; i < duandata.date.length; i++) {
                let value = {}
                if (i > 0 && duandata.data[i] > duandata.data[i - 1]) {
                    value = {
                        coord: [duandata.date[i], duandata.data[i]],
                        value: duandata.data[i],
                        symbolRotate: 0,
                        symbolSize: 5,
                        symbol: 'circle',
                        itemStyle: {
                            normal: {color: this.echartsConfig.downColor}
                        },
                        label: {
                            position: 'inside',
                            offset: [0, -10],
                            textBorderColor: this.echartsConfig.downColor,
                            textBorderWidth: 2,
                            color: 'white',
                        },
                    }
                } else {
                    value = {
                        coord: [duandata.date[i], duandata.data[i]],
                        value: duandata.data[i],
                        symbolRotate: 0,
                        symbolSize: 5,
                        symbol: 'circle',
                        itemStyle: {
                            normal: {color: this.echartsConfig.upColor}
                        },
                        label: {
                            position: 'inside',
                            offset: [0, 10],
                            textBorderColor: this.echartsConfig.upColor,
                            textBorderWidth: 2,
                            color: 'white',
                        },
                    }
                }

                duanPriceValues.push(value)
            }

            let higherDuanValues = []
            for (let i = 0; i < higherDuanData.date.length; i++) {
                higherDuanValues.push([higherDuanData.date[i], higherDuanData.data[i]])
            }

            let zsvalues = []
            for (let i = 0; i < zsdata.length; i++) {
                let value
                if (zsflag[i] > 0) {
                    value = [
                        {
                            coord: zsdata[i][0],
                            itemStyle: {
                                color: this.echartsConfig.upColor,
                                borderWidth: '2',
                                borderColor: 'red',
                                opacity: 0.2,
                            }
                        },
                        {
                            coord: zsdata[i][1],
                            itemStyle: {
                                color: this.echartsConfig.upColor,
                                borderWidth: '1',
                                borderColor: this.echartsConfig.upColor,
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
            // 段中枢
            for (let i = 0; i < duan_zsdata.length; i++) {
                let value
                if (duan_zsflag[i] > 0) {
                    value = [
                        {
                            coord: duan_zsdata[i][0],
                            itemStyle: {
                                color: this.echartsConfig.higherUpColor,
                                borderWidth: '2',
                                borderColor: this.echartsConfig.higherUpColor,
                                opacity: 0.2,
                            }
                        },
                        {
                            coord: duan_zsdata[i][1],
                            itemStyle: {
                                color: this.echartsConfig.higherUpColor,
                                borderWidth: '1',
                                borderColor: this.echartsConfig.higherUpColor,
                                opacity: 0.2,
                            }
                        }
                    ]
                } else {
                    value = [
                        {
                            coord: duan_zsdata[i][0],
                            itemStyle: {
                                color: this.echartsConfig.higherDownColor,
                                borderWidth: '1',
                                borderColor: this.echartsConfig.higherDownColor,
                                opacity: 0.2,
                            }
                        },
                        {
                            coord: duan_zsdata[i][1],
                            itemStyle: {
                                color: this.echartsConfig.higherDownColor,
                                borderWidth: '1',
                                borderColor: this.echartsConfig.higherDownColor,
                                opacity: 0.2,
                            }
                        }
                    ]
                }
                zsvalues.push(value)
            }
            // 高级别段中枢
            for (let i = 0; i < higher_duan_zsdata.length; i++) {
                let value
                if (higher_duan_zsflag[i] > 0) {
                    value = [
                        {
                            coord: higher_duan_zsdata[i][0],
                            itemStyle: {
                                color: this.echartsConfig.higherHigherUpColor,
                                borderWidth: '2',
                                borderColor: this.echartsConfig.higherHigherUpColor,
                                opacity: 0.1,
                            }
                        },
                        {
                            coord: higher_duan_zsdata[i][1],
                            itemStyle: {
                                color: this.echartsConfig.higherHigherUpColor,
                                borderWidth: '1',
                                borderColor: this.echartsConfig.higherHigherUpColor,
                                opacity: 0.1,
                            }
                        }
                    ]
                } else {
                    value = [
                        {
                            coord: higher_duan_zsdata[i][0],
                            itemStyle: {
                                color: this.echartsConfig.higherHigherDownColor,
                                borderWidth: '1',
                                borderColor: this.echartsConfig.higherHigherDownColor,
                                opacity: 0.1,
                            }
                        },
                        {
                            coord: higher_duan_zsdata[i][1],
                            itemStyle: {
                                color: this.echartsConfig.higherHigherDownColor,
                                borderWidth: '1',
                                borderColor: this.echartsConfig.higherHigherDownColor,
                                opacity: 0.1,
                            }
                        }
                    ]
                }
                zsvalues.push(value)
            }

            // 中枢拉回
            let huilaValues = []
            for (let i = 0; i < jsonObj.buy_zs_huila.date.length; i++) {
                let value = {
                    coord: [jsonObj.buy_zs_huila.date[i], jsonObj.buy_zs_huila.data[i]],
                    value: jsonObj.buy_zs_huila.data[i] + jsonObj.buy_zs_huila.tag[i],
                    symbolRotate: -90,
                    symbol: 'pin',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: this.echartsConfig.upColor, opacity: '0.9'}
                    },
                    label: {
                        // position: ['-50%','50%'],
                        position: 'inside',
                        offset: [5, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        // borderColor: 'blue',
                        // borderWidth: 1,
                    },
                }
                huilaValues.push(value)
            }
            for (let i = 0; i < jsonObj.sell_zs_huila.date.length; i++) {
                let value = {
                    coord: [jsonObj.sell_zs_huila.date[i], jsonObj.sell_zs_huila.data[i]],
                    value: jsonObj.sell_zs_huila.data[i] + jsonObj.sell_zs_huila.tag[i],
                    symbolRotate: 90,
                    symbol: 'pin',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: this.echartsConfig.downColor, opacity: '0.9'}
                    },
                    label: {
                        // position: ['-50%','50%'],
                        position: 'inside',
                        offset: [-5, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        // borderColor: 'blue',
                        // borderWidth: 1,
                    },
                }
                huilaValues.push(value)
            }
            // 大级别中枢拉回
            for (let i = 0; i < jsonObj.buy_zs_huila_higher.date.length; i++) {
                let value = {
                    coord: [jsonObj.buy_zs_huila_higher.date[i], jsonObj.buy_zs_huila_higher.data[i]],
                    value: jsonObj.buy_zs_huila_higher.data[i] + jsonObj.buy_zs_huila_higher.tag[i],
                    symbolRotate: -90,
                    symbol: 'pin',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: this.echartsConfig.higherUpColor, opacity: '0.9'}
                    },
                    label: {
                        // position: ['-50%','50%'],
                        position: 'inside',
                        offset: [5, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        // borderColor: 'blue',
                        // borderWidth: 1,
                    },
                }
                huilaValues.push(value)
            }
            for (let i = 0; i < jsonObj.sell_zs_huila_higher.date.length; i++) {
                let value = {
                    coord: [jsonObj.sell_zs_huila_higher.date[i], jsonObj.sell_zs_huila_higher.data[i]],
                    value: jsonObj.sell_zs_huila_higher.data[i] + jsonObj.sell_zs_huila_higher.tag[i],
                    symbolRotate: 90,
                    symbol: 'pin',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: this.echartsConfig.higherDownColor, opacity: '0.9'}
                    },
                    label: {
                        // position: ['-50%','50%'],
                        position: 'inside',
                        offset: [-5, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        // borderColor: 'blue',
                        // borderWidth: 1,
                    },
                }
                huilaValues.push(value)
            }
            // 中枢突破
            for (let i = 0; i < jsonObj.buy_zs_tupo.date.length; i++) {
                let value = {
                    coord: [jsonObj.buy_zs_tupo.date[i], jsonObj.buy_zs_tupo.data[i]],
                    value: jsonObj.buy_zs_tupo.data[i],
                    symbolRotate: 0,
                    symbol: 'arrow',
                    symbolSize: 30,
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: this.echartsConfig.upColor, opacity: '0.9'}
                    },
                    label: {
                        // position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        // borderColor: 'blue',
                        // borderWidth: 1,
                    },
                }
                huilaValues.push(value)
            }

            for (let i = 0; i < jsonObj.sell_zs_tupo.date.length; i++) {
                let value = {
                    coord: [jsonObj.sell_zs_tupo.date[i], jsonObj.sell_zs_tupo.data[i]],
                    value: jsonObj.sell_zs_tupo.data[i],
                    symbolRotate: 180,
                    symbolSize: 30,
                    symbol: 'arrow',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: this.echartsConfig.downColor, opacity: '0.9'}
                    },
                    label: {
                        // position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        // borderColor: 'blue',
                        // borderWidth: 1,
                    },
                }
                huilaValues.push(value)
            }
            // 大级别中枢突破
            for (let i = 0; i < jsonObj.buy_zs_tupo_higher.date.length; i++) {
                let value = {
                    coord: [jsonObj.buy_zs_tupo_higher.date[i], jsonObj.buy_zs_tupo_higher.data[i]],
                    value: jsonObj.buy_zs_tupo_higher.data[i],
                    symbolRotate: 0,
                    symbolSize: 30,
                    symbol: 'arrow',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: this.echartsConfig.higherUpColor, opacity: '0.9'}
                    },
                    label: {
                        // position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        // borderColor: 'blue',
                        // borderWidth: 1,
                    },
                }
                huilaValues.push(value)
            }
            for (let i = 0; i < jsonObj.sell_zs_tupo_higher.date.length; i++) {
                let value = {
                    coord: [jsonObj.sell_zs_tupo_higher.date[i], jsonObj.sell_zs_tupo_higher.data[i]],
                    value: jsonObj.sell_zs_tupo_higher.data[i],
                    symbolRotate: 180,
                    symbolSize: 30,
                    symbol: 'arrow',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: this.echartsConfig.higherDownColor, opacity: '0.9'}
                    },
                    label: {
                        // position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        // borderColor: 'blue',
                        // borderWidth: 1,
                    },
                }
                huilaValues.push(value)
            }
            // 3买卖V反
            for (let i = 0; i < jsonObj.buy_v_reverse.date.length; i++) {
                let value = {
                    coord: [jsonObj.buy_v_reverse.date[i], jsonObj.buy_v_reverse.data[i]],
                    value: jsonObj.buy_v_reverse.data[i],
                    symbolRotate: 0,
                    symbol: 'diamond',
                    symbolSize: 30,
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: this.echartsConfig.upColor, opacity: '0.9'}
                    },
                    label: {
                        // position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        // borderColor: 'blue',
                        // borderWidth: 1,
                    },
                }
                huilaValues.push(value)
            }

            for (let i = 0; i < jsonObj.sell_v_reverse.date.length; i++) {
                let value = {
                    coord: [jsonObj.sell_v_reverse.date[i], jsonObj.sell_v_reverse.data[i]],
                    value: jsonObj.sell_v_reverse.data[i],
                    symbolRotate: 180,
                    symbolSize: 30,
                    symbol: 'diamond',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: this.echartsConfig.downColor, opacity: '0.9'}
                    },
                    label: {
                        // position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        // borderColor: 'blue',
                        // borderWidth: 1,
                    },
                }
                huilaValues.push(value)
            }

            // 3买卖V反 大级别
            for (let i = 0; i < jsonObj.buy_v_reverse_higher.date.length; i++) {
                let value = {
                    coord: [jsonObj.buy_v_reverse_higher.date[i], jsonObj.buy_v_reverse_higher.data[i]],
                    value: jsonObj.buy_v_reverse_higher.data[i],
                    symbolRotate: 0,
                    symbol: 'diamond',
                    symbolSize: 30,
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: this.echartsConfig.higherUpColor, opacity: '0.9'}
                    },
                    label: {
                        // position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        // borderColor: 'blue',
                        // borderWidth: 1,
                    },
                }
                huilaValues.push(value)
            }

            for (let i = 0; i < jsonObj.sell_v_reverse_higher.date.length; i++) {
                let value = {
                    coord: [jsonObj.sell_v_reverse_higher.date[i], jsonObj.sell_v_reverse_higher.data[i]],
                    value: jsonObj.sell_v_reverse_higher.data[i],
                    symbolRotate: 180,
                    symbolSize: 30,
                    symbol: 'diamond',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: this.echartsConfig.higherDownColor, opacity: '0.9'}
                    },
                    label: {
                        // position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        // borderColor: 'blue',
                        // borderWidth: 1,
                    },
                }
                huilaValues.push(value)
            }

            // 线段破坏
            for (let i = 0; i < jsonObj.buy_duan_break.date.length; i++) {
                let value = {
                    coord: [jsonObj.buy_duan_break.date[i], jsonObj.buy_duan_break.data[i]],
                    value: jsonObj.buy_duan_break.data[i],
                    symbolRotate: 0,
                    symbol: 'circle',
                    symbolSize: 10,
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: this.echartsConfig.upColor, opacity: '0.9'}
                    },
                    label: {
                        // position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        // borderColor: 'blue',
                        // borderWidth: 1,
                    },
                }
                huilaValues.push(value)
            }

            for (let i = 0; i < jsonObj.sell_duan_break.date.length; i++) {
                let value = {
                    coord: [jsonObj.sell_duan_break.date[i], jsonObj.sell_duan_break.data[i]],
                    value: jsonObj.sell_duan_break.data[i],
                    symbolRotate: 180,
                    symbolSize: 10,
                    symbol: 'circle',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: this.echartsConfig.downColor, opacity: '0.9'}
                    },
                    label: {
                        // position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        // borderColor: 'blue',
                        // borderWidth: 1,
                    },
                }
                huilaValues.push(value)
            }
            // 大级别线段破坏
            for (let i = 0; i < jsonObj.buy_duan_break_higher.date.length; i++) {
                let value = {
                    coord: [jsonObj.buy_duan_break_higher.date[i], jsonObj.buy_duan_break_higher.data[i]],
                    value: jsonObj.buy_duan_break_higher.data[i],
                    symbolRotate: 0,
                    symbolSize: 10,
                    symbol: 'circle',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: this.echartsConfig.higherUpColor, opacity: '0.9'}
                    },
                    label: {
                        // position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        // borderColor: 'blue',
                        // borderWidth: 1,
                    },
                }
                huilaValues.push(value)
            }
            for (let i = 0; i < jsonObj.sell_duan_break_higher.date.length; i++) {
                let value = {
                    coord: [jsonObj.sell_duan_break_higher.date[i], jsonObj.sell_duan_break_higher.data[i]],
                    value: jsonObj.sell_duan_break_higher.data[i],
                    symbolRotate: 180,
                    symbolSize: 10,
                    symbol: 'circle',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: this.echartsConfig.higherDownColor, opacity: '0.9'}
                    },
                    label: {
                        // position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        // borderColor: 'blue',
                        // borderWidth: 1,
                    },
                }
                huilaValues.push(value)
            }
            let markLineData
            if (this.isPosition === 'true') {
                markLineData = this.getPositionMarklineData(jsonObj)
            } else {
                markLineData = this.getMarklineData(jsonObj)
            }
            // console.log("markline", markLineData)

            // let bcMACDValues = []
            // for (let i = 0; i < jsonObj.buyMACDBCData.date.length; i++) {
            //     let value = {
            //         coord: [jsonObj.buyMACDBCData.date[i], jsonObj.buyMACDBCData.diff[i]],
            //         value: jsonObj.buyMACDBCData.value[i],
            //         symbolRotate: -180,
            //         symbol: 'pin',
            //         itemStyle: {
            //             normal: {color: 'red'}
            //         },
            //         label: {
            //             position: 'inside',
            //             offset: [0, 10],
            //             textBorderColor: 'red',
            //             textBorderWidth: 2,
            //             color: 'white',
            //         },
            //     }
            //     bcMACDValues.push(value)
            // }
            // for (let i = 0; i < jsonObj.sellMACDBCData.date.length; i++) {
            //     let value = {
            //         coord: [jsonObj.sellMACDBCData.date[i], jsonObj.sellMACDBCData.diff[i]],
            //         value: jsonObj.sellMACDBCData.value[i],
            //         symbolRotate: 0,
            //         symbol: 'pin',
            //         itemStyle: {
            //             normal: {color: 'green'}
            //         }
            //     }
            //     bcMACDValues.push(value)
            // }
            //
            // const macddata = jsonObj.macd
            // const diffdata = jsonObj.diff
            // const deadata = jsonObj.dea
            // console.log('macd',macddata)
            // console.log('diffdata',diffdata)
            // console.log('deadata',deadata)
            return {
                date: stockDate,
                values: values,
                volume: volumeData,
                biValues: biValues,
                duanValues: duanValues,
                duanPriceValues: duanPriceValues,
                higherDuanValues: higherDuanValues,
                zsvalues: zsvalues,
                zsflag: zsflag,
                close: stockClose,
                markLineData: markLineData,
                huilaValues: huilaValues,
                // macd: macddata,
                // diff: diffdata,
                // dea: deadata,
                // bcMACDValues: bcMACDValues,

            }
        },
        // 通用开平动止标注数据
        getMarklineData(jsonObj) {
            let markLineData = []
            let lastBeichiType = this.getLastBeichiData(jsonObj)
            let lastBeichi = null
            // 当前价格
            this.currentPrice = jsonObj.close[jsonObj.close.length - 1]
            // 1手需要的保证金
            if (this.symbol === 'BTC') {
                this.marginPrice = (0.01 * this.currentPrice / this.marginLevel).toFixed(2)
            } else {
                // 内盘 和外盘
                this.marginPrice = (this.contractMultiplier * this.currentPrice / this.marginLevel).toFixed(2)
            }

            // console.log("最后的背驰:", period, lastBeichiType)
            if (lastBeichiType !== 0) {
                switch (lastBeichiType) {
                    // 回拉
                    case 1:
                        lastBeichi = jsonObj.buy_zs_huila
                        break
                    case 2:
                        lastBeichi = jsonObj.buy_zs_huila_higher
                        break
                    case 3:
                        lastBeichi = jsonObj.sell_zs_huila
                        break
                    case 4:
                        lastBeichi = jsonObj.sell_zs_huila_higher
                        break
                    // 线段破坏
                    case 5:
                        lastBeichi = jsonObj.buy_duan_break
                        break
                    case 6:
                        lastBeichi = jsonObj.buy_duan_break_higher
                        break
                    case 7:
                        lastBeichi = jsonObj.sell_duan_break
                        break
                    case 8:
                        lastBeichi = jsonObj.sell_duan_break_higher
                        break
                    // 突破
                    case 9:
                        lastBeichi = jsonObj.buy_zs_tupo
                        break
                    case 10:
                        lastBeichi = jsonObj.buy_zs_tupo_higher
                        break
                    case 11:
                        lastBeichi = jsonObj.sell_zs_tupo
                        break
                    case 12:
                        lastBeichi = jsonObj.sell_zs_tupo_higher
                        break
                    // V反
                    case 13:
                        lastBeichi = jsonObj.buy_v_reverse
                        break
                    case 14:
                        lastBeichi = jsonObj.buy_v_reverse_higher
                        break
                    case 15:
                        lastBeichi = jsonObj.sell_v_reverse
                        break
                    case 16:
                        lastBeichi = jsonObj.sell_v_reverse_higher
                        break
                    //背驰
                    case 17:
                        lastBeichi = jsonObj.buyMACDBCData
                        break
                    case 18:
                        lastBeichi = jsonObj.sellMACDBCData
                        break
                }
                // 背驰时的价格
                let beichiPrice = lastBeichi['data'][lastBeichi['data'].length - 1]
                // 止损价格
                let stopLosePrice = lastBeichi['stop_lose_price'][lastBeichi['stop_lose_price'].length - 1]
                // 第一次止盈价格
                let stopWinPrice = lastBeichi['stop_win_price'][lastBeichi['stop_win_price'].length - 1]
                // 第一次止盈百分比
                let stopWinPercent = 0
                // 止盈价格
                let targetPrice = 0
                // 达到2.3倍盈亏比 才能保证动止30% 止损不亏
                let diffPrice = Math.abs(beichiPrice - stopLosePrice) * 2.3
                // 当前收益百分比
                let currentPercent = ''
                // 当前收益（单位万/元）
                let currentProfit = ''
                if (lastBeichiType === 1 || lastBeichiType === 2 || lastBeichiType === 5 || lastBeichiType === 6 ||
                    lastBeichiType === 9 || lastBeichiType === 10 || lastBeichiType === 13 || lastBeichiType === 14 || lastBeichiType === 17) {
                    targetPrice = beichiPrice + diffPrice
                    currentPercent = ((this.currentPrice - beichiPrice) / beichiPrice * 100 * this.marginLevel).toFixed(2)
                    if (stopWinPrice !== 0) {
                        stopWinPercent = ((stopWinPrice - beichiPrice) / beichiPrice * 100 * this.marginLevel).toFixed(2)
                    }
                } else {
                    targetPrice = beichiPrice - diffPrice
                    currentPercent = ((beichiPrice - this.currentPrice) / beichiPrice * 100 * this.marginLevel).toFixed(2)
                    if (stopWinPrice !== 0) {
                        stopWinPercent = ((beichiPrice - stopWinPrice) / beichiPrice * 100 * this.marginLevel).toFixed(2)
                    }
                }
                let targetPercent = (Math.abs(beichiPrice - stopLosePrice) / beichiPrice * 100 * this.marginLevel).toFixed(2)
                // 准备参数
                this.openPrice = beichiPrice
                this.stopPrice = stopLosePrice
                // 当前保证金比例

                // 计算开仓手数
                this.calcAccount(this.openPrice, this.stopPrice)
                // console.log(beichiPrice, stopLosePrice, diffPrice, targetPrice)
                // 单位是万
                currentProfit = ((this.maxOrderCount * this.marginPrice * Number(currentPercent) / 100) / 10000).toFixed(2)
                // 跟据最新价格计算出来的信息
                this.currentInfo = ' 率: ' + currentPercent + '% 额: ' + currentProfit + ' 万,盈亏比:' +
                    (currentPercent / targetPercent).toFixed(1) + ' 新: ' + this.currentPrice.toFixed(2)
                let markLineCurrent = {
                    yAxis: this.currentPrice,
                    lineStyle: {
                        normal: {
                            opacity: 1,
                            type: 'dash',
                            width: 1,
                            color: 'yellow'
                        },
                    },
                    symbol: 'circle',
                    symbolSize: 1,
                    label: {
                        normal: {
                            color: this.echartsConfig.currentPriceColor,
                            formatter: '新: ' + this.currentPrice.toFixed(2)
                        },
                    },
                }
                markLineData.push(markLineCurrent)
                // 保本位
                if (beichiPrice) {
                    let markLineBeichi = {
                        yAxis: beichiPrice,
                        lineStyle: {
                            normal: {
                                opacity: 1,
                                type: 'dashed',
                                width: 1,
                                color: 'white'
                            },
                        },
                        symbol: 'circle',
                        symbolSize: 1,
                        label: {
                            normal: {
                                color: 'white',
                                formatter: '开: ' + beichiPrice.toFixed(2) + ' ' + this.maxOrderCount + ' 手',
                            },
                        },
                    }
                    markLineData.push(markLineBeichi)
                }

                // 止损位
                if (stopLosePrice) {
                    let markLineStop = {
                        yAxis: stopLosePrice,
                        lineStyle: {
                            normal: {
                                opacity: 1,
                                type: 'dashed',
                                width: 1,
                                color: this.echartsConfig.upColor
                            },
                        },
                        symbol: 'circle',
                        symbolSize: 1,
                        label: {
                            normal: {
                                color: this.echartsConfig.upColor,
                                formatter: '损: ' + stopLosePrice.toFixed(2) + '\n率: -' + targetPercent + '%',
                            },
                        },
                    }
                    markLineData.push(markLineStop)
                }
                // 兼容股票
                if (!jsonObj['fractal']) {
                    return markLineData
                }

                let higherBottomPrice = 0
                let higherHigherBottomPrice = 0
                let higherTopPrice = 0
                let higherHigherTopPrice = 0
                if (JSON.stringify(jsonObj['fractal'][0]) !== '{}' && jsonObj['fractal'][0]['direction'] === 1) {
                    higherBottomPrice = jsonObj['fractal'][0]['top_fractal']['bottom']
                    // 高级别分型线
                    let markLineFractal = {
                        yAxis: higherBottomPrice,
                        lineStyle: {
                            normal: {
                                opacity: 1,
                                type: 'dashed',
                                width: 1,
                                color: this.echartsConfig.higherColor
                            },
                        },
                        symbol: 'circle',
                        symbolSize: 1,
                        label: {
                            normal: {
                                color: this.echartsConfig.higherColor,
                                formatter: '顶: ' + jsonObj['fractal'][0]['period'] + ' ' + higherBottomPrice,
                                position: 'insideEndTop'
                            },
                        },
                    }
                    markLineData.push(markLineFractal)
                }
                if (JSON.stringify(jsonObj['fractal'][1]) !== '{}' && jsonObj['fractal'][1]['direction'] === 1) {
                    higherHigherBottomPrice = jsonObj['fractal'][1]['top_fractal']['bottom']
                    // 高高级别分型线
                    let markLineFractal = {
                        yAxis: higherHigherBottomPrice,
                        lineStyle: {
                            normal: {
                                opacity: 1,
                                type: 'dashed',
                                width: 1,
                                color: this.echartsConfig.higherHigherColor
                            },
                        },
                        symbol: 'circle',
                        symbolSize: 1,
                        label: {
                            normal: {
                                color: this.echartsConfig.higherHigherColor,
                                formatter: '顶: ' + jsonObj['fractal'][1]['period'] + ' ' + higherHigherBottomPrice,
                                position: 'insideEndTop'
                            },

                        },
                    }
                    markLineData.push(markLineFractal)
                }

                // 空单查找底分型
                if (JSON.stringify(jsonObj['fractal'][0]) !== '{}' && jsonObj['fractal'][0]['direction'] === -1) {
                    higherTopPrice = jsonObj['fractal'][0]['bottom_fractal']['top']
                    // 高级别分型线
                    let markLineFractal = {
                        yAxis: higherTopPrice,
                        lineStyle: {
                            normal: {
                                opacity: 1,
                                type: 'dashed',
                                width: 1,
                                color: this.echartsConfig.higherColor
                            },
                        },
                        symbol: 'circle',
                        symbolSize: 1,
                        label: {
                            normal: {
                                color: this.echartsConfig.higherColor,
                                formatter: '底分: ' + jsonObj['fractal'][0]['period'] + ' ' + higherTopPrice,
                                position: 'insideEndTop'
                            },

                        },
                    }
                    markLineData.push(markLineFractal)
                }
                if (JSON.stringify(jsonObj['fractal'][1]) !== '{}' && jsonObj['fractal'][1]['direction'] === -1) {
                    higherHigherTopPrice = jsonObj['fractal'][1]['bottom_fractal']['top']
                    // 高高级别分型线
                    let markLineFractal = {
                        yAxis: higherHigherTopPrice,
                        lineStyle: {
                            normal: {
                                opacity: 1,
                                type: 'dashed',
                                width: 1,
                                color: this.echartsConfig.higherHigherColor
                            },
                        },
                        symbol: 'circle',
                        symbolSize: 1,
                        label: {
                            normal: {
                                color: this.echartsConfig.higherHigherColor,
                                formatter: '底分: ' + jsonObj['fractal'][1]['period'] + ' ' + higherHigherTopPrice,
                                position: 'insideEndTop'

                            },
                        },
                    }
                    markLineData.push(markLineFractal)
                }
            }
            return markLineData
        },
        // 持仓状态下的开平动止数据
        /**
         * @param jsonObj
         */
        getPositionMarklineData(jsonObj) {
            let markLineData = []
            // 开仓价格
            let openPrice = this.currentPosition.price
            let openAmount = this.currentPosition.amount
            let direction = this.currentPosition.direction
            // 当前价格
            this.currentPrice = jsonObj.close[jsonObj.close.length - 1]
            // 合约乘数
            console.log("查bug", this.marginLevel, this.contractMultiplier, this.currentPrice)
            // 1手需要的保证金
            if (this.symbol === 'BTC') {
                this.marginPrice = (0.01 * this.currentPrice / this.marginLevel).toFixed(2)
            } else {
                // 内盘 和外盘
                this.marginPrice = (this.contractMultiplier * this.currentPrice / this.marginLevel).toFixed(2)
            }
            // 止损价格
            let stopLosePrice = this.currentPosition.stop_lose_price
            // 当前盈利百分比
            let currentPercent = ''
            if (direction === 'long') {
                currentPercent = ((this.currentPrice - openPrice) / openPrice * 100 * this.marginLevel).toFixed(2)
            } else {
                currentPercent = ((openPrice - this.currentPrice) / openPrice * 100 * this.marginLevel).toFixed(2)
            }
            // 止损百分比
            let stopLosePercent = (Math.abs(openPrice - stopLosePrice) / stopLosePrice * 100 * this.marginLevel).toFixed(2)
            // 如果中间做过动止，加仓，又没有平今的话，持仓成本是变动的，因此这个盈利率和盈亏比只是跟据开仓价来计算的
            this.currentInfo = '新: ' + this.currentPrice.toFixed(2)
            let markLineCurrent = {
                yAxis: this.currentPrice,
                lineStyle: {
                    normal: {
                        opacity: 1,
                        type: 'dash',
                        width: 1,
                        color: 'yellow'
                    },
                },
                symbol: 'circle',
                symbolSize: 1,
                label: {
                    normal: {
                        color: this.echartsConfig.currentPriceColor,
                        formatter: '新: ' + this.currentPrice.toFixed(2)
                    },
                },
            }
            markLineData.push(markLineCurrent)
            // 开仓价
            let markLineOpen = {
                yAxis: openPrice,
                lineStyle: {
                    normal: {
                        opacity: 1,
                        type: 'dashed',
                        width: 1,
                        color: 'white'
                    },
                },
                symbol: 'circle',
                symbolSize: 1,
                label: {
                    normal: {
                        color: 'white',
                        formatter: '开: ' + openPrice.toFixed(2) + ' ' + this.dynamicDirectionMap[direction] + ': ' + openAmount + ' 手',
                    },
                },
            }
            markLineData.push(markLineOpen)

            // 止损线
            let markLineStop = {
                yAxis: stopLosePrice,
                lineStyle: {
                    normal: {
                        opacity: 1,
                        type: 'dashed',
                        width: 1,
                        color: this.echartsConfig.upColor
                    },
                },
                symbol: 'circle',
                symbolSize: 1,
                label: {
                    normal: {
                        color: this.echartsConfig.upColor,
                        formatter: '止: ' + stopLosePrice.toFixed(2) + ' 率: -' + stopLosePercent + '%',
                    },
                },
            }
            markLineData.push(markLineStop)
            if (this.currentPosition.hasOwnProperty('dynamicPositionList')) {
                // 动止记录
                for (let i = 0; i < this.currentPosition.dynamicPositionList.length; i++) {
                    // 数量
                    let dynamicItem = this.currentPosition.dynamicPositionList[i]
                    // let dynamicPercent = (Math.abs(dynamicItem.price - openPrice) / openPrice * 100 * marginLevel).toFixed(2)
                    let stop_win_count = dynamicItem.stop_win_count
                    let direction = this.dynamicDirectionMap[dynamicItem.direction]
                    let markLineObj = {
                        yAxis: dynamicItem.stop_win_price,
                        lineStyle: {
                            normal: {
                                opacity: 1,
                                type: 'dashed',
                                width: 1,
                                color: this.echartsConfig.dynamicOpertionColor
                            },
                        },
                        label: {
                            normal: {
                                color: this.echartsConfig.dynamicOpertionColor,
                                formatter: '动止: ' + CommonTool.formatDate(dynamicItem.date_created, 'MM-dd HH:mm') + " " + dynamicItem.stop_win_price + ' ' + direction + ' ' + stop_win_count + '手' +
                                    ' 额：' + dynamicItem.stop_win_money,
                                position: 'insideMiddleTop'
                            }
                        },
                        symbol: 'circle',
                        symbolSize: 1
                    }
                    markLineData.push(markLineObj)
                }
            }
            // 兼容股票  111
            if (!jsonObj['fractal']) {
                return markLineData
            }
            let higherBottomPrice = 0
            let higherHigherBottomPrice = 0
            let higherTopPrice = 0
            let higherHigherTopPrice = 0
            //  多单查找顶型
            if (direction === 'long') {
                if (JSON.stringify(jsonObj['fractal'][0]) !== '{}' && jsonObj['fractal'][0]['direction'] === 1) {
                    higherBottomPrice = jsonObj['fractal'][0]['top_fractal']['bottom']
                    // 高级别分型线
                    let markLineFractal = {
                        yAxis: higherBottomPrice,
                        lineStyle: {
                            normal: {
                                opacity: 1,
                                type: 'dashed',
                                width: 1,
                                color: this.echartsConfig.higherColor
                            },
                        },
                        symbol: 'circle',
                        symbolSize: 1,
                        label: {
                            normal: {
                                color: this.echartsConfig.higherColor,
                                formatter: '顶: ' + jsonObj['fractal'][0]['period'] + ' ' + higherBottomPrice,
                                position: 'insideEndTop'

                            },
                        },
                    }
                    markLineData.push(markLineFractal)
                }
                if (JSON.stringify(jsonObj['fractal'][1]) !== '{}' && jsonObj['fractal'][1]['direction'] === 1) {
                    higherHigherBottomPrice = jsonObj['fractal'][1]['top_fractal']['bottom']
                    // 高高级别分型线
                    let markLineFractal = {
                        yAxis: higherHigherBottomPrice,
                        lineStyle: {
                            normal: {
                                opacity: 1,
                                type: 'dashed',
                                width: 1,
                                color: this.echartsConfig.higherHigherColor
                            },
                        },
                        symbol: 'circle',
                        symbolSize: 1,
                        label: {
                            normal: {
                                color: this.echartsConfig.higherHigherColor,
                                formatter: '顶: ' + jsonObj['fractal'][1]['period'] + ' ' + higherHigherBottomPrice,
                                position: 'insideEndTop'

                            },
                        },
                    }
                    markLineData.push(markLineFractal)
                }
            } else {
                // 空单查找底分型
                if (JSON.stringify(jsonObj['fractal'][0]) !== '{}' && jsonObj['fractal'][0]['direction'] === -1) {
                    higherTopPrice = jsonObj['fractal'][0]['bottom_fractal']['top']
                    // 高级别分型线
                    let markLineFractal = {
                        yAxis: higherTopPrice,
                        lineStyle: {
                            normal: {
                                opacity: 1,
                                type: 'dashed',
                                width: 1,
                                color: this.echartsConfig.higherColor
                            },
                        },
                        symbol: 'circle',
                        symbolSize: 1,
                        label: {
                            normal: {
                                color: this.echartsConfig.higherColor,
                                formatter: '底: ' + jsonObj['fractal'][0]['period'] + ' ' + higherTopPrice,
                                position: 'insideEndTop'

                            },
                        },
                    }
                    markLineData.push(markLineFractal)
                }
                if (JSON.stringify(jsonObj['fractal'][1]) !== '{}' && jsonObj['fractal'][1]['direction'] === -1) {
                    higherHigherTopPrice = jsonObj['fractal'][1]['bottom_fractal']['top']
                    // 高高级别分型线
                    let markLineFractal = {
                        yAxis: higherHigherTopPrice,
                        lineStyle: {
                            normal: {
                                opacity: 1,
                                type: 'dashed',
                                width: 1,
                                color: this.echartsConfig.higherHigherColor
                            },
                        },
                        symbol: 'circle',
                        symbolSize: 1,
                        label: {
                            normal: {
                                color: this.echartsConfig.higherHigherColor,
                                formatter: '底: ' + jsonObj['fractal'][1]['period'] + ' ' + higherHigherTopPrice,
                                position: 'insideEndTop'

                            },
                        },
                    }
                    markLineData.push(markLineFractal)
                }
            }
            return markLineData
        },
        quickCalcMaxCount() {
            this.calcAccount(this.quickCalc.openPrice, this.quickCalc.stopPrice)
            this.quickCalc.count = this.maxOrderCount
            this.quickCalc.stopRate = this.perOrderStopRate
            this.quickCalc.perOrderStopMoney = Math.round(this.perOrderStopMoney, 0)
        },
        // 计算开仓手数
        calcAccount(openPrice, stopPrice) {
            if (this.currentMarginRate == null) {
                alert('请选择保证金系数，开仓价，止损价')
                return
            }
            if (this.symbol.indexOf('BTC') !== -1) {
                this.account = this.digitCoinAccount
                // 火币1张就是100usd  20倍杠杠 1张保证金是5usd
                // OKEX 1张 = 0.01BTC  20倍杠杆， 1张就是 0.01* BTC的现价
                // 单位usdt
                this.perOrderMargin = 0.01 * this.currentPrice / 20
                this.perOrderStopRate = ((Math.abs(openPrice - stopPrice) / openPrice + this.digitCoinFee) * 20).toFixed(2)
                // 1手止损的百分比 需要加上手续费  0.05%  okex双向taker 就是 2%
                this.perOrderStopMoney = Number((this.perOrderMargin * this.perOrderStopRate).toFixed(2))
                this.maxAccountUseRate = 0.4
                this.stopRate = 0.1
            } else if (this.globalFutureSymbol.indexOf(this.symbol) !== -1) {
                // 外盘
                this.account = this.globalFutureAccount
                // 计算1手需要的保证金
                this.perOrderMargin = Math.floor(openPrice * this.contractMultiplier * this.currentMarginRate)
                this.perOrderStopMoney = Math.abs(openPrice - stopPrice) * this.contractMultiplier
                // 1手止损的百分比
                this.perOrderStopRate = (this.perOrderStopMoney / this.perOrderMargin).toFixed(2)
                this.maxAccountUseRate = 0.1
                this.stopRate = 0.01
            } else {
                // 内盘
                this.account = this.futureAccount
                // 计算1手需要的保证金
                this.perOrderMargin = Math.floor(openPrice * this.contractMultiplier * this.currentMarginRate)
                this.perOrderStopMoney = Math.abs(openPrice - stopPrice) * this.contractMultiplier
                // 1手止损的百分比
                this.perOrderStopRate = (this.perOrderStopMoney / this.perOrderMargin).toFixed(2)
                this.maxAccountUseRate = 0.1
                this.stopRate = 0.01
            }

            // 计算最大能使用的资金
            let maxAccountUse = this.account * 10000 * this.maxAccountUseRate
            // 计算最大止损金额
            let maxStopMoney = this.account * 10000 * this.stopRate
            // 1手止损的金额

            // 根据止损算出的开仓手数(四舍五入)
            let maxOrderCount1 = Math.round(maxStopMoney / this.perOrderStopMoney)

            // 根据最大资金使用率算出的开仓手数(四舍五入)
            let maxOrderCount2 = Math.round(maxAccountUse / this.perOrderMargin)

            this.maxOrderCount = maxOrderCount1 > maxOrderCount2 ? maxOrderCount2 : maxOrderCount1
            // 总保证金
            this.totalOrderMargin = this.perOrderMargin * this.maxOrderCount

            // 总止损额
            this.totalOrderStopMoney = this.perOrderStopMoney * this.maxOrderCount

            // 计算当前资金使用率
            this.accountUseRate = ((this.maxOrderCount * this.perOrderMargin) / this.account / 10000).toFixed(2)

            // 计算动态止盈手数， 即剩下仓位被止损也不会亏钱
            // 动止手数 * （动止价-开仓价）* 合约乘数 = （开仓手数-动止手数）* 1手止损
            // 动止手数  = 开仓手数 * 1手止损  /( （动止价-开仓价）* 合约乘数 + 1手止损)
            // 如果填入了动止价
            if (this.dynamicWinPrice != null) {
                this.dynamicWinCount = Math.round(this.maxOrderCount * this.perOrderStopMoney / ((this.dynamicWinPrice - openPrice) * this.contractMultiplier + this.perOrderStopMoney))
            }
            console.log("maxAccountUse:", maxAccountUse, " maxStopMoney :", maxStopMoney, " perOrderMargin:",
                this.perOrderMargin, " maxOrderCount:", this.maxOrderCount, " maxOrderCount2:", maxOrderCount2, " perOrderStopMoney:", this.perOrderStopMoney,
                " accountUseRate:", this.accountUseRate, " perOrderStopRate:", this.perOrderStopRate)
        },
        calculateMA(resultData, dayCount) {
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
        },
        /**
         *
         * @param jsonObj
         * @returns number
         * 1 本级别买回拉  2 高级别买回拉  3 本级别卖回拉 4 高级别卖回拉
         * 5 本级别线段破坏买 6 高级别线段破坏买  7 本级别线段破坏卖 8 高级别线段破坏卖
         * 9 本级别中枢突破买 10 高级别中枢突破买 11 本级别中枢突破卖 12 高级别中枢突破卖
         * 13 本级别三卖V买 14 高级别三卖V买 15 本级别三买V卖 16 高级别三买V卖
         * 17 本级别底背驰买    18 本级别顶背驰卖
         */
        getLastBeichiData(jsonObj) {
            // 回拉
            let buy_zs_huila = jsonObj.buy_zs_huila
            let buy_zs_huila_higher = jsonObj.buy_zs_huila_higher
            let sell_zs_huila = jsonObj.sell_zs_huila
            let sell_zs_huila_higher = jsonObj.sell_zs_huila_higher
            // 线段破坏
            let buy_duan_break = jsonObj.buy_duan_break
            let buy_duan_break_higher = jsonObj.buy_duan_break_higher
            let sell_duan_break = jsonObj.sell_duan_break
            let sell_duan_break_higher = jsonObj.sell_duan_break_higher

            // 突破
            let buy_zs_tupo = jsonObj.buy_zs_tupo
            let buy_zs_tupo_higher = jsonObj.buy_zs_tupo_higher
            let sell_zs_tupo = jsonObj.sell_zs_tupo
            let sell_zs_tupo_higher = jsonObj.sell_zs_tupo_higher

            // V反
            let buy_v_reverse = jsonObj.buy_v_reverse
            let buy_v_reverse_higher = jsonObj.buy_v_reverse_higher
            let sell_v_reverse = jsonObj.sell_v_reverse
            let sell_v_reverse_higher = jsonObj.sell_v_reverse_higher

            // 背驰
            let buyMACDBCData = jsonObj.buyMACDBCData
            let sellMACDBCData = jsonObj.sellMACDBCData

            // 回拉
            let buy_zs_huila_stamp = 0
            let buy_zs_huila_higher_stamp = 0
            let sell_zs_huila_Stamp = 0
            let sell_zs_huila_higher_stamp = 0
            // 线段破坏
            let buy_duan_break_stamp = 0
            let buy_duan_break_higher_stamp = 0
            let sell_duan_break_stamp = 0
            let sell_duan_break_higher_stamp = 0
            // 突破
            let buy_zs_tupo_stamp = 0
            let buy_zs_tupo_higher_stamp = 0
            let sell_zs_tupo_stamp = 0
            let sell_zs_tupo_higher_stamp = 0
            // V反
            let buy_v_reverse_stamp = 0
            let buy_v_reverse_higher_stamp = 0
            let sell_v_reverse_stamp = 0
            let sell_v_reverse_higher_stamp = 0

            // 背驰
            let buy_beichi_stamp = 0
            let sell_beichi_stamp = 0

            let buyTimeStr
            let higherBuyTimeStr
            let sellTimeStr
            let higherSellTimeStr
            // 回拉
            if (buy_zs_huila.date.length > 0) {
                buyTimeStr = buy_zs_huila.date[buy_zs_huila.date.length - 1]
                buy_zs_huila_stamp = this.timeStrToStamp(buyTimeStr)
            }
            if (buy_zs_huila_higher.date.length > 0) {
                higherBuyTimeStr = buy_zs_huila_higher.date[buy_zs_huila_higher.date.length - 1]
                buy_zs_huila_higher_stamp = this.timeStrToStamp(higherBuyTimeStr)
            }
            if (sell_zs_huila.date.length > 0) {
                sellTimeStr = sell_zs_huila.date[sell_zs_huila.date.length - 1]
                sell_zs_huila_Stamp = this.timeStrToStamp(sellTimeStr)
            }
            if (sell_zs_huila_higher.date.length > 0) {
                higherSellTimeStr = sell_zs_huila_higher.date[sell_zs_huila_higher.date.length - 1]
                sell_zs_huila_higher_stamp = this.timeStrToStamp(higherSellTimeStr)
            }

            // 线段破坏
            if (buy_duan_break.date.length > 0) {
                buyTimeStr = buy_duan_break.date[buy_duan_break.date.length - 1]
                buy_duan_break_stamp = this.timeStrToStamp(buyTimeStr)
            }
            if (buy_duan_break_higher.date.length > 0) {
                higherBuyTimeStr = buy_duan_break_higher.date[buy_duan_break_higher.date.length - 1]
                buy_duan_break_higher_stamp = this.timeStrToStamp(higherBuyTimeStr)
            }
            if (sell_duan_break.date.length > 0) {
                sellTimeStr = sell_duan_break.date[sell_duan_break.date.length - 1]
                sell_duan_break_stamp = this.timeStrToStamp(sellTimeStr)
            }
            if (sell_duan_break_higher.date.length > 0) {
                higherSellTimeStr = sell_duan_break_higher.date[sell_duan_break_higher.date.length - 1]
                sell_duan_break_higher_stamp = this.timeStrToStamp(higherSellTimeStr)
            }
            // 突破
            if (buy_zs_tupo.date.length > 0) {
                buyTimeStr = buy_zs_tupo.date[buy_zs_tupo.date.length - 1]
                buy_zs_tupo_stamp = this.timeStrToStamp(buyTimeStr)
            }
            if (buy_zs_tupo_higher.date.length > 0) {
                higherBuyTimeStr = buy_zs_tupo_higher.date[buy_zs_tupo_higher.date.length - 1]
                buy_zs_tupo_higher_stamp = this.timeStrToStamp(higherBuyTimeStr)
            }
            if (sell_zs_tupo.date.length > 0) {
                sellTimeStr = sell_zs_tupo.date[sell_zs_tupo.date.length - 1]
                sell_zs_tupo_stamp = this.timeStrToStamp(sellTimeStr)
            }
            if (sell_zs_tupo_higher.date.length > 0) {
                higherSellTimeStr = sell_zs_tupo_higher.date[sell_zs_tupo_higher.date.length - 1]
                sell_zs_tupo_higher_stamp = this.timeStrToStamp(higherSellTimeStr)
            }
            // V反
            if (buy_v_reverse.date.length > 0) {
                buyTimeStr = buy_v_reverse.date[buy_v_reverse.date.length - 1]
                buy_v_reverse_stamp = this.timeStrToStamp(buyTimeStr)
            }
            if (buy_v_reverse_higher.date.length > 0) {
                higherBuyTimeStr = buy_v_reverse_higher.date[buy_v_reverse_higher.date.length - 1]
                buy_v_reverse_higher_stamp = this.timeStrToStamp(higherBuyTimeStr)
            }
            if (sell_v_reverse.date.length > 0) {
                sellTimeStr = sell_v_reverse.date[sell_v_reverse.date.length - 1]
                sell_v_reverse_stamp = this.timeStrToStamp(sellTimeStr)
            }
            if (sell_v_reverse_higher.date.length > 0) {
                higherSellTimeStr = sell_v_reverse_higher.date[sell_v_reverse_higher.date.length - 1]
                sell_v_reverse_higher_stamp = this.timeStrToStamp(higherSellTimeStr)
            }
            // 背驰
            if (buyMACDBCData.date.length > 0) {
                buyTimeStr = buyMACDBCData.date[buyMACDBCData.date.length - 1]
                buy_beichi_stamp = this.timeStrToStamp(buyTimeStr)
            }
            if (sellMACDBCData.date.length > 0) {
                sellTimeStr = sellMACDBCData.date[sellMACDBCData.date.length - 1]
                sell_beichi_stamp = this.timeStrToStamp(sellTimeStr)
            }

            // 当线段破坏和中枢突破时间相等的时候，使用中枢突破信号，因为中枢突破止损更小
            if (buy_zs_tupo_stamp === buy_duan_break_stamp) {
                buy_duan_break_stamp = 0
            }
            if (buy_zs_tupo_higher_stamp === buy_duan_break_higher_stamp) {
                buy_duan_break_higher_stamp = 0
            }
            if (sell_zs_tupo_stamp === sell_duan_break_stamp) {
                sell_duan_break_stamp = 0
            }
            if (sell_zs_tupo_higher_stamp === sell_duan_break_higher_stamp) {
                sell_duan_break_higher_stamp = 0
            }

            let timeArray = [buy_zs_huila_stamp, buy_zs_huila_higher_stamp, sell_zs_huila_Stamp, sell_zs_huila_higher_stamp,
                buy_duan_break_stamp, buy_duan_break_higher_stamp, sell_duan_break_stamp, sell_duan_break_higher_stamp,
                buy_zs_tupo_stamp, buy_zs_tupo_higher_stamp, sell_zs_tupo_stamp, sell_zs_tupo_higher_stamp,
                buy_v_reverse_stamp, buy_v_reverse_higher_stamp, sell_v_reverse_stamp, sell_v_reverse_higher_stamp, buy_beichi_stamp, sell_beichi_stamp]
            let maxPos = 0
            let maxTime = timeArray[0]
            for (let i = 0; i < timeArray.length; i++) {
                if (timeArray[i] > maxTime) {
                    maxTime = timeArray[i]
                    maxPos = i
                }
            }

            if (buy_zs_huila_stamp === 0 && buy_zs_huila_higher_stamp === 0 && sell_zs_huila_Stamp === 0 && sell_zs_huila_higher_stamp === 0 &&
                buy_duan_break_stamp === 0 && buy_duan_break_higher_stamp === 0 && sell_duan_break_stamp === 0 && sell_duan_break_higher_stamp === 0 &&
                buy_zs_tupo_stamp === 0 && buy_zs_tupo_higher_stamp === 0 && sell_zs_tupo_stamp === 0 && sell_zs_tupo_higher_stamp === 0 &&
                buy_v_reverse_stamp === 0 && buy_v_reverse_higher_stamp === 0 && sell_v_reverse_stamp === 0 && sell_v_reverse_higher_stamp &&
                buy_beichi_stamp === 0 && sell_beichi_stamp === 0
            ) {
                return 0
            } else {
                return maxPos + 1
            }
        },
        timeStrToStamp(timeStr) {
            let date = timeStr.substring(0, 19)
            date = timeStr.replace(/-/g, '/') // 必须把日期'-'转为'/'
            return new Date(date).getTime()
        }

    }
}
