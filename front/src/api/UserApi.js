import axios from 'axios'

export const userApi = {
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
    //获取主力合约
    dominant() {
        let url = `/api/dominant`
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
    getBeichiList() {
        return axios({
            url: `/api/get_beichi_list`,
            method: 'get',
        })
    },
    getChangeiList() {
        return axios({
            url: `/api/get_change_list`,
            method: 'get',
        })
    },
    getDominant() {
        return axios({
            url: `/api/dominant`,
            method: 'get',
        })
    },
    //持仓操作
    // 新增一个持仓
    createPosition(data) {
        let url = `/api/create_position`
        return axios({
            url: url,
            method: 'post',
            data: data
        })
    },
    // 查询持仓
    getPosition(status,page,size) {
        let url = `/api/get_position?status=${status}&page=${page}&size=${size}`
        return axios({
            url: url,
            method: 'get'
        })
    },
    // 更新持仓
    updatePosition(data) {
        let url = `/api/update_position`
        return axios({
            url: url,
            method: 'post',
            data: data
        })
    }
}
