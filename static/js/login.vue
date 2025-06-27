if (typeof Vue === 'undefined' || typeof axios === 'undefined') {
    console.error('Vue or Axios failed to load. Please check your internet connection or CDN links.');
} else {
    const { createApp, ref, reactive, onMounted } = Vue;

    console.log("login.vue loaded successfully");

    const Login = {
        template: `
            <div class="container-fluid py-5">
                <div class="row justify-content-center">
                    <div class="col-md-12 col-lg-12">
                        <div class="register-card">
                            <h2 class="text-center mb-5">Login to Quiz Master</h2>
                            <form @submit.prevent="submitForm">
                                <div class="mb-4 position-relative">
                                    <label for="user_id" class="form-label" :class="{ 'label-active': isUserIdFocused }">
                                        <i class="bi bi-person-fill"></i> Username
                                    </label>
                                    <input v-model="form.user_id" type="text" class="form-control" id="user_id"
                                        placeholder="Enter username" required
                                        @focus="isUserIdFocused = true" @blur="isUserIdFocused = false">
                                </div>
                                <div class="mb-4 position-relative">
                                    <label for="password" class="form-label" :class="{ 'label-active': isPasswordFocused }">
                                        <i class="bi bi-lock-fill"></i> Password
                                    </label>
                                    <input v-model="form.password" type="password" class="form-control" id="password"
                                        placeholder="Enter password" required
                                        @focus="isPasswordFocused = true" @blur="isPasswordFocused = false">
                                </div>
                                <div class="text-center mb-4">
                                    <button type="submit" class="btn btn-primary">Login</button>
                                </div>
                                <div class="text-center mb-4">
                                    <a href="/" class="text-white">Don't have an account? Register here</a>
                                </div>
                                <div v-if="message" class="mt-3 alert" :class="messageType">{{ message }}</div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        `,
        setup() {
            const form = reactive({
                user_id: '',
                password: ''
            });
            const message = ref('');
            const messageType = ref('');
            const isUserIdFocused = ref(false);
            const isPasswordFocused = ref(false);

            const submitForm = async () => {
                try {
                    const response = await axios.post('/api/login', form);
                    message.value = response.data.message || 'Login successful!';
                    messageType.value = 'alert-success';
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                } catch (error) {
                    console.error('Login error:', error);
                    const msg = error?.response?.data?.message || 'Login failed. Please try again.';
                    message.value = msg;
                    messageType.value = 'alert-danger';
                }
            };

            onMounted(() => {
                console.log('Login component mounted');
            });

            return { form, submitForm, message, messageType, isUserIdFocused, isPasswordFocused };
        }
    };

    const style = document.createElement('style');
    style.id = 'login-style';
    style.textContent = `
        body {
            background: linear-gradient(135deg, #4b6cb7, #182848, #6b48ff);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            animation: gradientShift 15s ease infinite;
            background-size: 300% 300%;
        }
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .container-fluid {
            padding-left: 2rem;
            padding-right: 2rem;
        }
        .register-card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(12px);
            border: 2px solid transparent;
            border-image: linear-gradient(45deg, #3b82f6, #6b48ff) 1;
            border-radius: 25px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
            padding: 4rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            animation: fadeIn 1s ease-out;
            max-width: 1440px;
            margin: 0 auto;
        }
        .register-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 15px 50px rgba(0, 0, 0, 0.5);
        }
        .form-label {
            font-weight: 600;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: color 0.3s ease;
        }
        .form-label i {
            transition: color 0.3s ease;
        }
        .form-label.label-active i,
        .form-label:hover i {
            color: #3b82f6;
        }
        .form-control {
            background: rgba(255, 255, 255, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.5);
            color: #ffffff;
            border-radius: 10px;
            transition: all 0.3s ease;
            animation: fadeIn 1.2s ease-out;
        }
        .form-control:focus {
            background: rgba(255, 255, 255, 0.35);
            border-color: #3b82f6;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.7);
            color: #ffffff;
        }
        .form-control::placeholder {
            color: rgba(255, 255, 255, 0.9);
        }
        .btn-primary {
            background: linear-gradient(90deg, #3b82f6, #6b48ff);
            border: none;
            padding: 0.8rem 2.5rem;
            border-radius: 30px;
            font-weight: 700;
            transition: all 0.3s ease;
            animation: fadeIn 1.5s ease-out;
        }
        .btn-primary:hover {
            background: linear-gradient(90deg, #2563eb, #5b3eff);
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.8);
            transform: scale(1.1);
        }
        .alert {
            border-radius: 12px;
            animation: fadeIn 0.5s ease-out;
        }
        h2 {
            font-weight: 800;
            background: linear-gradient(90deg, #3b82f6, #6b48ff);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 3px 6px rgba(0, 0, 0, 0.3);
            animation: fadeIn 1s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        a {
            color: #ffffff;
            text-decoration: none;
            transition: color 0.3s ease;
        }
        a:hover {
            color: #3b82f6;
        }
    `;
    document.head.appendChild(style);

    const appElement = document.querySelector('#app');
    if (appElement && !appElement.__vue_app__) {
        createApp(Login).mount('#app');
    } else {
        console.error('Failed to mount Vue app: #app element not found or already mounted.');
    }
}