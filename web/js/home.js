var app = new Vue({
    el: '#app',
    data: {
        keyword: '',
        futureSymbolList:[],
        digitCoinsSymbolList:[{
            contract_multiplier: 1,
            de_listed_date: "forever",
            exchange: "HUOBI",
            listed_date: "forever",
            margin_rate: 0.05,
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
            margin_rate: 0.05,
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
    mounted() {
        this.getDominantSymbol()
    },
    methods: {
        formatSymbol(symbolInfo){
            console.log(symbolInfo)
            if(symbolInfo instanceof Object ){
                return symbolInfo.symbol +"("+symbolInfo.underlying_symbol+")"

            }else{
                return symbolInfo
            }
        },
        getDominantSymbol() {
            let that = this
            $.ajax({
                url: '/api/dominant',
                type: 'get',
                success: function (data) {
                   console.log("获取主力合约:",data)
                    that.futureSymbolList = data;
                    that.futureSymbolList.push(...that.digitCoinsSymbolList)
                    window.localStorage.setItem("symbolList",JSON.stringify(that.futureSymbolList))
                },
                error: function (error) {
                   console.log("获取主力合约失败:",error)

                }
            });
        },
        jumpToKline(symbol) {
            window.open("./kline.html?symbol=" + symbol)
        }
    }
})