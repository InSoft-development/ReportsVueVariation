<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'

import { useRoute } from 'vue-router'
import { useApplicationStore } from '../../stores/applicationStore.js'

import { getMultiAxisSensors, getPlotlyMultiAxisData, getPlotlyMultiAxisLayout } from '../../stores'
import PlotlyMultiAxises from '../local/PlotlyMultiAxises.vue'

export default {
  name: 'UPlotlyMultiAxises',
  components: { PlotlyMultiAxises },
  props: {
    selectedSignalCheckbox: String()
  },
  setup(props) {
    const applicationStore = useApplicationStore()

    // чекбоксы сигналов многоосевого графика
    const multiAxisSensors = ref([])
    // выбранные чекбоксы сигналов многоосевого графика
    const selectedMultiAxisSensors = ref([])

    // выбранный основной сигнал многоосевого графика
    const selectedSignal = ref(props.selectedSignalCheckbox)

    // объекты Plotly для построения многоосевого графика
    const PlotlyMultiData = ref([])
    const PlotlyMultiLayout = ref(null)

    const route = useRoute()
    // номер интервала из id открытой страницы
    let intervalID = ref(route.params.intervalsId)
    // флаг активации спинера при построении многоосевого графика
    const spinnerFlagMultiAxis = ref(true)

    onMounted(async () => {
      spinnerFlagMultiAxis.value = true
      await getMultiAxisSensors(
        props.selectedSignalCheckbox,
        multiAxisSensors,
        selectedMultiAxisSensors
      )
      await getPlotlyMultiAxisData(selectedMultiAxisSensors, intervalID, PlotlyMultiData)
      await getPlotlyMultiAxisLayout(selectedMultiAxisSensors, intervalID, PlotlyMultiLayout)
      spinnerFlagMultiAxis.value = false
      await applicationStore.setDictSelectedCheckbox(selectedSignal, selectedMultiAxisSensors)
    })

    watch(props, async () => {
      spinnerFlagMultiAxis.value = true
      console.log(props)
      selectedSignal.value = props.selectedSignalCheckbox
      await getMultiAxisSensors(
        props.selectedSignalCheckbox,
        multiAxisSensors,
        selectedMultiAxisSensors
      )
      await getPlotlyMultiAxisData(selectedMultiAxisSensors, intervalID, PlotlyMultiData)
      await getPlotlyMultiAxisLayout(selectedMultiAxisSensors, intervalID, PlotlyMultiLayout)
      spinnerFlagMultiAxis.value = false
      await applicationStore.setDictSelectedCheckbox(selectedSignal, selectedMultiAxisSensors)
    })

    // обработчик изменения состояния чекбоксов
    async function changeMultiSignalCheckbox() {
      spinnerFlagMultiAxis.value = true
      let tempArray = []
      // сортировка для сохранения порядка согласно списка чекбоксов
      // по ключам multiAxisSensors
      multiAxisSensors.value.forEach((elem) => {
        if (selectedMultiAxisSensors.value.includes(elem.name)) tempArray.push(elem.name)
      })
      selectedMultiAxisSensors.value = tempArray

      await getPlotlyMultiAxisData(selectedMultiAxisSensors, intervalID, PlotlyMultiData)
      await getPlotlyMultiAxisLayout(selectedMultiAxisSensors, intervalID, PlotlyMultiLayout)

      spinnerFlagMultiAxis.value = false

      applicationStore.setDictSelectedCheckbox(selectedSignal, selectedMultiAxisSensors)
    }

    onUnmounted(() => {
      applicationStore.removeFromDictSelectedCheckbox(selectedSignal)
    })

    return {
      selectedSignal,
      multiAxisSensors,
      selectedMultiAxisSensors,
      PlotlyMultiData,
      PlotlyMultiLayout,
      intervalID,
      spinnerFlagMultiAxis,
      changeMultiSignalCheckbox
    }
  }
}
</script>

<template>
  <main>
  <div class="container position-relative">
        <h4 class="color-h4">
          {{ selectedSignal }}
        </h4>
  </div>    

     <!-- <div> -->
    <div class="container position-relative card_11">
<!-- ////////////////////////////////////////////////////////////////////////////////////////////////////////// -->
      <div class="container position-relative card_12">
            <div
              class="row position-absolute top-50 start-50 translate-middle z-1"
              v-show="spinnerFlagMultiAxis"
            >
              <ProgressSpinner
                style="width: 100px; height: 100px"
                stroke-width="5"
                animation-duration=".3s"
                fill="var(--surface-ground)"
                class="z-2"
              />
            </div> 

              <PlotlyMultiAxises
                :interval-data-target="PlotlyMultiData"
                :interval-data-layout="PlotlyMultiLayout"
              ></PlotlyMultiAxises> 
      </div>
<!-- /////////////////////////////////////////////////////////////////////////////////////////////////////////  -->
    </div>




  <div class="container position-relative" style="top: 10px;">
    <div
      v-for="multiSensor of multiAxisSensors"
      :key="multiSensor.id"
      class="flex align-items-center"
    >
      <Checkbox
        style="bottom: 4px;"
        v-model="selectedMultiAxisSensors"
        :input-id="multiSensor.id"
        name="multiSensor"
        :value="multiSensor.name"
        @change="changeMultiSignalCheckbox"
      >
      </Checkbox>
      <label :for="multiSensor.name" style="margin-bottom: 5px;padding-left: 5px;">{{ multiSensor.name }}</label>
    </div>
  </div>
  <br />
</main>
</template>

<style scoped>
.color-h4 {
  color: #1f77b4;
  margin-left: auto;
  margin-top: 40px;
  margin-bottom: 7px;
}

.card_11 {
    /* background: var(--surface-card); */
    /* padding: 2rem; */
    /* border-radius: 10px; */
    /* margin-bottom: 1rem; */
    /* text-decoration: none; */
    width: 1299px;
    height: 450px;
    background: #1f77b4;
}
.card_12{
  width: 1299px;
}
.Graf{  
  /* clip-path: inset(0px 0px 0px 190px); */
  width: 1299;
 

  
}


</style>
