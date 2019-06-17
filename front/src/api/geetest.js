import axios from 'axios'
import geetest from '../tool/geetest.gt'

export function getGtCaptcha () {
  // 防止ios中多个极验一块出现时，极验会出bug问题
  let url = '/v2/w/gt/register?t=' + new Date().getTime() + '-' + Math.random().toString(32).substr(2)
  return axios({
    method: 'get',
    url: url,
    withCredentials: true
  })
}
