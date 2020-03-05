// @ is an alias to /src
import {futureApi} from '@/api/futureApi'
import CommonTool from "@/tool/CommonTool";
// import {mapGetters, mapMutations} from 'vuex'
// let moment = require('moment')
// import echarts from 'echarts/lib/echarts'
import MyHeader from '../MyHeader'
import FuturePositionList from '../FuturePositionList'

export default {
    name: 'futures-control',
    components: {
        "MyHeader": MyHeader,
        "FuturePositionList": FuturePositionList
    },
    data() {
        return {
            beichiListLoading: true,
            calcPosForm: {
                //start用于仓位管理计算
                currentSymbol: null,
                currentMarginRate: null,
                // 合约乘数
                contractMultiplier: null,
                // 账户总额
                account: 0,

                // 期货账户总额
                futureAccount: this.$futureAccount,
                // 数字货币账户总额
                digitCoinAccount: this.$digitCoinAccount,
                //开仓价格
                openPrice: null,
                //止损价格
                stopPrice: null,
                //开仓手数
                maxOrderCount: null,
                //资金使用率
                accountUseRate: null,
                //最大资金使用率
                maxAccountUseRate: 0.1,
                //止损系数
                stopRate: 0.01,
                //数字货币手续费 20倍杠杆
                digitCoinFee: 0.0006,

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
                //end仓位管理计算
            },
            keyword: '',
            futureSymbolList: [],
            futureSymbolMap:{},
            periodList: ['3m', '5m', '15m', '30m', '60m'],
            beichiList: {},
            changeList: null,//涨跌幅
            marginLevelCompany: 0.01,
            firstRequestDominant: true,

            //start用于仓位管理计算
            currentSymbol: null,
            currentMarginRate: null,
            // 合约乘数
            contractMultiplier: null,
            // 账户总额
            account: 0,

            // 期货账户总额
            futureAccount: this.$futureAccount,
            // 数字货币账户总额
            digitCoinAccount:this.$digitCoinAccount,
            //开仓价格
            openPrice: null,
            //止损价格
            stopPrice: null,
            //开仓手数
            maxOrderCount: null,
            //资金使用率
            accountUseRate: null,
            //最大资金使用率
            maxAccountUseRate: 0.1,
            //止损系数
            stopRate: 0.01,
            //数字货币手续费 20倍杠杆
            digitCoinFee: 0.0006,

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
            //end仓位管理计算

            digitCoinsSymbolList: [{
                contract_multiplier: 20,
                de_listed_date: "forever",
                exchange: "HUOBI",
                listed_date: "forever",
                margin_rate: 0.045,
                market_tplus: 0,
                maturity_date: "forever",
                order_book_id: "BTC_CQ",
                round_lot: 1,
                symbol: "比特币",
                trading_hours: "7*24",
                type: "Future",
                underlying_order_book_id: "null",
                underlying_symbol: "BTC_CQ",
                feeRate: 0.012
            },
                {
                    contract_multiplier: 20,
                    de_listed_date: "forever",
                    exchange: "HUOBI",
                    listed_date: "forever",
                    margin_rate: 0.045,
                    market_tplus: 0,
                    maturity_date: "forever",
                    order_book_id: "ETH_CQ",
                    round_lot: 1,
                    symbol: "以太坊",
                    trading_hours: "7*24",
                    type: "Future",
                    underlying_order_book_id: "null",
                    underlying_symbol: "ETH_CQ",
                }],
                //外盘
                outSideSymbolList: [{
                    contract_multiplier: 20,
                    de_listed_date: "forever",
                    exchange: "NYMEX能源",
                    listed_date: "forever",
                    margin_rate: 1,
                    market_tplus: 0,
                    maturity_date: "forever",
                    order_book_id: "us_sc",
                    round_lot: 1,
                    symbol: "us_sc",
                    trading_hours: "7*24",
                    type: "Future",
                    underlying_order_book_id: "null",
                    underlying_symbol: "us_sc",
                    feeRate: 0.012
                },
                {
                    contract_multiplier: 20,
                    de_listed_date: "forever",
                    exchange: "纽约COMEX",
                    listed_date: "forever",
                    margin_rate: 1,
                    market_tplus: 0,
                    maturity_date: "forever",
                    order_book_id: "us_au",
                    round_lot: 1,
                    symbol: "us_au",
                    trading_hours: "7*24",
                    type: "Future",
                    underlying_order_book_id: "null",
                    underlying_symbol: "us_au",
                    feeRate: 0.012
                },
                {
                    contract_multiplier: 20,
                    de_listed_date: "forever",
                    exchange: "纽约COMEX",
                    listed_date: "forever",
                    margin_rate: 1,
                    market_tplus: 0,
                    maturity_date: "forever",
                    order_book_id: "us_ag",
                    round_lot: 1,
                    symbol: "us_ag",
                    trading_hours: "7*24",
                    type: "Future",
                    underlying_order_book_id: "null",
                    underlying_symbol: "us_ag",
                    feeRate: 0.012
                },
                {
                    contract_multiplier: 20,
                    de_listed_date: "forever",
                    exchange: "美国",
                    listed_date: "forever",
                    margin_rate: 1,
                    market_tplus: 0,
                    maturity_date: "forever",
                    order_book_id: "us_m",
                    round_lot: 1,
                    symbol: "us_m",
                    trading_hours: "7*24",
                    type: "Future",
                    underlying_order_book_id: "null",
                    underlying_symbol: "us_m",
                    feeRate: 0.012
                },
                {
                    contract_multiplier: 20,
                    de_listed_date: "forever",
                    exchange: "美国",
                    listed_date: "forever",
                    margin_rate: 1,
                    market_tplus: 0,
                    maturity_date: "forever",
                    order_book_id: "us_cf",
                    round_lot: 1,
                    symbol: "us_cf",
                    trading_hours: "7*24",
                    type: "Future",
                    underlying_order_book_id: "null",
                    underlying_symbol: "us_cf",
                    feeRate: 0.012
                },
   // otherSymbol = ["BTC_CQ","ETH_CQ","us_sc","us_au","us_ag","us_m","us_cf","us_a","us_y","l_ni","l_zn","m_p","ja_ru"]
                {
                    contract_multiplier: 20,
                    de_listed_date: "forever",
                    exchange: "美国",
                    listed_date: "forever",
                    margin_rate: 1,
                    market_tplus: 0,
                    maturity_date: "forever",
                    order_book_id: "us_a",
                    round_lot: 1,
                    symbol: "us_a",
                    trading_hours: "7*24",
                    type: "Future",
                    underlying_order_book_id: "null",
                    underlying_symbol: "us_a",
                    feeRate: 0.012
                },
                {
                    contract_multiplier: 20,
                    de_listed_date: "forever",
                    exchange: "美国",
                    listed_date: "forever",
                    margin_rate: 1,
                    market_tplus: 0,
                    maturity_date: "forever",
                    order_book_id: "us_y",
                    round_lot: 1,
                    symbol: "us_y",
                    trading_hours: "7*24",
                    type: "Future",
                    underlying_order_book_id: "null",
                    underlying_symbol: "us_y",
                    feeRate: 0.012
                },
                {
                    contract_multiplier: 20,
                    de_listed_date: "forever",
                    exchange: "伦敦",
                    listed_date: "forever",
                    margin_rate: 1,
                    market_tplus: 0,
                    maturity_date: "forever",
                    order_book_id: "l_ni",
                    round_lot: 1,
                    symbol: "l_ni",
                    trading_hours: "7*24",
                    type: "Future",
                    underlying_order_book_id: "null",
                    underlying_symbol: "l_ni",
                    feeRate: 0.012
                },
                {
                    contract_multiplier: 20,
                    de_listed_date: "forever",
                    exchange: "伦敦",
                    listed_date: "forever",
                    margin_rate: 1,
                    market_tplus: 0,
                    maturity_date: "forever",
                    order_book_id: "l_zn",
                    round_lot: 1,
                    symbol: "l_zn",
                    trading_hours: "7*24",
                    type: "Future",
                    underlying_order_book_id: "null",
                    underlying_symbol: "l_zn",
                    feeRate: 0.012
                },
                {
                    contract_multiplier: 20,
                    de_listed_date: "forever",
                    exchange: "马来西亚",
                    listed_date: "forever",
                    margin_rate: 1,
                    market_tplus: 0,
                    maturity_date: "forever",
                    order_book_id: "m_p",
                    round_lot: 1,
                    symbol: "m_p",
                    trading_hours: "7*24",
                    type: "Future",
                    underlying_order_book_id: "null",
                    underlying_symbol: "m_p",
                    feeRate: 0.012
                },
       
                {
                    contract_multiplier: 20,
                    de_listed_date: "forever",
                    exchange: "日本",
                    listed_date: "forever",
                    margin_rate: 1,
                    market_tplus: 0,
                    maturity_date: "forever",
                    order_book_id: "ja_ru",
                    round_lot: 1,
                    symbol: "ja_ru",
                    trading_hours: "7*24",
                    type: "Future",
                    underlying_order_book_id: "null",
                    underlying_symbol: "ja_ru",
                    feeRate: 0.012
                },
                
            ],
            symbolSearch: '',
            percentage: 0,
            //级别多空方向
            levelDirectionList:[],
            activeTab:"first",
            // 结束日期
            endDate: CommonTool.dateFormat('yyyy-MM-dd'),
            prejudgeFormMap:"",
            //保存新增预判数据
            prejudgeFormList:[],
            //保存历史预判数据
            historyPrejudgeList:[],
            historyPrejudgeMap:{},
            // 显示更新还是新增按钮
            prejudgeCreateFlag:true,
            btnPrejudgeLoading:false,
            // current  新增状态 获取的是主力合约 ,提交的时候触发新增
            // history 历史状态 获取的不一定是主力合约 ，提交表格触发更新
            prejudgeTableStatus:'current',
            prejudgeTableId:"",
        }
    },
    computed: {
        value2Computed: {
            get: function () {
                return this.keyword;
            },
            set: function (val) {
                this.keyword = val.toUpperCase();
            }
        }
    },
    filters: {
        changeTagFilter(change) {
            if (change > 0) {
                return 'danger'
            } else if(change<0) {
                return 'primay'
            } else{
                return 'info'
            }
        }
    },
    mounted() {
        this.getChangeiList()
        this.getSignalList()
        this.getLevelDirectionList()
        this.getPrejudgeList()
        setInterval(() => {
            this.getSignalList()
            this.getChangeiList()
            this.getLevelDirectionList()
        }, 20000)
    },
    methods: {
        getLevelDirectionList(){
            futureApi.getLevelDirectionList().then(res => {
                console.log("获取多空方向列表:", res)
                this.levelDirectionList = res;
            }).catch((error) => {
                console.log("获取多空方向列表:", error)
            })
        },
        jumpToControl(type) {
            if (type === "futures") {
                this.$router.replace("/futures-control")
            } else {
                this.$router.replace("/stock-control")
            }
        },
        getDominantSymbol() {
            futureApi.getDominant().then(res => {
                console.log("获取主力合约:", res)
                this.futureSymbolList = res;
                this.futureSymbolList.push(...this.digitCoinsSymbolList)
                this.futureSymbolList.push(...this.outSideSymbolList)
                window.localStorage.setItem("symbolList", JSON.stringify(this.futureSymbolList))
                this.firstRequestDominant = false
                this.beichiListLoading = false
            }).catch((error) => {
                console.log("获取主力合约失败:", error)
                this.firstRequestDominant = false
            })
        },
        getSignalList() {
            futureApi.getSignalList().then(res => {
                console.log("获取背驰列表:", res)
                this.beichiList = res
                if (this.firstRequestDominant) {
                    // 主力合约后端需要2秒才能返回，前端不要每次都去请求
                    // 本地缓存有主力合约数据
                    let symbolList = window.localStorage.getItem("symbolList")
                    if (symbolList != null) {
                        this.beichiListLoading = false
                        this.futureSymbolList = JSON.parse(symbolList)
                        this.prejudgeFormList= JSON.parse(symbolList)
                        this.futureSymbolMap = {}
                        this.prejudgeFormMap = {}

                        this.prejudgeFormList.push(...this.outSideSymbolList)
                        this.futureSymbolList.push(...this.outSideSymbolList)
                        // console.log("111", this.futureSymbolList)
                        for (var i = 0; i < this.futureSymbolList.length - 1; i++) {
                            let symbolItem = this.futureSymbolList[i]
                            this.futureSymbolMap[symbolItem.order_book_id] = symbolItem
                            this.prejudgeFormMap[symbolItem.order_book_id] = ""
                        }
                        // 创建预判表单对象
                        
                    }
                    // 静默更新主力合约
                    this.getDominantSymbol()
                }
            }).catch((error) => {
                console.log("获取背驰列表失败:", error)
            })
        },
        getChangeiList() {
            futureApi.getChangeiList().then(res => {
                this.changeList = res
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
                console.log("获取涨跌幅列表 计算百分比", res, this.percentage)
            }).catch(() => {
                console.log("获取涨跌幅失败:", error)
            })
        },
        jumpToKline(symbol) {
            // 总控页面不关闭，开启新页面
            let routeUrl = this.$router.resolve({
                path: "/multi-period",
                 query: {
                    symbol: symbol,
                    endDate: CommonTool.dateFormat("yyyy-MM-dd")
                }
            });
            window.open(routeUrl.href, '_blank');
        },
        fillMarginRate(symbolInfo,price) {
            this.calcPosForm.currentMarginRate = Number((symbolInfo.margin_rate + this.marginLevelCompany).toFixed(3))
            this.calcPosForm.contractMultiplier = symbolInfo.contract_multiplier
            this.calcPosForm.currentSymbol = symbolInfo.underlying_symbol
            this.calcPosForm.openPrice = price
        },
        /**
         *  BTC期货属于币本位， 商品期货属于法币本位,他们的仓位管理计算不一样
         */
        calcAccount() {
            if (this.calcPosForm.currentMarginRate == null) {
                alert("请填入保证金系数，开仓价，止损价")
                return
            }
            if (this.calcPosForm.currentSymbol.indexOf("_CQ") === -1) {
                this.calcPosForm.account = this.calcPosForm.futureAccount
                // 计算1手需要的保证金
                this.calcPosForm.perOrderMargin = Math.floor(this.calcPosForm.openPrice * this.calcPosForm.contractMultiplier * this.calcPosForm.currentMarginRate)
                this.calcPosForm.perOrderStopMoney = Math.abs(this.calcPosForm.openPrice - this.calcPosForm.stopPrice) * this.calcPosForm.contractMultiplier
                // 1手止损的百分比
                this.calcPosForm.perOrderStopRate = (this.calcPosForm.perOrderStopMoney / this.calcPosForm.perOrderMargin).toFixed(2)
            } else {
                this.calcPosForm.account = this.calcPosForm.digitCoinAccount
                // 火币1张就是100usd  20倍杠杠 1张保证金是5usd
                this.calcPosForm.perOrderMargin = 5
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
            this.calcPosForm.totalOrderMargin = this.calcPosForm.perOrderMargin * this.calcPosForm.maxOrderCount

            // 总止损额
            this.calcPosForm.totalOrderStopMoney = this.calcPosForm.perOrderStopMoney * this.calcPosForm.maxOrderCount

            // 计算当前资金使用率
            this.calcPosForm.accountUseRate = ((this.calcPosForm.maxOrderCount * this.calcPosForm.perOrderMargin) / this.calcPosForm.account / 10000).toFixed(2)

            // 计算动态止盈手数， 即剩下仓位被止损也不会亏钱
            // 动止手数 * （动止价-开仓价）* 合约乘数 = （开仓手数-动止手数）* 1手止损
            // 动止手数  = 开仓手数 * 1手止损  /( （动止价-开仓价）* 合约乘数 + 1手止损)
            // 如果填入了动止价
            if (this.calcPosForm.dynamicWinPrice != null) {
                this.calcPosForm.dynamicWinCount = Math.round(this.calcPosForm.maxOrderCount * this.calcPosForm.perOrderStopMoney / ((this.calcPosForm.dynamicWinPrice - this.calcPosForm.openPrice) * this.calcPosForm.contractMultiplier + this.calcPosForm.perOrderStopMoney))
            }
            console.log("maxAccountUse:", maxAccountUse, " maxStopMoney :", maxStopMoney, " perOrderMargin:",
                this.calcPosForm.perOrderMargin, " maxOrderCount:", this.calcPosForm.maxOrderCount, " maxOrderCount2:", maxOrderCount2, " perOrderStopMoney:", this.calcPosForm.perOrderStopMoney,
                " accountUseRate:", this.calcPosForm.accountUseRate, " perOrderStopRate:", this.calcPosForm.perOrderStopRate)
        },
        customColorMethod(percentage) {
            if (percentage < 50) {
                return '#409EFF';
            } else {
                return '#F56C6C';
            }
        },
        handleChangeTab(tab, event){
            console.log(tab, event);
        },

        changePrejudgeDate(){
            this.getPrejudgeList()
        },

        createOrUpdatePrejudgeList(type){
            let data = {
                endDate:this.endDate,
                prejudgeList:type==='create'?this.prejudgeFormMap:this.historyPrejudgeMap
            }
            this.btnPrejudgeLoading = true
            if(type==="create"){
                futureApi.createPrejudgeList(data).then(res => {
                    console.log("创建预判成功:", res)
                    this.btnPrejudgeLoading = false
                    this.$notify({
                        title: "Success",
                        message: "创建预判成功",
                        type: "success",
                        duration: 2000
                      });
                    this.getPrejudgeList()
                }).catch(() => {
                    this.btnPrejudgeLoading = false
                    console.log("创建失败:", error)
                })    
            }else{
                data.id= this.prejudgeTableId
                futureApi.updatePrejudgeList(data).then(res => {
                    console.log("更新预判成功:", res)
                    this.btnPrejudgeLoading = false
                    this.$notify({
                        title: "Success",
                        message: "更新预判成功",
                        type: "success",
                        duration: 2000
                      });
                    this.getPrejudgeList()
                }).catch(() => {
                    this.btnPrejudgeLoading = false
                    console.log("更新失败:", error)
                })    
            }
        },
        getPrejudgeList(){
            // 如果这个日期是有数据的，就显示更新按钮，否则显示新增按钮
            futureApi.getPrejudgeList(this.endDate).then(res => {
                if(res == -1){
                    // this.prejudgeCreateFlag = true  
                    this.prejudgeTableStatus = 'current'
                }else{
                    // this.prejudgeCreateFlag = false

                    this.prejudgeTableStatus = 'history'
                    this.historyPrejudgeMap = res.prejudgeList
                    this.prejudgeTableId = res._id
                    this.historyPrejudgeList = []
                    for(let x in res.prejudgeList){
                        this.historyPrejudgeList.push(x)
                    }
                    console.log("获取预判成功:", res)    
                }
            }).catch(() => {
                console.log("获取预判失败:", error)
            })    
           
        },
        editPrejudgeList(){

        }
        
    }
}