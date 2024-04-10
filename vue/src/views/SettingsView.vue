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
    <div class="container position-relative" style="width: 740px; right: 10px;">
      <div class="row">
        <div class="col">
          <h1 style="margin-top: 40px;margin-bottom: 5px;">Настройки</h1>
        </div>
      </div>
    </div>

      <div class="container position-relative form" style="width: 740px; height: 400px;">
        <div class="row">
          <div class="col" style="margin-left: 50px;">
            <label for="left-input-number" class="label_1" style="margin-bottom: 0px;margin-top: 16px;">
              Ширина отступа в 5-ти минутках слева
            </label>
          </div>
          <div class="col" style="margin-left: 50px;">
            <label for="right-input-number" class="label_2" style="margin-bottom: 0px;margin-top: 16px;">
              Ширина отступа в 5-ти минутках справа
            </label>
          </div>
        </div>
        <div class="row">
          <div class="col" style="margin-left: 50px;">
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
          <div class="col" style="margin-left: 50px;">
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
        <div class="row" style="margin-top: 77px;margin-left: 50px;">
          <h4 style="padding-left: 1px;">Выберите ориентацию страниц при построении PDF-отчетов</h4>
        </div>
        
        <div class="row" style="margin-left: 50px; margin-bottom: 10px;padding-left: 0px;padding-right: 590px;" >
          <div class="container_1">
            <label for="book">
              <input
              type="radio"
              id="book"
              name="book"
              value="book"
              v-model="pickedRadioOrientation"
              @change="onChangeRadioButtons"
              checked
              />
              <span>Книжная</span>
            </label>

           


           
          </div>
        </div>


        <div class="row" style="margin-left: 50px; padding-right: 590px;">
          <div class="container_1" style="margin-left: 9px;">
             <label for="letter">
              <input              
              type="radio"
              id="letter"
              name="letter"
              value="letter"
              v-model="pickedRadioOrientation"
              @change="onChangeRadioButtons"
            />

              <span>Альбомная</span>
            </label>
            
           
          </div>
        </div>
      </div>
    
  </main>
</template>

<style scoped>
h1{
  color: #1f77b4;
}
.form{
  background: #fff; 
}
.label_1{
  font-size: 1.5rem;
}
.label_2{
  font-size: 1.5rem;
}


/* ///////////////////////////////////////// */
.container_1{
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
}
label{
  display: flex;
  cursor: pointer;
  font-weight: 500;
  position: relative;
}
label input{
  opacity: 0;
}
label span{
  display: flex;
  align-items: center;
  padding: 8px 15px 8px 8px;
  border-radius: 50px;
  transition: 0.25s ease;
}
label span:hover{
  background: #d6d6e5;
}
label input:checked ~ span{
  background: #d6d6e5;
}
label span::before{
  content: "";
  background-color: #fff;
  width: 29px;
  height: 29px;
  border-radius: 50px;
  margin-right: 7px;
  transition: .25s ease;
  box-shadow: inset 0 0 0 3px #1f77b4;
}

label input:checked ~ span::before{
  box-shadow: inset 0 0 0 8px #1f77b4;
}
</style>
