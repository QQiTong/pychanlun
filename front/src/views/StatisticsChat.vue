<template>

    <div class="statistic-echarts-main">
        <div class="block">
            <el-date-picker
                placeholder="选择日期"
                v-model="dateRange"
                @change="getStatisticList()"
                format="yyyy 年 MM 月 dd 日"
                value-format="yyyy-MM-dd"
                type="daterange"
                align="right"
                unlink-panels
                range-separator="to"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                size="mini"
                :picker-options="pickerOptions">
            </el-date-picker>
            <el-button @click="getStatisticList()" type="primary" size="mini" class="ml-5 primary-button">刷新</el-button>
            <div class="statistic-echarts-list">
                <div class="profit-chart" id="profit-chart-parent">
                    <div id="profit-chart"/>
                </div>
                <div class="pie-chart-list">
                    <div id="win-pie-chart-parent" class="pie-chart">
                        <div id="win-pie-chart"/>
                    </div>
                    <div id="lose-pie-chart-parent" class="pie-chart">
                        <div id="lose-pie-chart"/>
                    </div>
                </div>

            </div>

        </div>
    </div>

</template>
<script>
    import CommonTool from "../tool/CommonTool";
    import {futureApi} from "../api/futureApi";

    require('echarts/theme/macarons') // echarts theme

    export default {
        data() {
            return {
                statisticList: null,
                dateRange: [],
                profitChart: null,
                winPiechart: null,
                losePieChart: null,
                pickerOptions: {
                    shortcuts: [{
                        text: '最近一周',
                        onClick(picker) {
                            const end = new Date();
                            const start = new Date();
                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
                            picker.$emit('pick', [start, end]);
                        }
                    }, {
                        text: '最近一个月',
                        onClick(picker) {
                            const end = new Date();
                            const start = new Date();
                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
                            picker.$emit('pick', [start, end]);
                        }
                    }, {
                        text: '最近三个月',
                        onClick(picker) {
                            const end = new Date();
                            const start = new Date();
                            start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
                            picker.$emit('pick', [start, end]);
                        }
                    }]
                },
            }
        },
        mounted() {
            this.initChart()
            let now = new Date()
            let lastWeek = now.getTime() - 3600 * 1000 * 24 * 7
            const start = CommonTool.parseTime(lastWeek, '{y}-{m}-{d}')
            const end = CommonTool.dateFormat('yyyy-MM-dd')

            this.dateRange = [start, end]
            this.getStatisticList()
        },
        beforeDestroy() {
            if (!this.profitChart || !this.winPiechart || !this.losePieChart) {
                return
            }
            this.profitChart.dispose()
            this.profitChart = null
            this.winPiechart.dispose()
            this.winPiechart = null
            this.losePieChart.dispose()
            this.losePieChart = null
        },
        methods: {
            getStatisticList() {
                futureApi.getStatisticList(this.dateRange).then(res => {
                    console.log('统计图表:', res)
                    this.statisticList = res
                    this.processData()
                }).catch((error) => {
                    console.log('获取统计图表失败:', error)
                })
            },
            processData() {
                // 盈利列表
                this.profitChart.setOption({
                    backgroundColor: '#12161c',
                    title: {
                        text: '统计',
                        x: '20',
                        top: '20',
                        textStyle: {
                            color: '#fff',
                            fontSize: '22'
                        },
                        subtextStyle: {
                            color: '#fff',
                            fontSize: '16'
                        }
                    },
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            textStyle: {
                                color: '#fff'
                            }
                        }
                    },
                    grid: {
                        left: '5%',
                        right: '5%',
                        borderWidth: 0,
                        top: 150,
                        bottom: 95,
                        textStyle: {
                            color: '#fff'
                        }
                    },
                    legend: {
                        x: '5%',
                        top: '10%',
                        textStyle: {
                            color: '#fff'
                        },
                        data: ['盈利', '亏损', '净盈利']
                    },
                    calculable: true,
                    xAxis: [{
                        type: 'category',
                        axisLine: {
                            lineStyle: {
                                color: '#fff'
                            }
                        },
                        splitLine: {
                            show: false
                        },
                        axisTick: {
                            show: false
                        },
                        splitArea: {
                            show: false
                        },
                        axisLabel: {
                            interval: 0

                        },
                        data: this.statisticList.date
                    }],
                    yAxis: [{
                        type: 'value',
                        splitLine: {
                            show: false
                        },
                        axisLine: {
                            lineStyle: {
                                color: '#fff'
                            }
                        },
                        axisTick: {
                            show: false
                        },
                        axisLabel: {
                            interval: 0
                        },
                        splitArea: {
                            show: false
                        }
                    }],
                    dataZoom: [{
                        show: true,
                        height: 30,
                        xAxisIndex: [
                            0
                        ],
                        bottom: 30,
                        start: 10,
                        end: 80,
                        handleIcon: 'path://M306.1,413c0,2.2-1.8,4-4,4h-59.8c-2.2,0-4-1.8-4-4V200.8c0-2.2,1.8-4,4-4h59.8c2.2,0,4,1.8,4,4V413z',
                        handleSize: '110%',
                        handleStyle: {
                            color: '#d3dee5'

                        },
                        textStyle: {
                            color: '#fff'
                        },
                        borderColor: '#fff'

                    }, {
                        type: 'inside',
                        show: true,
                        height: 15,
                        start: 1,
                        end: 35
                    }],
                    series: [{
                        name: '盈利',
                        type: 'bar',
                        stack: 'total',
                        barMaxWidth: 35,
                        barGap: '10%',
                        itemStyle: {
                            normal: {
                                color: 'rgba(255,144,128,1)',
                                label: {
                                    show: true,
                                    textStyle: {
                                        color: '#fff'
                                    },
                                    position: 'insideTop',
                                    formatter(p) {
                                        return p.value > 0 ? p.value : ''
                                    }
                                }
                            }
                        },
                        data: this.statisticList.win_end_list
                    },

                        {
                            name: '亏损',
                            type: 'bar',
                            stack: 'total',
                            itemStyle: {
                                normal: {
                                    color: 'rgba(0,191,183,1)',
                                    barBorderRadius: 0,
                                    label: {
                                        show: true,
                                        position: 'top',
                                        formatter(p) {
                                            return p.value > 0 ? p.value : ''
                                        }
                                    }
                                }
                            },
                            data: this.statisticList.lose_end_list
                        }, {
                            name: '净盈利',
                            type: 'line',
                            stack: 'total',
                            symbolSize: 10,
                            symbol: 'circle',
                            itemStyle: {
                                normal: {
                                    color: 'rgba(252,230,48,1)',
                                    barBorderRadius: 0,
                                    label: {
                                        show: true,
                                        position: 'top',
                                        // formatter(p) {
                                        //     return p.value > 0 ? p.value : p.value
                                        // }
                                    }
                                }
                            },
                            data: this.statisticList.net_profit_list
                        }
                    ]
                })

                // 盈利品种列表
                this.winPiechart.setOption({
                    title: {
                        text: '平均盈利排行',
                        top: '2%',
                        textStyle: {
                            color: 'white'
                        }
                    },
                    xAxis: {
                        type: 'category',
                        data: this.statisticList.win_symbol_list,
                        axisLine: {lineStyle: {color: "white"}}
                    },
                    yAxis: {
                        type: 'value',
                        axisLine: {lineStyle: {color: "white"}},
                        splitLine: {
                            show: false
                        },
                    },
                    tooltip: {
                        trigger: 'item',
                        formatter: '{a} <br/>{b} : {c}'
                    },
                    legend: {
                        left: 'center',
                        bottom: '10',
                        data: this.statisticList.win_symbol_list
                    },

                    series: [
                        {
                            name: '盈利排行',
                            type: 'bar',
                            data: this.statisticList.win_money_list,
                            animationEasing: 'cubicInOut',
                            animationDuration: 2600,
                            itemStyle: {
                                normal: {
                                    color: function (params) {
                                        return '#EF5350'
                                    }
                                }
                            },
                        }
                    ]
                })
                // 亏损品种列表
                this.losePieChart.setOption({
                    title: {
                        text: '平均亏损排行',
                        top: '2%',
                        textStyle: {
                            color: 'white'
                        }
                    },
                    tooltip: {
                        trigger: 'item',
                        formatter: '{a} <br/>{b} : {c}'
                    },
                    legend: {
                        left: 'center',
                        bottom: '10',
                        data: this.statisticList.lose_symbol_list
                    },

                    xAxis: {
                        type: 'category',
                        data: this.statisticList.lose_symbol_list,
                        axisLine: {lineStyle: {color: "white"}},

                    },
                    yAxis: {
                        type: 'value',
                        axisLine: {lineStyle: {color: "white"}},
                        splitLine: {
                            show: false
                        },
                    },
                    series: [
                        {
                            name: '亏损占比',
                            type: 'bar',
                            data: this.statisticList.lose_money_list,
                            animationEasing: 'cubicInOut',
                            animationDuration: 2600,
                            itemStyle: {
                                normal: {
                                    color: function (params) {
                                        return '#26A69A'
                                    }
                                }
                            },
                        }
                    ]
                })
            },
            initChart() {
                this.profitChart = this.$echarts.init(document.getElementById('profit-chart'))
                this.winPiechart = this.$echarts.init(document.getElementById('win-pie-chart'))
                this.losePieChart = this.$echarts.init(document.getElementById('lose-pie-chart'))

                this.chartssize(document.getElementById('profit-chart-parent'),
                    document.getElementById('profit-chart'));
                this.chartssize(document.getElementById('win-pie-chart-parent'),
                    document.getElementById('win-pie-chart'));
                this.chartssize(document.getElementById('lose-pie-chart-parent'),
                    document.getElementById('lose-pie-chart'));
                this.profitChart.resize()
                this.winPiechart.resize()
                this.losePieChart.resize()

                window.addEventListener('resize', () => {
                    this.profitChart.resize()
                    this.winPiechart.resize()
                    this.losePieChart.resize()
                })
            },
            // 计算echarts 高度
            chartssize(container, charts) {
                function getStyle(el, name) {
                    if (window.getComputedStyle) {
                        return window.getComputedStyle(el, null)
                    } else {
                        return el.currentStyle
                    }
                }

                let wi = getStyle(container, 'width').width
                let hi = getStyle(container, 'height').height
                charts.style.height = hi
                charts.style.width = wi
            },
        }
    }
</script>
<style lang="stylus">
    .statistic-echarts-main {
        /*.profit-chart {
            flex 2
            height: 500px
            width: 1200px
        }

        .pie-chart {
            flex: 1
            width: 400px;
            height: 300px;
            margin-top 100px;
        }*/
    }

    input.el-range-input {
        background-color: #12161c;
        border: 1px solid rgba(127, 127, 122, .2);
        color: white
    }

    .el-date-editor .el-range-input {
        color: white !important
    }

    .statistic-echarts-list {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        height: 100%
        width: 100%
        margin-top 10px;

        .profit-chart {
            height: 500px
            width: 1000px
        }

        .pie-chart-list {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            flex-direction column
            height: 100%;

            .pie-chart {
                flex: 1
                width: 1200px;
                height: 300px;
            }
        }

    }

</style>