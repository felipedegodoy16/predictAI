<template>
    <div
        class="h-screen w-full flex overflow-hidden relative bg-[var(--color-vintage-cream)] dark:bg-[var(--color-vintage-dark)] transition-colors duration-500"
    >
        <!-- Star Constellation Canvas Background -->
        <canvas
            ref="canvasEl"
            class="absolute inset-0 w-full h-full z-0 pointer-events-auto"
        ></canvas>

        <div class="relative w-full h-full z-10 flex flex-col lg:flex-row">
            <!-- Left Panel: Slogan & Branding -->
            <div
                class="hidden lg:flex flex-1 flex-col justify-between p-12 xl:p-20 pointer-events-none"
            >
                <div class="flex items-center gap-3">
                    <div
                        class="w-12 h-12 rounded-xl bg-[var(--color-vintage-charcoal)] dark:bg-[var(--color-vintage-paper)] flex items-center justify-center shadow-lg"
                    >
                        <Activity
                            class="w-7 h-7 text-[var(--color-vintage-cream)] dark:text-[var(--color-vintage-charcoal)]"
                        />
                    </div>
                    <h1
                        class="text-2xl font-bold tracking-tight text-[var(--text-main)]"
                    >
                        PredictAI
                    </h1>
                </div>

                <div>
                    <h2
                        class="text-5xl xl:text-7xl font-bold tracking-tighter text-[var(--text-main)] leading-tight"
                    >
                        Recuperação de <br />
                        <span
                            class="text-[var(--color-vintage-rose)] hover:text-[var(--color-vintage-mint)] transition-colors duration-700"
                            >Acesso</span
                        >
                        <br />
                        Segura.
                    </h2>
                    <p
                        class="mt-6 text-xl text-[var(--text-muted)] max-w-md font-medium leading-relaxed"
                    >
                        Esqueceu sua senha? Não se preocupe. Enviaremos um
                        código de segurança seguro para recuperar sua conta.
                    </p>
                </div>

                <div
                    class="text-sm font-medium text-[var(--text-muted)] opacity-60"
                >
                    Revolucionando o chão de fábrica &copy; 2026
                </div>
            </div>

            <!-- Right Panel: Password Reset Form -->
            <div class="flex-1 flex items-center justify-center p-6 lg:p-12">
                <div
                    class="w-full max-w-md backdrop-blur-xl bg-[var(--bg-app)]/80 dark:bg-[var(--bg-card)]/80 p-8 sm:p-12 rounded-3xl shadow-2xl border border-[var(--border-color)] relative pointer-events-auto transition-transform duration-300 hover:-translate-y-1"
                >
                    <div class="flex lg:hidden flex-col items-center mb-10">
                        <div
                            class="w-14 h-14 rounded-2xl bg-[var(--color-vintage-charcoal)] dark:bg-[var(--color-vintage-paper)] flex items-center justify-center mb-4"
                        >
                            <Activity
                                class="w-8 h-8 text-[var(--color-vintage-cream)] dark:text-[var(--color-vintage-charcoal)]"
                            />
                        </div>
                        <h1
                            class="text-3xl font-bold tracking-tighter text-[var(--text-main)]"
                        >
                            PredictAI
                        </h1>
                    </div>

                    <div class="mb-10 flex flex-col items-start gap-4">
                        <router-link
                            :to="{ name: 'login' }"
                            class="flex items-center gap-2 text-sm font-bold text-[var(--color-vintage-blue)] hover:text-[var(--text-main)] transition-colors"
                        >
                            <ArrowLeft class="w-4 h-4" /> Voltar ao Login
                        </router-link>
                        <div>
                            <h3
                                class="text-2xl font-bold text-[var(--text-main)] tracking-tight"
                            >
                                Recuperar Senha
                            </h3>
                            <p
                                class="text-[var(--text-muted)] mt-2 font-medium"
                            >
                                Insira seu e-mail para receber uma nova senha.
                            </p>
                        </div>
                    </div>

                    <!-- Alert Component -->
                    <Transition
                        enter-active-class="transition duration-300 ease-out"
                        enter-from-class="transform -translate-y-4 opacity-0"
                        enter-to-class="transform translate-y-0 opacity-100"
                        leave-active-class="transition duration-200 ease-in"
                        leave-from-class="transform translate-y-0 opacity-100"
                        leave-to-class="transform -translate-y-4 opacity-0"
                    >
                        <div
                            v-if="errorMessage"
                            class="mb-6 p-4 rounded-xl border border-[var(--color-vintage-rose)] bg-[var(--color-vintage-rose)]/10 flex items-start gap-3"
                        >
                            <AlertCircle
                                class="w-5 h-5 text-[var(--color-vintage-rose)] flex-shrink-0 mt-0.5"
                            />
                            <p
                                class="text-sm text-[var(--color-vintage-rose)] font-semibold"
                            >
                                {{ errorMessage }}
                            </p>
                        </div>
                    </Transition>
                    <Transition
                        enter-active-class="transition duration-300 ease-out"
                        enter-from-class="transform -translate-y-4 opacity-0"
                        enter-to-class="transform translate-y-0 opacity-100"
                        leave-active-class="transition duration-200 ease-in"
                        leave-from-class="transform translate-y-0 opacity-100"
                        leave-to-class="transform -translate-y-4 opacity-0"
                    >
                        <div
                            v-if="successMessage"
                            class="mb-6 p-4 rounded-xl border border-[var(--color-vintage-mint)] bg-[var(--color-vintage-mint)]/10 flex items-start gap-3"
                        >
                            <CheckCircle
                                class="w-5 h-5 text-[var(--color-vintage-mint)] flex-shrink-0 mt-0.5"
                            />
                            <p
                                class="text-sm text-[var(--color-vintage-mint)] font-semibold"
                            >
                                {{ successMessage }}
                            </p>
                        </div>
                    </Transition>

                    <!-- Step 1: Request Email -->
                    <form
                        v-if="step === 1"
                        @submit.prevent="handleRequestCode"
                        class="space-y-6"
                    >
                        <div
                            class="space-y-1.5 border-b-2 border-transparent focus-within:border-[var(--color-vintage-mint)] transition-colors"
                        >
                            <label
                                class="block text-xs font-bold uppercase tracking-wider text-[var(--text-muted)]"
                                >E-mail Corporativo</label
                            >
                            <div class="relative flex items-center">
                                <Mail
                                    class="w-5 h-5 absolute left-0 text-[var(--text-muted)]"
                                />
                                <input
                                    v-model="email"
                                    type="email"
                                    required
                                    class="w-full bg-transparent border-none py-3 pl-8 text-[var(--text-main)] placeholder:text-[var(--text-muted)]/50 focus:ring-0 focus:outline-none"
                                    placeholder="admin@predictai.com"
                                    :disabled="isLoading"
                                />
                            </div>
                        </div>

                        <button
                            v-if="!successMessage"
                            type="submit"
                            class="w-full group bg-[var(--color-vintage-charcoal)] dark:bg-[var(--color-vintage-paper)] text-[var(--color-vintage-cream)] dark:text-[var(--color-vintage-charcoal)] h-14 rounded-xl font-bold text-lg flex items-center justify-center gap-2 hover:shadow-xl active:scale-[0.98] transition-all disabled:opacity-70 disabled:active:scale-100"
                            :disabled="isLoading"
                        >
                            <Loader2
                                v-if="isLoading"
                                class="w-6 h-6 animate-spin"
                            />
                            <div v-else class="flex items-center gap-2">
                                Redefinir Senha
                                <ArrowRight
                                    class="w-5 h-5 group-hover:translate-x-1 transition-transform"
                                />
                            </div>
                        </button>
                    </form>


                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import {
    Activity,
    Mail,
    Lock,
    AlertCircle,
    Loader2,
    ArrowRight,
    ArrowLeft,
    Key,
    CheckCircle,
    Check,
} from 'lucide-vue-next';
import api from '@/services/api';

const router = useRouter();

const step = ref(1);

const email = ref('');

const isLoading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');
const canvasEl = ref(null);

const clearMessages = () => {
    errorMessage.value = '';
    successMessage.value = '';
};

const handleRequestCode = async () => {
    clearMessages();
    isLoading.value = true;
    try {
        const response = await api.post('/users/forgot-password/', {
            email: email.value,
        });
        successMessage.value = response.data.detail || 'Uma nova senha foi enviada para ' + email.value;
        // Optionally redirect to login after a few seconds
        setTimeout(() => {
            router.push({ name: 'login' });
        }, 5000);
    } catch (error) {
        errorMessage.value =
            error.response?.data?.detail ||
            error.response?.data?.email?.[0] ||
            'Erro ao processar solicitação.';
    } finally {
        isLoading.value = false;
    }
};

// --------------------------------------------------------------------------
// CONSTELLATION PARTICLES ANIMATION (Reused from LoginView)
// --------------------------------------------------------------------------
let animationFrameId;
let ctx;
let particlesArray = [];
let mouse = { x: null, y: null, radius: 150 };

onMounted(() => {
    const canvas = canvasEl.value;
    ctx = canvas.getContext('2d');

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    window.addEventListener('mousemove', (e) => {
        mouse.x = e.x;
        mouse.y = e.y;
    });
    window.addEventListener('mouseout', () => {
        mouse.x = null;
        mouse.y = null;
    });

    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        initParticles();
    });

    class Particle {
        constructor(x, y, dx, dy, size, color) {
            this.x = x;
            this.y = y;
            this.dx = dx;
            this.dy = dy;
            this.size = size;
            this.color = color;
            this.baseX = this.x;
            this.baseY = this.y;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
            ctx.fillStyle = this.color;
            ctx.fill();
        }
        update() {
            this.x += this.dx;
            this.y += this.dy;

            if (this.x < 0 || this.x > canvas.width) this.dx = -this.dx;
            if (this.y < 0 || this.y > canvas.height) this.dy = -this.dy;

            if (mouse.x != null && mouse.y != null) {
                let dx = mouse.x - this.x;
                let dy = mouse.y - this.y;
                let distance = Math.sqrt(dx * dx + dy * dy);
                let maxDist = mouse.radius;

                if (distance < maxDist) {
                    let forceDirX = dx / distance;
                    let forceDirY = dy / distance;
                    let force = (maxDist - distance) / maxDist;
                    let moveX = forceDirX * force * 1.5;
                    let moveY = forceDirY * force * 1.5;

                    this.x -= moveX;
                    this.y -= moveY;
                }
            }

            this.draw();
        }
    }

    function initParticles() {
        particlesArray = [];
        let numberOfParticles = (canvas.width * canvas.height) / 8000;
        const colors = ['#90A99E'];

        for (let i = 0; i < numberOfParticles; i++) {
            let size = Math.random() * 2 + 1;
            let x =
                Math.random() * (canvas.width - size * 2 - size * 2) + size * 2;
            let y =
                Math.random() * (canvas.height - size * 2 - size * 2) +
                size * 2;
            let dx = (Math.random() - 0.5) * 0.8;
            let dy = (Math.random() - 0.5) * 0.8;
            let color = colors[Math.floor(Math.random() * colors.length)];

            particlesArray.push(new Particle(x, y, dx, dy, size, color));
        }
    }

    function connectParticles() {
        let opacityValue = 1;
        for (let a = 0; a < particlesArray.length; a++) {
            for (let b = a; b < particlesArray.length; b++) {
                let distance =
                    (particlesArray[a].x - particlesArray[b].x) *
                        (particlesArray[a].x - particlesArray[b].x) +
                    (particlesArray[a].y - particlesArray[b].y) *
                        (particlesArray[a].y - particlesArray[b].y);

                let maxConnectDist = 12000;
                if (distance < maxConnectDist) {
                    let isDarkMode =
                        document.documentElement.classList.contains('dark');
                    opacityValue = 1 - distance / maxConnectDist;
                    ctx.strokeStyle = isDarkMode
                        ? `rgba(244, 239, 230, ${opacityValue * 0.15})`
                        : `rgba(42, 38, 38, ${opacityValue * 0.15})`;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(particlesArray[a].x, particlesArray[a].y);
                    ctx.lineTo(particlesArray[b].x, particlesArray[b].y);
                    ctx.stroke();
                }
            }

            if (mouse.x && mouse.y) {
                let distCursor =
                    (particlesArray[a].x - mouse.x) ** 2 +
                    (particlesArray[a].y - mouse.y) ** 2;
                if (distCursor < 18000) {
                    let isDarkMode =
                        document.documentElement.classList.contains('dark');
                    let cursOpacity = 1 - distCursor / 18000;
                    ctx.strokeStyle = isDarkMode
                        ? `rgba(144, 169, 158, ${cursOpacity * 0.8})`
                        : `rgba(144, 169, 158, ${cursOpacity * 0.5})`;
                    ctx.lineWidth = 1.5;
                    ctx.beginPath();
                    ctx.moveTo(particlesArray[a].x, particlesArray[a].y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.stroke();
                }
            }
        }
    }

    function animate() {
        animationFrameId = requestAnimationFrame(animate);
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        for (let i = 0; i < particlesArray.length; i++) {
            particlesArray[i].update();
        }
        connectParticles();
    }

    initParticles();
    animate();
});

onBeforeUnmount(() => {
    cancelAnimationFrame(animationFrameId);
});
</script>
