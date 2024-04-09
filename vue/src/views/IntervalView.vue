<script>
import { useRoute } from 'vue-router'
import { ref, onMounted, reactive, watch } from 'vue'

import { useApplicationStore } from '../stores/applicationStore'
import UPlotlyInterval from '../components/global/UPlotlyInterval.vue'
import UPlotlyMultiAxises from '../components/global/UPlotlyMultiAxises.vue'
import {
  getPlotlyDataInterval,
  getPlotlyIntervalLayoutInterval,
  getTopAndOtherGroupSensors,
  createTabReport
} from '../stores'

export default {
  name: 'IntervalView',
  components: { UPlotlyInterval, UPlotlyMultiAxises },
  props: {
    activeMethod: String,
    activeGroup: String
  },
  setup(props) {
    const route = useRoute()
    let intervalID = ref(route.params.intervalsId)
    const applicationStore = useApplicationStore()

    // Надпись над графиком и дата интервала
    const targetLabel = ref('')
    const dateLabel = ref('')

    // объекты Plotly для построения графика на интервале
    let PlotlyIntervalDataTarget = reactive({
      x: Array(),
      y: Array(),
      type: 'scatter'
    })

    let PlotlyIntervalLayoutTarget = reactive({
      title: String(),
      showlegend: false,
      uirevision: 'true',
      shapes: Array()
    })

    // датчики, внесшие максимальный вклад на периоде
    const topSensors = ref([])
    // остальные датчики группы
    const otherGroupSensors = ref([])

    // выбранные датчики, внесшие максимальный вклад на периоде
    const selectedTopSensors = ref([])
    // выбранные остальные датчики группы, внесшие максимальный вклад на периоде
    const selectedOtherGroupSensors = ref([])

    // объекты Plotly для построения графика на интервале
    const PlotlyMultiAxisData = ref([])
    const PlotlyMultiAxisLayout = ref([])

    // значение выполенния прогресс бара при построении отчета по периоду
    const progressTabBarValue = ref('0')
    // флаг показа прогресс бара
    let progressTabBarActive = ref(false)
    // флаг активации спинера при построении графика интервала
    const spinnerFlagInterval = ref(true)

    onMounted(async () => {
      let interval = applicationStore.intervals.value[intervalID.value]
      // Фраза над интервальным графиком за весь период целевой переменной
      if (props.activeMethod === 'potentials')
        targetLabel.value = 'График вероятности наступления аномалии на интервале'
      else if (props.activeMethod === 'LSTM')
        targetLabel.value = 'График функции потерь на интервале'
      else targetLabel.value = 'График целевой функции на интервале'

      dateLabel.value = `${interval[0]} % ${interval[1]}`

      await getPlotlyDataInterval(
        props.activeMethod,
        props.activeGroup,
        PlotlyIntervalDataTarget,
        interval
      )
      await getPlotlyIntervalLayoutInterval(
        props.activeMethod,
        props.activeGroup,
        interval,
        PlotlyIntervalLayoutTarget
      )

      spinnerFlagInterval.value = false

      await getTopAndOtherGroupSensors(
        props.activeMethod,
        props.activeGroup,
        topSensors,
        otherGroupSensors,
        selectedTopSensors,
        intervalID.value
      )
    })

    watch(route, async () => {
      spinnerFlagInterval.value = true
      intervalID.value = route.params.intervalsId

      let interval = applicationStore.intervals.value[intervalID.value]
      // Фраза над интервальным графиком за весь период целевой переменной
      if (props.activeMethod === 'potentials')
        targetLabel.value = 'График вероятности наступления аномалии на интервале'
      else if (props.activeMethod === 'LSTM')
        targetLabel.value = 'График функции потерь на интервале'
      else targetLabel.value = 'График целевой функции на интервале'

      dateLabel.value = `${interval[0]} % ${interval[1]}`

      getPlotlyDataInterval(
        props.activeMethod,
        props.activeGroup,
        PlotlyIntervalDataTarget,
        interval
      )
      await getPlotlyIntervalLayoutInterval(
        props.activeMethod,
        props.activeGroup,
        interval,
        PlotlyIntervalLayoutTarget
      )

      // снимаем выделение чекбоксов
      selectedTopSensors.value = []
      selectedOtherGroupSensors.value = []

      await getTopAndOtherGroupSensors(
        props.activeMethod,
        props.activeGroup,
        topSensors,
        otherGroupSensors,
        selectedTopSensors,
        intervalID.value
      )

      spinnerFlagInterval.value = false
    })

    // обработчик нажатия на кнопку PDF отчет
    function onButtonPdfReportClick() {
      alert('Запуск построения PDF отчета на интервале')
      const interval = applicationStore.intervals.value[intervalID.value]
      createTabReport(
        props.activeMethod,
        props.activeGroup,
        interval,
        selectedTopSensors,
        selectedOtherGroupSensors,
        progressTabBarValue,
        progressTabBarActive
      )
    }

    // обработчик переключения чекбоксов
    function changeCheckbox(event) {
      // временный массив для сортировки
      let tempArray = []

      // сортировка для сохранения порядка согласно списка чекбоксов
      // по ключам topSensors
      topSensors.value.forEach((elem) => {
        if (selectedTopSensors.value.includes(elem.name)) tempArray.push(elem.name)
      })
      selectedTopSensors.value = tempArray

      // сортировка для сохранения порядка согласно списка чекбоксов
      // по ключам otherGroupSensors
      tempArray = []
      otherGroupSensors.value.forEach((elem) => {
        if (selectedOtherGroupSensors.value.includes(elem.name)) tempArray.push(elem.name)
      })
      selectedOtherGroupSensors.value = tempArray
    }

    // обновление прогресс бара по значению из python
    function setProgressTabBarValue(count) {
      progressTabBarValue.value = String(count)
    }
    window.eel.expose(setProgressTabBarValue, 'setProgressTabBarValue')

    return {
      intervalID,
      targetLabel,
      dateLabel,
      onButtonPdfReportClick,
      PlotlyIntervalDataTarget,
      PlotlyIntervalLayoutTarget,
      topSensors,
      otherGroupSensors,
      selectedTopSensors,
      selectedOtherGroupSensors,
      PlotlyMultiAxisData,
      PlotlyMultiAxisLayout,
      changeCheckbox,
      progressTabBarValue,
      progressTabBarActive,
      setProgressTabBarValue,
      spinnerFlagInterval
    }
  }
}
</script>

<template>
  <main>
    
    <div class="container position-relative" style="width: 946px;">
      <div class="row">
        <div class="col-md-6">
          <div>
            <h4 class="Num">{{ dateLabel }}</h4>
          </div>
        </div>
        <div class="col-md-3">
          <div>
            <Button @click="onButtonPdfReportClick" style="left: -20px;top: 12px;">PDF отчет</Button>
          </div>
        </div>
        <div class="col-md-3" v-if="progressTabBarActive">
          <div>
            <ProgressBar  :value="progressTabBarValue"></ProgressBar>
          </div>
        </div>
      </div>
      <div class="row">
        <h3 class="color-h3">{{ targetLabel }}</h3>
      </div>
    


     <!-- <div class="container position-relative"> -->
        <div
          class="row position-absolute top-50 start-50 translate-middle z-1"
          v-show="spinnerFlagInterval"
        >
          <ProgressSpinner
            style="width: 100px; height: 100px"
            stroke-width="5"
            animation-duration=".3s"
            fill="var(--surface-ground)"
            class="z-2"
          />
        </div>
        <div class="row">
          <UPlotlyInterval 
            :interval-data-target="PlotlyIntervalDataTarget"
            :interval-data-layout="PlotlyIntervalLayoutTarget"
          >
          </UPlotlyInterval>
        </div>
    </div>
      <!-- </div> -->

       <div class="container position-relative" style="width: 946px;">
        <h3 class="color-h3" style="margin-top: 40px;margin-bottom: 5px;">Сигналы, внесшие наибольший вклад</h3>
      </div>

        <div class="container position-relative" style="width: 946px;">
          <div v-for="top of topSensors" :key="top.id" class="flex align-items-center">
            <Checkbox
              style="bottom: 4px;"
              v-model="selectedTopSensors"
              :input-id="top.id"
              name="top"
              :value="top.name"
              @change="changeCheckbox"
            ></Checkbox>
            <label :for="top.name" style="margin-bottom: 5px;padding-left: 5px;">{{ top.name }}</label>
            <br />
          </div>
        </div>

        <div class="container position-relative" style="width: 946px;">
            <h3 class="color-h3" style="margin-top: 40px;margin-bottom: 5px;">Остальные сигналы группы</h3>
        </div>

        <div class="container position-relative" style="width: 946px;">
          <div v-for="other of otherGroupSensors" :key="other.id" class="flex align-items-center">
            <Checkbox
              style="bottom: 4px;"
              v-model="selectedOtherGroupSensors"
              :input-id="other.id"
              name="other"
              :value="other.name"
              @change="changeCheckbox"
            ></Checkbox>
            <label :for="other.name" style="margin-bottom: 5px;padding-left: 5px;">{{ other.name }}</label>
            <br />
          </div>
        </div>

  
          <!-- <div> -->
            <div v-for="topSignal of selectedTopSensors"  >             
              <UPlotlyMultiAxises :selected-signal-checkbox="topSignal"></UPlotlyMultiAxises>           
            </div> 
                   
            <div v-for="otherSignal of selectedOtherGroupSensors">           
              <UPlotlyMultiAxises :selected-signal-checkbox="otherSignal"></UPlotlyMultiAxises>           
            </div>  
          <!-- </div> -->
          

     
     
    
  </main>
</template>

<style scoped>
.color-h3 {
  color: #1f77b4;
}
.Num{
  margin-left: auto;
  margin-top: 20px;
  margin-bottom: 20px;
}

</style>
