var app = new Vue({
    el: '#app',
    data: {
        keyword: '',
        futureSymbolList: [],
        periodList: ['3min', '5min', '15min', '30min', '60min', '4hour', '1day'],
        beichiList: {},
        changeList: {},//涨跌幅
        firstRequestDominant: true,
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
        // this.getDominantSymbol()
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
        }
    }
})