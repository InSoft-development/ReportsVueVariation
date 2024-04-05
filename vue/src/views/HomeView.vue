<script>
// //////////////////////////Header//////////////////
import  Header  from '../components/header/Header.vue'
// ///////////////////////////////////////////////////
import { ref, reactive, onMounted, watch } from 'vue'

import { useApplicationStore } from '../stores/applicationStore'
import UPlotlyInterval from '../components/global/UPlotlyInterval.vue'
import UAddedRow from '../components/global/UAddedRow.vue'

import { saveAddedIntervals, removeIntervalById, updateInterval } from '../stores'

import {
  getPlotlyDataInterval,
  getPlotlyCommonLayoutInterval,
  getMinMaxDateFromDataTarget,
  getAddedToTableIntervals
} from '../stores'

export default {
  name: 'HomeView',
  components: { UPlotlyInterval, UAddedRow, Header },
  props: {
    activeMethod: String,
    activeGroup: String,
    flagHomePageUpdate: Boolean
  },
  emits: ['updateNewInterval'],
  setup(props, context) {
    const applicationStore = useApplicationStore()
    // Надпись над графиком
    const targetLabel = ref('')

    // объекты Plotly
    let PlotlyCommonDataTarget = reactive({
      x: Array(),
      y: Array(),
      type: 'scatter'
    })

    let PlotlyCommonLayoutTarget = reactive({
      title: String(),
      showlegend: false,
      uirevision: 'true',
      shapes: Array()
    })

    // Даты начала и конца введенного периода
    const dateTimeBegin = ref()
    const dateTimeEnd = ref()

    // минимальное и максимальное время из фрейма срезов
    const minTime = ref(new Date())
    const maxTime = ref(new Date())

    // массив объектов интервалов для формироавния таблицы добавленных пользователем интервалов
    let addedToTableIntervals = ref([])

    // флаг перехода в режим редактирования интервала
    const editModeFlag = ref(false)

    // флаг активации спинера при построении графика
    const spinnerFlagHome = ref(true)

    onMounted(async () => {
      // Фраза над общим графиком за весь период целевой переменной
      if (props.activeMethod === 'potentials')
        targetLabel.value = 'График вероятности наступления аномалии за весь период'
      else if (props.activeMethod === 'LSTM')
        targetLabel.value = 'График функции потерь за весь период'
      else targetLabel.value = 'График целевой функции за весь период'

      await getPlotlyDataInterval(props.activeMethod, props.activeGroup, PlotlyCommonDataTarget)
      await getPlotlyCommonLayoutInterval(
        props.activeMethod,
        props.activeGroup,
        PlotlyCommonLayoutTarget
      )
      spinnerFlagHome.value = false
      await getMinMaxDateFromDataTarget(minTime, maxTime, dateTimeBegin, dateTimeEnd)
      await getAddedToTableIntervals(props.activeMethod, props.activeGroup, addedToTableIntervals)
    })

    watch(props, async () => {
      spinnerFlagHome.value = true
      // Фраза над общим графиком за весь период целевой переменной
      if (props.activeMethod === 'potentials')
        targetLabel.value = 'График вероятности наступления аномалии за весь период'
      else if (props.activeMethod === 'LSTM')
        targetLabel.value = 'График функции потерь за весь период'
      else targetLabel.value = 'График целевой функции за весь период'

      await getPlotlyDataInterval(props.activeMethod, props.activeGroup, PlotlyCommonDataTarget)
      await getPlotlyCommonLayoutInterval(
        props.activeMethod,
        props.activeGroup,
        PlotlyCommonLayoutTarget
      )
      spinnerFlagHome.value = false
      await getAddedToTableIntervals(props.activeMethod, props.activeGroup, addedToTableIntervals)
    })

    // обработчик сброса даты начала - отменить ограничение диапазона даты конца
    function onDateTimeBeginClearButtonClick(event) {
      minTime.value = applicationStore.minDateFromData
    }

    // обработчик сброса даты конца - отменить ограничение диапазона даты начала
    function onDateTimeEndClearButtonClick(event) {
      maxTime.value = applicationStore.maxDateFromData
    }

    // обработчик нажатия на кнопку Создать
    function onButtonCreateClick() {
      saveAddedIntervals(
        props.activeMethod,
        props.activeGroup,
        dateTimeBegin.value,
        dateTimeEnd.value
      )
      context.emit('updateNewInterval')
      getAddedToTableIntervals(props.activeMethod, props.activeGroup, addedToTableIntervals)
    }

    // обработка эмита при нажатии кнопки редактирования в таблице добавленных интервалов
    function editMode(editionFlag, idRow) {
      addedToTableIntervals.value.forEach((elem) => {
        if (elem.id !== idRow) elem.buttonDisabled = !elem.buttonDisabled
      })

      if (editModeFlag.value) {
        // обновление редактируемого интервала
        updateInterval(
          props.activeMethod,
          props.activeGroup,
          addedToTableIntervals.value[idRow].begin,
          addedToTableIntervals.value[idRow].end,
          idRow
        )
        context.emit('updateNewInterval')
        getAddedToTableIntervals(props.activeMethod, props.activeGroup, addedToTableIntervals)
      }

      editModeFlag.value = !editModeFlag.value
    }

    // обработка эмита при нажатии кнопки удаления в таблице добавленных интервалов
    function removeInterval(idRow) {
      editModeFlag.value = false
      removeIntervalById(props.activeMethod, props.activeGroup, idRow)
      context.emit('updateNewInterval')
      getAddedToTableIntervals(props.activeMethod, props.activeGroup, addedToTableIntervals)
    }

    // изменение минимальной даты начала при редактировании интервала
    function changeDateTimeIntervalBegin(dateTimeBegin, idRow) {
      addedToTableIntervals.value[idRow].begin = dateTimeBegin
    }

    // изменение максимальной даты конца при редактировании интервала
    function changeDateTimeIntervalEnd(dateTimeEnd, idRow) {
      addedToTableIntervals.value[idRow].end = dateTimeEnd
    }

    return {
      targetLabel,
      PlotlyCommonDataTarget,
      PlotlyCommonLayoutTarget,
      dateTimeBegin,
      dateTimeEnd,
      minTime,
      maxTime,
      addedToTableIntervals,
      editModeFlag,
      spinnerFlagHome,
      onButtonCreateClick,
      onDateTimeBeginClearButtonClick,
      onDateTimeEndClearButtonClick,
      editMode,
      changeDateTimeIntervalBegin,
      changeDateTimeIntervalEnd,
      removeInterval
    }
  }
}
</script>

<template>
  
  <main>
    
   
    <div class="container position-relative"  >
      <div class="row mb-5">
        <div class="col-12 mb-5">

          <h2 class="color-h2">{{ targetLabel }}</h2>
        <!-- <div class="card_2"> -->
          
          <div
          
            class="row position-absolute top-50 start-50 translate-middle z-1"
            v-show="spinnerFlagHome"
          >
            <ProgressSpinner
              style="width: 100px; height: 100px"
              stroke-width="5"
              animation-duration=".3s"
              fill="var(--surface-ground)"
              class="z-2"
            />
          </div>
          
            <UPlotlyInterval
              :interval-data-target="PlotlyCommonDataTarget"
              :interval-data-layout="PlotlyCommonLayoutTarget"
            >
            </UPlotlyInterval>
          
    </div>
  </div>
</div>
   <!-- </div> -->


      <div class="container position-relative">
          <h2 class="color-h4">Добавить период</h2>
      </div>


    <div class="container">
      <div class="row">
        <div class="col">
          <div class="font-bold block mb-2">Начало периода</div>
          <Calendar
            id="calendar-begin"
            v-model="dateTimeBegin"
            show-time
            hour-format="24"
            show-seconds="true"
            placeholder="ДД/ММ/ГГ ЧЧ:ММ:СС"
            manualInput="false"
            date-format="dd/mm/yy"
            :min-date="minTime"
            :max-date="maxTime"
            show-icon
            show-button-bar
            @clear-click="onDateTimeBeginClearButtonClick"
          />
        </div>
        <div class="col">
          <div class="font-bold block mb-2">Конец периода</div>
          <Calendar
            id="calendar-end"
            v-model="dateTimeEnd"
            show-time
            hour-format="24"
            show-seconds="true"
            placeholder="ДД/ММ/ГГ ЧЧ:ММ:СС"
            manualInput="false"
            date-format="dd/mm/yy"
            :min-date="minTime"
            :max-date="maxTime"
            show-icon
            show-button-bar
            @clear-click="onDateTimeEndClearButtonClick"
          />
        </div>
        <div class="col">
          <br />
          <Button @click="onButtonCreateClick">Создать</Button>
        </div>
      </div>
      <div class="row">
        <div class="col">
          <div class="alert alert-danger" role="alert" v-if="!dateTimeBegin">
            Введите начало периода
          </div>
        </div>
        <div class="col">
          <div class="alert alert-danger" role="alert" v-if="!dateTimeEnd">
            Введите конец периода
          </div>
        </div>
        <div class="col"></div>
      </div>
    </div>
    <br />
    <div class="container">
      <div class="row" v-if="Object.keys(addedToTableIntervals).length !== 0">
        <div class="col">Добавленный период</div>
        <div class="col">Начало периода</div>
        <div class="col">Конец периода</div>
        <div class="col"></div>
        <hr />
      </div>
      <div v-for="val in addedToTableIntervals">
        <UAddedRow
          :id="val.id"
          :button-disabled="val.buttonDisabled"
          :name-of-period="val.period"
          :begin-period="val.begin"
          :end-period="val.end"
          :min-time="minTime"
          :max-time="maxTime"
          @editModeInterval="editMode"
          @remove="removeInterval"
          @changeDateTimeBegin="changeDateTimeIntervalBegin"
          @changeDateTimeEnd="changeDateTimeIntervalEnd"
        />
      </div>
    </div>
    <br />

    
  
  </main>
</template>

<style scoped>
.color-h2 {
  color: #1f77b4;
  margin-left: auto;
  margin-top: 20px;
  margin-bottom: 20px;
}
.color-h4 {
  color: #1f77b4;
  margin-left: auto;
  margin-top: 20px;
  margin-bottom: 20px;
}
.font-bold block mb-2{
  margin-left: auto;
}
.services{
  display: flex;
}
.services__item{
  flex: 1 1 0;
  position: relative; 
}
.btn{
  background: #1f77b4;
  color: #fff;
  margin-bottom: 1px;
  top: 2px;
 }

.btn:hover{
  background-color: #244964;;
  color: #fff;
}
/* .p-button {
    color: #ffffff;
    background: red;
    border: 1px solid #007bff;
    padding: 0.5rem 0.75rem;
    font-size: 1rem;
    transition: background-color 0.15s, border-color 0.15s, box-shadow 0.15s;
    border-radius: 4px;
    outline-color: transparent;
  } */
/* .tt{
  text-align: center;
} */


/* body {
    font-family: var(--font-family);
    font-weight: normal;
    background: var(--surface-ground);
    color: var(--text-color);
    padding: 1rem;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
} */
/* .plot-container plotly{
  position: relative;
  width: 1299px;
  height: 450px;
} */
/* .card{
 position: relative;
 width: 1000px;
 height: 520px;
 padding: 80px 50px 20px;
 box-shadow: 15px 15px 20px rgba(0,0,0,0.1),
 -15px -15px 20px #fffb;
 border-radius: 20px;
 justify-content: center;
 align-items: center;
 flex-direction: column;
 
} */
 
 

 /* .container_G{  
  position: relative;
  top: -40px;
  height: 350px;
  padding: 0;
  box-shadow: 15px 15px 20px rgba(0,0,0,0.1),
 -15px -15px 20px #fffb;
 border-radius: 20px;
 justify-content: center;
 align-items: center;
 
 }  */



</style>
