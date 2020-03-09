Date.prototype.format = function (fmt) {
    var o = {
        "M+": this.getMonth() + 1, //月份
        "d+": this.getDate(), //日
        "h+": this.getHours(), //小时
        "m+": this.getMinutes(), //分
        "s+": this.getSeconds(), //秒
        "q+": Math.floor((this.getMonth() + 3) / 3), //季度
        "S": this.getMilliseconds() //毫秒
    };
    if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (var k in o)
        if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    return fmt;
}
var app = new Vue({
    el: '#app',
    data: {
        futureSymbolList: [],
        futureSymbolMap: {},
        timer: null,
        symbol: "",
        period: "",
        requestFlag: true,
        marginLevelCompany: 1.125,// 不同期货公司提高的点数不一样
        marginPrice: 0,//每手需要的保证金

        //start用于仓位管理计算
        currentSymbol: null,
        currentMarginRate: null,
        // 合约乘数
        contractMultiplier: 1,
        // 账户总额
        account: 19,
        // 期货账户总额
        futuresAccount: 19,
        // 数字货币账户总额
        digitCoinAccount: 0.01,
        //开仓价格
        openPrice: null,
        //止损价格
        stopPrice: null,
        //开仓手数
        maxOrderCount: null,
        //资金使用率
        accountUseRate: null,
        //最大资金使用率
        maxAccountUseRate: 0.1,
        //止损系数
        stopRate: 0.01,
        //数字货币手续费 20倍杠杆
        digitCoinFee: 0.0006,

        // 1手需要的保证金
        perOrderMargin: 0,
        // 1手止损金额
        perOrderStopMoney: 0,
        // 1手止损百分比
        perOrderStopRate: 0,
        // 总保证金
        totalOrderMargin: 0,
        // 总止损额
        totalOrderStopMoney: 0,

        // 动态止盈价格(动态止盈部分手数使剩下的止损也不亏钱)
        dynamicWinPrice: null,
        // 动态止盈手数
        dynamicWinCount: 0,
        //end仓位管理计算
        // 结束日期
        endDate: null,

        digitCoinsSymbolList: [{
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
        window.replaceParamVal = this.replaceParamVal
        let that = this;
        this.symbol = getParams('symbol') || 'BTC_CQ'
        this.period = getParams('period')
        //  大图只显示选中的k线图
        if (this.period !== "") {
            document.getElementById(this.period).style.display = "block"
            this.endDate = getParams('endDate')
        }
        console.log("symbol", this.symbol, this.period)

        // 取出本地缓存
        let symbolList = window.localStorage.getItem("symbolList")
        // 本地缓存有主力合约数据
        if (symbolList != null) {
            this.futureSymbolList = JSON.parse(symbolList)
            this.futureSymbolMap = {}
            for (var i = 0; i < this.futureSymbolList.length - 1; i++) {
                let symbolItem = this.futureSymbolList[i]
                this.futureSymbolMap[symbolItem.order_book_id] = symbolItem
            }
            this.requestSymbolData()
        }else{
            // 新设备 直接进入大图页面 先获取主力合约数据
            this.getDominantSymbol()
        }
    },
    methods: {
        // 请求数据
        requestSymbolData(){
            let that = this
            this.switchSymbol(this.symbol, 'refresh')
            // 如果是大图关闭轮询
            if (this.period !== "") {
                return
            }
            that.timer = setInterval(() => {
                if (that.requestFlag) {
                    that.switchSymbol(that.symbol, 'update')
                } else {
                    // console.log('wait...')
                }
            }, 10000);
        },
        getDominantSymbol() {
            let that = this;
            $.ajax({
                url: '/api/dominant',
                type: 'get',
                success: function (data) {
                    console.log("获取主力合约:", data);
                    that.futureSymbolList = data;
                    that.futureSymbolList.push(...that.digitCoinsSymbolList)
                    that.futureSymbolMap = {}
                    for (var i = 0; i < that.futureSymbolList.length - 1; i++) {
                        let symbolItem = that.futureSymbolList[i]
                        that.futureSymbolMap[symbolItem.order_book_id] = symbolItem
                    }
                    window.localStorage.setItem("symbolList", JSON.stringify(that.futureSymbolList))
                    that.requestSymbolData()
                },
                error: function (error) {
                    console.log("获取主力合约失败:", error)
                }
            });
        },
        switchSymbol(symbol, update) {
            this.symbol = symbol
            let that = this;
            // document.title = symbol
            if (this.period !== "") {
                document.title = symbol + "-" + this.period
            } else {
                document.title = symbol
            }

            if (that.timer) {
                clearTimeout(that.timer)
                that.timer = setInterval(() => {
                    console.log("状态:", this.requestFlag)
                    if (this.requestFlag) {
                        that.switchSymbol(symbol, 'update')
                    } else {
                        // console.log('wait...')
                    }
                }, 10000);
            }


            if (update == undefined) {
                console.log("undefine")
                update = 'refresh'
            }
            console.log("切换币种:", symbol)
            // 如果是大图，只请求一个周期的数据
            if (this.period !== "") {
                that.sendRequest(symbol, this.period, update)

            } else {
                for (var i = 0; i < 8; i++) {
                    switch (i) {
                        // case 0:
                        //     that.sendRequest(symbol, '1m', update)
                        //     break;
                        case 1:
                            that.sendRequest(symbol, '3m', update)
                            break;
                        case 2:
                            that.sendRequest(symbol, '5m', update)
                            break;
                        case 3:
                            that.sendRequest(symbol, '15m', update)
                            break;
                        case 4:
                            that.sendRequest(symbol, '30m', update)
                            break;
                        case 5:
                            that.sendRequest(symbol, '60m', update)
                            break;
                        case 6:
                            that.sendRequest(symbol, '240m', update)
                            break;
                        // case 7:
                        //     that.sendRequest(symbol, '1d', update)
                        //     break;
                    }
                }
            }


        },
        refreshOption(chart, resultData, period) {
            var option = chart.getOption();
            option.series[0].data = resultData.values;
            option.series[0].markArea.data = resultData.zsvalues;
            option.series[0].markLine.data = resultData.markLineData;
            option.series[0].markPoint.data = resultData.huilaValues;
            option.series[1].data = resultData.biValues;
            option.series[2].data = resultData.duanValues;
            option.series[2].markPoint.data = resultData.duanPriceValues;

            option.series[3].data = resultData.higherDuanValues;
            option.series[4].data = calculateMA(resultData, 5);
            option.series[5].data = calculateMA(resultData, 10);
            // option.series[5].data = resultData.macd;
            // option.series[6].data = resultData.diff;
            // option.series[6].markPoint.data = resultData.bcMACDValues;
            // option.series[7].data = resultData.dea;
            // option.series[7].markPoint.data = resultData.macdAreaValues;

            // option.series[8].data = resultData.macdBigLevel;
            // option.series[9].data = resultData.diffBigLevel;
            // option.series[10].data = resultData.deaBigLevel;

            // option.series[11].data = resultData.volume;

            // option.series[15].data = resultData.markLineData;


            option.xAxis[0].data = resultData.time;
            // option.xAxis[1].data = resultData.time;
            // option.xAxis[2].data = resultData.timeBigLevel;
            // option.xAxis[3].data = resultData.time;
            // var lastPrice = resultData.close[resultData.close.length - 1]


            return option
        },
        sendRequest(symbol, period, update) {
            let that = this;
            that.requestFlag = false;
            var data
            if (that.endDate != null) {
                data = {'symbol': symbol, 'period': period, 'endDate': that.endDate}
            } else {
                data = {'symbol': symbol, 'period': period}
            }
            $.ajax({
                url: '/api/stock_data',
                data: data,
                type: 'get',
                success: function (data) {
                    that.requestFlag = true;
                    // $(".loading-style-4").hide();
                    that.symbol = symbol;
                    // var result = draw(data, 'refresh', period);
                    var result = that.draw(data, update, period);
                    // 如果请求的symbol 和period 不一致 ,直接return
                },
                error: function (error) {
                    that.requestFlag = true;
                    // $(".loading-style-4").hide();

                }
            });
        },

        draw(stockJsonData, update, period) {
            var that = this;
            var zoomStart = 55
            const resultData = this.splitData( stockJsonData, period);

            dataTitle = that.symbol + "  " + period
            const margin_rate = that.futureSymbolMap[that.symbol] && that.futureSymbolMap[that.symbol].margin_rate || 1;
            let marginLevel = (1 / (margin_rate * this.marginLevelCompany)).toFixed(2)
            const trading_hours = that.futureSymbolMap[that.symbol] && that.futureSymbolMap[that.symbol].trading_hours;
            const maturity_date = that.futureSymbolMap[that.symbol] && that.futureSymbolMap[that.symbol].maturity_date;
            subText = "杠杆倍数: " + marginLevel + " 每手保证金: " + this.marginPrice + " 合约乘数: " + this.contractMultiplier + " 交易时间: " + trading_hours + " 交割时间: " + maturity_date;
            var currentChart = null
            // if (period === '1m') {
            //     currentChart = myChart1
            // } else
            //
            if (period === '3m') {
                currentChart = myChart3
            } else if (period === '5m') {
                currentChart = myChart5
            } else if (period === '15m') {
                currentChart = myChart15
            } else if (period === '30m') {
                currentChart = myChart30
            } else if (period === '60m') {
                currentChart = myChart60
            } else if (period === '240m') {
                currentChart = myChart240
            }
            // else if (period === '1d') {
            //     currentChart = myChart1d
            // }
            var option;
            if (update === 'update') {
                // console.log('更新了', update);
                option = that.refreshOption(currentChart, resultData, period)

            } else {
                option = {
                    animation: false,
                    backgroundColor: bgColor,
                    title: {
                        text: dataTitle,
                        subtext: subText,
                        left: '2%',
                        textStyle: {
                            color: 'white'
                        }
                    },
                    tooltip: { //提示框
                        trigger: 'axis', //触发类型：axis坐标轴触发,item
                        axisPointer: { //坐标轴指示器配置项
                            type: 'cross' //指示器类型，十字准星
                        },
                    },
                    axisPointer: {
                        link: {xAxisIndex: 'all'},
                    },
                    toolbox: {
                        orient: 'horizontal',
                        itemSize: 25,
                        itemGap: 8,
                        top: 16,
                        right: '1.4%',
                        feature: {
                            myLevel1: {
                                show: true,
                                title: '放大',
                                icon: 'image://img/big-kline.png',
                                onclick: function () {
                                    window.open("kline-big.html?symbol=" + that.symbol + "&period=" + period + "&endDate=" + new Date().format("yyyy-MM-dd"))
                                }
                            },
                            // myLevel3: {
                            //     show: true,
                            //     title: '3分钟',
                            //     icon: 'image://img/icon_3m.png',
                            //     onclick: function () {
                            //         period = '3m'
                            //         option.title.subtext = '3m'
                            //
                            //         refresh('refresh');
                            //     }
                            // },
                            // myLevel5: {
                            //     show: true,
                            //     title: '5分钟',
                            //     icon: 'image://img/icon_5m.png',
                            //     onclick: function () {
                            //         period = '5m'
                            //         option.title.subtext = '5m'
                            //         refresh('refresh');
                            //
                            //     }
                            // },
                            // myLevel15: {
                            //     show: true,
                            //     title: '15分钟',
                            //     icon: 'image://img/icon_15m.png',
                            //     onclick: function () {
                            //         that.period = '15m'
                            //         option.title.subtext = '15m'
                            //         refresh();
                            //     }
                            // },
                            // myLevel30: {
                            //     show: true,
                            //     title: '30分钟',
                            //     icon: 'image://img/icon_30m.png',
                            //     onclick: function () {
                            //         that.period = '30m'
                            //         option.title.subtext = '30m'
                            //         refresh();
                            //     }
                            // },
                            //     myLevel60: {
                            //         show: true,
                            //         title: '60分钟',
                            //         icon: 'image://img/icon_1h.png',
                            //         onclick: function () {
                            //             that.period = '60m'
                            //             option.title.subtext = '60m'
                            //             refresh();
                            //         }
                            //     },
                            //     myLevel240: {
                            //         show: true,
                            //         title: '240分钟',
                            //         icon: 'image://img/icon_240m.png',
                            //         onclick: function () {
                            //             that.period = '60m'
                            //             option.title.subtext = '60m'
                            //             refresh();
                            //         }
                            //     },
                            //     myLevelDay: {
                            //         show: true,
                            //         title: '日',
                            //         icon: 'image://img/icon_1d.png',
                            //         background: '#555',
                            //         onclick: function () {
                            //             that.period = '1d'
                            //             option.title.subtext = '1d'
                            //             refresh();
                            //         }
                            //     },
                            //     myLevelWeek: {
                            //         show: true,
                            //         title: '周',
                            //         icon: 'image://img/icon_1w.png',
                            //         background: '#555',
                            //         onclick: function () {
                            //             that.period = '1week'
                            //             option.title.subtext = '1week'
                            //             refresh();
                            //         }
                            //     },
                            //
                            //     myAutoRefresh: {
                            //         type: 'jpeg',//png
                            //         //name: resultData.info
                            //         background: '#555',
                            //
                            //         icon: 'image://img/icon_refresh.svg',
                            //         title: '刷新',
                            //         onclick: function () {
                            //             refresh();
                            //         }
                            //     },
                        },
                    },
                    color: ['yellow', 'green', 'blue', 'white', 'white', 'red' /*'white', 'white', 'white'*/],
                    legend: {
                        data: ['笔', '段', '高级别段', 'MA5', 'MA10', 'MA60' /*'布林上轨', '布林中轨', '布林下轨'*/],

                        selected: {
                            '笔': true,
                            '段': true,
                            '高级别段': true,
                            'MA5': false,
                            'MA10': false,
                            'MA60': false,
                            // 'markline': true
                        },
                        top: 10,
                        textStyle: {
                            color: 'white'
                        }
                    },
                    grid: [
                        {//直角坐标系
                            left: '0%',
                            right: '12%',
                            height: '85%',
                            top: 50,
                        },
                        // {
                        //     top: '65%',
                        //     height: '20%',
                        //     left: '0%',
                        //     right: '10%',
                        // },
                        // {
                        //     top: '80%',
                        //     height: '15%',
                        //     left: '0%',
                        //     right: '10%',
                        // },
                        // {
                        //     top: '90%',
                        //     height: '5%',
                        //     left: '3.2%',
                        //     right: '3.35%',
                        // }
                    ],
                    xAxis: [
                        {
                            type: 'category',
                            data: resultData.time,
                            scale: true,
                            boundaryGap: false,
                            splitLine: {show: false},
                            splitNumber: 20,
                            min: 'dataMin',
                            max: 'dataMax',
                            axisLine: {onZero: true, lineStyle: {color: '#8392A5'}},
                            // axisPointer: {
                            //     label: {
                            //         formatter: function (params) {
                            //             var seriesValue = (params.seriesData[0] || {}).value;
                            //             return params.value
                            //                 + (seriesValue != null
                            //                         ? '\n' + echarts.format.addCommas(seriesValue)
                            //                         : ''
                            //                 );
                            //         }
                            //     }
                            // }
                        },
                        // {
                        //     type: 'category',
                        //     gridIndex: 1,
                        //     data: resultData.time,
                        //     axisTick: {
                        //         show: false
                        //     },
                        //     axisLabel: {
                        //         show: true
                        //     },
                        //     axisLine: {lineStyle: {color: '#8392A5'}}
                        //
                        //
                        // },
                        // {
                        //     type: 'category',
                        //     gridIndex: 2,
                        //     data: resultData.timeBigLevel,
                        //     axisTick: {
                        //         show: false
                        //     },
                        //     axisLabel: {
                        //         show: false
                        //     },
                        //     // axisLine: {lineStyle: {color: '#8392A5'}}
                        // },
                        // {
                        //     type: 'category',
                        //     gridIndex: 3,
                        //     data: resultData.time,
                        //     axisTick: {
                        //         show: false
                        //     },
                        //     axisLabel: {
                        //         show: false
                        //     },
                        //     axisLine: {lineStyle: {color: '#8392A5'}}
                        // }
                    ],
                    yAxis: [
                        {
                            scale: true,
                            splitArea: {
                                show: false
                            },
                            splitLine: {
                                lineStyle: {
                                    opacity: 0.3,
                                    type: 'dashed',
                                    color: bgColor
                                }
                            },
                            axisLine: {lineStyle: {color: bgColor}},
                        },
                        //本级别macd
                        // {
                        //     gridIndex: 1,
                        //     splitNumber: 2,
                        //     axisTick: {
                        //         show: false
                        //     },
                        //     splitLine: {
                        //         show: false
                        //     },
                        //     axisLabel: {
                        //         show: true
                        //     },
                        //     axisLine: {onZero: true, lineStyle: {color: '#8392A5'}},
                        // },
                        //大级别macd
                        // {
                        //     gridIndex: 2,
                        //     splitNumber: 2,
                        //     axisLine: {
                        //         onZero: false
                        //     },
                        //     axisTick: {
                        //         show: false
                        //     },
                        //     splitLine: {
                        //         show: false
                        //     },
                        //     axisLabel: {
                        //         show: true
                        //     },
                        //     axisLine: {lineStyle: {color: '#8392A5'}},
                        // },
                        // 成交量
                        // {
                        //     gridIndex: 3,
                        //     splitNumber: 1,
                        //     axisLine: {
                        //         onZero: false
                        //     },
                        //     axisTick: {
                        //         show: false
                        //     },
                        //     splitLine: {
                        //         show: false
                        //     },
                        //     axisLabel: {
                        //         show: false
                        //     },
                        //     axisLine: {lineStyle: {color: '#8392A5'}},
                        // },
                    ],
                    dataZoom: [

                        {
                            type: 'inside',
                            xAxisIndex: [0, 0],
                            start: zoomStart,
                            end: 100,
                            minSpan: 10,
                        },
                        // {
                        //     type: 'inside',
                        //     xAxisIndex: [0, 1],
                        //     start: zoomStart,
                        //     end: 100,
                        //     minSpan: 10,
                        // },
                        // {
                        //     type: 'inside',
                        //     xAxisIndex: [0, 1],
                        //     start: zoomStart,
                        //     end: 100,
                        //     minSpan: 10,
                        // },
                        // {
                        //     xAxisIndex: [0, 1, 2],
                        //     type: 'slider',
                        //     start: zoomStart,
                        //     end: 100,
                        //     top: '95%',
                        //     minSpan: 10,
                        //     textStyle: {
                        //         color: '#8392A5'
                        //     },
                        //     dataBackground: {
                        //         areaStyle: {
                        //             color: '#8392A5'
                        //         },
                        //         lineStyle: {
                        //             opacity: 0.8,
                        //             color: '#8392A5'
                        //         }
                        //     },
                        //     handleStyle: {
                        //         color: '#fff',
                        //         shadowBlur: 3,
                        //         shadowColor: 'rgba(0, 0, 0, 0.6)',
                        //         shadowOffsetX: 2,
                        //         shadowOffsetY: 2
                        //     }
                        //
                        // }
                    ],
                    series: [
                        //index 0
                        {
                            name: 'K线图',
                            type: 'candlestick',
                            data: resultData.values,
                            animation: false,
                            itemStyle: {
                                normal: {
                                    color: upColor,
                                    color0: downColor,
                                    borderColor: upBorderColor,
                                    borderColor0: downBorderColor
                                }
                            },
                            markPoint: {
                                data: resultData.huilaValues,
                                animation: false
                            },
                            markArea: {
                                silent: true,
                                data: resultData.zsvalues,
                            },
                            markLine: {
                                silent: true,
                                data: resultData.markLineData,
                                symbol: 'circle',
                                symbolSize: 1,
                            }
                        },
                        //index 1
                        {
                            name: '笔',
                            type: 'line',
                            z: 1,
                            data: resultData.biValues,
                            lineStyle: {
                                normal: {
                                    opacity: 1,
                                    type: 'dashed',
                                    width: 1,
                                    color: 'yellow'
                                },
                            },
                            symbol: 'none',
                            animation: false
                        },
                        //index 2
                        {
                            name: '段',
                            type: 'line',
                            z: 1,
                            data: resultData.duanValues,
                            lineStyle: {
                                normal: {
                                    opacity: 1,
                                    type: 'solid',
                                    width: 2,
                                    color: 'green'
                                },
                            },
                            markPoint: {
                                data: resultData.duanPriceValues
                            },
                            symbol: 'none',
                            animation: false
                        },
                        //index 3
                        {
                            name: '高级别段',
                            type: 'line',
                            z: 1,
                            data: resultData.higherDuanValues,
                            lineStyle: {
                                normal: {
                                    opacity: 1,
                                    type: 'solid',
                                    width: 2,
                                    color: 'blue'
                                },
                            },
                            symbol: 'none',
                            animation: false
                        },
                        //index 4
                        {
                            name: 'MA5',
                            type: 'line',
                            data: calculateMA(resultData, 5),
                            smooth: true,
                            lineStyle: {
                                normal: {
                                    opacity: 0.9,
                                    type: 'solid',
                                    width: 1,
                                    color: "white"
                                },
                            },
                            symbol: 'none',
                            animation: false
                        },
                        //index 5
                        {
                            name: 'MA10',
                            type: 'line',
                            data: calculateMA(resultData, 10),
                            smooth: true,
                            lineStyle: {
                                normal: {
                                    opacity: 0.9,
                                    type: 'solid',
                                    width: 1,
                                    color: "yellow"
                                },
                            },
                            symbol: 'none',
                            animation: false
                        },
                        {
                            name: 'MA60',
                            type: 'line',
                            data: calculateMA(resultData, 60),
                            smooth: true,
                            lineStyle: {
                                normal: {
                                    opacity: 1,
                                    type: 'solid',
                                    width: 2,
                                    color: "red"
                                },
                            },
                            symbol: 'none',
                            animation: false
                        },
                        //index 5
                        // {
                        //     name: 'MACD',
                        //     type: 'bar',
                        //     xAxisIndex: 1,
                        //     yAxisIndex: 1,
                        //     data: resultData.macd,
                        //     barWidth: 2,
                        //     itemStyle: {
                        //         normal: {
                        //             color: function (params) {
                        //                 var colorList;
                        //                 if (params.data >= 0) {
                        //                     if (params.data >= macdUpLastValue) {
                        //                         colorList = macdUpDarkColor
                        //                     } else {
                        //                         colorList = macdUpLightColor
                        //                     }
                        //                     macdUpLastValue = params.data
                        //                 } else {
                        //                     if (params.data <= macdDownLastValue) {
                        //                         colorList = macdDownDarkColor
                        //                     } else {
                        //                         colorList = macdDownLightColor
                        //                     }
                        //                     macdDownLastValue = params.data
                        //                 }
                        //                 return colorList;
                        //             },
                        //         }
                        //     }
                        // },
                        //index 6

                        // {
                        //     name: 'DIFF',
                        //     type: 'line',
                        //     xAxisIndex: 1,
                        //     yAxisIndex: 1,
                        //     data: resultData.diff,
                        //     smooth: true,
                        //     lineStyle: {
                        //         normal: {
                        //             opacity: 1,
                        //             type: 'solid',
                        //             width: 1,
                        //             color: 'white'
                        //         },
                        //     },
                        //     symbol: 'none',
                        //     animation: false,
                        //     markPoint: {
                        //         data: resultData.bcMACDValues
                        //     },
                        // },
                        //index 7

                        // {
                        //     name: 'DEA',
                        //     type: 'line',
                        //     xAxisIndex: 1,
                        //     yAxisIndex: 1,
                        //     data: resultData.dea,
                        //     smooth: true,
                        //     lineStyle: {
                        //         normal: {
                        //             opacity: 1,
                        //             type: 'solid',
                        //             width: 1,
                        //             color: 'yellow'
                        //         },
                        //     },
                        //     symbol: 'none',
                        //     animation: false,
                        //     markPoint: {
                        //         data: resultData.macdAreaValues
                        //     },
                        // },
                        //index 8
                        //大级别MACD
                        // {
                        //     name: 'BigMACD',
                        //     type: 'bar',
                        //     xAxisIndex: 2,
                        //     yAxisIndex: 2,
                        //     data: resultData.macdBigLevel,
                        //     barWidth: 3,
                        //     itemStyle: {
                        //         normal: {
                        //             color: function (params) {
                        //                 var colorList;
                        //
                        //                 if (params.data >= 0) {
                        //                     if (params.data >= bigMacdUpLastValue) {
                        //                         colorList = macdUpDarkColor
                        //                     } else {
                        //                         colorList = macdUpLightColor
                        //                     }
                        //                     bigMacdUpLastValue = params.data
                        //                 } else {
                        //                     if (params.data <= bigMacdDownLastValue) {
                        //                         colorList = macdDownDarkColor
                        //                     } else {
                        //                         colorList = macdDownLightColor
                        //                     }
                        //                     bigMacdDownLastValue = params.data
                        //                 }
                        //                 return colorList;
                        //             },
                        //         }
                        //     }
                        // },
                        // {
                        //     name: 'DIFF',
                        //     type: 'line',
                        //     xAxisIndex: 2,
                        //     yAxisIndex: 2,
                        //     data: resultData.diffBigLevel,
                        //     smooth: true,
                        //     lineStyle: {
                        //         normal: {
                        //             opacity: 1,
                        //             type: 'solid',
                        //             width: 1,
                        //             color: 'white'
                        //         },
                        //     },
                        //     symbol: 'none',
                        //     animation: false,
                        //     markPoint: {
                        //         // data: resultData.bcMACDValues
                        //     },
                        // },
                        //index 9
                        // {
                        //     name: 'DEA',
                        //     type: 'line',
                        //     xAxisIndex: 2,
                        //     yAxisIndex: 2,
                        //     data: resultData.deaBigLevel,
                        //     smooth: true,
                        //     lineStyle: {
                        //         normal: {
                        //             opacity: 1,
                        //             type: 'solid',
                        //             width: 1,
                        //             color: 'yellow'
                        //         },
                        //     },
                        //     symbol: 'none',
                        //     animation: false
                        // },
                        //index 10
                        // {
                        //     name: 'Volume',
                        //     type: 'bar',
                        //     xAxisIndex: 3,
                        //     yAxisIndex: 3,
                        //     data: resultData.volume,
                        //     itemStyle: {
                        //         normal: {
                        //             color: function (params) {
                        //                 var colorList;
                        //                 // fix
                        //                 if (!resultData.values[params.dataIndex]) {
                        //                     return 'red'
                        //                 }
                        //                 if (resultData.values[params.dataIndex][1] > resultData.values[params.dataIndex][0]) {
                        //                     colorList = 'red';
                        //                 } else {
                        //                     colorList = downColor;
                        //                 }
                        //                 return colorList;
                        //             },
                        //         }
                        //     }
                        // },

                    ],
                    graphic: [],
                };
            }
            // 更新均线颜色
            // option.series[16].lineStyle.color = {
            //     colorStops: colorStops
            //
            // }
            currentChart.setOption(option);
        },
        splitData(jsonObj, period) {
            const stockDate = jsonObj.date;
            const stockHigh = jsonObj.high;
            const stockLow = jsonObj.low;
            const stockOpen = jsonObj.open;
            const stockClose = jsonObj.close;
            const volumeData = jsonObj.volume;

            const bidata = jsonObj.bidata;
            const duandata = jsonObj.duandata;
            const higherDuanData = jsonObj.higherDuanData;

            // console.log('bidata', bidata);
            // console.log('duandata', duandata);

            const zsdata = jsonObj.zsdata;
            const zsflag = jsonObj.zsflag;

            const duan_zsdata = jsonObj.duan_zsdata;
            const duan_zsflag = jsonObj.duan_zsflag;

            const higher_duan_zsdata = jsonObj.higher_duan_zsdata;
            const higher_duan_zsflag = jsonObj.higher_duan_zsflag;


            //
            // const macddata = jsonObj.macd;
            // const diffdata = jsonObj.diff;
            // const deadata = jsonObj.dea;

            // const macdBigLevel = jsonObj.macdBigLevel;
            // const diffBigLevel = jsonObj.diffBigLevel;
            // const deaBigLevel = jsonObj.deaBigLevel;
            // const dateBigLevel = jsonObj.dateBigLevel;

            var values = [];
            for (var i = 0; i < stockDate.length; i++) {
                values.push([stockOpen[i], stockClose[i], stockLow[i], stockHigh[i]]);
            }

            var biValues = [];
            for (var i = 0; i < bidata.date.length; i++) {
                biValues.push([bidata.date[i], bidata.data[i]])
            }
            var duanValues = [];
            for (var i = 0; i < duandata.date.length; i++) {
                duanValues.push([duandata.date[i], duandata.data[i]])
            }
            var duanPriceValues = [];
            for (var i = 0; i < duandata.date.length; i++) {
                var value = {}
                if (i > 0 && duandata.data[i] > duandata.data[i - 1]) {
                    value = {
                        coord: [duandata.date[i], duandata.data[i]],
                        value: duandata.data[i],
                        symbolRotate: 0,
                        symbolSize: 5,
                        symbol: 'circle',
                        itemStyle: {
                            normal: {color: downColor}
                        },
                        label: {
                            position: 'inside',
                            offset: [0, -10],
                            textBorderColor: downColor,
                            textBorderWidth: 2,
                            color: 'white',
                        },
                    }
                } else {
                    value = {
                        coord: [duandata.date[i], duandata.data[i]],
                        value: duandata.data[i],
                        symbolRotate: 0,
                        symbolSize: 5,
                        symbol: 'circle',
                        itemStyle: {
                            normal: {color: upColor}
                        },
                        label: {
                            position: 'inside',
                            offset: [0, 10],
                            textBorderColor: upColor,
                            textBorderWidth: 2,
                            color: 'white',
                        },
                    };
                }

                duanPriceValues.push(value);
            }

            var higherDuanValues = [];
            for (var i = 0; i < higherDuanData.date.length; i++) {
                higherDuanValues.push([higherDuanData.date[i], higherDuanData.data[i]])
            }


            var zsvalues = [];
            for (var i = 0; i < zsdata.length; i++) {
                var value;
                if (zsflag[i] > 0) {
                    value = [
                        {
                            coord: zsdata[i][0],
                            itemStyle: {
                                color: upColor,
                                borderWidth: '2',
                                borderColor: 'red',
                                opacity: 0.2,
                            }
                        },
                        {
                            coord: zsdata[i][1],
                            itemStyle: {
                                color: upColor,
                                borderWidth: '1',
                                borderColor: upColor,
                                opacity: 0.2,
                            }
                        }
                    ];
                } else {
                    value = [
                        {
                            coord: zsdata[i][0],
                            itemStyle: {
                                color: downColor,
                                borderWidth: '1',
                                borderColor: downColor,
                                opacity: 0.2,
                            }
                        },
                        {
                            coord: zsdata[i][1],
                            itemStyle: {
                                color: downColor,
                                borderWidth: '1',
                                borderColor: downColor,
                                opacity: 0.2,
                            }
                        }
                    ];
                }
                zsvalues.push(value);
            }
            //段中枢
            for (var i = 0; i < duan_zsdata.length; i++) {
                var value;
                if (duan_zsflag[i] > 0) {
                    value = [
                        {
                            coord: duan_zsdata[i][0],
                            itemStyle: {
                                color: higherUpColor,
                                borderWidth: '2',
                                borderColor: higherUpColor,
                                opacity: 0.2,
                            }
                        },
                        {
                            coord: duan_zsdata[i][1],
                            itemStyle: {
                                color: higherUpColor,
                                borderWidth: '1',
                                borderColor: higherUpColor,
                                opacity: 0.2,
                            }
                        }
                    ];
                } else {
                    value = [
                        {
                            coord: duan_zsdata[i][0],
                            itemStyle: {
                                color: higherDownColor,
                                borderWidth: '1',
                                borderColor: higherDownColor,
                                opacity: 0.2,
                            }
                        },
                        {
                            coord: duan_zsdata[i][1],
                            itemStyle: {
                                color: higherDownColor,
                                borderWidth: '1',
                                borderColor: higherDownColor,
                                opacity: 0.2,
                            }
                        }
                    ];
                }
                zsvalues.push(value);
            }
            //高级别段中枢
            for (var i = 0; i < higher_duan_zsdata.length; i++) {
                var value;
                if (higher_duan_zsflag[i] > 0) {
                    value = [
                        {
                            coord: higher_duan_zsdata[i][0],
                            itemStyle: {
                                color: higherHigherUpColor,
                                borderWidth: '2',
                                borderColor: higherHigherUpColor,
                                opacity: 0.1,
                            }
                        },
                        {
                            coord: higher_duan_zsdata[i][1],
                            itemStyle: {
                                color: higherHigherUpColor,
                                borderWidth: '1',
                                borderColor: higherHigherUpColor,
                                opacity: 0.1,
                            }
                        }
                    ];
                } else {
                    value = [
                        {
                            coord: higher_duan_zsdata[i][0],
                            itemStyle: {
                                color: higherHigherDownColor,
                                borderWidth: '1',
                                borderColor: higherHigherDownColor,
                                opacity: 0.1,
                            }
                        },
                        {
                            coord: higher_duan_zsdata[i][1],
                            itemStyle: {
                                color: higherHigherDownColor,
                                borderWidth: '1',
                                borderColor: higherHigherDownColor,
                                opacity: 0.1,
                            }
                        }
                    ];
                }
                zsvalues.push(value);
            }


            // 中枢拉回
            var huilaValues = [];
            for (var i = 0; i < jsonObj.buy_zs_huila.date.length; i++) {
                var value = {
                    coord: [jsonObj.buy_zs_huila.date[i], jsonObj.buy_zs_huila.data[i]],
                    value: jsonObj.buy_zs_huila.data[i]+jsonObj.buy_zs_huila.tag[i],
                    symbolRotate: -90,
                    symbol: 'pin',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: upColor, opacity: '0.9'}
                    },
                    label: {
                        //position: ['-50%','50%'],
                        position: 'inside',
                        offset: [5, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        //borderColor: 'blue',
                        //borderWidth: 1,
                    },
                };
                huilaValues.push(value);
            }
            for (var i = 0; i < jsonObj.sell_zs_huila.date.length; i++) {
                var value = {
                    coord: [jsonObj.sell_zs_huila.date[i], jsonObj.sell_zs_huila.data[i]],
                    value: jsonObj.sell_zs_huila.data[i]+jsonObj.sell_zs_huila.tag[i],
                    symbolRotate: 90,
                    symbol: 'pin',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: downColor, opacity: '0.9'}
                    },
                    label: {
                        //position: ['-50%','50%'],
                        position: 'inside',
                        offset: [-5, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        //borderColor: 'blue',
                        //borderWidth: 1,
                    },
                };
                huilaValues.push(value);
            }
            // 大级别中枢拉回
            for (var i = 0; i < jsonObj.buy_zs_huila_higher.date.length; i++) {
                var value = {
                    coord: [jsonObj.buy_zs_huila_higher.date[i], jsonObj.buy_zs_huila_higher.data[i]],
                    value: jsonObj.buy_zs_huila_higher.data[i]+jsonObj.buy_zs_huila_higher.tag[i],
                    symbolRotate: -90,
                    symbol: 'pin',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: higherUpColor, opacity: '0.9'}
                    },
                    label: {
                        //position: ['-50%','50%'],
                        position: 'inside',
                        offset: [5, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        //borderColor: 'blue',
                        //borderWidth: 1,
                    },
                };
                huilaValues.push(value);
            }
            for (var i = 0; i < jsonObj.sell_zs_huila_higher.date.length; i++) {
                var value = {
                    coord: [jsonObj.sell_zs_huila_higher.date[i], jsonObj.sell_zs_huila_higher.data[i]],
                    value: jsonObj.sell_zs_huila_higher.data[i]+jsonObj.sell_zs_huila_higher.tag[i],
                    symbolRotate: 90,
                    symbol: 'pin',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: higherDownColor, opacity: '0.9'}
                    },
                    label: {
                        //position: ['-50%','50%'],
                        position: 'inside',
                        offset: [-5, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        //borderColor: 'blue',
                        //borderWidth: 1,
                    },
                };
                huilaValues.push(value);
            }
            // 中枢突破
            for (var i = 0; i < jsonObj.buy_zs_tupo.date.length; i++) {
                var value = {
                    coord: [jsonObj.buy_zs_tupo.date[i], jsonObj.buy_zs_tupo.data[i]],
                    value: jsonObj.buy_zs_tupo.data[i],
                    symbolRotate: 0,
                    symbol: 'arrow',
                    symbolSize: 30,
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: upColor, opacity: '0.9'}
                    },
                    label: {
                        //position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        //borderColor: 'blue',
                        //borderWidth: 1,
                    },
                };
                huilaValues.push(value);
            }

            for (var i = 0; i < jsonObj.sell_zs_tupo.date.length; i++) {
                var value = {
                    coord: [jsonObj.sell_zs_tupo.date[i], jsonObj.sell_zs_tupo.data[i]],
                    value: jsonObj.sell_zs_tupo.data[i],
                    symbolRotate: 180,
                    symbolSize: 30,
                    symbol: 'arrow',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: downColor, opacity: '0.9'}
                    },
                    label: {
                        //position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        //borderColor: 'blue',
                        //borderWidth: 1,
                    },
                };
                huilaValues.push(value);
            }
            //大级别中枢突破
            for (var i = 0; i < jsonObj.buy_zs_tupo_higher.date.length; i++) {
                var value = {
                    coord: [jsonObj.buy_zs_tupo_higher.date[i], jsonObj.buy_zs_tupo_higher.data[i]],
                    value: jsonObj.buy_zs_tupo_higher.data[i],
                    symbolRotate: 0,
                    symbolSize: 30,
                    symbol: 'arrow',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: higherUpColor, opacity: '0.9'}
                    },
                    label: {
                        //position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        //borderColor: 'blue',
                        //borderWidth: 1,
                    },
                };
                huilaValues.push(value);
            }
            for (var i = 0; i < jsonObj.sell_zs_tupo_higher.date.length; i++) {
                var value = {
                    coord: [jsonObj.sell_zs_tupo_higher.date[i], jsonObj.sell_zs_tupo_higher.data[i]],
                    value: jsonObj.sell_zs_tupo_higher.data[i],
                    symbolRotate: 180,
                    symbolSize: 30,
                    symbol: 'arrow',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: higherDownColor, opacity: '0.9'}
                    },
                    label: {
                        //position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        //borderColor: 'blue',
                        //borderWidth: 1,
                    },
                };
                huilaValues.push(value);
            }
            // 3买卖V反
            for (var i = 0; i < jsonObj.buy_v_reverse.date.length; i++) {
                var value = {
                    coord: [jsonObj.buy_v_reverse.date[i], jsonObj.buy_v_reverse.data[i]],
                    value: jsonObj.buy_v_reverse.data[i],
                    symbolRotate: 0,
                    symbol: 'diamond',
                    symbolSize: 30,
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: upColor, opacity: '0.9'}
                    },
                    label: {
                        //position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        //borderColor: 'blue',
                        //borderWidth: 1,
                    },
                };
                huilaValues.push(value);
            }

            for (var i = 0; i < jsonObj.sell_v_reverse.date.length; i++) {
                var value = {
                    coord: [jsonObj.sell_v_reverse.date[i], jsonObj.sell_v_reverse.data[i]],
                    value: jsonObj.sell_v_reverse.data[i],
                    symbolRotate: 180,
                    symbolSize: 30,
                    symbol: 'diamond',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: downColor, opacity: '0.9'}
                    },
                    label: {
                        //position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        //borderColor: 'blue',
                        //borderWidth: 1,
                    },
                };
                huilaValues.push(value);
            }

            // 3买卖V反 大级别
            for (var i = 0; i < jsonObj.buy_v_reverse_higher.date.length; i++) {
                var value = {
                    coord: [jsonObj.buy_v_reverse_higher.date[i], jsonObj.buy_v_reverse_higher.data[i]],
                    value: jsonObj.buy_v_reverse_higher.data[i],
                    symbolRotate: 0,
                    symbol: 'diamond',
                    symbolSize: 30,
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: higherUpColor, opacity: '0.9'}
                    },
                    label: {
                        //position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        //borderColor: 'blue',
                        //borderWidth: 1,
                    },
                };
                huilaValues.push(value);
            }

            for (var i = 0; i < jsonObj.sell_v_reverse_higher.date.length; i++) {
                var value = {
                    coord: [jsonObj.sell_v_reverse_higher.date[i], jsonObj.sell_v_reverse_higher.data[i]],
                    value: jsonObj.sell_v_reverse_higher.data[i],
                    symbolRotate: 180,
                    symbolSize: 30,
                    symbol: 'diamond',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: higherDownColor, opacity: '0.9'}
                    },
                    label: {
                        //position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        //borderColor: 'blue',
                        //borderWidth: 1,
                    },
                };
                huilaValues.push(value);
            }


            // 线段破坏
            for (var i = 0; i < jsonObj.buy_duan_break.date.length; i++) {
                var value = {
                    coord: [jsonObj.buy_duan_break.date[i], jsonObj.buy_duan_break.data[i]],
                    value: jsonObj.buy_duan_break.data[i],
                    symbolRotate: 0,
                    symbol: 'circle',
                    symbolSize: 10,
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: upColor, opacity: '0.9'}
                    },
                    label: {
                        //position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        //borderColor: 'blue',
                        //borderWidth: 1,
                    },
                };
                huilaValues.push(value);
            }

            for (var i = 0; i < jsonObj.sell_duan_break.date.length; i++) {
                var value = {
                    coord: [jsonObj.sell_duan_break.date[i], jsonObj.sell_duan_break.data[i]],
                    value: jsonObj.sell_duan_break.data[i],
                    symbolRotate: 180,
                    symbolSize: 10,
                    symbol: 'circle',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: downColor, opacity: '0.9'}
                    },
                    label: {
                        //position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        //borderColor: 'blue',
                        //borderWidth: 1,
                    },
                };
                huilaValues.push(value);
            }
            //大级别线段破坏
            for (var i = 0; i < jsonObj.buy_duan_break_higher.date.length; i++) {
                var value = {
                    coord: [jsonObj.buy_duan_break_higher.date[i], jsonObj.buy_duan_break_higher.data[i]],
                    value: jsonObj.buy_duan_break_higher.data[i],
                    symbolRotate: 0,
                    symbolSize: 10,
                    symbol: 'circle',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: higherUpColor, opacity: '0.9'}
                    },
                    label: {
                        //position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        //borderColor: 'blue',
                        //borderWidth: 1,
                    },
                };
                huilaValues.push(value);
            }
            for (var i = 0; i < jsonObj.sell_duan_break_higher.date.length; i++) {
                var value = {
                    coord: [jsonObj.sell_duan_break_higher.date[i], jsonObj.sell_duan_break_higher.data[i]],
                    value: jsonObj.sell_duan_break_higher.data[i],
                    symbolRotate: 180,
                    symbolSize: 10,
                    symbol: 'circle',
                    symbolOffset: [0, '0%'],
                    itemStyle: {
                        normal: {color: higherDownColor, opacity: '0.9'}
                    },
                    label: {
                        //position: ['-50%','50%'],
                        position: 'inside',
                        offset: [0, 5],
                        textBorderColor: 'red',
                        textBorderWidth: 3,
                        color: 'white',
                        //borderColor: 'blue',
                        //borderWidth: 1,
                    },
                };
                huilaValues.push(value);
            }


            // 买卖点
            // var mmdValues = [];
            // for (var i = 0; i < jsonObj.buyData.date.length; i++) {
            //     var value = {
            //         coord: [jsonObj.buyData.date[i], jsonObj.buyData.data[i]],
            //         value: jsonObj.buyData.value[i],
            //         symbolRotate: -180,
            //         symbol: 'pin',
            //         symbolOffset: [0, '0%'],
            //         itemStyle: {
            //             normal: {color: 'red', opacity: '0.9'}
            //         },
            //         label: {
            //             //position: ['-50%','50%'],
            //             position: 'inside',
            //             offset: [0, 10],
            //             textBorderColor: 'red',
            //             textBorderWidth: 3,
            //             color: 'white',
            //             //borderColor: 'blue',
            //             //borderWidth: 1,
            //         },
            //     };
            //     mmdValues.push(value);
            // }
            // for (var i = 0; i < jsonObj.sellData.date.length; i++) {
            //     var value = {
            //         coord: [jsonObj.sellData.date[i], jsonObj.sellData.data[i]],
            //         value: jsonObj.sellData.value[i],
            //
            //         itemStyle: {
            //             normal: {color: 'green', opacity: '0.9'}
            //         }
            //     };
            //     mmdValues.push(value);
            // }
            //var value = {
            //    name: 'lowest value',
            //    type: 'min',
            //    valueDim: 'lowest',
            //    symbolRotate: -90,
            //    symbol: 'pin',
            //    itemStyle: {
            //        normal: {
            //            color: 'white',
            //            opacity: '0.75'
            //        }
            //    },
            //    label: {
            //        position: 'inside',
            //        offset: [8, 2],
            //
            //        //textBorderWidth: 1,
            //        color: 'blue',
            //    },
            //};
            //mmdValues.push(value);
            //var value = {
            //    name: 'highest value',
            //    type: 'max',
            //    valueDim: 'highest',
            //    symbolRotate: -90,
            //    symbol: 'pin',
            //    itemStyle: {
            //        normal: {
            //            color: 'white',
            //            opacity: '0.75'
            //        }
            //    },
            //    label: {
            //        position: 'inside',
            //        offset: [8, 2],
            //        //textBorderColor: 'blue',
            //        //textBorderWidth: 1,
            //        color: 'blue',
            //    },
            //};
            //mmdValues.push(value);

            // for (var i = 0; i < jsonObj.buyBCData.date.length; i++) {
            //     var value = {
            //         coord: [jsonObj.buyBCData.date[i], jsonObj.buyBCData.data[i]],
            //         value: jsonObj.buyBCData.value[i],
            //         symbolRotate: 90,
            //         symbol: 'pin',
            //         itemStyle: {
            //             normal: {color: 'red', opacity: '0.85'}
            //         },
            //         label: {
            //             position: 'inside',
            //             offset: [-5, 2],
            //             textBorderColor: 'red',
            //             textBorderWidth: 2,
            //             color: 'white',
            //         },
            //     };
            //     mmdValues.push(value);
            // }
            // for (var i = 0; i < jsonObj.sellBCData.date.length; i++) {
            //     var value = {
            //         coord: [jsonObj.sellBCData.date[i], jsonObj.sellBCData.data[i]],
            //         value: jsonObj.sellBCData.value[i],
            //         symbolRotate: 90,
            //         symbol: 'pin',
            //         itemStyle: {
            //             normal: {color: 'green', opacity: '0.85'}
            //         },
            //         label: {
            //             position: 'inside',
            //             offset: [-5, 2],
            //             textBorderColor: 'red',
            //             textBorderWidth: 2,
            //             color: 'white',
            //         },
            //     };
            //     mmdValues.push(value);
            // }
            //
            // var macdAreaValues = [];
            // for (var i = 0; i < jsonObj.macdAreaData.date.length; i++) {
            //     var value
            //     if (jsonObj.macdAreaData.value[i] > 0) {
            //         value = {
            //             coord: [jsonObj.macdAreaData.date[i], jsonObj.macdAreaData.data[i]],
            //             value: jsonObj.macdAreaData.value[i],
            //             symbolRotate: 180,
            //             symbol: 'circle',
            //             symbolSize: '5',
            //             itemStyle: {
            //                 normal: {color: downColor}
            //             },
            //             label: {
            //                 position: 'inside',
            //                 offset: [0, -30],
            //                 textBorderColor: upColor,
            //                 textBorderWidth: 2,
            //                 color: 'white',
            //             },
            //         };
            //     } else {
            //         value = {
            //             coord: [jsonObj.macdAreaData.date[i], jsonObj.macdAreaData.data[i]],
            //             value: Math.abs(jsonObj.macdAreaData.value[i]),
            //             symbolRotate: 180,
            //             symbol: 'circle',
            //             symbolSize: '5',
            //             itemStyle: {
            //                 normal: {color: upColor}
            //             },
            //             label: {
            //                 position: 'inside',
            //                 offset: [0, 20],
            //                 textBorderColor: downColor,
            //                 textBorderWidth: 2,
            //                 color: 'white',
            //             },
            //         };
            //     }
            //
            //     macdAreaValues.push(value);
            // }


            // var bcMACDValues = [];
            // for (var i = 0; i < jsonObj.buyMACDBCData.date.length; i++) {
            //     var value = {
            //         coord: [jsonObj.buyMACDBCData.date[i], jsonObj.buyMACDBCData.data[i]],
            //         value: jsonObj.buyMACDBCData.value[i],
            //         symbolRotate: -180,
            //         symbol: 'pin',
            //         itemStyle: {
            //             normal: {color: 'red'}
            //         },
            //         label: {
            //             position: 'inside',
            //             offset: [0, 10],
            //             textBorderColor: 'red',
            //             textBorderWidth: 2,
            //             color: 'white',
            //         },
            //     };
            //     bcMACDValues.push(value);
            // }
            // for (var i = 0; i < jsonObj.sellMACDBCData.date.length; i++) {
            //     var value = {
            //         coord: [jsonObj.sellMACDBCData.date[i], jsonObj.sellMACDBCData.data[i]],
            //         value: jsonObj.sellMACDBCData.value[i],
            //         symbolRotate: 0,
            //         symbol: 'pin',
            //         itemStyle: {
            //             normal: {color: 'green'}
            //         }
            //     };
            //     bcMACDValues.push(value);
            // }
            var markLineData = [];
            var lastBeichiType = getLastBeichiData(jsonObj)
            var lastBeichi = null
            const margin_rate = this.futureSymbolMap[this.symbol] && this.futureSymbolMap[this.symbol].margin_rate || 1;
            let marginLevel = Number((1 / (margin_rate * this.marginLevelCompany)).toFixed(2))
            // 当前价格
            var currentPrice = stockClose[stockClose.length - 1]
            // 合约乘数
            this.contractMultiplier = this.futureSymbolMap[this.symbol] && this.futureSymbolMap[this.symbol].contract_multiplier || 1;
            // 1手需要的保证金
            this.marginPrice = (this.contractMultiplier * currentPrice / marginLevel).toFixed(0)
            // console.log("最后的背驰:", period, lastBeichiType)
            if (lastBeichiType !== 0) {
                switch (lastBeichiType) {
                    // 回拉
                    case 1:
                        lastBeichi = jsonObj.buy_zs_huila
                        break
                    case 2:
                        lastBeichi = jsonObj.buy_zs_huila_higher
                        break
                    case 3:
                        lastBeichi = jsonObj.sell_zs_huila
                        break
                    case 4:
                        lastBeichi = jsonObj.sell_zs_huila_higher
                        break
                    //线段破坏
                    case 5:
                        lastBeichi = jsonObj.buy_duan_break
                        break
                    case 6:
                        lastBeichi = jsonObj.buy_duan_break_higher
                        break
                    case 7:
                        lastBeichi = jsonObj.sell_duan_break
                        break
                    case 8:
                        lastBeichi = jsonObj.sell_duan_break_higher
                        break
                    //突破
                    case 9:
                        lastBeichi = jsonObj.buy_zs_tupo
                        break
                    case 10:
                        lastBeichi = jsonObj.buy_zs_tupo_higher
                        break
                    case 11:
                        lastBeichi = jsonObj.sell_zs_tupo
                        break
                    case 12:
                        lastBeichi = jsonObj.sell_zs_tupo_higher
                        break
                    // V反
                    case 13:
                        lastBeichi = jsonObj.buy_v_reverse
                        break
                    case 14:
                        lastBeichi = jsonObj.buy_v_reverse_higher
                        break
                    case 15:
                        lastBeichi = jsonObj.sell_v_reverse
                        break
                    case 16:
                        lastBeichi = jsonObj.sell_v_reverse_higher
                        break

                }
                // 背驰时的价格
                var beichiPrice = lastBeichi['data'][lastBeichi['data'].length - 1]
                // 止损价格
                var stopLosePrice = lastBeichi['stop_lose_price'][lastBeichi['stop_lose_price'].length - 1]
                // 第一次成笔的止盈价格
                var stopWinPrice = lastBeichi['stop_win_price'][lastBeichi['stop_win_price'].length - 1]
                //第一次成笔的止盈百分比
                var stopWinPercent = 0
                // 止盈价格
                var targetPrice = 0
                var diffPrice = Math.abs(beichiPrice - stopLosePrice)
                // 当前收益百分比
                var currentPercent = ""
                // 当前收益（单位万/元）
                var currentProfit = ""
                if (lastBeichiType === 1 || lastBeichiType === 2 || lastBeichiType === 5 || lastBeichiType === 6 ||
                    lastBeichiType === 9 || lastBeichiType === 10 || lastBeichiType === 13 || lastBeichiType === 14) {
                    targetPrice = beichiPrice + diffPrice
                    currentPercent = ((currentPrice - beichiPrice) / beichiPrice * 100 * marginLevel).toFixed(2)
                    if (stopWinPrice !== 0) {
                        stopWinPercent = ((stopWinPrice - beichiPrice) / beichiPrice * 100 * marginLevel).toFixed(2)
                    }
                } else {
                    targetPrice = beichiPrice - diffPrice
                    currentPercent = ((beichiPrice - currentPrice) / beichiPrice * 100 * marginLevel).toFixed(2)
                    if (stopWinPrice !== 0) {
                        stopWinPercent = ((beichiPrice - stopWinPrice) / beichiPrice * 100 * marginLevel).toFixed(2)
                    }
                }
                var targetPercent = (Math.abs(beichiPrice - stopLosePrice) / beichiPrice * 100 * marginLevel).toFixed(2)
                // 准备参数
                this.openPrice = beichiPrice;
                this.stopPrice = stopLosePrice;
                // 当前保证金比例
                const margin_rate = this.futureSymbolMap[this.symbol] && this.futureSymbolMap[this.symbol].margin_rate || 1;
                this.currentMarginRate = margin_rate * this.marginLevelCompany
                this.currentSymbol = this.symbol;
                // 计算开仓手数
                this.calcAccount()
                // console.log(beichiPrice, stopLosePrice, diffPrice, targetPrice)
                // 单位是万
                currentProfit = ((this.maxOrderCount * this.marginPrice * Number(currentPercent) / 100) / 10000).toFixed(2)
                // 当前最新价
                if (currentPrice) {
                    var markLineCurrent = {
                        yAxis: currentPrice,
                        lineStyle: {
                            normal: {
                                opacity: 1,
                                type: 'dash',
                                width: 1,
                                color: 'yellow'
                            },
                        },
                        symbol: 'circle',
                        symbolSize: 1,
                        label: {
                            normal: {
                                color: 'yellow',
                                formatter: '最新价: ' + currentPrice.toFixed(2) + "\n盈利率: " + currentPercent + "% \n盈利额: " + currentProfit + " 万 \n盈亏比: 1 : "
                                    + (currentPercent / targetPercent).toFixed(1),
                            },
                        },
                    }
                    markLineData.push(markLineCurrent)
                }

                // 保本位
                if (beichiPrice) {
                    var markLineBeichi = {
                        yAxis: beichiPrice,
                        lineStyle: {
                            normal: {
                                opacity: 1,
                                type: 'dashed',
                                width: 1,
                                color: 'white'
                            },
                        },
                        symbol: 'circle',
                        symbolSize: 1,
                        label: {
                            normal: {
                                color: 'white',
                                formatter: '开仓: ' + beichiPrice.toFixed(2) + "\n数量: " + this.maxOrderCount + ' 手',
                            },
                        },
                    }
                    markLineData.push(markLineBeichi)
                }

                //止损位
                if (stopLosePrice) {
                    var markLineStop = {
                        yAxis: stopLosePrice,
                        lineStyle: {
                            normal: {
                                opacity: 1,
                                type: 'dashed',
                                width: 1,
                                color: upColor
                            },
                        },
                        symbol: 'circle',
                        symbolSize: 1,
                        label: {
                            normal: {
                                color: upColor,
                                formatter: '止损: ' + stopLosePrice.toFixed(2) + '\n盈利率: -' + targetPercent + '%',
                            },
                        },
                    }
                    markLineData.push(markLineStop)
                }

                // 目标价位
                if (targetPrice) {
                    var markLineTarget = {
                        yAxis: targetPrice,
                        lineStyle: {
                            normal: {
                                opacity: 1,
                                type: 'dashed',
                                width: 1,
                                color: downColor
                            },
                        },
                        label: {
                            normal: {
                                color: downColor,
                                formatter: '动态止盈: ' + targetPrice.toFixed(2) + '\n (' + targetPercent + '%)',
                            }
                        },
                        symbol: 'circle',
                        symbolSize: 1,
                    }
                    markLineData.push(markLineTarget)
                }

                // 第一次成笔的目标价位
                // var markLineStopWin = {
                //     yAxis: stopWinPrice,
                //     lineStyle: {
                //         normal: {
                //             opacity: 1,
                //             type: 'dashed',
                //             width: 1,
                //             color: 'green'
                //         },
                //     },
                //     label: {
                //         normal: {
                //             color: 'green',
                //             formatter: '笔盈:' + stopWinPrice.toFixed(2) + ' (' + stopWinPercent + '%)',
                //         }
                //     },
                //     symbol: 'circle',
                //     symbolSize: 1,
                // }

                // if (stopWinPrice !== 0) {
                //     markLineData.push(markLineStopWin)
                // }

            }


            // console.log("markline", markLineData)


            // 高级别macd背驰点标注 buyHigherMACDBCData
            // for (var i = 0; i < jsonObj.buyHigherMACDBCData.date.length; i++) {
            //     var value = {
            //         coord: [jsonObj.buyHigherMACDBCData.date[i], jsonObj.buyHigherMACDBCData.data[i]],
            //         value: jsonObj.buyHigherMACDBCData.value[i],
            //         symbolRotate: 90,
            //         symbol: 'pin',
            //         itemStyle: {
            //             normal: {color: 'Purple'}
            //         },
            //         label: {
            //             position: 'inside',
            //             offset: [-5, 5],
            //             textBorderColor: 'Purple',
            //             textBorderWidth: 1,
            //             color: 'white',
            //         },
            //     };
            //     bcMACDValues.push(value);
            // }
            // for (var i = 0; i < jsonObj.sellHigherMACDBCData.date.length; i++) {
            //     var value = {
            //         coord: [jsonObj.sellHigherMACDBCData.date[i], jsonObj.sellHigherMACDBCData.data[i]],
            //         value: jsonObj.sellHigherMACDBCData.value[i],
            //         symbolRotate: 90,
            //         symbol: 'pin',
            //         label: {
            //             position: 'inside',
            //             offset: [-5, 5],
            //             textBorderColor: 'blue',
            //             textBorderWidth: 1,
            //             color: 'white',
            //         },
            //         itemStyle: {
            //             normal: {color: 'blue'}
            //         }
            //     };
            //     bcMACDValues.push(value);
            // }
            //
            return {
                time: stockDate,
                values: values,
                volume: volumeData,
                biValues: biValues,
                duanValues: duanValues,
                duanPriceValues: duanPriceValues,
                higherDuanValues: higherDuanValues,
                zsvalues: zsvalues,
                zsflag: zsflag,
                // macd: macddata,
                // diff: diffdata,
                // dea: deadata,
                // macdBigLevel: macdBigLevel,
                // diffBigLevel: diffBigLevel,
                // deaBigLevel: deaBigLevel,
                // timeBigLevel: dateBigLevel,
                // boll_up: boll_up,
                // boll_middle: boll_middle,
                // boll_bottom: boll_bottom,
                // mmdValues: mmdValues,
                // bcMACDValues: bcMACDValues,
                close: stockClose,
                // macdAreaValues: macdAreaValues,
                // ama: amaValues,

                markLineData: markLineData,
                huilaValues: huilaValues,

            };
        },
        //计算开仓手数
        calcAccount() {
            if (this.currentMarginRate == null) {
                alert("请选择保证金系数，开仓价，止损价")
                return
            }
            if (this.currentSymbol.indexOf("_CQ") === -1) {
                this.account = this.futuresAccount
                // 计算1手需要的保证金
                this.perOrderMargin = Math.floor(this.openPrice * this.contractMultiplier * this.currentMarginRate)
                this.perOrderStopMoney = Math.abs(this.openPrice - this.stopPrice) * this.contractMultiplier
                // 1手止损的百分比
                this.perOrderStopRate = (this.perOrderStopMoney / this.perOrderMargin).toFixed(2)
            } else {
                this.account = this.digitCoinAccount
                // 火币1张就是100usd  20倍杠杠 1张保证金是5usd
                this.perOrderMargin = 5
                this.perOrderStopRate = (Math.abs(this.openPrice - this.stopPrice) / this.openPrice + this.digitCoinFee) * 20
                this.perOrderStopMoney = Number((this.perOrderMargin * this.perOrderStopRate).toFixed(2))
            }

            // 计算最大能使用的资金
            let maxAccountUse = this.account * 10000 * this.maxAccountUseRate
            // 计算最大止损金额
            let maxStopMoney = this.account * 10000 * this.stopRate
            // 1手止损的金额

            // 根据止损算出的开仓手数(四舍五入)
            let maxOrderCount1 = Math.round(maxStopMoney / this.perOrderStopMoney)

            // 根据最大资金使用率算出的开仓手数(四舍五入)
            let maxOrderCount2 = Math.round(maxAccountUse / this.perOrderMargin)


            this.maxOrderCount = maxOrderCount1 > maxOrderCount2 ? maxOrderCount2 : maxOrderCount1
            // 总保证金
            this.totalOrderMargin = this.perOrderMargin * this.maxOrderCount

            // 总止损额
            this.totalOrderStopMoney = this.perOrderStopMoney * this.maxOrderCount

            // 计算当前资金使用率
            this.accountUseRate = ((this.maxOrderCount * this.perOrderMargin) / this.account / 10000).toFixed(2)

            // 计算动态止盈手数， 即剩下仓位被止损也不会亏钱
            // 动止手数 * （动止价-开仓价）* 合约乘数 = （开仓手数-动止手数）* 1手止损
            // 动止手数  = 开仓手数 * 1手止损  /( （动止价-开仓价）* 合约乘数 + 1手止损)
            // 如果填入了动止价
            if (this.dynamicWinPrice != null) {
                this.dynamicWinCount = Math.round(this.maxOrderCount * this.perOrderStopMoney / ((this.dynamicWinPrice - this.openPrice) * this.contractMultiplier + this.perOrderStopMoney))
            }
            console.log("maxAccountUse:", maxAccountUse, " maxStopMoney :", maxStopMoney, " perOrderMargin:",
                this.perOrderMargin, " maxOrderCount:", this.maxOrderCount, " maxOrderCount2:", maxOrderCount2, " perOrderStopMoney:", this.perOrderStopMoney,
                " accountUseRate:", this.accountUseRate, " perOrderStopRate:", this.perOrderStopRate)
        },
        //获取主力合约历史k线
        // historyKline(endDate) {
        //     console.log("click", this.symbol)
        //
        //     this.endDate = endDate
        //     console.log("endDate:",this.endDate)
        //     this.switchSymbol(this.symbol, "refresh")
        // },
        switchHistoryPeriod(period) {
            this.period = period;
            this.replaceParamVal("period", period)
            // this.switchSymbol(this.symbol, "refresh")
        },
        switchHistorySymbol(symbol) {
            this.symbol = symbol;
            this.replaceParamVal("symbol", symbol)
            // this.switchSymbol(this.symbol, "refresh")
        },
        replaceParamVal(paramName, replaceWith) {
            var oUrl = window.location.href.toString();
            var re = eval('/(' + paramName + '=)([^&]*)/gi');
            var nUrl = oUrl.replace(re, paramName + '=' + replaceWith);
            this.location = nUrl;
            window.location.href = nUrl
        }

    }
})


// const myChart1 = echarts.init(document.getElementById('main1'));
const myChart3 = echarts.init(document.getElementById('main3'));
const myChart5 = echarts.init(document.getElementById('main5'));
const myChart15 = echarts.init(document.getElementById('main15'));
const myChart30 = echarts.init(document.getElementById('main30'));
const myChart60 = echarts.init(document.getElementById('main60'));
const myChart240 = echarts.init(document.getElementById('main240'));
// const myChart1d = echarts.init(document.getElementById('main1d'));

const bgColor = '#202529';
const upColor = 'red';
const upBorderColor = 'red';
const downColor = '#14d0cd';
const downBorderColor = '#14d0cd';

const higherUpColor = "purple"
const higherDownColor = "green"

const higherHigherUpColor = "pink"
const higherHigherDownColor = "blue"


const macdUpDarkColor = '#EF5350'
const macdUpLightColor = '#FFCDD2'
const macdDownDarkColor = '#26A69A'
const macdDownLightColor = '#B2DFDB'
var macdUpLastValue = Number.MIN_SAFE_INTEGER
var macdDownLastValue = Number.MAX_SAFE_INTEGER
var bigMacdUpLastValue = Number.MIN_SAFE_INTEGER
var bigMacdDownLastValue = Number.MAX_SAFE_INTEGER

var amaLastValue = Number.MIN_SAFE_INTEGER
var amaFlag = false

// 自适应宽高
setTimeout(function () {
    window.onresize = function () {
        console.log('resize')
        // myChart1.resize();
    }
}, 200);

/**
 *
 * @param jsonObj
 * @returns number
 * 1 本级别买回拉  2 高级别买回拉  3 本级别卖回拉 4 高级别卖回拉
 * 5 本级别线段破坏买 6 高级别线段破坏买  7 本级别线段破坏卖 8 高级别线段破坏卖
 * 9 本级别中枢突破买 10 高级别中枢突破买 11 本级别中枢突破卖 12 高级别中枢突破卖
 * 13 本级别三卖V买 14 高级别三卖V买 15 本级别三买V卖 16 高级别三买V卖
 */
function getLastBeichiData(jsonObj) {
    // 回拉
    var buy_zs_huila = jsonObj.buy_zs_huila
    var buy_zs_huila_higher = jsonObj.buy_zs_huila_higher
    var sell_zs_huila = jsonObj.sell_zs_huila
    var sell_zs_huila_higher = jsonObj.sell_zs_huila_higher
    // 线段破坏
    var buy_duan_break = jsonObj.buy_duan_break
    var buy_duan_break_higher = jsonObj.buy_duan_break_higher
    var sell_duan_break = jsonObj.sell_duan_break
    var sell_duan_break_higher = jsonObj.sell_duan_break_higher

    // 突破
    var buy_zs_tupo = jsonObj.buy_zs_tupo
    var buy_zs_tupo_higher = jsonObj.buy_zs_tupo_higher
    var sell_zs_tupo = jsonObj.sell_zs_tupo
    var sell_zs_tupo_higher = jsonObj.sell_zs_tupo_higher

    // V反
    var buy_v_reverse = jsonObj.buy_v_reverse
    var buy_v_reverse_higher = jsonObj.buy_v_reverse_higher
    var sell_v_reverse = jsonObj.sell_v_reverse
    var sell_v_reverse_higher = jsonObj.sell_v_reverse_higher


    // 回拉
    var buy_zs_huila_stamp = 0
    var buy_zs_huila_higher_stamp = 0
    var sell_zs_huila_Stamp = 0
    var sell_zs_huila_higher_stamp = 0
    // 线段破坏
    var buy_duan_break_stamp = 0
    var buy_duan_break_higher_stamp = 0
    var sell_duan_break_stamp = 0
    var sell_duan_break_higher_stamp = 0
    // 突破
    var buy_zs_tupo_stamp = 0
    var buy_zs_tupo_higher_stamp = 0
    var sell_zs_tupo_stamp = 0
    var sell_zs_tupo_higher_stamp = 0
    // V反
    var buy_v_reverse_stamp = 0
    var buy_v_reverse_higher_stamp = 0
    var sell_v_reverse_stamp = 0
    var sell_v_reverse_higher_stamp = 0

    var buyTimeStr
    var higherBuyTimeStr
    var sellTimeStr
    var higherSellTimeStr
    // 回拉
    if (buy_zs_huila.date.length > 0) {
        buyTimeStr = buy_zs_huila.date[buy_zs_huila.date.length - 1]
        buy_zs_huila_stamp = timeStrToStamp(buyTimeStr)
    }
    if (buy_zs_huila_higher.date.length > 0) {
        higherBuyTimeStr = buy_zs_huila_higher.date[buy_zs_huila_higher.date.length - 1]
        buy_zs_huila_higher_stamp = timeStrToStamp(higherBuyTimeStr)
    }
    if (sell_zs_huila.date.length > 0) {
        sellTimeStr = sell_zs_huila.date[sell_zs_huila.date.length - 1]
        sell_zs_huila_Stamp = timeStrToStamp(sellTimeStr)
    }
    if (sell_zs_huila_higher.date.length > 0) {
        higherSellTimeStr = sell_zs_huila_higher.date[sell_zs_huila_higher.date.length - 1]
        sell_zs_huila_higher_stamp = timeStrToStamp(higherSellTimeStr)
    }

    // 线段破坏
    if (buy_duan_break.date.length > 0) {
        buyTimeStr = buy_duan_break.date[buy_duan_break.date.length - 1]
        buy_duan_break_stamp = timeStrToStamp(buyTimeStr)
    }
    if (buy_duan_break_higher.date.length > 0) {
        higherBuyTimeStr = buy_duan_break_higher.date[buy_duan_break_higher.date.length - 1]
        buy_duan_break_higher_stamp = timeStrToStamp(higherBuyTimeStr)
    }
    if (sell_duan_break.date.length > 0) {
        sellTimeStr = sell_duan_break.date[sell_duan_break.date.length - 1]
        sell_duan_break_stamp = timeStrToStamp(sellTimeStr)
    }
    if (sell_duan_break_higher.date.length > 0) {
        higherSellTimeStr = sell_duan_break_higher.date[sell_duan_break_higher.date.length - 1]
        sell_duan_break_higher_stamp = timeStrToStamp(higherSellTimeStr)
    }
    // 突破
    if (buy_zs_tupo.date.length > 0) {
        buyTimeStr = buy_zs_tupo.date[buy_zs_tupo.date.length - 1]
        buy_zs_tupo_stamp = timeStrToStamp(buyTimeStr)
    }
    if (buy_zs_tupo_higher.date.length > 0) {
        higherBuyTimeStr = buy_zs_tupo_higher.date[buy_zs_tupo_higher.date.length - 1]
        buy_zs_tupo_higher_stamp = timeStrToStamp(higherBuyTimeStr)
    }
    if (sell_zs_tupo.date.length > 0) {
        sellTimeStr = sell_zs_tupo.date[sell_zs_tupo.date.length - 1]
        sell_zs_tupo_stamp = timeStrToStamp(sellTimeStr)
    }
    if (sell_zs_tupo_higher.date.length > 0) {
        higherSellTimeStr = sell_zs_tupo_higher.date[sell_zs_tupo_higher.date.length - 1]
        sell_zs_tupo_higher_stamp = timeStrToStamp(higherSellTimeStr)
    }
    // V反
    if (buy_v_reverse.date.length > 0) {
        buyTimeStr = buy_v_reverse.date[buy_v_reverse.date.length - 1]
        buy_v_reverse_stamp = timeStrToStamp(buyTimeStr)
    }
    if (buy_v_reverse_higher.date.length > 0) {
        higherBuyTimeStr = buy_v_reverse_higher.date[buy_v_reverse_higher.date.length - 1]
        buy_v_reverse_higher_stamp = timeStrToStamp(higherBuyTimeStr)
    }
    if (sell_v_reverse.date.length > 0) {
        sellTimeStr = sell_v_reverse.date[sell_v_reverse.date.length - 1]
        sell_v_reverse_stamp = timeStrToStamp(sellTimeStr)
    }
    if (sell_v_reverse_higher.date.length > 0) {
        higherSellTimeStr = sell_v_reverse_higher.date[sell_v_reverse_higher.date.length - 1]
        sell_v_reverse_higher_stamp = timeStrToStamp(higherSellTimeStr)
    }


    // 当线段破坏和中枢突破时间相等的时候，使用中枢突破信号，因为中枢突破止损更小
    if (buy_zs_tupo_stamp === buy_duan_break_stamp) {
        buy_duan_break_stamp = 0
    }
    if (buy_zs_tupo_higher_stamp === buy_duan_break_higher_stamp) {
        buy_duan_break_higher_stamp = 0
    }
    if (sell_zs_tupo_stamp === sell_duan_break_stamp) {
        sell_duan_break_stamp = 0
    }
    if (sell_zs_tupo_higher_stamp === sell_duan_break_higher_stamp) {
        sell_duan_break_higher_stamp = 0
    }

    var timeArray = [buy_zs_huila_stamp, buy_zs_huila_higher_stamp, sell_zs_huila_Stamp, sell_zs_huila_higher_stamp,
        buy_duan_break_stamp, buy_duan_break_higher_stamp, sell_duan_break_stamp, sell_duan_break_higher_stamp,
        buy_zs_tupo_stamp, buy_zs_tupo_higher_stamp, sell_zs_tupo_stamp, sell_zs_tupo_higher_stamp,
        buy_v_reverse_stamp, buy_v_reverse_higher_stamp, sell_v_reverse_stamp, sell_v_reverse_higher_stamp]
    var maxPos = 0
    var maxTime = timeArray[0]
    for (var i = 0; i < timeArray.length; i++) {
        if (timeArray[i] > maxTime) {
            maxTime = timeArray[i]
            maxPos = i
        }
    }

    if (buy_zs_huila_stamp === 0 && buy_zs_huila_higher_stamp === 0 && sell_zs_huila_Stamp === 0 && sell_zs_huila_higher_stamp === 0 &&
        buy_duan_break_stamp === 0 && buy_duan_break_higher_stamp === 0 && sell_duan_break_stamp === 0 && sell_duan_break_higher_stamp === 0 &&
        buy_zs_tupo_stamp === 0 && buy_zs_tupo_higher_stamp === 0 && sell_zs_tupo_stamp === 0 && sell_zs_tupo_higher_stamp === 0 &&
        buy_v_reverse_stamp === 0 && buy_v_reverse_higher_stamp === 0 && sell_v_reverse_stamp === 0 && sell_v_reverse_higher_stamp
    ) {
        return 0
    } else {
        return maxPos + 1
    }
}


function timeStrToStamp(timeStr) {
    date = timeStr.substring(0, 19);
    date = timeStr.replace(/-/g, '/'); //必须把日期'-'转为'/'
    var timestamp = new Date(date).getTime();
    return timestamp
}

function calculateMA(resultData, dayCount) {
    var result = [];
    for (var i = 0, len = resultData.values.length; i < len; i++) {
        if (i < dayCount) {
            result.push('-');
            continue;
        }
        var sum = 0;
        for (var j = 0; j < dayCount; j++) {
            sum += resultData.values[i - j][1];
        }
        result.push((sum / dayCount).toFixed(5));
    }
    return result;
}

function sleep(delay) {
    var start = (new Date()).getTime();
    while ((new Date()).getTime() - start < delay) {
        continue;
    }
}

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

function goHome() {
    window.location.replace("./index.html")
}
