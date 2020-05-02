import axios from 'axios'

export const stockApi = {
    /**
     * 获取K线数据
     */
    stockData(data) {
        let url
        if (!data.endDate) {
            url = `/api/stock_data?period=${data.period}&symbol=${data.symbol}`
        } else {
            url = `/api/stock_data?period=${data.period}&symbol=${data.symbol}&endDate=${data.endDate}`
        }
        return axios({
            url: url,
            method: 'get',
        })
    },
    saveStockData(data) {
        let url = `/api/save_stock_data?period=${data.period}&symbol=${data.symbol}`
        return axios({
            url: url,
            method: 'get',
            data: data
        })
    },
    getStockSignalList(page) {
        return axios({
            url: `/api/get_stock_signal_list?page=${page}`,
            method: 'get',
        })
    },

    // 持仓操作
    // 新增一个持仓
    createPosition(data) {
        let url = `/api/create_stock_position`
        return axios({
            url: url,
            method: 'post',
            data: data
        })
    },
    // 查询单个持仓
    getPosition(symbol, period, status) {
        let url = `/api/get_stock_position?symbol=${symbol}&period=${period}&status=${status}`
        return axios({
            url: url,
            method: 'get'
        })
    },
    // 查询持仓列表
    getPositionList(status, page, size) {
        let url = `/api/get_stock_position_list?status=${status}&page=${page}&size=${size}`
        return axios({
            url: url,
            method: 'get'
        })
    },
    // 更新持仓
    updatePosition(data) {
        let url = `/api/update_stock_position`
        return axios({
            url: url,
            method: 'post',
            data: data
        })
    },
    // 更新持仓状态
    updatePositionStatus(id, status) {
        let url = `/api/update_stock_position_status?id=${id}&status=${status}`
        return axios({
            url: url,
            method: 'get'
        })
    }
}
