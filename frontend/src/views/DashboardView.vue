<template>
  <div class="h-full flex flex-col gap-6 relative pb-10">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tighter flex items-center gap-2">
          Visão Analítica
        </h1>
        <p class="text-[var(--text-muted)] font-medium">Monitoramento e personalização de painéis dinâmicos.</p>
      </div>
      
      <div class="flex gap-4 items-center">
        <!-- New Button for opening widget manager/builder -->
        <button 
          @click="openManager()"
          class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[var(--color-vintage-charcoal)] dark:bg-[var(--color-vintage-paper)] text-[var(--color-vintage-cream)] dark:text-[var(--color-vintage-charcoal)] font-bold shadow-md hover:-translate-y-0.5 transition-transform"
        >
          <Settings2 class="w-5 h-5" />
          Gerenciar Gráficos
        </button>

        <div class="hidden sm:flex vintage-panel px-6 py-2 items-center gap-4">
          <div class="p-2 bg-[var(--color-vintage-mint)]/20 rounded-lg">
            <Activity class="w-5 h-5 text-[var(--color-vintage-mint)]" />
          </div>
          <div>
            <p class="text-xs font-bold uppercase text-[var(--text-muted)]">Saúde Global</p>
            <p class="text-xl font-bold">92.4%</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="visibleWidgets.length === 0" class="vintage-panel flex-1 flex flex-col items-center justify-center p-12 text-center min-h-[400px]">
      <div class="w-20 h-20 bg-[var(--bg-app)] rounded-full flex items-center justify-center mb-6">
        <LucidePieChart class="w-10 h-10 text-[var(--text-muted)]" />
      </div>
      <h2 class="text-2xl font-bold mb-2">Nenhum gráfico visível</h2>
      <p class="text-[var(--text-muted)] mb-6 max-w-md">Você ocultou todos os gráficos de base. Adicione ou restaure gráficos para poder visualizar suas métricas preditivas.</p>
      <button @click="openManager()" class="px-6 py-3 rounded-lg border-2 border-[var(--color-vintage-mint)] text-[var(--color-vintage-mint)] font-bold hover:bg-[var(--color-vintage-mint)]/10 transition-colors">
        Configurar Painel
      </button>
    </div>

    <!-- Main Grid Array Render -->
    <TransitionGroup name="list" tag="div" class="grid grid-cols-1 lg:grid-cols-3 gap-8 flex-1">
      <div 
        v-for="widget in visibleWidgets" 
        :key="widget.id"
        class="vintage-panel relative flex flex-col p-6 group min-h-[450px]"
        :class="{ 'lg:col-span-2': widget.span === 2, 'lg:col-span-3': widget.span === 3 }"
      >
        <!-- Background Blur Decorators -->
        <div class="absolute inset-0 overflow-hidden rounded-xl pointer-events-none">
          <div 
            v-if="widget.type === 'line' || widget.type === 'line_temp' || widget.type === 'line_compare'"
            class="absolute -top-24 -right-24 w-64 h-64 bg-[var(--color-vintage-mustard)] opacity-5 rounded-full blur-3xl animate-pulse" style="animation-duration: 8s;"
          ></div>
          <div 
            v-else-if="widget.type === 'radar' || widget.type === 'radar_risk' || widget.type === 'scatter'"
            class="absolute -bottom-16 -right-16 w-48 h-48 bg-[var(--color-vintage-mint)] opacity-10 rounded-full blur-2xl animate-pulse" style="animation-duration: 12s;"
          ></div>
          <div 
            v-else
            class="absolute -left-32 top-0 w-96 h-96 bg-[var(--color-vintage-charcoal)] opacity-5 rounded-full blur-3xl"
          ></div>
        </div>
        
        <div class="flex justify-between items-center mb-6 relative z-10">
          <div>
            <h3 class="text-lg font-bold tracking-tight flex items-center gap-2">
              {{ widget.title }}
              <span v-if="!widget.isDefault" class="text-[10px] font-bold bg-[var(--color-vintage-mustard)] text-[var(--color-vintage-charcoal)] px-2 py-0.5 rounded-full uppercase">CUSTOM</span>
            </h3>
            <p class="text-sm font-medium text-[var(--text-muted)]">{{ widget.subtitle || 'Métricas operacionais' }}</p>
          </div>
          
          <!-- Actions Menu -->
          <div class="relative flex gap-2">
            <button @click="hideWidget(widget.id)" title="Ocultar Gráfico" class="p-2 rounded-lg bg-[var(--color-vintage-rose)]/10 text-[var(--color-vintage-rose)] hover:bg-[var(--color-vintage-rose)] hover:text-[var(--bg-app)] transition-colors group-hover:opacity-100 lg:opacity-0 focus:opacity-100">
              <EyeOff class="w-5 h-5 mx-auto" />
            </button>
            <button v-if="!widget.isDefault" @click="editWidget(widget.id)" title="Editar Gráfico" class="p-2 rounded-lg bg-[var(--color-vintage-mint)]/10 text-[var(--color-vintage-mint)] hover:bg-[var(--color-vintage-mint)] hover:text-white transition-colors group-hover:opacity-100 lg:opacity-0 focus:opacity-100">
              <Edit3 class="w-5 h-5 mx-auto" />
            </button>
          </div>
        </div>

        <div class="h-[380px] w-full flex-1 relative z-10 transition-all duration-300">
          <!-- CRITICAL FIX: :update-options="{ notMerge: true }" to prevent ghost-merging bugs in ECharts when swapping types -->
          <v-chart class="chart" :option="getChartOption(widget)" :update-options="{ notMerge: true }" autoresize />
        </div>
      </div>
    </TransitionGroup>

    <!-- WIDGET MANAGER MODAL OVERLAY -->
    <Teleport to="body">
      <div v-if="showWidgetManager" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="showWidgetManager = false"></div>
        
        <div class="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-3xl w-full max-w-5xl max-h-[90vh] flex flex-col relative z-[101] shadow-2xl overflow-hidden animate-in fade-in zoom-in-100 duration-300">
          <!-- Header -->
          <div class="p-6 border-b border-[var(--border-color)] flex justify-between items-center bg-[var(--bg-app)] shrink-0">
            <h2 class="text-2xl font-bold tracking-tight">Análise Preditiva e Dashboards</h2>
            <button @click="showWidgetManager = false" class="p-2 hover:bg-[var(--bg-card)] rounded-lg transition-colors">
              <X class="w-6 h-6 text-[var(--text-muted)]" />
            </button>
          </div>

          <!-- Body -->
          <div class="p-6 overflow-y-auto flex-1 flex flex-col gap-8 md:grid md:grid-cols-12 md:gap-8 min-h-0">
            
            <!-- LEFT SIDE: LIST OF ALL WIDGETS -->
            <div class="flex flex-col gap-6 border-[var(--border-color)] md:border-r md:pr-8 md:col-span-5">
              <section>
                <h3 class="text-lg font-bold mb-3 flex items-center gap-2">
                  <ShieldCheck class="w-5 h-5 text-[var(--color-vintage-mint)]" />
                  Gráficos Nativos
                </h3>
                
                <div class="flex flex-col gap-2">
                  <div v-for="dw in widgets.filter(w => w.isDefault)" :key="'manage-'+dw.id" class="p-3 rounded-xl border border-[var(--border-color)] flex justify-between items-center bg-[var(--bg-app)]/50">
                    <div class="flex items-center gap-3">
                      <div class="w-3 h-3 rounded-full" :class="dw.isVisible ? 'bg-[var(--color-vintage-mint)]' : 'bg-[var(--text-muted)]'"></div>
                      <span class="font-bold text-sm truncate max-w-[150px]">{{ dw.title }}</span>
                    </div>
                    <button 
                      @click="dw.isVisible = !dw.isVisible; saveWidgets()"
                      class="px-2 py-1 rounded text-xs font-bold transition-colors w-24 text-center"
                      :class="dw.isVisible ? 'bg-[var(--color-vintage-charcoal)]/10 text-[var(--color-vintage-charcoal)] dark:bg-[var(--color-vintage-paper)]/10 dark:text-[var(--color-vintage-paper)]' : 'bg-[var(--color-vintage-mint)] text-white'"
                    >
                      {{ dw.isVisible ? 'OCULTAR' : 'ATIVAR' }}
                    </button>
                  </div>
                </div>
              </section>

              <section>
                <h3 class="text-lg font-bold mb-3 flex items-center gap-2">
                  <LayoutTemplate class="w-5 h-5 text-[var(--color-vintage-mustard)]" />
                  Seus Gráficos
                </h3>
                
                <div class="flex flex-col gap-2">
                  <div v-if="widgets.filter(w => !w.isDefault).length === 0" class="text-sm font-medium text-[var(--text-muted)] italic p-4 text-center border overflow-hidden rounded-xl bg-[var(--bg-app)]/20 border-dashed">
                    Você ainda não criou os seus painéis.<br>Preencha o formulário ao lado!
                  </div>
                  <!-- Custom Items -->
                  <div v-for="cw in widgets.filter(w => !w.isDefault)" :key="'manage-'+cw.id" class="p-3 rounded-xl border border-[var(--color-vintage-mustard)]/30 flex justify-between items-center bg-[var(--bg-app)]/50" :class="{'ring-2 ring-[var(--color-vintage-mint)]' : editingWidgetId === cw.id}">
                    <div class="flex items-center gap-3">
                      <div class="w-3 h-3 rounded-full" :class="cw.isVisible ? 'bg-[var(--color-vintage-mint)]' : 'bg-[var(--text-muted)]'"></div>
                      <span class="font-bold text-sm truncate max-w-[90px]">{{ cw.title }}</span>
                    </div>
                    <div class="flex items-center gap-1">
                      <button @click="editWidgetInModal(cw)" title="Editar" class="p-1.5 rounded hover:bg-[var(--color-vintage-mustard)]/20 text-[var(--color-vintage-mustard)] transition-colors">
                        <Edit3 class="w-4 h-4" />
                      </button>
                      <button @click="deleteWidget(cw.id)" title="Deletar" class="p-1.5 rounded hover:bg-red-500/20 text-red-500 transition-colors">
                        <Trash2 class="w-4 h-4" />
                      </button>
                      <button 
                        @click="cw.isVisible = !cw.isVisible; saveWidgets()"
                        class="px-2 py-1 rounded text-xs font-bold transition-colors w-[65px] text-center ml-1"
                        :class="cw.isVisible ? 'bg-[var(--color-vintage-charcoal)]/10 text-[var(--color-vintage-charcoal)] dark:bg-[var(--color-vintage-paper)]/10 dark:text-[var(--color-vintage-paper)]' : 'bg-[var(--color-vintage-mint)] text-white'"
                      >
                        {{ cw.isVisible ? 'OCULTAR' : 'ATIVAR' }}
                      </button>
                    </div>
                  </div>
                </div>
              </section>
            </div>

            <!-- RIGHT SIDE: CREATOR WIZARD -->
            <div class="flex flex-col md:col-span-7">
               <h3 class="text-xl font-bold mb-4 flex items-center gap-2">
                <Sparkles class="w-5 h-5 text-[var(--color-vintage-mint)]" />
                {{ editingWidgetId ? 'Editando Gráfico' : 'Montagem Prática Avançada' }}
              </h3>
              <p class="text-sm text-[var(--text-muted)] font-medium mb-4">Aproveite todo o poder de renderização nativa da nossa plataforma preditiva com dezenas de visualizações disponíveis.</p>
              
              <form @submit.prevent="saveCustomWidget" class="bg-[var(--color-vintage-charcoal)]/5 dark:bg-[var(--color-vintage-paper)]/5 p-6 rounded-2xl border border-[var(--border-color)] space-y-6 flex-1 shadow-inner">
                
                <!-- Título -->
                <div>
                  <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Nome do Gráfico / Análise</label>
                  <input 
                    v-model="newWidgetForm.title"
                    type="text" 
                    required
                    class="w-full bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl py-3 px-3 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors" 
                    placeholder="Ex: Dispersão Térmica Geral..."
                  />
                </div>

                <!-- Type & Metric -->
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  <div>
                     <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Estrutura Visual ECharts</label>
                     <select v-model="newWidgetForm.type" required class="w-full bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl py-3 px-3 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors font-semibold">
                       <optgroup label="Tabelas Evolutivas/Linhas">
                          <option value="line">Linha Suave (Única Métrica)</option>
                          <option value="line_compare">Linha Dupla (Contraste de 2 Métricas)</option>
                       </optgroup>
                       <optgroup label="Comparativos / Barras">
                          <option value="bar">Barras Simples</option>
                          <option value="bar_stacked">Barras Empilhadas (Mix Proporcional)</option>
                       </optgroup>
                       <optgroup label="Modelos Complexos Multi-variados">
                          <option value="pie">Gráfico de Pizza (Composição)</option>
                          <option value="radar">Polígono Radar (Multidimensional)</option>
                          <option value="scatter">Gráfico de Dispersão (Anomalias)</option>
                          <option value="gauge">Velocímetro (Indicador de Ponteiro)</option>
                       </optgroup>
                     </select>
                  </div>
                  <div>
                     <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Indicador Paramétrico</label>
                     <select v-model="newWidgetForm.metric" required class="w-full bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl py-3 px-3 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mustard)] transition-colors font-semibold">
                       <option value="temp">Sobreaquecimento / Térmica</option>
                       <option value="vib">Desgaste Mecânico / Vibração</option>
                       <option value="cost">Custos Operacionais Brutos</option>
                       <option value="energy">Consumo Eletromagnético (KWh)</option>
                       <option value="prod">Quedas de Produção em Lotes</option>
                     </select>
                  </div>
                </div>

                <!-- Span -->
                <div>
                  <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1">Layout do Contêiner</label>
                  <select v-model="newWidgetForm.span" class="w-full bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl py-3 px-3 text-sm text-[var(--text-main)] focus:outline-none">
                    <option :value="1">Modo Retrato (1/3 da Tela)</option>
                    <option :value="2">Modo Paisagem (2/3 da Tela)</option>
                    <option :value="3">Modo Panorama (Toma a linha inteira)</option>
                  </select>
                </div>

                <!-- Colors -->
                <div>
                  <label class="block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-3">Tonalidade Predominante Visual</label>
                  <div class="flex flex-wrap gap-4 items-center">
                    <!-- Default Palette -->
                    <label v-for="(colorHex, colorName) in availableColors" :key="'col-'+colorName" class="cursor-pointer relative">
                      <input type="radio" v-model="newWidgetForm.color" :value="colorName" class="peer sr-only" name="customColor" />
                      <div class="w-10 h-10 rounded-full border-[3px] border-transparent peer-checked:scale-110 peer-checked:shadow-xl transition-all flex items-center justify-center hover:opacity-80" :style="{ backgroundColor: colorHex, borderColor: newWidgetForm.color === colorName ? 'var(--text-main)' : 'transparent' }">
                        <Check v-if="newWidgetForm.color === colorName" class="w-5 h-5 text-white" />
                      </div>
                    </label>

                    <!-- FREE CUSTOM COLOR PIPETTE -->
                    <label class="cursor-pointer relative flex items-center gap-2 group">
                      <input type="radio" v-model="newWidgetForm.color" value="Custom" class="peer sr-only" name="customColor" />
                      <div class="w-10 h-10 rounded-full border-[3px] border-transparent peer-checked:scale-110 peer-checked:shadow-xl transition-all flex items-center justify-center overflow-hidden hover:opacity-80 relative" :style="{ borderColor: newWidgetForm.color === 'Custom' ? 'var(--text-main)' : 'transparent', background: 'conic-gradient(red, yellow, lime, aqua, blue, magenta, red)' }">
                         <Check v-if="newWidgetForm.color === 'Custom'" class="w-5 h-5 text-white drop-shadow-md z-10 pointer-events-none" />
                      </div>
                      <!-- The actual input that controls HEX -->
                      <input 
                        v-if="newWidgetForm.color === 'Custom'" 
                        type="color" 
                        v-model="newWidgetForm.customHex" 
                        class="w-12 h-10 p-0 border border-[var(--border-color)] rounded-lg cursor-pointer bg-transparent animate-in zoom-in ml-1" 
                        title="Escolha qualquer cor da paleta"
                      />
                    </label>
                  </div>
                </div>

                <!-- Submit / Cancel -->
                <div class="flex gap-4 pt-4">
                  <button v-if="editingWidgetId" type="button" @click="cancelEdit" class="flex-1 border-2 border-[var(--border-color)] text-[var(--text-muted)] font-bold text-sm h-12 rounded-xl hover:bg-[var(--bg-app)] hover:text-[var(--text-main)] transition-colors">
                    Cancelar Edição
                  </button>
                  <button type="submit" class="flex-2 w-full flex justify-center items-center gap-2 font-bold text-[15px] h-12 rounded-xl hover:opacity-90 active:scale-[0.98] transition-all shadow-md" :class="editingWidgetId ? 'bg-[var(--color-vintage-mustard)] text-[var(--color-vintage-charcoal)]' : 'bg-[var(--color-vintage-mint)] text-white'">
                    <PlusCircle v-if="!editingWidgetId" class="w-5 h-5" />
                    <Check v-else class="w-5 h-5" />
                    {{ editingWidgetId ? 'Gravar Alterações' : 'Concluir Gráfico' }}
                  </button>
                </div>

              </form>
            </div>

          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Activity, Settings2, EyeOff, Trash2, Edit3, PieChart as LucidePieChart, X, ShieldCheck, Sparkles, Check, PlusCircle, LayoutTemplate } from 'lucide-vue-next'

import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
// Imported multiple EChart types to fulfill dynamic chart builder extension
import { LineChart, BarChart, RadarChart, PieChart, ScatterChart, GaugeChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, BarChart, RadarChart, PieChart, ScatterChart, GaugeChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent])

// Theme Colors Configuration
const vColors = {
  Mint: '#90A99E',
  Mustard: '#DABA78',
  Rose: '#C69F9B',
  Primary: '#7B8C9C',
  Dark: '#2A2626'
}

const availableColors = {
  Mint: vColors.Mint,
  Mustard: vColors.Mustard,
  Rose: vColors.Rose,
  Primary: vColors.Primary
}

const textColor = '#5e5757'
const gridColor = 'rgba(156, 149, 136, 0.15)'

// ==========================================
// STATE MANAGEMENT: WIDGETS
// ==========================================
const showWidgetManager = ref(false)
const editingWidgetId = ref(null)

const DEFAULT_WIDGETS = [
  { id: 'def_1', type: 'line_temp', isDefault: true, isVisible: true, title: 'Evolução de Temperatura X Vibração', subtitle: 'Média analítica (14 dias) duplo-eixo', span: 2 },
  { id: 'def_2', type: 'radar_risk', isDefault: true, isVisible: true, title: 'Risco por Setor Global', subtitle: 'Matriz Paramétrica', span: 1 },
  { id: 'def_3', type: 'bar_freq', isDefault: true, isVisible: true, title: 'Frequência de Anomalias Reais', subtitle: 'Alarmes disparados por componente mecânico (Trimestre)', span: 3 }
]

const widgets = ref([])

const visibleWidgets = computed(() => {
  return widgets.value.filter(w => w.isVisible)
})

onMounted(() => {
  const stored = localStorage.getItem('predictai_widgets')
  if (stored) {
    try {
      widgets.value = JSON.parse(stored)
      const hasDefaults = widgets.value.some(w => w.isDefault)
      if(!hasDefaults) widgets.value = [...DEFAULT_WIDGETS, ...widgets.value]
    } catch (e) {
      widgets.value = JSON.parse(JSON.stringify(DEFAULT_WIDGETS))
    }
  } else {
    widgets.value = JSON.parse(JSON.stringify(DEFAULT_WIDGETS))
  }
})

const saveWidgets = () => {
  localStorage.setItem('predictai_widgets', JSON.stringify(widgets.value))
}

watch(widgets, () => saveWidgets(), { deep: true })

const hideWidget = (id) => {
  const w = widgets.value.find(x => x.id === id)
  if (w) w.isVisible = false
}

const deleteWidget = (id) => {
  if (confirm("Você tem total certeza de que deseja deletar este Gráfico Personalizado? A exclusão é permanente.")) {
    widgets.value = widgets.value.filter(x => x.id !== id)
    if (editingWidgetId.value === id) cancelEdit()
  }
}

const openManager = () => {
  cancelEdit()
  showWidgetManager.value = true
}

// ==========================================
// CUSTOM BUILDER WIZARD
// ==========================================
const newWidgetForm = ref({
  title: '',
  type: 'line',
  metric: 'temp',
  color: 'Mint',
  customHex: '#5b1fc2',
  span: 1
})

const resetForm = () => {
  newWidgetForm.value = { title: '', type: 'line', metric: 'temp', color: 'Mint', customHex: '#5b1fc2', span: 1 }
  editingWidgetId.value = null
}

const cancelEdit = () => {
  resetForm()
}

const editWidgetInModal = (widget) => {
  editingWidgetId.value = widget.id
  
  // Determine if it was a predefined color or a custom HEX string
  const isPredefinedColor = Object.keys(availableColors).includes(widget.colorTheme)
  
  newWidgetForm.value = {
    title: widget.title,
    type: widget.type,
    metric: widget.metric || 'temp',
    color: isPredefinedColor ? widget.colorTheme : 'Custom',
    customHex: isPredefinedColor ? '#5b1fc2' : widget.colorTheme,
    span: widget.span || 1
  }
}

const editWidget = (id) => {
  const customWidget = widgets.value.find(w => w.id === id)
  if (customWidget) {
    showWidgetManager.value = true
    editWidgetInModal(customWidget)
  }
}

const saveCustomWidget = () => {
  // If the user picked "Custom", the theme color we store is the HEX value they picked
  const finalCompiledColor = newWidgetForm.value.color === 'Custom' ? newWidgetForm.value.customHex : newWidgetForm.value.color

  if (editingWidgetId.value) {
    // UPDATE
    const w = widgets.value.find(x => x.id === editingWidgetId.value)
    if (w) {
      w.title = newWidgetForm.value.title
      w.subtitle = `Indicador Focado: ${newWidgetForm.value.metric.toUpperCase()}`
      w.type = newWidgetForm.value.type
      w.metric = newWidgetForm.value.metric
      w.colorTheme = finalCompiledColor
      w.span = newWidgetForm.value.span
    }
  } else {
    // CREATE NEW
    const newId = 'custom_' + Date.now().toString()
    widgets.value.push({
      id: newId,
      isDefault: false,
      isVisible: true,
      title: newWidgetForm.value.title,
      subtitle: `Indicador Adicional: ${newWidgetForm.value.metric.toUpperCase()}`,
      type: newWidgetForm.value.type,
      metric: newWidgetForm.value.metric,
      colorTheme: finalCompiledColor,
      span: newWidgetForm.value.span
    })
  }
  
  resetForm()
}

// ==========================================
// MASSIVE ECHARTS ADAPTER GENERATOR
// ==========================================
const getChartOption = (widget) => {
  if (widget.type === 'line_temp') return defaultLineTempOption()
  if (widget.type === 'radar_risk') return defaultRadarRiskOption()
  if (widget.type === 'bar_freq') return defaultBarFreqOption()

  // Grab color. If colorTheme isn't in availableColors, it's a Custom hex color string!
  const colorHex = availableColors[widget.colorTheme] || widget.colorTheme || vColors.Mint
  
  // Complementary color for dual-axes
  let secondaryColorHex = vColors.Primary
  if (colorHex === vColors.Mint) secondaryColorHex = vColors.Mustard
  else if (colorHex === vColors.Mustard) secondaryColorHex = vColors.Rose
  else if (colorHex === vColors.Rose) secondaryColorHex = vColors.Primary
  else secondaryColorHex = '#333' // Safe fallback for custom hex blending
  
  // Fake generic structures tailored for the AI context
  let mockXAxis = ['Mês 1', 'Mês 2', 'Mês 3', 'Mês 4', 'Mês 5', 'Mês 6']
  let mockData1 = [12, 43, 20, 56, 45, 66]
  let mockData2 = [8, 30, 25, 40, 60, 55] // Used for compares/stacks
  let maxBounds = 100
  
  if (widget.metric === 'temp') { mockData1 = [75, 82, 85, 78, 90, 88]; mockData2 = [2.1, 2.5, 3.0, 2.8, 3.5, 3.1]; maxBounds=100; }
  if (widget.metric === 'cost') { mockData1 = [5000, 4200, 8000, 6300, 7100, 8500]; mockData2 = [4000, 4100, 6000, 6500, 6000, 8000]; maxBounds=10000;}
  if (widget.metric === 'energy') { mockData1 = [120, 150, 110, 200, 180, 220]; mockData2 = [110, 130, 100, 180, 150, 190]; maxBounds=300;}
  if (widget.metric === 'prod') { mockData1 = [2, 0, 1, 4, 3, 0]; mockData2 = [0, 1, 0, 2, 1, 0]; maxBounds=5;}
  if (widget.metric === 'vib') { mockData1 = [2.1, 2.8, 3.6, 3.0, 4.2, 5.0]; mockData2 = [1.8, 2.5, 3.5, 3.2, 4.0, 4.5]; maxBounds=6; }

  // 1. SIMPLE LINE
  if (widget.type === 'line') {
    return {
      color: [colorHex],
      tooltip: { trigger: 'axis', appendToBody: true, backgroundColor: 'rgba(253, 251, 247, 0.95)', textStyle: { color: textColor } },
      grid: { left: '3%', right: '5%', bottom: '10%', top: '15%', containLabel: true },
      xAxis: { type: 'category', boundaryGap: false, data: mockXAxis, axisLine: { lineStyle: { color: gridColor } }, axisLabel: { color: textColor } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: gridColor, type: 'dashed' } }, axisLabel: { color: textColor } },
      series: [{ type: 'line', smooth: true, lineStyle: { width: 4 }, showSymbol: true, areaStyle: { opacity: 0.1 }, data: mockData1, animationDuration: 1500, animationEasing: 'cubicOut' }]
    }
  } 
  
  // 2. DUAL-AXIS COMPARE LINE
  if (widget.type === 'line_compare') {
    return {
      color: [colorHex, secondaryColorHex],
      tooltip: { trigger: 'axis', appendToBody: true, backgroundColor: 'rgba(253, 251, 247, 0.95)', textStyle: { color: textColor } },
      legend: { data: ['Base Real', 'Predição IA'], textStyle: { color: textColor }, bottom: 0 },
      grid: { left: '3%', right: '5%', bottom: '15%', top: '15%', containLabel: true },
      xAxis: { type: 'category', boundaryGap: false, data: mockXAxis, axisLine: { lineStyle: { color: gridColor } }, axisLabel: { color: textColor } },
      yAxis: [{ type: 'value', splitLine: { lineStyle: { color: gridColor, type: 'dashed' } }, axisLabel: { color: textColor } }],
      series: [
        { name: 'Base Real', type: 'line', smooth: true, lineStyle: { width: 4 }, data: mockData1, animationDuration: 1700 },
        { name: 'Predição IA', type: 'line', smooth: true, lineStyle: { width: 3, type: 'dotted' }, data: mockData2, animationDuration: 2200 }
      ]
    }
  }

  // 3. BAR CHART
  if (widget.type === 'bar') {
    return {
      color: [colorHex],
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, appendToBody: true, backgroundColor: 'rgba(253, 251, 247, 0.95)' },
      grid: { left: '3%', right: '5%', bottom: '10%', top: '15%', containLabel: true },
      xAxis: { type: 'category', data: mockXAxis, axisLine: { lineStyle: { color: gridColor } }, axisLabel: { color: textColor } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: gridColor, type: 'dashed' } }, axisLabel: { color: textColor } },
      series: [{ type: 'bar', barWidth: '40%', itemStyle: { borderRadius: [6, 6, 0, 0] }, data: mockData1, animationDuration: 1500, animationEasing: 'elasticOut' }]
    }
  }

  // 4. STACKED BARS
  if (widget.type === 'bar_stacked') {
    return {
      color: [colorHex, secondaryColorHex],
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, appendToBody: true, backgroundColor: 'rgba(253, 251, 247, 0.95)' },
      legend: { data: ['Nível Crítico', 'Alerta Padrão'], textStyle: { color: textColor }, bottom: 0 },
      grid: { left: '3%', right: '5%', bottom: '15%', top: '15%', containLabel: true },
      xAxis: { type: 'category', data: mockXAxis, axisLine: { lineStyle: { color: gridColor } }, axisLabel: { color: textColor } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: gridColor, type: 'dashed' } }, axisLabel: { color: textColor } },
      series: [
        { name: 'Nível Crítico', type: 'bar', stack: 'total', barWidth: '40%', data: mockData1, animationDuration: 1500 },
        { name: 'Alerta Padrão', type: 'bar', stack: 'total', barWidth: '40%', itemStyle: { borderRadius: [6, 6, 0, 0] }, data: mockData2, animationDuration: 1800 }
      ]
    }
  }

  // 5. PIE/DONUT
  if (widget.type === 'pie') {
    const pieData = mockXAxis.map((label, idx) => ({ name: label, value: mockData1[idx] }))
    return {
      color: [colorHex, secondaryColorHex, vColors.Primary, vColors.Mint, vColors.Dark, vColors.Rose],
      tooltip: { trigger: 'item', appendToBody: true, backgroundColor: 'rgba(253, 251, 247, 0.95)' },
      legend: { bottom: '0%', left: 'center', textStyle: { color: textColor } },
      series: [{ type: 'pie', radius: ['40%', '70%'], avoidLabelOverlap: false, itemStyle: { borderRadius: 10, borderColor: 'var(--bg-app)', borderWidth: 2 }, label: { show: false }, data: pieData, animationDuration: 1500, animationType: 'scale' }]
    }
  }

  // 6. SCATTER PLOT
  if (widget.type === 'scatter') {
    const rawScatterData = mockData1.map((val, idx) => [val, mockData2[idx], Math.random() * 15 + 5]) // [x, y, radius]
    return {
      color: [colorHex],
      tooltip: { trigger: 'item', appendToBody: true, backgroundColor: 'rgba(253, 251, 247, 0.95)' },
      grid: { left: '5%', right: '5%', bottom: '10%', top: '15%', containLabel: true },
      xAxis: { type: 'value', axisLine: { lineStyle: { color: gridColor } }, axisLabel: { color: textColor }, splitLine: { lineStyle: { color: gridColor, type: 'dashed' } } },
      yAxis: { type: 'value', axisLabel: { color: textColor }, splitLine: { lineStyle: { color: gridColor, type: 'dashed' } } },
      series: [{
        symbolSize: (data) => data[2] * 2,
        data: rawScatterData,
        type: 'scatter',
        itemStyle: { opacity: 0.8, borderColor: colorHex, borderWidth: 2 },
        animationDelay: (idx) => idx * 50
      }]
    }
  }

  // 7. MULTIVARIATE RADAR
  if (widget.type === 'radar') {
    return {
      color: [colorHex, secondaryColorHex],
      tooltip: { trigger: 'item', appendToBody: true },
      legend: { bottom: 0, data: ['Grupo A', 'Grupo B'], textStyle: { color: textColor, fontSize: 11 } },
      radar: {
        indicator: mockXAxis.map(x => ({ name: x, max: maxBounds })),
        splitArea: { areaStyle: { color: ['rgba(250,250,250,0.05)', 'rgba(200,200,200,0.05)'] } },
        axisLine: { lineStyle: { color: gridColor } },
        splitLine: { lineStyle: { color: gridColor } },
        axisName: { color: textColor, fontSize: 10, fontWeight: 'bold' }
      },
      series: [{
        name: 'Parâmetros Operacionais',
        type: 'radar',
        symbol: 'circle',
        symbolSize: 6,
        areaStyle: { opacity: 0.2 },
        data: [
          { value: mockData1, name: 'Grupo A' },
          { value: mockData2, name: 'Grupo B', areaStyle: { opacity: 0.05 }, lineStyle: { type: 'dashed' } }
        ],
        animationDuration: 2000,
      }]
    }
  }

  // 8. TACHOMETER/GAUGE
  if (widget.type === 'gauge') {
    return {
      tooltip: { formatter: '{a} <br/>{b} : {c}%', appendToBody: true },
      series: [
        {
          name: 'Pressão Interna',
          type: 'gauge',
          progress: { show: true, width: 18, itemStyle: { color: colorHex } },
          axisLine: { lineStyle: { width: 18, color: [[1, gridColor]] } },
          axisTick: { show: false },
          splitLine: { length: 15, lineStyle: { width: 2, color: textColor } },
          axisLabel: { distance: 25, color: textColor, fontSize: 13 },
          pointer: { show: true, itemStyle: { color: textColor } },
          detail: { valueAnimation: true, formatter: '{value}', fontSize: 35, color: colorHex, offsetCenter: [0, '70%'] },
          data: [{ value: Math.round(mockData1[0]), name: 'Nível' }],
          animationDuration: 3000
        }
      ]
    }
  }

  return {}
}

const defaultLineTempOption = () => ({
  color: [vColors.Mint, vColors.Mustard],
  tooltip: { trigger: 'axis', appendToBody: true, backgroundColor: 'rgba(253, 251, 247, 0.95)', borderColor: '#e2dac9', textStyle: { color: '#2A2626' } },
  legend: { data: ['Temperatura (°C)', 'Vibração (mm/s)'], textStyle: { color: textColor }, bottom: 5 },
  grid: { left: '3%', right: '5%', bottom: '15%', top: '12%', containLabel: true },
  xAxis: { type: 'category', boundaryGap: false, data: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14'], axisLine: { lineStyle: { color: gridColor } }, axisLabel: { color: textColor } },
  yAxis: [
    { type: 'value', name: 'Temp (°C)', splitLine: { lineStyle: { color: gridColor, type: 'dashed' } }, axisLabel: { color: textColor }, nameTextStyle: { color: textColor } },
    { type: 'value', name: 'Vibração', position: 'right', splitLine: { show: false }, axisLabel: { color: textColor } }
  ],
  series: [
    { name: 'Temperatura (°C)', type: 'line', smooth: true, lineStyle: { width: 4 }, showSymbol: false, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(144, 169, 158, 0.5)' }, { offset: 1, color: 'rgba(144, 169, 158, 0.0)' }] } }, data: [65, 68, 66, 75, 82, 85, 78, 70, 68, 69, 72, 80, 88, 85], animationDuration: 2000, animationEasing: 'cubicOut' },
    { name: 'Vibração (mm/s)', type: 'line', yAxisIndex: 1, smooth: true, lineStyle: { width: 3, type: 'dashed' }, showSymbol: false, itemStyle: { color: vColors.Mustard }, data: [2.1, 2.3, 2.8, 3.5, 4.2, 4.0, 3.2, 2.5, 2.6, 2.9, 3.1, 4.5, 5.2, 4.8], animationDuration: 2500, animationEasing: 'cubicOut' }
  ]
})

const defaultRadarRiskOption = () => ({
  color: [vColors.Rose, vColors.Primary],
  tooltip: { trigger: 'item', appendToBody: true },
  legend: { bottom: 0, data: ['Hoje', 'Média'], textStyle: { color: textColor, fontSize: 11 } },
  radar: {
    indicator: [{ name: 'Temp', max: 10 }, { name: 'Vibração', max: 10 }, { name: 'Óleo', max: 10 }, { name: 'Eixo', max: 10 }, { name: 'Tensão', max: 10 }],
    splitArea: { areaStyle: { color: ['rgba(250,250,250,0.1)', 'rgba(200,200,200,0.1)'] } },
    axisLine: { lineStyle: { color: gridColor } },
    splitLine: { lineStyle: { color: gridColor } },
    axisName: { color: textColor, fontSize: 10, fontWeight: 'bold' }
  },
  series: [{
    name: 'Riscos Setoriais',
    type: 'radar',
    symbol: 'none',
    areaStyle: { opacity: 0.3 },
    data: [{ value: [8, 6, 7, 4, 3], name: 'Hoje' }, { value: [4, 5, 4, 5, 4], name: 'Média', areaStyle: { opacity: 0.1 } }],
    animationDuration: 2000,
  }]
})

const defaultBarFreqOption = () => ({
  color: [vColors.Primary],
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, appendToBody: true },
  grid: { left: '2%', right: '2%', bottom: '5%', top: '10%', containLabel: true },
  xAxis: { type: 'category', data: ['Motores', 'Compressor', 'Bombas', 'Tornos CNC', 'Injetoras', 'Fornos'], axisLine: { lineStyle: { color: gridColor } }, axisLabel: { color: textColor, fontWeight: 'bold' } },
  yAxis: { type: 'value', splitLine: { lineStyle: { color: gridColor, type: 'dotted' } }, axisLabel: { color: textColor } },
  series: [{
    name: 'Alertas', type: 'bar', barWidth: '30%', itemStyle: { borderRadius: [6, 6, 0, 0] },
    data: [{ value: 45, itemStyle: { color: vColors.Primary } }, { value: 72, itemStyle: { color: vColors.Rose } }, { value: 30, itemStyle: { color: vColors.Primary } }, { value: 55, itemStyle: { color: vColors.Mustard } }, { value: 20, itemStyle: { color: vColors.Primary } }, { value: 15, itemStyle: { color: vColors.Primary } }],
    animationDuration: 1800, animationEasing: 'elasticOut', animationDelay: (idx) => idx * 100
  }]
})

</script>

<style scoped>
.chart {
  width: 100%;
  height: 100%;
}

/* List Transitions */
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.list-leave-active {
  position: absolute;
}
</style>
