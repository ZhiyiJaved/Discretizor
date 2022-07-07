import axios from 'axios'

axios.interceptors.response.use(function (response) {
  return response
})

// 请求方式的配置
export default {
  post (url, data) { //  post
    return axios({
      method: 'post',
      url,
      data,
      baseURL: 'http://127.0.0.1:5000/',
      headers: {
        'Content-Type': 'application/json; charset=UTF-8',
        'Access-Control-Allow-Origin': 'True'
      },
      transformRequest: [function (data) {
        return JSON.stringify(data)
      }]
    })
  },
  get (url, params) { // get
    return axios({
      baseURL: 'http://127.0.0.1:5000/',
      method: 'get',
      url,
      params, // get 请求时带的参数
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Access-Control-Allow-Origin': 'True'
      },
      transformRequest: [function (data) {
        return JSON.stringify(data)
      }]
    })
  }
}
