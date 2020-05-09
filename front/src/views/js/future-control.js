// @ is an alias to /src
import {futureApi} from '@/api/futureApi'
import CommonTool from '@/tool/CommonTool'
// import {mapGetters, mapMutations} from 'vuex'
// let moment = require('moment')
// import echarts from 'echarts/lib/echarts'
import MyHeader from '../MyHeader'
import FuturePositionList from '../FuturePositionList'
import StatisticsChat from "../StatisticsChat";
import PieChart from "../PieChart";

export default {
    name: 'futures-control',
    components: {
        'MyHeader': MyHeader,
        'FuturePositionList': FuturePositionList,
        'StatisticsChat': StatisticsChat,
        'PieChart': PieChart,
    },
    data() {
        return {
            btcTicker: "",
            beichiListLoading: true,
            calcPosForm: {
                // start用于仓位管理计算
                currentSymbol: null,
                currentMarginRate: null,
                marginLevel: null,
                // 合约乘数
                contractMultiplier: null,
                // 账户总额
                account: 0,

                // 期货账户总额
                futureAccount: this.$futureAccount,
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
                // okex 手续费 0.05% 开仓加平仓就是0.1%
                digitCoinFee: 0.001,

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
            },
            keyword: '',
            futureSymbolList: [],
            futureSymbolMap: {},
            periodList: ['3m', '5m', '15m', '30m', '60m'],
            beichiList: {},
            changeList: null, // 涨跌幅
            globalFutureChangeList: null,
            marginLevelCompany: 0.01,
            firstRequestDominant: true,

            // start用于仓位管理计算
            currentSymbol: null,
            currentMarginRate: null,

            // 账户总额
            account: 0,

            // 期货账户总额
            futureAccount: this.$futureAccount,
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
            symbolSearch: '',
            // 内盘涨跌幅百分比
            percentage: 0,
            // 外盘盘涨跌幅百分比
            globalFuturePercentage: 0,
            // 内外盘信号 多空
            signalPercentage: 0,
            globalSignalPercentage: 0,
            // 级别多空方向
            levelDirectionList: [],
            activeTab: 'first',
            // 结束日期
            endDate: CommonTool.dateFormat('yyyy-MM-dd'),
            prejudgeFormMap: '',
            // 保存新增预判数据
            prejudgeFormList: [],
            // 保存历史预判数据
            historyPrejudgeList: [],
            historyPrejudgeMap: {},
            // 显示更新还是新增按钮
            prejudgeCreateFlag: true,
            btnPrejudgeLoading: false,
            // current  新增状态 获取的是主力合约 ,提交的时候触发新增
            // history 历史状态 获取的不一定是主力合约 ，提交表格触发更新
            prejudgeTableStatus: 'current',
            prejudgeTableId: '',
            globalFutureSymbol: this.$globalFutureSymbol
        }
    },
    computed: {
        value2Computed: {
            get: function () {
                return this.keyword
            },
            set: function (val) {
                this.keyword = val.toUpperCase()
            }
        }
    },
    filters: {
        changeTagFilter(change) {
            if (change > 0) {
                return 'up-red'
            } else if (change < 0) {
                return 'down-green'
            } else {
                return 'zero-gray'
            }
        }
    },

    mounted() {
        // this.subscribeWS()
        this.getChangeiList()
        this.getSignalList()
        // this.getLevelDirectionList()
        this.getPrejudgeList()
        this.getBTCTicker()
        this.getGlobalFutureChangeList()
        setInterval(() => {
            this.getSignalList()
            this.getChangeiList()
            // this.getLevelDirectionList()
            this.getBTCTicker()
            this.getGlobalFutureChangeList()
        }, 20000)
    },
    methods: {
        onInputChange() {
            this.createOrUpdatePrejudgeList('update')
        },
        subscribeWS() {
            let ws = new WebSocket('ws://localhost:5000/control')
            ws.onopen = function (evt) {
                console.log('Connection open ...')
                let subChangeList = {'event': 'changeList'}
                ws.send(JSON.stringify(subChangeList))
            }
            // ws.addEventListener('open', function (event) {
            //    ws.send('Hello Server!');
            // };
            ws.onmessage = (event) => {
                console.log('Received Message: ' + event.data)
                let jsonObj = JSON.parse(event.data)
                console.log(jsonObj)
                if (jsonObj.event === 'changeList') {
                    this.changeList = jsonObj.data
                }
            }
            ws.onclose = function (evt) {
                console.log('Connection closed.')
            }
        },
        getBTCTicker() {
            futureApi.getBTCTicker().then(res => {
                this.btcTicker = res
                console.log('获取okexTiker', this.btcTicker)
            }).catch((error) => {
                console.log('获取okexTiker失败:', error)
            })
        },
        processChangeList() {
            // 计算多空分布
            let long = 0
            let short = 0
            for (let item in this.changeList) {
                if (this.changeList[item]['change'] > 0) {
                    long = long + 1
                } else {
                    short = short + 1
                }
            }
            this.percentage = parseInt(long / (long + short) * 100)
            console.log('获取涨跌幅列表 计算百分比', this.changeList, this.percentage)
        },
        processGlobalFutureChangeList() {
            // 计算多空分布
            let long = 0
            let short = 0
            for (let item in this.globalFutureChangeList) {
                if (this.globalFutureChangeList[item]['change'] > 0) {
                    long = long + 1
                } else {
                    short = short + 1
                }
            }
            this.globalFuturePercentage = parseInt(long / (long + short) * 100)
            console.log('获取外盘涨跌幅列表 计算百分比', this.globalFutureChangeList, this.globalFuturePercentage)
        },
        // getLevelDirectionList() {
        //     futureApi.getLevelDirectionList().then(res => {
        //         console.log('获取多空方向列表:', res)
        //         this.levelDirectionList = res
        //     }).catch((error) => {
        //         console.log('获取多空方向列表:', error)
        //     })
        // },
        jumpToControl(type) {
            if (type === 'futures') {
                this.$router.replace('/futures-control')
            } else {
                this.$router.replace('/stock-control')
            }
        },
        getDominantSymbol() {
            futureApi.getDominant().then(res => {
                console.log('获取主力合约:', res)
                this.futureSymbolList = res
                window.localStorage.setItem('symbolList', JSON.stringify(this.futureSymbolList))
                this.firstRequestDominant = false
                this.beichiListLoading = false
            }).catch((error) => {
                console.log('获取主力合约失败:', error)
                this.firstRequestDominant = false
            })
        },
        getSignalList() {
            futureApi.getSignalList().then(res => {
                // console.log('获取背驰列表:', res)
                this.beichiList = res
                this.processBeichiList()
                if (this.firstRequestDominant) {
                    // 主力合约后端需要2秒才能返回，前端不要每次都去请求
                    // 本地缓存有主力合约数据
                    let symbolList = window.localStorage.getItem('symbolList')
                    if (symbolList != null) {
                        this.beichiListLoading = false
                        this.futureSymbolList = JSON.parse(symbolList)
                        this.prejudgeFormList = JSON.parse(symbolList)
                        this.futureSymbolMap = {}
                        this.prejudgeFormMap = {}
                        // console.log("111", this.futureSymbolList)
                        for (var i = 0; i < this.futureSymbolList.length - 1; i++) {
                            let symbolItem = this.futureSymbolList[i]
                            this.futureSymbolMap[symbolItem.order_book_id] = symbolItem
                            this.prejudgeFormMap[symbolItem.order_book_id] = ''
                        }
                        // 创建预判表单对象
                    }
                    // 静默更新主力合约
                    this.getDominantSymbol()
                }
            }).catch((error) => {
                console.log('获取背驰列表失败:', error)
            })
        },

        processBeichiList() {
            let long = 0
            let short = 0
            let globalLong = 0
            let globalShort = 0
            for (let symbol in this.beichiList) {
                let count = 0
                let item = this.beichiList[symbol]
                // console.log("背驰item:", item, symbol)
                for (let j in item) {
                    let innerItem = item[j]
                    if (innerItem !== '' && innerItem.indexOf('B') !== -1) {
                        count++
                    }
                    if (innerItem !== '' && innerItem.indexOf('多') !== -1) {
                        count++
                    }
                }
                // 外盘没有3分钟，多空比例需要提高一点
                // if (this.globalFutureSymbol.indexOf(symbol) !== -1) {
                //     item['percentage'] = count * 12.5
                // } else {
                item['percentage'] = count * 10
                // }
                // 外盘
                if (this.globalFutureSymbol.indexOf(symbol) !== -1) {
                    if (item['percentage'] >= 50) {
                        globalLong++
                    } else {
                        globalShort++
                    }
                    this.globalSignalPercentage = parseInt(globalLong / (globalLong + globalShort) * 100)
                } else {
                    if (item['percentage'] >= 50) {
                        long++
                    } else {
                        short++
                    }
                    this.signalPercentage = parseInt(long / (long + short) * 100)
                }
            }
        },
        getChangeiList() {
            futureApi.getChangeiList().then(res => {
                this.changeList = res
                this.processChangeList()
            }).catch((error) => {
                console.log('获取涨跌幅失败:', error)
            })
        },
        getGlobalFutureChangeList() {
            futureApi.getGlobalFutureChangeList().then(res => {
                this.globalFutureChangeList = res
                this.processGlobalFutureChangeList()
            }).catch((error) => {
                console.log('获取涨跌幅失败:', error)
            })
        },
        jumpToKline(symbol) {
            // 夜盘交易，时间算第二天的
            let date = new Date()
            let nextDay = date.getTime() + 3600 * 1000 * 24
            // 总控页面不关闭，开启新页面
            let routeUrl = this.$router.resolve({
                path: '/multi-period',
                query: {
                    symbol: symbol,
                    endDate: CommonTool.parseTime(nextDay, '{y}-{m}-{d}')
                }
            })
            window.open(routeUrl.href, '_blank')
        },
        fillMarginRate(symbolInfo, price) {
            if (symbolInfo.order_book_id.indexOf('BTC') === -1) {
                this.calcPosForm.currentMarginRate = Number((symbolInfo.margin_rate + this.marginLevelCompany).toFixed(3))
                this.calcPosForm.account = this.calcPosForm.futureAccount
                this.calcPosForm.maxAccountUseRate = 0.1
                this.calcPosForm.stopRate = 0.01
            } else {
                this.calcPosForm.account = this.calcPosForm.digitCoinAccount
                this.calcPosForm.maxAccountUseRate = 0.4
                this.calcPosForm.stopRate = 0.1
                this.calcPosForm.currentMarginRate = symbolInfo.margin_rate
            }
            this.calcPosForm.marginLevel = (1 / this.calcPosForm.currentMarginRate).toFixed(2)
            this.calcPosForm.contractMultiplier = symbolInfo.contract_multiplier
            this.calcPosForm.currentSymbol = symbolInfo.underlying_symbol
            this.calcPosForm.openPrice = price
        },
        /**
         *  火币BTC期货属于币本位，OKEX 期货属于金本位
         *  商品期货属于法币本位,他们的仓位管理计算不一样
         */
        calcAccount() {
            if (this.calcPosForm.currentMarginRate == null) {
                alert('请填入保证金系数，开仓价，止损价')
                return
            }
            if (this.calcPosForm.currentSymbol.indexOf('BTC') === -1) {
                this.calcPosForm.account = this.calcPosForm.futureAccount
                // 计算1手需要的保证金
                this.calcPosForm.perOrderMargin = Math.floor(this.calcPosForm.openPrice * this.calcPosForm.contractMultiplier * this.calcPosForm.currentMarginRate)
                this.calcPosForm.perOrderStopMoney = Math.abs(this.calcPosForm.openPrice - this.calcPosForm.stopPrice) * this.calcPosForm.contractMultiplier
                // 1手止损的百分比
                this.calcPosForm.perOrderStopRate = (this.calcPosForm.perOrderStopMoney / this.calcPosForm.perOrderMargin).toFixed(2)
            } else {
                this.calcPosForm.account = this.calcPosForm.digitCoinAccount
                // 火币1张就是100usd  20倍杠杠 1张保证金是5usd
                // OKEX 1张 = 0.01BTC  20倍杠杆， 1张就是 0.01* BTC的现价
                if (this.btcTicker === '') {
                    alert('请先获取btc最新价格')
                    return
                }
                this.calcPosForm.perOrderMargin = (0.01 * Number(this.btcTicker.price) / 20).toFixed(2)
                this.calcPosForm.perOrderStopRate = ((Math.abs(this.calcPosForm.openPrice - this.calcPosForm.stopPrice) / this.calcPosForm.openPrice + this.calcPosForm.digitCoinFee) * 20).toFixed(2)
                this.calcPosForm.perOrderStopMoney = Number((this.calcPosForm.perOrderMargin * this.calcPosForm.perOrderStopRate).toFixed(2))
            }
            // 计算最大能使用的资金
            let maxAccountUse = this.calcPosForm.account * 10000 * this.calcPosForm.maxAccountUseRate
            // 计算最大止损金额
            let maxStopMoney = this.calcPosForm.account * 10000 * this.calcPosForm.stopRate
            // 1手止损的金额

            // 根据止损算出的开仓手数(四舍五入)
            let maxOrderCount1 = Math.round(maxStopMoney / this.calcPosForm.perOrderStopMoney)

            // 根据最大资金使用率算出的开仓手数(四舍五入)
            let maxOrderCount2 = Math.round(maxAccountUse / this.calcPosForm.perOrderMargin)

            this.calcPosForm.maxOrderCount = maxOrderCount1 > maxOrderCount2 ? maxOrderCount2 : maxOrderCount1
            // 总保证金
            this.calcPosForm.totalOrderMargin = (this.calcPosForm.perOrderMargin * this.calcPosForm.maxOrderCount).toFixed(2)

            // 总止损额
            this.calcPosForm.totalOrderStopMoney = (this.calcPosForm.perOrderStopMoney * this.calcPosForm.maxOrderCount).toFixed(2)

            // 计算当前资金使用率
            this.calcPosForm.accountUseRate = ((this.calcPosForm.maxOrderCount * this.calcPosForm.perOrderMargin) / this.calcPosForm.account / 10000).toFixed(2)

            // 计算动态止盈手数， 即剩下仓位被止损也不会亏钱
            // 动止手数 * （动止价-开仓价）* 合约乘数 = （开仓手数-动止手数）* 1手止损
            // 动止手数  = 开仓手数 * 1手止损  /( （动止价-开仓价）* 合约乘数 + 1手止损)
            // 如果填入了动止价
            if (this.calcPosForm.dynamicWinPrice != null) {
                this.calcPosForm.dynamicWinCount = Math.round(this.calcPosForm.maxOrderCount * this.calcPosForm.perOrderStopMoney / ((this.calcPosForm.dynamicWinPrice - this.calcPosForm.openPrice) * this.calcPosForm.contractMultiplier + this.calcPosForm.perOrderStopMoney))
            }
            console.log('maxAccountUse:', maxAccountUse, ' maxStopMoney :', maxStopMoney, ' perOrderMargin:',
                this.calcPosForm.perOrderMargin, ' maxOrderCount:', this.calcPosForm.maxOrderCount, ' maxOrderCount2:', maxOrderCount2, ' perOrderStopMoney:', this.calcPosForm.perOrderStopMoney,
                ' accountUseRate:', this.calcPosForm.accountUseRate, ' perOrderStopRate:', this.calcPosForm.perOrderStopRate)
        },
        customColorMethod(percentage) {
            if (percentage < 50) {
                return '#279D61'
            } else {
                return '#D04949'
            }
        },
        handleChangeTab(tab, event) {
            // console.log(tab, event)
        },

        changePrejudgeDate() {
            this.getPrejudgeList()
        },

        createOrUpdatePrejudgeList(type) {
            let data = {
                endDate: this.endDate,
                prejudgeList: type === 'create' ? this.prejudgeFormMap : this.historyPrejudgeMap
            }
            this.btnPrejudgeLoading = true
            if (type === 'create') {
                futureApi.createPrejudgeList(data).then(res => {
                    console.log('创建预判成功:', res)
                    this.btnPrejudgeLoading = false
                    this.$notify({
                        title: 'Success',
                        message: '创建预判成功',
                        type: 'success',
                        duration: 2000
                    })
                    this.getPrejudgeList()
                }).catch(() => {
                    this.btnPrejudgeLoading = false
                    console.log('创建失败:', error)
                })
            } else {
                data.id = this.prejudgeTableId
                futureApi.updatePrejudgeList(data).then(res => {
                    console.log('更新预判成功:', res)
                    this.btnPrejudgeLoading = false
                    this.$notify({
                        title: 'Success',
                        message: '更新预判成功',
                        type: 'success',
                        duration: 2000
                    })
                    this.getPrejudgeList()
                }).catch(() => {
                    this.btnPrejudgeLoading = false
                    console.log('更新失败:', error)
                })
            }
        },
        getPrejudgeList() {
            // 如果这个日期是有数据的，就显示更新按钮，否则显示新增按钮
            futureApi.getPrejudgeList(this.endDate).then(res => {
                if (res == -1) {
                    // this.prejudgeCreateFlag = true
                    this.prejudgeTableStatus = 'current'
                } else {
                    // this.prejudgeCreateFlag = false

                    this.prejudgeTableStatus = 'history'
                    this.historyPrejudgeMap = res.prejudgeList
                    this.prejudgeTableId = res._id
                    this.historyPrejudgeList = []
                    for (let x in res.prejudgeList) {
                        this.historyPrejudgeList.push(x)
                    }
                    console.log('获取预判成功:', res)
                }
            }).catch(() => {
                console.log('获取预判失败:', error)
            })
        },
        editPrejudgeList() {

        }

    }
}
