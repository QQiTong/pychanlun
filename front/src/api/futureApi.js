import axios from 'axios'

export const futureApi = {
    /**
     * 获取账户信息
     */
    getAccountInfo () {
        let url = `/api/get_account_info`
        return axios({
            url: url,
            method: 'get',
        })
    },
    /**
     * 获取外盘列表前端标识
     */
    getGlobalFutureSymbol () {
        let url = `/api/get_global_future_symbol`
        return axios({
            url: url,
            method: 'get',
        })
    },
    /**
     * 获取K线数据
     */
    stockData (data) {
        let url
        if (!data.endDate) {
            url = `/api/stock_data?period=${data.period}&symbol=${data.symbol}&biType=${data.biType}&secondChance=${data.secondChance}`
        } else {
            url = `/api/stock_data?period=${data.period}&symbol=${data.symbol}&endDate=${data.endDate}&biType=${data.biType}&secondChance=${data.secondChance}`
        }
        return axios({
            url: url,
            method: 'get',
        })
    },

    // 获取期货统计列表
    getStatisticList (dateRange) {
        let url = `/api/get_statistic_list?dateRange=${dateRange}`
        return axios({
            url: url,
            method: 'get',
        })
    },
    // 获取期货合约配置
    getFutureConfig () {
        let url = `/api/get_future_config`
        return axios({
            url: url,
            method: 'get',
        })
    },
    // 获取主力合约
    dominant () {
        let url = `/api/dominant`
        return axios({
            url: url,
            method: 'get',
        })
    },
    saveStockData (data) {
        let url = `/api/save_stock_data?period=${data.period}&symbol=${data.symbol}`
        return axios({
            url: url,
            method: 'get',
            data: data
        })
    },
    getStockSignalList (page) {
        return axios({
            url: `/api/get_stock_signal_list?page=${page}`,
            method: 'get',
        })
    },
    getSignalList () {
        return axios({
            url: `/api/get_future_signal_list`,
            method: 'get',
        })
    },
    getChangeiList () {
        return axios({
            url: `/api/get_change_list`,
            method: 'get',
        })
    },
    getDayMaUpDownList () {
        return axios({
            url: `/api/get_day_ma_up_down_list`,
            method: 'get',
        })
    },
    getDayMaList (symbol) {
        return axios({
            url: `/api/get_day_ma_list?symbol=${symbol}`,
            method: 'get',
        })
    },
    getGlobalFutureChangeList () {
        return axios({
            url: `/api/get_global_future_change_list`,
            method: 'get',
        })
    },
    getDominant () {
        return axios({
            url: `/api/dominant`,
            method: 'get',
        })
    },
    // 持仓操作
    // 新增一个持仓
    createPosition (data) {
        let url = `/api/create_position`
        return axios({
            url: url,
            method: 'post',
            data: data
        })
    },
    // 查询单个持仓
    getPosition (symbol, period, status, direction) {
        let url = `/api/get_position?symbol=${symbol}&period=${period}&status=${status}&direction=${direction}`
        return axios({
            url: url,
            method: 'get'
        })
    },
    // 查询持仓列表
    getPositionList (status, page, size, endDate) {
        let url = `/api/get_position_list?status=${status}&page=${page}&size=${size}&endDate=${endDate}`
        return axios({
            url: url,
            method: 'get'
        })
    },
    // 更新持仓
    updatePosition (data) {
        let url = `/api/update_position`
        return axios({
            url: url,
            method: 'post',
            data: data
        })
    },
    // 更新持仓状态
    // updatePositionStatus (id, status) {
    //     let url = `/api/update_position_status?id=${id}&status=${status}`
    //     return axios({
    //         url: url,
    //         method: 'get'
    //     })
    // },
    // 更新自动录入的持仓列表
    updatePositionStatus (id, status, close_price) {
        let url = `/api/update_position_status?id=${id}&status=${status}&close_price=${close_price}`
        return axios({
            url: url,
            method: 'get'
        })
    },
    // 获取级别多空方向
    // getLevelDirectionList () {
    //     let url = `/api/get_future_level_direction_list`
    //     return axios({
    //         url: url,
    //         method: 'get'
    //     })
    // },
    // 创建预判
    createPrejudgeList (data) {
        let url = `/api/create_future_prejudge_list`
        return axios({
            url: url,
            method: 'post',
            data: data
        })
    },
    // 获取预判
    getPrejudgeList (endDate) {
        let url = `/api/get_future_prejudge_list?endDate=${endDate}`
        return axios({
            url: url,
            method: 'get'
        })
    },
    // 更新预判
    updatePrejudgeList (data) {
        let url = `/api/update_future_prejudge_list`
        return axios({
            url: url,
            method: 'post',
            data: data
        })
    },
    // 获取okex btc ticker 这个接口单独获取不能阻塞掉商品期货
    getBTCTicker () {
        let url = '/api/get_btc_ticker'
        return axios({
            url: url,
            method: 'get',
        })
    },
}
