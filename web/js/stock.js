var app = new Vue({
    el: '#app',
    data: {
        signalList: [],
        periodList: ['3m', '5m', '15m', '30m', '60m'],
        beichiList: {}
    },
    mounted() {
        this.getSignalList()
    },
    methods: {
        getSignalList() {
            let that = this
            $.ajax({
                url: '/api/get_stock_signal_list',
                type: 'get',
                success: function (data) {
                    that.signalList = data
                },
                error: function (error) {
                    console.log("获取股票信号列表失败:", error)
                }
            });
        },
        jumpToKline(symbol, period) {
            window.open(`./kline-big.html?symbol=${symbol}&period=${period}`);
        }
    }
});
