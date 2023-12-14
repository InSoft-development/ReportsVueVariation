<script>
import { useRoute } from 'vue-router'
import { ref, onMounted, onUpdated } from 'vue'

import { useApplicationStore } from '../stores/applicationStore.js'

export default {
  name: 'SettingView',
  setup() {
    const applicationStore = useApplicationStore()

    // элемент ввода границы отступа слева
    const leftInputNumber = ref(0)
    // элемент ввода границы отступа справа
    const rightInputNumber = ref(0)
    // выбранная ориентация страниц построения отчета
    const pickedRadioOrientation = ref('book')

    onMounted(() => {
      leftInputNumber.value = applicationStore.leftSpace
      rightInputNumber.value = applicationStore.rightSpace
      pickedRadioOrientation.value = applicationStore.pickedOrientation
    })

    // отслеживаем изменения в InputNumber ширины отступа
    onUpdated(() => {
      applicationStore.setSpace(leftInputNumber.value, rightInputNumber.value)
    })

    // обработчик изменения состояний кнопок выбора ориентации страниц отчета
    function onChangeRadioButtons() {
      applicationStore.pickedOrientation = pickedRadioOrientation.value
    }

    return {
      leftInputNumber,
      rightInputNumber,
      pickedRadioOrientation,
      onChangeRadioButtons
    }
  }
}
</script>

<template>
  <main>
    <div class="about">
      <h1>Настройки</h1>
      <div class="container">
        <div class="row">
          <div class="col">
            <label for="left-input-number" class="font-bold block mb-2">
              Ширина отступа в 5-ти минутках слева
            </label>
          </div>
          <div class="col">
            <label for="right-input-number" class="font-bold block mb-2">
              Ширина отступа в 5-ти минутках справа
            </label>
          </div>
        </div>
        <div class="row">
          <div class="col">
            <InputNumber
              v-model="leftInputNumber"
              inputId="left-input-number"
              mode="decimal"
              show-buttons
              :min="0"
              :max="50000"
              :step="1"
              :allow-empty="false"
              :aria-label="leftInputNumber"
            />
          </div>
          <div class="col">
            <InputNumber
              v-model="rightInputNumber"
              inputId="right-input-number"
              mode="decimal"
              show-buttons
              :min="0"
              :max="50000"
              :step="1"
              :allow-empty="false"
              :aria-label="rightInputNumber"
            />
          </div>
        </div>
        <div class="row">
          <h4>Выберите ориентацию страниц при построении PDF-отчетов</h4>
        </div>
        <div class="row">
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="book"
              name="book"
              value="book"
              v-model="pickedRadioOrientation"
              @change="onChangeRadioButtons"
            />
            <label class="form-check-label" for="book">
              <span class="badge rounded-pill bg-primary">Книжная</span>
            </label>
          </div>
        </div>
        <div class="row">
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="letter"
              name="letter"
              value="letter"
              v-model="pickedRadioOrientation"
              @change="onChangeRadioButtons"
            />
            <label class="form-check-label" for="letter">
              <span class="badge rounded-pill bg-primary">Альбомная</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>
