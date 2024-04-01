<script>
import { ref, onMounted, reactive, watch } from 'vue'

import { getPlotlyHist } from '../stores'
import PlotlyMultiAxises from '../components/local/PlotlyMultiAxises.vue'

export default {
  name: 'AdditionView',
  components: { PlotlyMultiAxises },
  props: {
    activeGroup: String
  },
  setup(props) {
    // Plotly гистограмма
    let PlotlyHistData = ref([])

    let PlotlyHistLayout = reactive({
      showlegend: false,
      uirevision: 'true',
      xaxis: {
        title: 'Распределение потенциала'
      },
      yaxis: {
        title: 'Количество попаданий'
      },
      shapes: Array()
    })

    onMounted(async () => {
      await getPlotlyHist(props.activeGroup, PlotlyHistData, PlotlyHistLayout)
    })

    watch(props, () => {
      getPlotlyHist(props.activeGroup, PlotlyHistData, PlotlyHistLayout)
    })

    return {
      PlotlyHistData,
      PlotlyHistLayout
    }
  }
}
</script>

<template>
  <main>
    <div class="container position-relative">
       <h2 class="color-h2" style="margin-top: 40px;margin-bottom: 5px;">Гистограмма распределения ошибки восстановления значений датчиков</h2>
    </div>
   
    <div class="container position-relative">
      <div class="row">
        <div class="col">
          <PlotlyMultiAxises
            :interval-data-target="PlotlyHistData"
            :interval-data-layout="PlotlyHistLayout"
          >
          </PlotlyMultiAxises>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.color-h2 {
  color: #1f77b4;
}
</style>
