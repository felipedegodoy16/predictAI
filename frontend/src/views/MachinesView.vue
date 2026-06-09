<template>
  <div class="h-full flex flex-col gap-6 relative pb-10">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tighter">Frota Operacional</h1>
        <p class="text-[var(--text-muted)] font-medium">Gestão, status e cadastramento de equipamentos ativos.</p>
      </div>
      <button v-if="!authStore.isViewer" @click="openCreateModal"
        class="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[var(--color-vintage-mint)] text-white font-bold shadow-md hover:-translate-y-0.5 transition-transform">
        <Plus class="w-5 h-5" /> Cadastrar Máquina
      </button>
    </div>

    <!-- Toolbar -->
    <div class="flex flex-col md:flex-row gap-4 items-center justify-between">
      <div class="flex-1 w-full relative">
        <label for="machine-search" class="sr-only">Pesquisar</label>
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search class="w-5 h-5 text-[var(--text-muted)]" />
        </div>
        <input id="machine-search" v-model="searchQuery" @keyup.enter="handleSearch" type="text"
          placeholder="Pesquisar por Nº Série, Fabricante, Modelo..."
          class="w-full max-w-md pl-10 pr-4 py-2.5 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl text-sm focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors text-[var(--text-main)] font-medium shadow-sm" />
        <button v-if="searchQuery" @click="clearSearch"
          class="absolute inset-y-0 left-[26rem] flex items-center text-[var(--text-muted)] hover:text-[var(--text-main)]">
          <X class="w-4 h-4 ml-2" />
        </button>
      </div>

      <div class="flex gap-4 w-full md:w-auto">
        <div class="hidden sm:flex items-center bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-1 shadow-sm shrink-0">
          <button @click="viewMode = 'table'" class="w-8 h-8 rounded-lg transition-all focus:outline-none flex items-center justify-center"
            :class="viewMode === 'table' ? 'bg-[var(--bg-app)] text-[var(--color-vintage-mint)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'">
            <List class="w-5 h-5" />
          </button>
          <button @click="viewMode = 'grid'" class="w-8 h-8 rounded-lg transition-all focus:outline-none flex items-center justify-center"
            :class="viewMode === 'grid' ? 'bg-[var(--bg-app)] text-[var(--color-vintage-mint)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'">
            <LayoutGrid class="w-5 h-5" />
          </button>
        </div>

        <div class="flex items-center bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl px-2 shadow-sm">
          <Filter class="w-4 h-4 text-[var(--text-muted)] ml-2 shrink-0" />
          <select v-model="statusFilter" @change="fetchMachines"
            class="bg-transparent border-none focus:outline-none py-2.5 px-3 text-sm font-bold text-[var(--text-main)] cursor-pointer">
            <option value="">Status: Todos</option>
            <option value="ativa">Status: Ativa</option>
            <option value="manutencao">Status: Em Manutenção</option>
            <option value="inativa">Status: Inativa</option>
          </select>
        </div>

        <div class="flex items-center bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl px-2 shadow-sm">
          <Layers class="w-4 h-4 text-[var(--text-muted)] ml-2 shrink-0" />
          <select v-model="pageSize" @change="resetPagination"
            class="bg-transparent border-none focus:outline-none py-2.5 px-3 text-sm font-bold text-[var(--text-main)] cursor-pointer">
            <option :value="10">Exibir 10</option>
            <option :value="20">Exibir 20</option>
            <option :value="50">Exibir 50</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Table / Grid -->
    <div class="vintage-panel flex-1 flex flex-col overflow-hidden relative shadow-md">
      <div v-if="loading" class="absolute inset-0 z-10 bg-[var(--bg-card)]/50 backdrop-blur-sm flex items-center justify-center">
        <div class="w-10 h-10 border-4 border-[var(--color-vintage-mint)] border-t-transparent rounded-full animate-spin"></div>
      </div>

      <!-- TABLE -->
      <div v-if="viewMode === 'table'" class="overflow-x-auto">
        <table class="w-full text-left text-sm whitespace-nowrap">
          <thead class="bg-[var(--bg-app)] border-b border-[var(--border-color)] text-[10px] uppercase tracking-wider font-extrabold text-[var(--text-muted)]">
            <tr>
              <th class="px-6 py-4">Máquina / Nº Série</th>
              <th class="px-6 py-4">Status</th>
              <th class="px-6 py-4">Fabricante / Modelo</th>
              <th class="px-6 py-4">Linha de Prod.</th>
              <th class="px-6 py-4">Sensores</th>
              <th class="px-6 py-4 text-center">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[var(--border-color)] font-medium">
            <tr v-if="machines.length === 0 && !loading">
              <td colspan="6" class="px-6 py-12 text-center text-[var(--text-muted)]">Nenhum equipamento encontrado.</td>
            </tr>
            <tr v-for="mach in machines" :key="mach.id"
              class="hover:bg-[var(--bg-app)]/50 transition-colors group cursor-pointer"
              @click="openDetailModal(mach)">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-xl bg-[var(--bg-app)] border border-[var(--border-color)] flex items-center justify-center shadow-sm">
                    <Cpu class="w-5 h-5 text-[var(--text-muted)]" />
                  </div>
                  <div>
                    <p class="font-bold text-[var(--text-main)] text-[15px] group-hover:text-[var(--color-vintage-mint)] transition-colors">
                      {{ mach.manufacturer }} {{ mach.model }}
                    </p>
                    <p class="text-xs text-[var(--text-muted)] uppercase tracking-wider">{{ mach.serial_number }}</p>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="px-3 py-1 text-[11px] uppercase tracking-wider font-bold rounded-full border"
                  :class="statusClass(mach.current_status?.status)">
                  {{ statusLabel(mach.current_status?.status) }}
                </span>
              </td>
              <td class="px-6 py-4">
                <p class="text-sm font-bold text-[var(--text-main)]">{{ mach.manufacturer || '—' }}</p>
                <p class="text-xs text-[var(--text-muted)]">{{ mach.model || '—' }}</p>
              </td>
              <td class="px-6 py-4 text-sm text-[var(--text-muted)] font-bold">{{ mach.production_line || '—' }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-1">
                  <span class="text-xs font-bold text-[var(--text-main)]">{{ mach.sensors?.length || 0 }}</span>
                  <Radio class="w-3.5 h-3.5 text-[var(--text-muted)]" />
                </div>
              </td>
              <td class="px-6 py-4 text-center">
                <div class="flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button v-if="!authStore.isViewer" @click.stop="openEditModal(mach)" title="Editar"
                    class="p-1.5 rounded hover:bg-[var(--color-vintage-mint)]/20 text-[var(--color-vintage-mint)] transition-colors">
                    <Edit3 class="w-4 h-4" />
                  </button>
                  <button v-if="authStore.isAdminOrManager" @click.stop="deleteMachine(mach.id)" title="Deletar"
                    class="p-1.5 rounded hover:bg-[var(--color-vintage-rose)]/20 text-[var(--color-vintage-rose)] transition-colors">
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- GRID -->
      <div v-else-if="viewMode === 'grid'" class="p-6 overflow-y-auto w-full h-[calc(100vh-280px)]">
        <div v-if="machines.length === 0 && !loading" class="text-center text-[var(--text-muted)] py-12">Nenhum equipamento encontrado.</div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 content-start pb-8">
          <div v-for="mach in machines" :key="mach.id"
            class="bg-[var(--bg-app)] border border-[var(--border-color)] rounded-2xl p-5 hover:border-[var(--color-vintage-mint)] transition-all group flex flex-col gap-4 shadow-sm cursor-pointer"
            @click="openDetailModal(mach)">
            <div class="flex justify-between items-start">
              <div class="flex items-center gap-3">
                <div class="w-12 h-12 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] flex items-center justify-center shadow-sm">
                  <Cpu class="w-6 h-6 text-[var(--text-muted)] group-hover:text-[var(--color-vintage-mint)] transition-colors" />
                </div>
                <div>
                  <p class="font-bold text-[var(--text-main)] text-[15px]">{{ mach.manufacturer }} {{ mach.model }}</p>
                  <p class="text-xs text-[var(--text-muted)] uppercase tracking-wider">{{ mach.serial_number }}</p>
                </div>
              </div>
              <span class="px-2.5 py-1 text-[10px] uppercase tracking-wider font-bold rounded-full border shrink-0"
                :class="statusClass(mach.current_status?.status)">
                {{ statusLabel(mach.current_status?.status) }}
              </span>
            </div>

            <!-- Sensor chips -->
            <div v-if="mach.sensors?.length" class="flex flex-wrap gap-1.5">
              <span v-for="s in mach.sensors.slice(0,4)" :key="s.id"
                class="text-[10px] font-bold px-2 py-0.5 rounded-full border"
                :class="sensorChipClass(s)">
                {{ s.sensor_type }} {{ s.last_value != null ? s.last_value.toFixed(1) + ' ' + s.unit : '' }}
              </span>
              <span v-if="mach.sensors.length > 4" class="text-[10px] font-bold px-2 py-0.5 rounded-full border border-[var(--border-color)] text-[var(--text-muted)]">
                +{{ mach.sensors.length - 4 }} mais
              </span>
            </div>
            <div v-else class="text-[11px] text-[var(--text-muted)]">Sem sensores cadastrados</div>

            <div class="mt-auto pt-4 border-t border-[var(--border-color)] flex gap-2">
              <button v-if="!authStore.isViewer" @click.stop="openEditModal(mach)"
                class="flex-1 flex justify-center items-center gap-1.5 py-2 rounded-lg bg-[var(--bg-card)] hover:bg-[var(--color-vintage-mint)] hover:text-white text-[var(--text-main)] text-xs font-bold transition-colors border border-[var(--border-color)] hover:border-transparent">
                <Edit3 class="w-3.5 h-3.5" /> Editar
              </button>
              <button v-if="authStore.isAdminOrManager" @click.stop="deleteMachine(mach.id)"
                class="py-2 px-3 rounded-lg bg-[var(--bg-card)] hover:bg-[var(--color-vintage-rose)]/10 text-[var(--text-muted)] hover:text-[var(--color-vintage-rose)] transition-colors border border-[var(--border-color)] hover:border-[var(--color-vintage-rose)]/30">
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="mt-auto border-t border-[var(--border-color)] bg-[var(--bg-app)]/50 p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p class="text-xs font-bold text-[var(--text-muted)]">
          Mostrando <span class="text-[var(--text-main)]">{{ paginationStart }}</span>–<span class="text-[var(--text-main)]">{{ paginationEnd }}</span> de <span class="text-[var(--text-main)]">{{ totalItems }}</span>
        </p>
        <div class="flex items-center gap-2">
          <button @click="prevPage" :disabled="currentPage === 1"
            class="p-2 border border-[var(--border-color)] rounded-lg text-[var(--text-muted)] hover:bg-[var(--bg-card)] hover:text-[var(--text-main)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
            <ChevronLeft class="w-4 h-4" />
          </button>
          <span class="text-xs font-bold px-4 tracking-widest text-[var(--text-main)]">{{ currentPage }} / {{ totalPages }}</span>
          <button @click="nextPage" :disabled="currentPage === totalPages"
            class="p-2 border border-[var(--border-color)] rounded-lg text-[var(--text-muted)] hover:bg-[var(--bg-card)] hover:text-[var(--text-main)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════
         CREATE / EDIT MODAL
    ══════════════════════════════════════════════════════════ -->
    <Teleport to="body">
      <div v-if="showModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="closeModal"></div>

        <div class="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-3xl w-full max-w-3xl max-h-[92vh] flex flex-col relative z-[101] shadow-2xl overflow-hidden">

          <!-- Modal header -->
          <div class="p-6 border-b border-[var(--border-color)] flex justify-between items-center bg-[var(--bg-app)] shrink-0">
            <div>
              <h2 class="text-xl font-bold tracking-tight text-[var(--text-main)]">{{ isEditing ? 'Editar Máquina' : 'Nova Máquina na Planta' }}</h2>
              <p class="text-xs text-[var(--text-muted)] font-bold mt-1">Preencha os dados do equipamento e adicione sensores.</p>
            </div>
            <button @click="closeModal" class="p-2 hover:bg-[var(--bg-card)] rounded-lg transition-colors">
              <X class="w-5 h-5 text-[var(--text-muted)]" />
            </button>
          </div>

          <!-- Tabs -->
          <div class="flex border-b border-[var(--border-color)] bg-[var(--bg-app)] shrink-0">
            <button @click="activeTab = 'machine'"
              class="px-6 py-3 text-sm font-bold transition-colors border-b-2"
              :class="activeTab === 'machine' ? 'border-[var(--color-vintage-mint)] text-[var(--color-vintage-mint)]' : 'border-transparent text-[var(--text-muted)] hover:text-[var(--text-main)]'">
              <Cpu class="w-4 h-4 inline mr-1.5" />Dados da Máquina
            </button>
            <button @click="activeTab = 'sensors'"
              class="px-6 py-3 text-sm font-bold transition-colors border-b-2"
              :class="activeTab === 'sensors' ? 'border-[var(--color-vintage-mint)] text-[var(--color-vintage-mint)]' : 'border-transparent text-[var(--text-muted)] hover:text-[var(--text-main)]'">
              <Radio class="w-4 h-4 inline mr-1.5" />Sensores
              <span class="ml-1.5 text-[10px] font-bold bg-[var(--text-main)]/10 text-[var(--text-main)] px-1.5 py-0.5 rounded-full">{{ sensors.length }}</span>
            </button>
          </div>

          <form @submit.prevent="saveMachine" class="flex-1 overflow-y-auto">

            <!-- TAB: Machine data -->
            <div v-show="activeTab === 'machine'" class="p-6 space-y-5">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-5">

                <div class="col-span-2">
                  <label class="field-label">Fabricante *</label>
                  <input v-model="form.manufacturer" type="text" required placeholder="Ex: Siemens, ABB, WEG..."
                    class="field-input" />
                </div>

                <div>
                  <label class="field-label">Modelo *</label>
                  <input v-model="form.model" type="text" required placeholder="Ex: CNC-500X"
                    class="field-input" />
                </div>

                <div>
                  <label class="field-label">Nº de Série *</label>
                  <input v-model="form.serial_number" type="text" required placeholder="ABC-12345"
                    class="field-input" />
                </div>

                <div>
                  <label class="field-label">Linha de Produção</label>
                  <input v-model="form.production_line" type="text" placeholder="Ex: Linha A, Setor 3"
                    class="field-input" />
                </div>

                <div>
                  <label class="field-label">Data de Instalação</label>
                  <input v-model="form.installation_date" type="date"
                    class="field-input" />
                </div>

                <div>
                  <label class="field-label" title="0 = contínuo">Int. Telemetria (min)</label>
                  <input v-model.number="form.telemetry_interval" type="number" min="0"
                    placeholder="0" class="field-input" />
                </div>

                <div>
                  <label class="field-label" title="Em dias">Int. Manutenção Prev. (dias)</label>
                  <input v-model.number="form.preventive_maintenance_interval" type="number" min="1"
                    placeholder="Ex: 180" class="field-input" />
                </div>

                <!-- Status (only when editing) -->
                <div v-if="isEditing" class="col-span-2">
                  <label class="field-label">Status Operacional</label>
                  <select v-model="form.status" class="field-input font-bold">
                    <option value="ativa">Ativa (Operando)</option>
                    <option value="manutencao">Em Manutenção</option>
                    <option value="inativa">Inativa (Desligada)</option>
                  </select>
                </div>

              </div>
            </div>

            <!-- TAB: Sensors -->
            <div v-show="activeTab === 'sensors'" class="p-6 space-y-4">

              <!-- Existing sensors list -->
              <div v-if="sensors.length > 0" class="space-y-3">
                <div v-for="(s, i) in sensors" :key="i"
                  class="flex items-center gap-3 p-4 bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl group">
                  <div class="w-8 h-8 rounded-lg bg-[var(--color-vintage-mint)]/10 text-[var(--color-vintage-mint)] flex items-center justify-center shrink-0">
                    <Radio class="w-4 h-4" />
                  </div>
                  <div class="flex-1 grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                    <div>
                      <p class="text-[10px] font-bold uppercase text-[var(--text-muted)]">Tipo</p>
                      <p class="font-bold text-[var(--text-main)]">{{ s.sensor_type }}</p>
                    </div>
                    <div>
                      <p class="text-[10px] font-bold uppercase text-[var(--text-muted)]">Unidade</p>
                      <p class="font-bold text-[var(--text-main)]">{{ s.unit }}</p>
                    </div>
                    <div>
                      <p class="text-[10px] font-bold uppercase text-[var(--text-muted)]">Limite</p>
                      <p class="font-bold text-[var(--text-main)]">{{ s.limit_temp ?? '—' }}</p>
                    </div>
                    <div>
                      <p class="text-[10px] font-bold uppercase text-[var(--text-muted)]">Última leitura</p>
                      <p class="font-bold text-[var(--text-main)]">{{ s.last_value != null ? s.last_value.toFixed(2) + ' ' + s.unit : 'Sem dados' }}</p>
                    </div>
                  </div>
                  <button type="button" @click="removeSensor(i)"
                    class="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg text-[var(--color-vintage-rose)] hover:bg-[var(--color-vintage-rose)]/10 transition-all shrink-0">
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div v-else class="text-center py-8 text-[var(--text-muted)] text-sm border-2 border-dashed border-[var(--border-color)] rounded-xl">
                Nenhum sensor adicionado. Clique em <strong>+ Adicionar Sensor</strong> abaixo.
              </div>

              <!-- Add sensor form -->
              <div class="p-4 bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl space-y-4">
                <p class="text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)]">Novo Sensor</p>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

                  <div>
                    <label class="field-label">Tipo de Sensor *</label>
                    <select v-model="newSensor.sensor_type" class="field-input font-bold">
                      <option value="">Selecione...</option>
                      <option value="temperatura">Temperatura</option>
                      <option value="vibracao">Vibração</option>
                      <option value="pressao">Pressão</option>
                      <option value="corrente">Corrente Elétrica</option>
                      <option value="umidade">Umidade</option>
                      <option value="velocidade">Velocidade</option>
                      <option value="outro">Outro</option>
                    </select>
                  </div>

                  <div>
                    <label class="field-label">Unidade de Medida *</label>
                    <input v-model="newSensor.unit" type="text" placeholder="Ex: °C, mm/s, bar, A..."
                      class="field-input" />
                  </div>

                  <div>
                    <label class="field-label">Limite para Alerta</label>
                    <input v-model.number="newSensor.limit_temp" type="number" step="0.01"
                      placeholder="Valor que dispara alerta crítico"
                      class="field-input" />
                  </div>

                  <div>
                    <label class="field-label">Descrição</label>
                    <input v-model="newSensor.description" type="text" placeholder="Ex: Sensor no rolamento dianteiro"
                      class="field-input" />
                  </div>

                </div>
                <button type="button" @click="addSensor"
                  class="flex items-center gap-2 px-4 py-2 rounded-xl bg-[var(--color-vintage-mint)]/10 text-[var(--color-vintage-mint)] border border-[var(--color-vintage-mint)]/30 font-bold text-sm hover:bg-[var(--color-vintage-mint)] hover:text-white transition-all">
                  <Plus class="w-4 h-4" /> Adicionar Sensor
                </button>
              </div>
            </div>

            <!-- Actions -->
            <div class="p-6 border-t border-[var(--border-color)] bg-[var(--bg-app)] flex gap-4 shrink-0">
              <button type="button" @click="closeModal"
                class="flex-1 py-3 border-2 border-[var(--border-color)] text-[var(--text-muted)] font-bold text-sm rounded-xl hover:bg-[var(--bg-card)] hover:text-[var(--text-main)] transition-colors">
                Cancelar
              </button>
              <button type="submit"
                class="flex-1 py-3 bg-[var(--color-vintage-mint)] text-white font-bold text-sm rounded-xl shadow-md hover:opacity-90 active:scale-[0.98] transition-all flex justify-center items-center gap-2">
                <Save class="w-4 h-4" />
                {{ isEditing ? 'Salvar Mudanças' : 'Cadastrar Equipamento' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- ══════════════════════════════════════════════════════════
         DETAIL MODAL (read-only with live sensor values)
    ══════════════════════════════════════════════════════════ -->
    <Teleport to="body">
      <div v-if="showDetailModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="showDetailModal = false"></div>

        <div class="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-3xl w-full max-w-2xl max-h-[92vh] flex flex-col relative z-[101] shadow-2xl overflow-hidden">
          <!-- header -->
          <div class="p-6 border-b border-[var(--border-color)] bg-[var(--bg-app)] flex justify-between items-start shrink-0">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="px-2.5 py-1 text-[10px] uppercase tracking-wider font-bold rounded-full border"
                  :class="statusClass(selectedMachine?.current_status?.status)">
                  {{ statusLabel(selectedMachine?.current_status?.status) }}
                </span>
              </div>
              <h2 class="text-xl font-bold text-[var(--text-main)]">
                {{ selectedMachine?.manufacturer }} {{ selectedMachine?.model }}
              </h2>
              <p class="text-xs text-[var(--text-muted)] mt-0.5 uppercase tracking-wider font-bold">
                {{ selectedMachine?.serial_number }}
              </p>
            </div>
            <div class="flex items-center gap-2">
              <button v-if="!authStore.isViewer" @click="openEditModal(selectedMachine); showDetailModal = false"
                class="px-3 py-2 rounded-xl bg-[var(--color-vintage-mint)]/10 text-[var(--color-vintage-mint)] border border-[var(--color-vintage-mint)]/30 font-bold text-sm hover:bg-[var(--color-vintage-mint)] hover:text-white transition-all flex items-center gap-1.5">
                <Edit3 class="w-4 h-4" /> Editar
              </button>
              <button @click="showDetailModal = false" class="p-2 hover:bg-[var(--bg-card)] rounded-lg transition-colors">
                <X class="w-5 h-5 text-[var(--text-muted)]" />
              </button>
            </div>
          </div>

          <!-- info grid -->
          <div class="p-6 space-y-5 overflow-y-auto flex-1">
            <div class="grid grid-cols-2 gap-4">
              <div class="p-4 bg-[var(--bg-app)] rounded-xl border border-[var(--border-color)]">
                <p class="text-[10px] font-bold uppercase text-[var(--text-muted)] mb-1">Linha de Produção</p>
                <p class="font-bold text-[var(--text-main)]">{{ selectedMachine?.production_line || '—' }}</p>
              </div>
              <div class="p-4 bg-[var(--bg-app)] rounded-xl border border-[var(--border-color)]">
                <p class="text-[10px] font-bold uppercase text-[var(--text-muted)] mb-1">Data de Instalação</p>
                <p class="font-bold text-[var(--text-main)]">{{ selectedMachine?.installation_date || '—' }}</p>
              </div>
            </div>

            <!-- Sensors with live values -->
            <div>
              <p class="text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-3">
                Sensores ({{ selectedMachine?.sensors?.length || 0 }})
              </p>
              <div v-if="selectedMachine?.sensors?.length" class="space-y-3">
                <div v-for="s in selectedMachine.sensors" :key="s.id"
                  class="flex items-center gap-4 p-4 bg-[var(--bg-app)] border rounded-xl transition-colors"
                  :class="sensorBorderClass(s)">
                  <!-- Indicator dot -->
                  <div class="w-3 h-3 rounded-full shrink-0" :class="sensorDotClass(s)"></div>
                  <div class="flex-1">
                    <div class="flex items-center justify-between">
                      <p class="font-bold text-sm text-[var(--text-main)]">{{ s.sensor_type }}</p>
                      <p class="text-lg font-black" :class="sensorValueClass(s)">
                        {{ s.last_value != null ? s.last_value.toFixed(2) : '—' }}
                        <span class="text-xs font-bold text-[var(--text-muted)]">{{ s.unit }}</span>
                      </p>
                    </div>
                    <div class="flex items-center justify-between mt-1">
                      <p class="text-[11px] text-[var(--text-muted)]">{{ s.description || 'Sem descrição' }}</p>
                      <p class="text-[11px] text-[var(--text-muted)]">
                        Limite: <span class="font-bold">{{ s.limit_temp ?? '—' }} {{ s.unit }}</span>
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-6 text-sm text-[var(--text-muted)] border-2 border-dashed border-[var(--border-color)] rounded-xl">
                Nenhum sensor cadastrado nesta máquina.
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Plus, Filter, Edit3, Trash2, X, ChevronLeft, ChevronRight, Layers, Cpu, Save, LayoutGrid, List, Radio } from 'lucide-vue-next'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

// ── State ──────────────────────────────────────────────────────────────────────
const authStore = useAuthStore()
const viewMode = ref('table')
const machines = ref([])
const totalItems = ref(0)
const loading = ref(true)

const searchQuery = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const totalPages = computed(() => Math.max(1, Math.ceil(totalItems.value / pageSize.value)))
const paginationStart = computed(() => ((currentPage.value - 1) * pageSize.value) + (totalItems.value > 0 ? 1 : 0))
const paginationEnd = computed(() => Math.min(currentPage.value * pageSize.value, totalItems.value))

// Modal — create/edit
const showModal = ref(false)
const isEditing = ref(false)
let currentEditingId = null
const activeTab = ref('machine')

const emptyForm = {
  manufacturer: '',
  model: '',
  serial_number: '',
  production_line: '',
  installation_date: '',
  telemetry_interval: 0,
  preventive_maintenance_interval: null,
  status: 'ativa',
}
const form = ref({ ...emptyForm })

// Sensors list (for the form)
const sensors = ref([])
const newSensor = ref({ sensor_type: '', unit: '', limit_temp: null, description: '', is_active: true })

// Detail modal
const showDetailModal = ref(false)
const selectedMachine = ref(null)

// ── Formatters ─────────────────────────────────────────────────────────────────
const statusLabel = (s) => {
  const map = { ativa: 'Ativa', manutencao: 'Em Manutenção', inativa: 'Inativa' }
  return map[s] || s || 'Sem Status'
}
const statusClass = (s) => ({
  'bg-[var(--color-vintage-mint)]/10 text-[var(--color-vintage-mint)] border-[var(--color-vintage-mint)]/20': s === 'ativa',
  'bg-[var(--color-vintage-mustard)]/10 text-[var(--color-vintage-mustard)] border-[var(--color-vintage-mustard)]/20': s === 'manutencao',
  'bg-[var(--color-vintage-rose)]/10 text-[var(--color-vintage-rose)] border-[var(--color-vintage-rose)]/20': s === 'inativa' || !s,
})

// Sensor color helpers (based on last_value vs limit_temp)
const sensorStatus = (s) => {
  if (s.last_value == null || !s.limit_temp) return 'ok'
  const ratio = s.last_value / s.limit_temp
  if (ratio >= 1.0) return 'critical'
  if (ratio >= 0.9) return 'warning'
  return 'ok'
}
const sensorDotClass = (s) => {
  const st = sensorStatus(s)
  if (st === 'critical') return 'bg-[var(--color-vintage-rose)]'
  if (st === 'warning') return 'bg-[var(--color-vintage-mustard)]'
  return 'bg-[var(--color-vintage-mint)]'
}
const sensorBorderClass = (s) => {
  const st = sensorStatus(s)
  if (st === 'critical') return 'border-[var(--color-vintage-rose)]/40'
  if (st === 'warning') return 'border-[var(--color-vintage-mustard)]/40'
  return 'border-[var(--border-color)]'
}
const sensorValueClass = (s) => {
  const st = sensorStatus(s)
  if (st === 'critical') return 'text-[var(--color-vintage-rose)]'
  if (st === 'warning') return 'text-[var(--color-vintage-mustard)]'
  return 'text-[var(--color-vintage-mint)]'
}
const sensorChipClass = (s) => {
  const st = sensorStatus(s)
  if (st === 'critical') return 'bg-[var(--color-vintage-rose)]/10 text-[var(--color-vintage-rose)] border-[var(--color-vintage-rose)]/30'
  if (st === 'warning') return 'bg-[var(--color-vintage-mustard)]/10 text-[var(--color-vintage-mustard)] border-[var(--color-vintage-mustard)]/30'
  return 'bg-[var(--color-vintage-mint)]/10 text-[var(--color-vintage-mint)] border-[var(--color-vintage-mint)]/20'
}

// ── Data ───────────────────────────────────────────────────────────────────────
const fetchMachines = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, size: pageSize.value }
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (statusFilter.value) params.status = statusFilter.value

    const res = await api.get('/machines/', { params })
    if (res.data.results) {
      machines.value = res.data.results
      totalItems.value = res.data.count
    } else {
      machines.value = res.data
      totalItems.value = res.data.length
    }
  } catch (e) {
    console.error('Erro ao carregar máquinas:', e)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => { currentPage.value = 1; fetchMachines() }
const clearSearch = () => { searchQuery.value = ''; handleSearch() }
const resetPagination = () => { currentPage.value = 1; fetchMachines() }
const prevPage = () => { if (currentPage.value > 1) { currentPage.value--; fetchMachines() } }
const nextPage = () => { if (currentPage.value < totalPages.value) { currentPage.value++; fetchMachines() } }

// ── Sensors form helpers ────────────────────────────────────────────────────────
const addSensor = () => {
  if (!newSensor.value.sensor_type || !newSensor.value.unit) {
    alert('Preencha o tipo e a unidade do sensor.')
    return
  }
  sensors.value.push({ ...newSensor.value, last_value: null })
  newSensor.value = { sensor_type: '', unit: '', limit_temp: null, description: '', is_active: true }
}

const removeSensor = async (index) => {
  const s = sensors.value[index]
  if (s.id) {
    // Already saved — delete from API
    if (!confirm('Remover este sensor permanentemente?')) return
    try {
      await api.delete(`/sensors/${s.id}/`)
    } catch (e) {
      alert('Não foi possível remover o sensor.')
      return
    }
  }
  sensors.value.splice(index, 1)
}

// ── Modal flows ────────────────────────────────────────────────────────────────
const openCreateModal = () => {
  isEditing.value = false
  currentEditingId = null
  form.value = { ...emptyForm }
  sensors.value = []
  newSensor.value = { sensor_type: '', unit: '', limit_temp: null, description: '', is_active: true }
  activeTab.value = 'machine'
  showModal.value = true
}

const openEditModal = (machine) => {
  isEditing.value = true
  currentEditingId = machine.id
  form.value = {
    manufacturer: machine.manufacturer || '',
    model: machine.model || '',
    serial_number: machine.serial_number || '',
    production_line: machine.production_line || '',
    installation_date: machine.installation_date || '',
    telemetry_interval: machine.telemetry_interval || 0,
    preventive_maintenance_interval: machine.preventive_maintenance_interval || null,
    status: machine.current_status?.status || 'ativa',
  }
  sensors.value = machine.sensors ? machine.sensors.map(s => ({ ...s })) : []
  newSensor.value = { sensor_type: '', unit: '', limit_temp: null, description: '', is_active: true }
  activeTab.value = 'machine'
  showModal.value = true
}

const openDetailModal = (machine) => {
  selectedMachine.value = machine
  showDetailModal.value = true
}

const closeModal = () => { showModal.value = false }

// ── Save ──────────────────────────────────────────────────────────────────────
const saveMachine = async () => {
  loading.value = true
  try {
    let machineId = currentEditingId

    const payload = {
      manufacturer: form.value.manufacturer,
      model: form.value.model,
      serial_number: form.value.serial_number,
      production_line: form.value.production_line,
      installation_date: form.value.installation_date || null,
      telemetry_interval: form.value.telemetry_interval || 0,
      preventive_maintenance_interval: form.value.preventive_maintenance_interval || null,
    }

    if (isEditing.value) {
      await api.patch(`/machines/${machineId}/`, payload)
      // Update status if changed
      if (form.value.status) {
        await api.post(`/machines/${machineId}/status/`, { status: form.value.status, reason: 'Atualização manual' })
          .catch(() => {}) // non-critical
      }
    } else {
      const res = await api.post('/machines/', payload)
      machineId = res.data.id
    }

    // Save new sensors (those without an id are new)
    const newSensors = sensors.value.filter(s => !s.id)
    for (const s of newSensors) {
      await api.post('/sensors/', {
        machine: machineId,
        sensor_type: s.sensor_type,
        unit: s.unit,
        description: s.description || '',
        limit_temp: s.limit_temp || null,
        is_active: true,
      })
    }

    closeModal()
    await fetchMachines()
  } catch (err) {
    console.error(err)
    alert('Erro ao salvar. Verifique os campos obrigatórios.')
  } finally {
    loading.value = false
  }
}

const deleteMachine = async (id) => {
  if (!confirm('Deseja realmente excluir este equipamento?')) return
  try {
    loading.value = true
    await api.delete(`/machines/${id}/`)
    if (machines.value.length === 1 && currentPage.value > 1) currentPage.value--
    await fetchMachines()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchMachines)
</script>

<style scoped>
@reference "tailwindcss";
.field-label {
  @apply block text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-1;
}
.field-input {
  @apply w-full bg-[var(--bg-app)] border border-[var(--border-color)] rounded-xl py-3 px-4 text-sm text-[var(--text-main)] focus:outline-none focus:border-[var(--color-vintage-mint)] transition-colors;
}
</style>
