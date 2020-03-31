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

    require('echarts/theme/macarons') // echarts theme

    export default {
        data() {
            return {
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
                console.log(this.dateRange)
            },
            initChart() {
                this.profitChart = this.$echarts.init(document.getElementById('profit-chart'))
                this.winPiechart = this.$echarts.init(document.getElementById('win-pie-chart'), 'macarons')
                this.losePieChart = this.$echarts.init(document.getElementById('lose-pie-chart'), 'macarons')

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


                const xData = (function () {
                    const data = []
                    for (let i = 1; i < 13; i++) {
                        data.push(i + 'day')
                    }
                    return data
                }())
                this.profitChart.setOption({
                    backgroundColor: '#344b58',
                    title: {
                        text: '统计',
                        x: '20',
                        top: '20',
                        textStyle: {
                            color: '#fff',
                            fontSize: '22'
                        },
                        subtextStyle: {
                            color: '#90979c',
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
                            color: '#90979c'
                        },
                        data: ['盈利', '亏损', '净盈利']
                    },
                    calculable: true,
                    xAxis: [{
                        type: 'category',
                        axisLine: {
                            lineStyle: {
                                color: '#90979c'
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
                        data: xData
                    }],
                    yAxis: [{
                        type: 'value',
                        splitLine: {
                            show: false
                        },
                        axisLine: {
                            lineStyle: {
                                color: '#90979c'
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
                        borderColor: '#90979c'

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
                        data: [
                            709,
                            1917,
                            2455,
                            2610,
                            1719,
                            1433,
                            1544,
                            3285,
                            5208,
                            3372,
                            2484,
                            4078
                        ]
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
                            data: [
                                327,
                                1776,
                                507,
                                1200,
                                800,
                                482,
                                204,
                                1390,
                                1001,
                                951,
                                381,
                                220
                            ]
                        }, {
                            name: 'average',
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
                                        formatter(p) {
                                            return p.value > 0 ? p.value : ''
                                        }
                                    }
                                }
                            },
                            data: [
                                1036,
                                3693,
                                2962,
                                3810,
                                2519,
                                1915,
                                1748,
                                4675,
                                6209,
                                4323,
                                2865,
                                4298
                            ]
                        }
                    ]
                })
                this.winPiechart.setOption({
                    title: {
                        text: '盈利占比',
                        top: '2%',
                        textStyle: {
                            color: 'black'
                        }
                    },
                    tooltip: {
                        trigger: 'item',
                        formatter: '{a} <br/>{b} : {c} ({d}%)'
                    },
                    legend: {
                        left: 'center',
                        bottom: '10',
                        data: ['螺纹', '橡胶', '豆粕', '沪镍', '黄金']
                    },
                    series: [
                        {
                            name: '盈利占比',
                            type: 'pie',
                            roseType: 'radius',
                            radius: [15, 95],
                            center: ['50%', '38%'],
                            data: [
                                {value: 320, name: '螺纹'},
                                {value: 240, name: '橡胶'},
                                {value: 149, name: '豆粕'},
                                {value: 100, name: '沪镍'},
                                {value: 59, name: '黄金'}
                            ],
                            animationEasing: 'cubicInOut',
                            animationDuration: 2600
                        }
                    ]
                })
                this.losePieChart.setOption({
                    title: {
                        text: '亏损占比',
                        top: '2%',
                        textStyle: {
                            color: 'black'
                        }
                    },
                    tooltip: {
                        trigger: 'item',
                        formatter: '{a} <br/>{b} : {c} ({d}%)'
                    },
                    legend: {
                        left: 'center',
                        bottom: '10',
                        data: ['白银', '燃油', '棕榈', '沥青', '聚丙烯']
                    },
                    series: [
                        {
                            name: '盈利占比',
                            type: 'pie',
                            roseType: 'radius',
                            radius: [15, 95],
                            center: ['50%', '38%'],
                            data: [
                                {value: 320, name: '白银'},
                                {value: 240, name: '燃油'},
                                {value: 149, name: '棕榈'},
                                {value: 100, name: '沥青'},
                                {value: 59, name: '聚丙烯'}
                            ],
                            animationEasing: 'cubicInOut',
                            animationDuration: 2600
                        }
                    ]
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

    .statistic-echarts-list {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        height: 100%
        width: 100%

        .profit-chart {
            height: 500px
            width: 1000px
        }

        .pie-chart-list {
            padding-top 100px;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            height: 100%;

            .pie-chart-item {
                flex: 1
                width: 200px;
                height: 300px;
            }
        }

    }

</style>