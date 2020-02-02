var app = new Vue({
    el: '#app',
    data: {
        signalList: [],
        periodList: ['3m', '5m', '15m', '30m', '60m'],
        beichiList: {}
    },
    mounted() {
        const page = getParams('page') || '1';
        this.getSignalList(page)
    },
    methods: {
        getSignalList(page) {
            let that = this
            $.ajax({
                url: `/api/get_stock_signal_list?page=${page}`,
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

function getParams(name) {
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
}
