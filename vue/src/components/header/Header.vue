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


.p-tabview-nav-container {
    position: relative;
  }

  .p-tabview-scrollable .p-tabview-nav-container {
    overflow: hidden;
  }

  .p-tabview-nav-content {
    overflow-x: auto;
    overflow-y: hidden;
    scroll-behavior: smooth;
    scrollbar-width: none;
    overscroll-behavior: contain auto;
  }

  .p-tabview-nav {
    display: flex;
    margin: 0;
    padding: 0;
    list-style-type: none;
    flex: 1 1 auto;
  }

  .p-tabview-header-action {
    cursor: pointer;
    user-select: none;
    display: flex;
    align-items: center;
    position: relative;
    text-decoration: none;
    overflow: hidden;
  }

  .p-tabview-ink-bar {
    display: none;
    z-index: 1;
  }

  .p-tabview-header-action:focus {
    z-index: 1;
  }

  .p-tabview-title {
    line-height: 1;
    white-space: nowrap;
  }

  .p-tabview-nav-btn {
    position: absolute;
    top: 0;
    z-index: 2;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .p-tabview-nav-prev {
    left: 0;
  }

  .p-tabview-nav-next {
    right: 0;
  }

  .p-tabview-nav-content::-webkit-scrollbar {
    display: none;
  }

  .p-tabview .p-tabview-nav {
    background: #ffffff;
    border:  1px solid #e2e8f0;
    border-width: 0 0 1px 0;
  }
  .p-tabview .p-tabview-nav li {
    margin-right: 0;
  }
  .p-tabview .p-tabview-nav li .p-tabview-nav-link {
    border: solid  #e2e8f0;
    border-width: 0 0 1px 0;
    border-color: transparent transparent #e2e8f0 transparent;
    background: #ffffff;
    color: #64748b;
    padding: 1rem 1.125rem;
    font-weight: 600;
    border-top-right-radius: 6px;
    border-top-left-radius: 6px;
    transition: box-shadow background-color 0.2s, color 0.2s, border-color 0.2s, box-shadow 0.2s, outline-color 0.2s;
    margin: 0 0 -1px 0;
    outline-color: transparent;
  }
  .p-tabview .p-tabview-nav li .p-tabview-nav-link:not(.p-disabled):focus-visible {
    outline:  1px solid var(--p-focus-ring-color);
    outline-offset: -2px;
    box-shadow: inset none;
  }
  .p-tabview .p-tabview-nav li:not(.p-highlight):not(.p-disabled):hover .p-tabview-nav-link {
    background: #ffffff;
    border-color: #e2e8f0;;
    color:  #334155;
  }
  .p-tabview .p-tabview-nav li.p-highlight .p-tabview-nav-link {
    background: #ffffff;
    border-color:#e2e8f0;
    color: #10b981;
  }
  .p-tabview .p-tabview-nav-btn.p-link {
    background: #ffffff;
    color: #10b981;
    width: 2.5rem;
    box-shadow:  0 3px 1px -2px rgba(0, 0, 0, 0.2), 0 2px 2px 0 rgba(0, 0, 0, 0.14), 0 1px 5px 0 rgba(0, 0, 0, 0.12);
    border-radius: 0;
    outline-color: transparent;
  }
  .p-tabview .p-tabview-nav-btn.p-link:focus-visible {
    outline:  1px solid var(--p-focus-ring-color);
    outline-offset: -2px;
    box-shadow: inset none;
  }
  .p-tabview .p-tabview-panels {
    background: #ffffff;
    padding: 0.875rem 1.125rem 1.125rem 1.125rem;
    border: 0 none;
    color:  #334155;
    border-bottom-right-radius: 6px;
    border-bottom-left-radius: 6px;
  }

  .p-tabview .p-tabview-ink-bar {
    z-index: 1;
    display: block;
    position: absolute;
    bottom: 0;
    height: 1px;
    background-color: #10b981;
    transition: 250ms cubic-bezier(0.35, 0, 0.25, 1);
  }
  .p-tabview .p-tabview-nav {
    position: relative;
  }
  .p-tabview .p-tabview-nav li .p-tabview-nav-link {
    transition: background-color 0.2s, color 0.2s, border-color 0.2s, box-shadow 0.2s, outline-color 0.2s;
  }
  .p-tabview .p-tabview-nav-btn.p-link {
    color: #64748b;
    transition: background-color 0.2s, color 0.2s, border-color 0.2s, box-shadow 0.2s, outline-color 0.2s;
    box-shadow: 0 3px 1px -2px rgba(0, 0, 0, 0.2), 0 2px 2px 0 rgba(0, 0, 0, 0.14), 0 1px 5px 0 rgba(0, 0, 0, 0.12);
    box-shadow: 0px 0px 10px 50px rgba(255, 255, 255, 0.6);
  }
  .p-tabview .p-tabview-nav-btn.p-link:hover {
    color: #475569;
  }

  .p-ink {
    display: block;
    position: absolute;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 100%;
    transform: scale(0);
    pointer-events: none;
  }

  .p-ink-active {
    animation: ripple 0.4s linear;
  }






  
</style>
