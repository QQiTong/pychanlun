var app = new Vue({
    el: '#app',
    data: {
        keyword: '',
        futureSymbolList: [],
        periodList: ['3min', '5min', '15min', '30min', '60min', '4hour', '1day'],
        beichiList: {},
        changeList: {},//涨跌幅
        marginLevelCompany: 1.125,
        firstRequestDominant: true,

        //start用于仓位管理计算
        currentMarginRate:null,
        // 合约乘数
        contractMultiplier:null,
        // 账户总额
        account:null,
        //开仓价格
        openPrice:null,
        //止损价格
        stopPrice:null,
        //开仓手数
        maxOrderCount:null,
        //资金使用率
        accountUseRate:null,
        //最大资金使用率
        maxAccountUseRate:0.3,
        //止损系数
        stopRate:0.03,


        //end仓位管理计算

        digitCoinsSymbolList: [{
            contract_multiplier: 1,
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
        },
            {
                contract_multiplier: 1,
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
            }]
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
    mounted() {
        this.getBeichiList()
        this.getChangeiList()
        setInterval(() => {
            this.getBeichiList()
            this.getChangeiList()
        }, 10000)

    },
    methods: {
        getDominantSymbol() {
            let that = this
            $.ajax({
                url: '/api/dominant',
                type: 'get',
                success: function (data) {
                    console.log("获取主力合约:", data)
                    that.futureSymbolList = data;
                    that.futureSymbolList.push(...that.digitCoinsSymbolList)
                    window.localStorage.setItem("symbolList", JSON.stringify(that.futureSymbolList))
                    that.firstRequestDominant = false
                },
                error: function (error) {
                    console.log("获取主力合约失败:", error)
                    that.firstRequestDominant = false
                }
            });
        },
        getBeichiList() {
            let that = this
            $.ajax({
                url: '/api/get_beichi_list',
                type: 'get',
                success: function (data) {
                    console.log("获取背驰列表:", data)
                    that.beichiList = data
                    if (that.firstRequestDominant) {
                        that.getDominantSymbol()
                    }
                },
                error: function (error) {
                    console.log("获取背驰列表失败:", error)

                }
            });
        },
        getChangeiList() {
            let that = this
            $.ajax({
                url: '/api/get_change_list',
                type: 'get',
                success: function (data) {
                    that.changeList = data
                    console.log("获取涨跌幅列表:", data)
                },
                error: function (error) {
                    console.log("获取涨跌幅失败:", error)
                }
            });
        },
        jumpToKline(symbol) {
            window.open("./kline.html?symbol=" + symbol)
        },
        fillMarginRate(marginRate,contract_multiplier){
            this.currentMarginRate = Number((marginRate*this.marginLevelCompany).toFixed(2))
            this.contractMultiplier = contract_multiplier
        },
        calcAccount(){
            // 计算最大能使用的资金
            let maxAccountUse = this.account *10000* this.maxAccountUseRate
            // 计算最大止损金额
            let maxStopMoney = this.account *10000* this.stopRate
            // 计算1手需要的保证金
            let perOrderMargin = this.openPrice * this.contractMultiplier * this.currentMarginRate

            // 1手止损的金额
            let perOrderStopMoney = Math.abs(this.openPrice - this.stopPrice) * this.contractMultiplier

            // 根据止损算出的开仓手数
            this.maxOrderCount = Math.floor(maxStopMoney / perOrderStopMoney)

            // 根据最大资金使用率算出的开仓手数
            let maxOrderCount2 = Math.floor(maxAccountUse / perOrderMargin)





            // 计算当前资金使用率
            this.accountUseRate =  (this.maxOrderCount * perOrderMargin) / this.account / 10000
            console.log("maxAccountUse:",maxAccountUse," maxStopMoney :",maxStopMoney ," perOrderMargin:",
                perOrderMargin," maxOrderCount:",this.maxOrderCount," maxOrderCount2:",maxOrderCount2," perOrderStopMoney:",perOrderStopMoney,
                " accountUseRate:",this.accountUseRate)
        }


    }
})