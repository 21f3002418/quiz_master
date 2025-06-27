console.log('UserDashboard component loaded');

const UserDashboard = {
  props: ['userId', 'userName'],
  template: `
    <div class="user-dashboard">
      <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
          <a class="navbar-brand" href="#">User Dashboard - Welcome, {{ userName }}!</a>
          <div class="collapse navbar-collapse">
            <ul class="navbar-nav">
              <li class="nav-item">
                <a href="#" class="nav-link" @click.prevent="currentView = 'home'">Home</a>
              </li>
              <li class="nav-item">
                <a href="#" class="nav-link" @click.prevent="currentView = 'score'">Score</a>
              </li>
              <li class="nav-item">
                <a href="#" class="nav-link" @click.prevent="logout">Logout</a>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      <div class="container py-4 content-wrapper">
        <!-- Home View -->
        <div v-if="currentView === 'home'">
          <h2>Select a Subject</h2>
          <div class="row">
            <div v-for="subject in subjects" :key="subject.subject_id" class="col-md-4 mb-3">
              <div class="card">
                <div class="card-body">
                  <h5 class="card-title">{{ subject.name }}</h5>
                  <p class="card-text">{{ subject.description }}</p>
                  <button @click="selectSubject(subject)" class="btn btn-primary">View Chapters</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Subject View -->
        <div v-if="currentView === 'subject' && selectedSubject">
          <button @click="goBack" class="btn btn-secondary mb-3">Back</button>
          <h2>{{ selectedSubject.name }} Chapters</h2>
          <div class="row">
            <div v-for="chapter in filteredChapters" :key="chapter.chapter_id" class="col-md-4 mb-3">
              <div class="card">
                <div class="card-body">
                  <h5 class="card-title">{{ chapter.name }}</h5>
                  <p class="card-text">{{ chapter.description }}</p>
                  <button @click="selectChapter(chapter)" class="btn btn-primary">View Quizzes</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Chapter View -->
        <div v-if="currentView === 'chapter' && selectedChapter">
          <button @click="goBack" class="btn btn-secondary mb-3">Back</button>
          <h2>{{ selectedChapter.name }} Quizzes</h2>
          <div class="row">
            <div v-for="quiz in filteredQuizzes" :key="quiz.quiz_id" class="col-md-4 mb-3">
              <div class="card">
                <div class="card-body">
                  <h4 class="card-title">{{ quiz.name }}</h4>
                  <button @click="startQuiz(quiz)" class="btn btn-primary">Start Quiz</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quiz View -->
        <div v-if="currentView === 'quiz' && selectedQuiz">
          <button @click="goBack" class="btn btn-secondary mb-3">Back</button>
          <h2>{{ selectedQuiz.name }} Quiz</h2>
          <div v-if="quizInProgress && currentQuestionIndex < questions.length">
            <p>{{ questions[currentQuestionIndex].question_statement }}</p>
            <div>
              <input type="radio" :id="'option1_' + currentQuestionIndex" :value="questions[currentQuestionIndex].option_1" v-model="selectedAnswer">
              <label :for="'option1_' + currentQuestionIndex">{{ questions[currentQuestionIndex].option_1 }}</label>
            </div>
            <div>
              <input type="radio" :id="'option2_' + currentQuestionIndex" :value="questions[currentQuestionIndex].option_2" v-model="selectedAnswer">
              <label :for="'option2_' + currentQuestionIndex">{{ questions[currentQuestionIndex].option_2 }}</label>
            </div>
            <button @click="nextQuestion" class="btn btn-primary mt-2">Next</button>
          </div>
          <div v-if="!quizInProgress && currentQuestionIndex >= questions.length">
            <h3>Your Score: {{ totalScore }} / {{ questions.length }}</h3>
            <!-- Score remains visible until user navigates back -->
          </div>
        </div>

        <!-- Score View -->
        <div v-if="currentView === 'score'">
          <h2>Your Scores</h2>
          <table class="table table-bordered">
            <thead>
              <tr>
                <th>Subject Name</th>
                <th>Chapter Name</th>
                <th>Quiz Name</th>
                <th>Marks Secured / Total Marks</th>
                <th>Attempt Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="score in userScores" :key="score.score_id">
                <td>{{ score.subject_name }}</td>
                <td>{{ score.chapter_name }}</td>
                <td>{{ score.quiz_name }}</td>
                <td>{{ score.total_score }} / {{ score.total_questions }}</td>
                <td>{{ score.time_stamp_of_attempt }}</td>
              </tr>
            </tbody>
          </table>
          <h3>Performance by Subject</h3>
          <div class="row">
            <div class="col-md-6 chart-container">
              <h4>Average Percentage per Subject</h4>
              <canvas id="percentageChart" class="mt-4" style="max-height: 200px; height: 200px;"></canvas>
            </div>
            <div class="col-md-6 chart-container">
              <h4>Proportion of Quizzes Attempted per Subject</h4>
              <canvas id="quizProportionChart" class="mt-4" style="max-height: 300px; height: auto;"></canvas>
            </div>
          </div>
        </div>
      </div>

      <footer class="footer">
        <p>© 2025 User Dashboard. All rights reserved.</p>
      </footer>
    </div>
  `,
  data() {
    return {
      currentView: 'home',
      selectedSubject: null,
      selectedChapter: null,
      selectedQuiz: null,
      quizInProgress: false,
      currentQuestionIndex: 0,
      selectedAnswer: '',
      totalScore: 0,
      subjects: [],
      chapters: [],
      quizzes: [],
      questions: [],
      userScores: [],
      percentageChart: null,
      quizProportionChart: null
    };
  },
  computed: {
    filteredChapters() {
      if (!this.selectedSubject) return [];
      return this.chapters.filter(chapter => chapter.subject_id === this.selectedSubject.subject_id);
    },
    filteredQuizzes() {
      if (!this.selectedChapter) return [];
      return this.quizzes.filter(quiz => quiz.chapter_id === this.selectedChapter.chapter_id);
    }
  },
  watch: {
    currentView(newValue) {
      console.log('View changed to:', newValue); // Debug log
      if (newValue === 'score' && this.userScores.length > 0) {
        this.$nextTick(() => this.renderPerformanceChart());
      }
    }
  },
  methods: {
    goBack() {
      if (this.currentView === 'quiz') {
        this.currentView = 'chapter';
        this.selectedQuiz = null;
        this.resetQuiz();
      } else if (this.currentView === 'chapter') {
        this.currentView = 'subject';
        this.selectedChapter = null;
      } else if (this.currentView === 'subject') {
        this.currentView = 'home';
        this.selectedSubject = null;
      }
    },
    async fetchSubjects() {
      try {
        const response = await fetch('/api/user/subjects');
        if (!response.ok) throw new Error('Failed to fetch subjects');
        this.subjects = await response.json();
      } catch (error) {
        console.error('Error fetching subjects:', error);
        alert('Failed to load subjects. Please try again.');
      }
    },
    async fetchChapters() {
      try {
        const response = await fetch('/api/user/chapters');
        if (!response.ok) throw new Error('Failed to fetch chapters');
        this.chapters = await response.json();
      } catch (error) {
        console.error('Error fetching chapters:', error);
        alert('Failed to load chapters. Please try again.');
      }
    },
    async fetchQuizzes() {
      try {
        const response = await fetch('/api/user/quizzes');
        if (!response.ok) throw new Error('Failed to fetch quizzes');
        this.quizzes = await response.json();
      } catch (error) {
        console.error('Error fetching quizzes:', error);
        alert('Failed to load quizzes. Please try again.');
      }
    },
    async fetchQuestions(quizId) {
      try {
        const response = await fetch(`/api/user/questions?quiz_id=${quizId}`);
        if (!response.ok) throw new Error('Failed to fetch questions');
        this.questions = await response.json();
        this.currentQuestionIndex = 0;
        this.selectedAnswer = '';
        this.totalScore = 0;
        this.quizInProgress = true;
      } catch (error) {
        console.error('Error fetching questions:', error);
        alert('Failed to load questions. Please try again.');
      }
    },
    async fetchScores() {
      try {
        const response = await fetch(`/api/user/scores?user_id=${this.userId}`);
        if (!response.ok) throw new Error('Failed to fetch scores');
        const scores = await response.json();
        console.log('Fetched scores:', scores);
        this.userScores = scores;
        if (this.currentView === 'score') {
          this.$nextTick(() => this.renderPerformanceChart());
        }
      } catch (error) {
        console.error('Error fetching scores:', error);
        alert('Failed to load scores. Please try again.');
      }
    },
    selectSubject(subject) {
      this.selectedSubject = { ...subject };
      this.currentView = 'subject';
    },
    selectChapter(chapter) {
      this.selectedChapter = { ...chapter };
      this.currentView = 'chapter';
    },
    startQuiz(quiz) {
      this.selectedQuiz = { ...quiz };
      this.currentView = 'quiz';
      this.fetchQuestions(quiz.quiz_id);
    },
    async nextQuestion() {
      if (this.selectedAnswer === this.questions[this.currentQuestionIndex].correct_option) {
        this.totalScore += 1;
      }
      this.currentQuestionIndex++;
      this.selectedAnswer = '';
      if (this.currentQuestionIndex >= this.questions.length) {
        this.quizInProgress = false;
        // Automatically save score when quiz ends
        const scoreData = {
          quiz_id: this.selectedQuiz.quiz_id,
          user_id: this.userId,
          total_score: this.totalScore,
          time_stamp_of_attempt: new Date().toISOString()
        };
        try {
          const response = await fetch('/api/user/scores', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(scoreData)
          });
          const result = await response.json();
          if (response.ok) {
            alert(result.message); // Score saved successfully alert
            await this.fetchScores();
            // Removed manual push of newScore to avoid duplicate
          } else {
            alert(result.message || 'Failed to save score');
          }
        } catch (error) {
          console.error('Error submitting score:', error);
          alert('An error occurred while saving the score.');
        }
        // Do not call resetQuiz here, keep score visible
      }
    },
    resetQuiz() {
      this.selectedQuiz = null;
      this.quizInProgress = false;
      this.currentQuestionIndex = 0;
      this.selectedAnswer = '';
      this.totalScore = 0;
      this.questions = [];
    },
    logout() {
      if (confirm('Are you sure you want to logout?')) {
        window.location.href = '/logout';
      }
    },
    getTotalQuestions(quizId) {
      return 1; // Redundant, using total_questions from API
    },
    renderPerformanceChart() {
      // Destroy existing charts if they exist
      if (this.percentageChart) this.percentageChart.destroy();
      if (this.quizProportionChart) this.quizProportionChart.destroy();

      // Calculate average percentage per subject
      const percentageData = {};
      this.userScores.forEach(score => {
        if (!percentageData[score.subject_name]) {
          percentageData[score.subject_name] = { total: 0, count: 0 };
        }
        const maxScore = score.total_questions || 1;
        percentageData[score.subject_name].total += (score.total_score / maxScore) * 100; // Convert to percentage
        percentageData[score.subject_name].count += 1;
      });
      const percentageLabels = Object.keys(percentageData);
      const percentageValues = percentageLabels.map(subject => percentageData[subject].count ? (percentageData[subject].total / percentageData[subject].count).toFixed(2) : 0);
      console.log('Percentage Labels:', percentageLabels, 'Percentage Values:', percentageValues); // Debug log

      // Calculate proportion of quizzes attempted per subject
      const quizCount = {};
      this.userScores.forEach(score => {
        quizCount[score.subject_name] = (quizCount[score.subject_name] || 0) + 1;
      });
      const totalQuizzes = Object.values(quizCount).reduce((a, b) => a + b, 0);
      const proportionLabels = Object.keys(quizCount);
      const proportionValues = proportionLabels.map(subject => totalQuizzes ? ((quizCount[subject] / totalQuizzes) * 100).toFixed(2) : 0);
      console.log('Proportion Labels:', proportionLabels, 'Proportion Values:', proportionValues); // Debug log

      // Generate unique colors for each subject
      const colors = percentageLabels.map((_, index) => `hsl(${index * 360 / percentageLabels.length}, 70%, 50%)`);

      // Render Percentage Bar Chart
      const percentageCtx = document.getElementById('percentageChart');
      if (percentageCtx) {
        console.log('Percentage Canvas found, creating chart'); // Debug log
        this.percentageChart = new Chart(percentageCtx, {
          type: 'bar',
          data: {
            labels: percentageLabels,
            datasets: [{
              label: 'Average Percentage',
              data: percentageValues,
              backgroundColor: colors, // Unique colors for each bar
              borderColor: colors.map(color => color.replace('0.5', '1')), // Solid border colors
              borderWidth: 1
            }]
          },
          options: {
            scales: { y: { beginAtZero: true, max: 100, title: { display: true, text: 'Percentage (%)' } } },
            plugins: { legend: { display: true, position: 'top', labels: { generateLabels: chart => percentageLabels.map((label, index) => ({ text: label, fillStyle: colors[index] })) } } }, // Show only subject names
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2 // Adjust aspect ratio to control height vs. width
          }
        });
      } else {
        console.log('Percentage Canvas not found'); // Debug log
      }

      // Render Quiz Proportion Pie Chart
      const proportionCtx = document.getElementById('quizProportionChart');
      if (proportionCtx) {
        console.log('Proportion Canvas found, creating chart'); // Debug log
        this.quizProportionChart = new Chart(proportionCtx, {
          type: 'pie',
          data: {
            labels: proportionLabels,
            datasets: [{
              label: 'Proportion of Quizzes Attempted',
              data: proportionValues,
              backgroundColor: ['rgba(255, 99, 132, 0.5)', 'rgba(54, 162, 235, 0.5)', 'rgba(255, 206, 86, 0.5)', 'rgba(75, 192, 192, 0.5)', 'rgba(153, 102, 255, 0.5)'],
              borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)', 'rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)'],
              borderWidth: 1
            }]
          },
          options: {
            plugins: { legend: { position: 'right' } },
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 1.5 // Adjust to fit the pie chart fully
          }
        });
      } else {
        console.log('Proportion Canvas not found'); // Debug log
      }
    }
  },
  mounted() {
    this.fetchSubjects();
    this.fetchChapters();
    this.fetchQuizzes();
    if (this.userId) this.fetchScores();
  }
};

const style = document.createElement('style');
style.textContent = `
  .user-dashboard {
    min-height: 100vh;
    background: linear-gradient(135deg, #4b6cb7, #182848, #6b48ff);
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
  }
  .content-wrapper {
    flex: 1 0 auto;
    padding-bottom: 40px; /* Increased space above footer */
  }
  .container {
    min-height: 100%;
    padding-bottom: 0;
  }
  .navbar-dark .navbar-nav .nav-link { color: #ffffff; }
  .navbar-dark .navbar-nav .nav-link:hover { color: #6b48ff; }
  .card { background: rgba(255, 255, 255, 0.1); color: #ffffff; border: none; border-radius: 10px; transition: transform 0.3s; }
  .card:hover { transform: translateY(-5px); }
  .table { background: rgba(255, 255, 255, 0.95); color: #000000; border-radius: 10px; }
  .table th { background: rgba(54, 162, 235, 0.2); }
  .btn-secondary { background-color: #6c757d; border-color: #6c757d; }
  .btn-secondary:hover { background-color: #5a6268; border-color: #5a6268; }
  .chart-container {
    overflow: visible;
    margin-bottom: 40px; /* Increased distance from footer */
  }
  canvas#percentageChart, canvas#quizProportionChart {
    max-width: 100%;
    height: auto !important;
  }
  .footer {
    flex-shrink: 0;
    background: linear-gradient(135deg, #4b6cb7, #182848, #6b48ff); /* Match background */
    color: #ffffff;
    text-align: center;
    padding: 10px 0;
    width: 100%;
  }
  body {
    margin: 0;
    padding: 0;
    background: linear-gradient(135deg, #4b6cb7, #182848, #6b48ff);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
`;
document.head.appendChild(style);