var app = new Vue({
    el: '#app',
    data: {
        strategyType: 0,
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
        account: 10,
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
        // this.getChangeiList()
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
            this.currentMarginRate = Number((symbolInfo.margin_rate * this.marginLevelCompany).toFixed(3))
            this.contractMultiplier = symbolInfo.contract_multiplier
            this.currentSymbol = symbolInfo.underlying_symbol
        },
        /**
         *  BTC期货属于币本位， 商品期货属于法币本位,他们的仓位管理计算不一样
         */
        calcAccount() {
            if (this.currentMarginRate == null) {
                alert("请填入保证金系数，开仓价，止损价")
                return
            }
            // 计算最大能使用的资金
            let maxAccountUse = this.account * 10000 * this.maxAccountUseRate
            // 计算最大止损金额
            let maxStopMoney = this.account * 10000 * this.stopRate
            // 1手止损的金额

            if (this.currentSymbol.indexOf("_CQ") === -1) {
                // 计算1手需要的保证金
                this.perOrderMargin = Math.floor(this.openPrice * this.contractMultiplier * this.currentMarginRate)
                this.perOrderStopMoney = Math.abs(this.openPrice - this.stopPrice) * this.contractMultiplier
                // 1手止损的百分比
                this.perOrderStopRate = (this.perOrderStopMoney / this.perOrderMargin).toFixed(2)
            } else {
                // 火币1张就是100usd  20倍杠杠 1张保证金是5usd
                this.perOrderMargin = 5
                this.perOrderStopRate = (Math.abs(this.openPrice - this.stopPrice) / this.openPrice + this.digitCoinFee) * 20
                this.perOrderStopMoney = Number((this.perOrderMargin * this.perOrderStopRate).toFixed(2))
            }

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
                this.dynamicWinCount = Math.round(this.maxOrderCount * this.perOrderStopMoney / ((this.dynamicWinPrice - this.openPrice) * this.contractMultiplier + this.perOrderStopMoney))
            }
            console.log("maxAccountUse:", maxAccountUse, " maxStopMoney :", maxStopMoney, " perOrderMargin:",
                this.perOrderMargin, " maxOrderCount:", this.maxOrderCount, " maxOrderCount2:", maxOrderCount2, " perOrderStopMoney:", this.perOrderStopMoney,
                " accountUseRate:", this.accountUseRate, " perOrderStopRate:", this.perOrderStopRate)
        },
        switchStrategy(strategyType) {
            this.strategyType = strategyType
            this.getBeichiList()
        }

    }
})