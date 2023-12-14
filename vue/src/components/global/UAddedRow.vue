<script>
import { ref, watch } from 'vue'

export default {
  name: 'UAddedRow',
  props: {
    id: Number,
    nameOfPeriod: String,
    buttonDisabled: Boolean,
    beginPeriod: Date,
    endPeriod: Date,
    minTime: Date,
    maxTime: Date
  },
  emits: ['editModeInterval', 'remove', 'changeDateTimeBegin', 'changeDateTimeEnd'],
  setup(props, context) {
    // наименование периода
    const nameOfPeriod = props.nameOfPeriod
    // флаг отключения строки таблицы добавленных интервалов
    const buttonDisabled = ref(props.buttonDisabled)
    // минимально доступная для выбора дата добавленных интервалов
    let minTimePeriod = ref(props.minTime)
    // максимально доступная для выбора дата добавленных интервалов
    let maxTimePeriod = ref(props.maxTime)

    // выбранная начальная дата добавленного интервала
    let dateTimeBeginPeriod = ref(props.beginPeriod)
    // выбранная конечная дата добавленного интервала
    let dateTimeEndPeriod = ref(props.endPeriod)

    // флаг переход в/из режима редактирования добавленного интервала
    let dateTimePeriodEditionMode = ref(true)

    // обработчик перехода в режим редактирования добавленного интервала
    function onEditButtonClick() {
      dateTimePeriodEditionMode.value = !dateTimePeriodEditionMode.value
      context.emit('editModeInterval', dateTimePeriodEditionMode.value, props.id)
    }

    // обработчик удаления добавленного интервала
    function onRemoveButtonClick() {
      context.emit('remove', props.id)
    }

    watch(props, () => {
      buttonDisabled.value = props.buttonDisabled
      minTimePeriod.value = props.minTime
      maxTimePeriod.value = props.maxTime
    })

    // обработчик выбора даты начала
    function onDateTimeBeginSelected(val) {
      dateTimeBeginPeriod.value = val
      context.emit('changeDateTimeBegin', dateTimeBeginPeriod.value, props.id)
    }

    // обработчик выбора даты конца
    function onDateTimeEndSelected(val) {
      dateTimeEndPeriod.value = val
      context.emit('changeDateTimeEnd', dateTimeEndPeriod.value, props.id)
    }

    return {
      nameOfPeriod,
      buttonDisabled,
      minTimePeriod,
      maxTimePeriod,
      dateTimeBeginPeriod,
      dateTimeEndPeriod,
      dateTimePeriodEditionMode,
      onEditButtonClick,
      onRemoveButtonClick,
      onDateTimeBeginSelected,
      onDateTimeEndSelected
    }
  }
}
</script>

<template>
  <div class="row">
    <div class="col">{{ nameOfPeriod }}</div>
    <div class="col">
      <Calendar
        id="calendar-period-begin"
        v-model="dateTimeBeginPeriod"
        :disabled="dateTimePeriodEditionMode"
        show-time
        hour-format="24"
        show-seconds="true"
        placeholder="ДД/ММ/ГГ ЧЧ:ММ:СС"
        manualInput="false"
        date-format="dd/mm/yy"
        :min-date="minTimePeriod"
        :max-date="maxTimePeriod"
        show-icon
        show-button-bar
        @date-select="onDateTimeBeginSelected"
      />
    </div>
    <div class="col">
      <Calendar
        id="calendar-period-end"
        v-model="dateTimeEndPeriod"
        :disabled="dateTimePeriodEditionMode"
        show-time
        hour-format="24"
        show-seconds="true"
        placeholder="ДД/ММ/ГГ ЧЧ:ММ:СС"
        manualInput="false"
        date-format="dd/mm/yy"
        :min-date="minTimePeriod"
        :max-date="maxTimePeriod"
        show-icon
        show-button-bar
        @date-select="onDateTimeEndSelected"
      />
    </div>
    <div class="col" v-if="buttonDisabled">
      <Button icon="pi pi-pencil" @click="onEditButtonClick" disabled></Button>
      <Button icon="pi pi-trash" @click="onRemoveButtonClick" disabled></Button>
    </div>
    <div class="col" v-else>
      <Button icon="pi pi-pencil" @click="onEditButtonClick"></Button>
      <Button icon="pi pi-trash" @click="onRemoveButtonClick"></Button>
    </div>
  </div>
  <hr />
</template>
