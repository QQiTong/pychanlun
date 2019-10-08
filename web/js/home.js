var app = new Vue({
    el: '#app',
    data: {
        strategyType: 4,
        keyword: '',
        futureSymbolList: [],
        periodList: ['3m', '5m', '15m', '30m', '60m'],
        beichiList: {},
        changeList: {},//涨跌幅
        marginLevelCompany: 1.125,
        firstRequestDominant: true,

        //start用于仓位管理计算
        currentSymbol: null,
        currentMarginRate: null,
        // 合约乘数
        contractMultiplier: null,
        // 账户总额
        account: null,
        //开仓价格
        openPrice: null,
        //止损价格
        stopPrice: null,
        //开仓手数
        maxOrderCount: null,
        //资金使用率
        accountUseRate: null,
        //最大资金使用率
        maxAccountUseRate: 0.3,
        //止损系数
        stopRate: 0.03,
        //数字货币手续费 20倍杠杆
        digitCoinFee:0.012,

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
            feeRate:0.012
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
        // setInterval(() => {
        //     this.getBeichiList()
        //     this.getChangeiList()
        // }, 10000)

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
                data: {'strategyType': that.strategyType},
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
        fillMarginRate(symbolInfo) {
            this.currentMarginRate = Number((symbolInfo.margin_rate * this.marginLevelCompany).toFixed(2))
            this.contractMultiplier = symbolInfo.contract_multiplier
            this.currentSymbol = symbolInfo.underlying_symbol
        },
        /**
         *  BTC期货属于币本位， 商品期货属于法币本位,他们的仓位管理计算不一样
         */
        calcAccount() {
            if (this.currentSymbol.indexOf("_CQ")===-1) {
                // 计算最大能使用的资金
                let maxAccountUse = this.account * 10000 * this.maxAccountUseRate
                // 计算最大止损金额
                let maxStopMoney = this.account * 10000 * this.stopRate
                // 计算1手需要的保证金
                let perOrderMargin = this.openPrice * this.contractMultiplier * this.currentMarginRate

                // 1手止损的金额
                let perOrderStopMoney = Math.abs(this.openPrice - this.stopPrice) * this.contractMultiplier

                // 根据止损算出的开仓手数
                let maxOrderCount1 = Math.floor(maxStopMoney / perOrderStopMoney)

                // 根据最大资金使用率算出的开仓手数
                let maxOrderCount2 = Math.floor(maxAccountUse / perOrderMargin)


                this.maxOrderCount = maxOrderCount1 > maxOrderCount2 ? maxOrderCount2 : maxOrderCount1


                // 计算当前资金使用率
                this.accountUseRate = ((this.maxOrderCount * perOrderMargin) / this.account / 10000).toFixed(2)
                console.log("maxAccountUse:", maxAccountUse, " maxStopMoney :", maxStopMoney, " perOrderMargin:",
                    perOrderMargin, " maxOrderCount:", this.maxOrderCount, " maxOrderCount2:", maxOrderCount2, " perOrderStopMoney:", perOrderStopMoney,
                    " accountUseRate:", this.accountUseRate)
            }else{
                 // 计算最大能使用的资金
                let maxAccountUse = this.account * 10000 * this.maxAccountUseRate
                // 计算最大止损金额
                let maxStopMoney = this.account * 10000 * this.stopRate


                // 止损的比例
                let totalStopRate = (Math.abs(this.openPrice - this.stopPrice)/this.openPrice+this.digitCoinFee) * (1/this.currentMarginRate)
                // 根据止损算出的开仓手数
                let maxOrderCount1 =  Math.floor(maxStopMoney  / totalStopRate / 100)

                 // 根据最大资金使用率算出的开仓手数
                let maxOrderCount2 = Math.floor(maxAccountUse / totalStopRate / 100)
                this.maxOrderCount = maxOrderCount1 > maxOrderCount2 ? maxOrderCount2 : maxOrderCount1
                // 计算n手需要的保证金
                let totalMargin = this.maxOrderCount * 100 / (1/this.margin_rate) / this.openPrice
                // 考虑到滑点等情况 ，手续费全部按 吃单成交 20倍杠杆买卖各0.6% 共1.2%
                console.log("maxAccountUse:", maxAccountUse, " maxStopMoney :", maxStopMoney, " totalStopRate:",
                    totalStopRate, " maxOrderCount:", this.maxOrderCount, " maxOrderCount2:", maxOrderCount2, "totalMargin:", totalMargin,
                    " accountUseRate:", this.accountUseRate)

            }


        },
        switchStrategy(strategyType) {
            this.strategyType = strategyType
            this.getBeichiList()
        }

    }
})