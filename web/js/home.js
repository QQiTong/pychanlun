var app = new Vue({
    el: '#app',
    data: {
        keyword: '',
        futureSymbolList:[],
        digitCoinsSymbolList:['BTC_CQ','ETH_CQ']
    },
    mounted() {
        this.getDominantSymbol()
    },
    methods: {
        getDominantSymbol() {
            let that = this
            $.ajax({
                url: '/api/dominant',
                type: 'get',
                success: function (data) {
                   console.log("获取主力合约:",data)
                    that.futureSymbolList = data;
                    that.futureSymbolList.push(...that.digitCoinsSymbolList)

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