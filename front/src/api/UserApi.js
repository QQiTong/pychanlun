import axios from 'axios'

export const userApi = {
    /**
     * 获取消息
     */
    stockData(data) {
        let url = `/api/stock_data?kxType=${data.period}&symbol=${data.symbol}`;
        return axios({
            url: url,
            method: 'get',
            data: data
        })
    },
}
