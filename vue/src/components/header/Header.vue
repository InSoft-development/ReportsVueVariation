<template>
     <div class="card_1">
        <TabView  :scrollable="true">
            <TabPanel class="pan" v-for="tab in scrollableTabs" :key="tab.title" :header="tab.title">
                <p class="m-0">{{ tab.content }}</p>
            </TabPanel>
        </TabView>
    </div>

</template>

<script>
import { ref } from 'vue';
export default {
    
    name: 'Header',
    data() {
        return {
            scrollableTabs: Array.from({ length: 20 }, (_, i) => ({ title: `2021-06-07 11:09:00 % 2021-06-07 23:39:00 ${i + 1}`, content: `2021-06-07 11:09:00 % 2021-06-07 23:39:00 ${i + 1} Content` }))
        };
    }
};


</script>

<!-- export default{
    name: 'Header',
    
} -->

<style>
html {
    font-size: 14px;
    scroll-behavior: smooth;
}
/* background: var(--surface-ground); */

 body {
    font-family: var(--font-family);
    font-weight: normal;
    background: var(--surface-ground);
    color: var(--text-color);
    padding: 1rem;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
.card_1 {
    background: var(--surface-card);
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 1rem;
    text-decoration: none;
}

p {
    line-height: 1.75;
}





  
</style>
