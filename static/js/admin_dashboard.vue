console.log('AdminDashboard component loaded')

const AdminDashboard = {
    template: `
        <div class="admin-dashboard">
            <div class="container py-4">
                <h1 class="dashboard-title text-center mb-5">Quiz Master Admin Dashboard</h1>

            <!-- Breadcrumb Navigation -->
                <nav aria-label="breadcrumb" class="custom-breadcrumb mb-4">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item">
                        <a href="#" @click.prevent="currentView = 'subjects'; selectedSubject = null; selectedChapter = null; selectedQuiz = null">Subjects</a>
                    </li>
                    <li v-if="selectedSubject" class="breadcrumb-item">
                        <a href="#" @click.prevent="currentView = 'chapters'; selectedChapter = null; selectedQuiz = null">{{ selectedSubject.name }}</a>
                    </li>
                    <li v-if="selectedChapter" class="breadcrumb-item">
                        <a href="#" @click.prevent="currentView = 'quizzes'; selectedQuiz = null">{{ selectedChapter.name }}</a>
                    </li>
                    <li v-if="selectedQuiz" class="breadcrumb-item active" aria-current="page">{{ selectedQuiz.name }}</li>
                </ol>
            </nav>

                <!-- Content Card -->
                <div class="content-card">
            <!-- Subjects View -->
            <div v-if="currentView === 'subjects'">
                <h2>Manage Subjects</h2>
                <form @submit.prevent="createSubject" class="mb-4">
                    <div class="mb-3">
                        <label for="subjectName" class="form-label">Subject Name</label>
                        <input v-model="newSubject.name" type="text" class="form-control" id="subjectName" required>
                    </div>
                    <div class="mb-3">
                        <label for="subjectDescription" class="form-label">Description</label>
                        <textarea v-model="newSubject.description" class="form-control" id="subjectDescription" required></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Create Subject</button>
                </form>
                <h3>Existing Subjects</h3>
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Description</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="subject in subjects" :key="subject.subject_id">
                                    <td>
                                        <span v-if="!subject.editing">{{ subject.name }}</span>
                                        <input v-else v-model="subject.name" type="text" class="form-control" required>
                                    </td>
                                    <td>
                                        <span v-if="!subject.editing">{{ subject.description }}</span>
                                        <textarea v-else v-model="subject.description" class="form-control" required></textarea>
                                    </td>
                            <td>
                                <button @click="selectSubject(subject)" class="btn btn-sm btn-primary me-2">View Chapters</button>
                                <button v-if="!subject.editing" @click="editSubject(subject)" class="btn btn-sm btn-warning me-2">Edit</button>
                                <button v-else @click="updateSubject(subject)" class="btn btn-sm btn-success me-2">Save</button>
                                <button @click="deleteSubject(subject.subject_id)" class="btn btn-sm btn-danger">Delete</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Chapters View -->
            <div v-if="currentView === 'chapters' && selectedSubject">
                <h2>Manage Chapters for {{ selectedSubject.name }}</h2>
                <form @submit.prevent="createChapter" class="mb-4">
                    <div class="mb-3">
                        <label for="chapterName" class="form-label">Chapter Name</label>
                        <input v-model="newChapter.name" type="text" class="form-control" id="chapterName" required>
                    </div>
                    <div class="mb-3">
                        <label for="chapterDescription" class="form-label">Description</label>
                        <textarea v-model="newChapter.description" class="form-control" id="chapterDescription" required></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Create Chapter</button>
                </form>
                <h3>Existing Chapters</h3>
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Description</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="chapter in filteredChapters" :key="chapter.chapter_id">
                                    <td>
                                        <span v-if="!chapter.editing">{{ chapter.name }}</span>
                                        <input v-else v-model="chapter.name" type="text" class="form-control" required>
                                    </td>
                                    <td>
                                        <span v-if="!chapter.editing">{{ chapter.description }}</span>
                                        <textarea v-else v-model="chapter.description" class="form-control" required></textarea>
                                    </td>
                            <td>
                                <button @click="selectChapter(chapter)" class="btn btn-sm btn-primary me-2">View Quizzes</button>
                                <button v-if="!chapter.editing" @click="editChapter(chapter)" class="btn btn-sm btn-warning me-2">Edit</button>
                                <button v-else @click="updateChapter(chapter)" class="btn btn-sm btn-success me-2">Save</button>
                                <button @click="deleteChapter(chapter.chapter_id)" class="btn btn-sm btn-danger">Delete</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Quizzes View -->
            <div v-if="currentView === 'quizzes' && selectedChapter">
                <h2>Manage Quizzes for {{ selectedChapter.name }}</h2>
                <form @submit.prevent="createQuiz" class="mb-4">
                    <div class="mb-3">
                        <label for="quizName" class="form-label">Quiz Name</label>
                        <input v-model="newQuiz.name" type="text" class="form-control" id="quizName" required>
                    </div>
                
                    
                    <button type="submit" class="btn btn-primary">Create Quiz</button>
                </form>
                <h3>Existing Quizzes</h3>
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="quiz in filteredQuizzes" :key="quiz.quiz_id">
                                    <td>
                                        <span v-if="!quiz.editing">{{ quiz.name }}</span>
                                        <input v-else v-model="quiz.name" type="text" class="form-control" required>
                                    </td>
                                    
                            <td>
                                <button @click="selectQuiz(quiz)" class="btn btn-sm btn-primary me-2">View Questions</button>
                                <button v-if="!quiz.editing" @click="editQuiz(quiz)" class="btn btn-sm btn-warning me-2">Edit</button>
                                <button v-else @click="updateQuiz(quiz)" class="btn btn-sm btn-success me-2">Save</button>
                                <button @click="deleteQuiz(quiz.quiz_id)" class="btn btn-sm btn-danger">Delete</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Questions View -->
            <div v-if="currentView === 'questions' && selectedQuiz">
                <h2>Manage Questions for {{ selectedQuiz.name }}</h2>
                <form @submit.prevent="createQuestion" class="mb-4">
                    <div class="mb-3">
                        <label for="questionStatement" class="form-label">Question Statement</label>
                        <textarea v-model="newQuestion.question_statement" class="form-control" id="questionStatement" required></textarea>
                    </div>
                    <div class="mb-3">
                        <label for="option1" class="form-label">Option 1</label>
                        <input v-model="newQuestion.option_1" type="text" class="form-control" id="option1" required @input="updateCorrectOption">
                    </div>
                    <div class="mb-3">
                        <label for="option2" class="form-label">Option 2</label>
                        <input v-model="newQuestion.option_2" type="text" class="form-control" id="option2" required @input="updateCorrectOption">
                    </div>
                    <div class="mb-3">
                        <label for="correctOption" class="form-label">Correct Option</label>
                        <select v-model="newQuestion.correct_option" class="form-control" id="correctOption" required>
                            <option value="" disabled>Select the correct option</option>
                            <option v-if="newQuestion.option_1" :value="newQuestion.option_1">{{ newQuestion.option_1 }}</option>
                            <option v-if="newQuestion.option_2" :value="newQuestion.option_2">{{ newQuestion.option_2 }}</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">Create Question</button>
                </form>
                <h3>Existing Questions</h3>
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Question</th>
                            <th>Option 1</th>
                            <th>Option 2</th>
                            <th>Correct Option</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="question in filteredQuestions" :key="question.question_id">
                            <td>
                                <span v-if="!question.editing">{{ question.question_statement }}</span>
                                <textarea v-else v-model="question.question_statement" class="form-control"></textarea>
                            </td>
                            <td>
                                <span v-if="!question.editing">{{ question.option_1 }}</span>
                                <input v-else v-model="question.option_1" type="text" class="form-control">
                            </td>
                            <td>
                                <span v-if="!question.editing">{{ question.option_2 }}</span>
                                <input v-else v-model="question.option_2" type="text" class="form-control">
                            </td>
                            <td>
                                <span v-if="!question.editing">{{ question.correct_option }}</span>
                                <select v-else v-model="question.correct_option" class="form-control">
                                    <option :value="question.option_1">{{ question.option_1 }}</option>
                                    <option :value="question.option_2">{{ question.option_2 }}</option>
                                </select>
                            </td>
                            <td>
                                <button v-if="!question.editing" @click="editQuestion(question)" class="btn btn-sm btn-warning me-2">Edit</button>
                                <button v-else @click="updateQuestion(question)" class="btn btn-sm btn-success me-2">Save</button>
                                <button @click="deleteQuestion(question.question_id)" class="btn btn-sm btn-danger">Delete</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Search View -->
            <div v-if="currentView === 'search'">
                <h2>Search</h2>
                <div class="mb-3">
                    <input v-model="searchQuery" @input="search" type="text" class="form-control" placeholder="Search users, subjects, or quizzes...">
                </div>
                <h3>Users</h3>
                <table class="table table-bordered" v-if="searchResults.users.length">
                    <thead>
                        <tr>
                            <th>User ID</th>
                            <th>Email</th>
                            <th>Name</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="user in searchResults.users" :key="user.user_id">
                            <td>{{ user.user_id }}</td>
                            <td>{{ user.email_id }}</td>
                            <td>{{ user.name }}</td>
                        </tr>
                    </tbody>
                </table>
                <p v-else>No users found.</p>

                <h3>Subjects</h3>
                <table class="table table-bordered" v-if="searchResults.subjects.length">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="subject in searchResults.subjects" :key="subject.subject_id">
                            <td>{{ subject.name }}</td>
                            <td>{{ subject.description }}</td>
                        </tr>
                    </tbody>
                </table>
                <p v-else>No subjects found.</p>

                <h3>Quizzes</h3>
                <table class="table table-bordered" v-if="searchResults.quizzes.length">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Chapter ID</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="quiz in searchResults.quizzes" :key="quiz.quiz_id">
                            <td>{{ quiz.name }}</td>
                            <td>{{ quiz.chapter_id }}</td>
                        </tr>
                    </tbody>
                </table>
                <p v-else>No quizzes found.</p>
            </div>

            <!-- Summary View -->
            <div v-if="currentView === 'summary'">
                <h2>Summary</h2>
                <div class="row">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Users</h5>
                                <p class="card-text">{{ summary.user_count }}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Subjects</h5>
                                <p class="card-text">{{ summary.subject_count }}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Quizzes</h5>
                                <p class="card-text">{{ summary.quiz_count }}</p>
                            </div>
                        </div>
                    </div>
                </div>
                <canvas id="summaryChart" class="mt-4"></canvas>
                    </div>
                </div>
            </div>
        </div>
    `,
    data() {
        return {
            currentView: 'subjects',
            selectedSubject: null,
            selectedChapter: null,
            selectedQuiz: null,
            subjects: [],
            newSubject: { name: '', description: '' },
            chapters: [],
            newChapter: { name: '', description: '' },
            quizzes: [],
            newQuiz: { name: ''},
            questions: [],
            newQuestion: { question_statement: '', option_1: '', option_2: '', correct_option: '' },
            searchQuery: '',
            searchResults: { users: [], subjects: [], quizzes: [] },
            summary: { user_count: 0, subject_count: 0, quiz_count: 0 },
            chart: null
        }
    },
    computed: {
        filteredChapters() {
            if (!this.selectedSubject) return []
            return this.chapters.filter(chapter => chapter.subject_id === this.selectedSubject.subject_id)
        },
        filteredQuizzes() {
            if (!this.selectedChapter) return []
            return this.quizzes.filter(quiz => quiz.chapter_id === this.selectedChapter.chapter_id)
        },
        filteredQuestions() {
            if (!this.selectedQuiz) return []
            return this.questions.filter(question => question.quiz_id === this.selectedQuiz.quiz_id)
        }
    },
    methods: {
        // Subject Methods
        async fetchSubjects() {
            try {
                const response = await fetch('/api/admin/subjects')
                if (!response.ok) throw new Error('Failed to fetch subjects')
                this.subjects = await response.json()
                this.subjects.forEach(subject => subject.editing = false)
            } catch (error) {
                console.error('Error fetching subjects:', error)
                alert('Failed to load subjects. Please try again.')
            }
        },
        async createSubject() {
            try {
                const response = await fetch('/api/admin/subjects', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.newSubject)
                })
                const result = await response.json()
                if (response.ok) {
                    alert(result.message)
                    this.newSubject = { name: '', description: '' }
                    this.fetchSubjects()
                } else {
                    alert(result.message)
                }
            } catch (error) {
                console.error('Error creating subject:', error)
                alert('Failed to create subject. Please try again.')
            }
        },
        editSubject(subject) {
            subject.editing = true
        },
        async updateSubject(subject) {
            try {
                const response = await fetch(`/api/admin/subjects/${subject.subject_id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: subject.name, description: subject.description })
                })
                const result = await response.json()
                if (response.ok) {
                    alert(result.message)
                    subject.editing = false
                    if (this.selectedSubject && this.selectedSubject.subject_id === subject.subject_id) {
                        this.selectedSubject = { ...subject, editing: false }
                    }
                } else {
                    alert(result.message)
                }
            } catch (error) {
                console.error('Error updating subject:', error)
                alert('Failed to update subject. Please try again.')
            }
        },
        async deleteSubject(subject_id) {
            if (confirm('Are you sure you want to delete this subject?')) {
                try {
                    const response = await fetch(`/api/admin/subjects/${subject_id}`, {
                        method: 'DELETE'
                    })
                    const result = await response.json()
                    alert(result.message)
                    this.fetchSubjects()
                    this.fetchChapters()
                    if (this.selectedSubject && this.selectedSubject.subject_id === subject_id) {
                        this.currentView = 'subjects'
                        this.selectedSubject = null
                        this.selectedChapter = null
                        this.selectedQuiz = null
                    }
                } catch (error) {
                    console.error('Error deleting subject:', error)
                    alert('Failed to delete subject. Please try again.')
                }
            }
        },
        selectSubject(subject) {
            this.selectedSubject = { ...subject }
            this.currentView = 'chapters'
            this.selectedChapter = null
            this.selectedQuiz = null
        },

        // Chapter Methods
        async fetchChapters() {
            try {
                const response = await fetch('/api/admin/chapters')
                if (!response.ok) throw new Error('Failed to fetch chapters')
                this.chapters = await response.json()
                this.chapters.forEach(chapter => chapter.editing = false)
            } catch (error) {
                console.error('Error fetching chapters:', error)
                alert('Failed to load chapters. Please try again.')
            }
        },
        async createChapter() {
            try {
                const chapterData = {
                    name: this.newChapter.name,
                    description: this.newChapter.description,
                    subject_id: this.selectedSubject.subject_id
                }
                const response = await fetch('/api/admin/chapters', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(chapterData)
                })
                const result = await response.json()
                if (response.ok) {
                    alert(result.message)
                    this.newChapter = { name: '', description: '' }
                    this.fetchChapters()
                } else {
                    alert(result.message)
                }
            } catch (error) {
                console.error('Error creating chapter:', error)
                alert('Failed to create chapter. Please try again.')
            }
        },
        editChapter(chapter) {
            chapter.editing = true
        },
        async updateChapter(chapter) {
            try {
                const response = await fetch(`/api/admin/chapters/${chapter.chapter_id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: chapter.name,
                        description: chapter.description,
                        subject_id: this.selectedSubject.subject_id
                    })
                })
                const result = await response.json()
                if (response.ok) {
                    alert(result.message)
                    chapter.editing = false
                    if (this.selectedChapter && this.selectedChapter.chapter_id === chapter.chapter_id) {
                        this.selectedChapter = { ...chapter, editing: false }
                    }
                } else {
                    alert(result.message)
                }
            } catch (error) {
                console.error('Error updating chapter:', error)
                alert('Failed to update chapter. Please try again.')
            }
        },
        async deleteChapter(chapter_id) {
            if (confirm('Are you sure you want to delete this chapter?')) {
                try {
                    const response = await fetch(`/api/admin/chapters/${chapter_id}`, {
                        method: 'DELETE'
                    })
                    const result = await response.json()
                    alert(result.message)
                    this.fetchChapters()
                    this.fetchQuizzes()
                    if (this.selectedChapter && this.selectedChapter.chapter_id === chapter_id) {
                        this.currentView = 'chapters'
                        this.selectedChapter = null
                        this.selectedQuiz = null
                    }
                } catch (error) {
                    console.error('Error deleting chapter:', error)
                    alert('Failed to delete chapter. Please try again.')
                }
            }
        },
        selectChapter(chapter) {
            this.selectedChapter = { ...chapter }
            this.currentView = 'quizzes'
            this.selectedQuiz = null
        },

        // Quiz Methods
        async fetchQuizzes() {
            try {
                const response = await fetch('/api/admin/quizzes')
                if (!response.ok) throw new Error('Failed to fetch quizzes')
                this.quizzes = await response.json()
                this.quizzes.forEach(quiz => quiz.editing = false)
            } catch (error) {
                console.error('Error fetching quizzes:', error)
                alert('Failed to load quizzes. Please try again.')
            }
        },
        async createQuiz() {
            try {
                const quizData = {
                    name: this.newQuiz.name,
                    chapter_id: this.selectedChapter.chapter_id
                }
                const response = await fetch('/api/admin/quizzes', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(quizData)
                })
                const result = await response.json()
                if (response.ok) {
                    alert(result.message)
                    this.newQuiz = { name: ''}
                    this.fetchQuizzes()
                } else {
                    alert(result.message)
                }
            } catch (error) {
                console.error('Error creating quiz:', error)
                alert('Failed to create quiz. Please try again.')
            }
        },
        editQuiz(quiz) {
            quiz.editing = true
        },
        async updateQuiz(quiz) {
            try {
                const response = await fetch(`/api/admin/quizzes/${quiz.quiz_id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: quiz.name,
                        chapter_id: this.selectedChapter.chapter_id
                    })
                })
                const result = await response.json()
                if (response.ok) {
                    alert(result.message)
                    quiz.editing = false
                    if (this.selectedQuiz && this.selectedQuiz.quiz_id === quiz.quiz_id) {
                        this.selectedQuiz = { ...quiz, editing: false }
                    }
                } else {
                    alert(result.message)
                }
            } catch (error) {
                console.error('Error updating quiz:', error)
                alert('Failed to update quiz. Please try again.')
            }
        },
        async deleteQuiz(quiz_id) {
            if (confirm('Are you sure you want to delete this quiz?')) {
                try {
                    const response = await fetch(`/api/admin/quizzes/${quiz_id}`, {
                        method: 'DELETE'
                    })
                    const result = await response.json()
                    alert(result.message)
                    this.fetchQuizzes()
                    this.fetchQuestions()
                    if (this.selectedQuiz && this.selectedQuiz.quiz_id === quiz_id) {
                        this.currentView = 'quizzes'
                        this.selectedQuiz = null
                    }
                } catch (error) {
                    console.error('Error deleting quiz:', error)
                    alert('Failed to delete quiz. Please try again.')
                }
            }
        },
        selectQuiz(quiz) {
            this.selectedQuiz = { ...quiz }
            this.currentView = 'questions'
        },

        // Question Methods
        async fetchQuestions() {
            try {
                const response = await fetch('/api/admin/questions')
                if (!response.ok) throw new Error('Failed to fetch questions')
                this.questions = await response.json()
                this.questions.forEach(question => question.editing = false)
            } catch (error) {
                console.error('Error fetching questions:', error)
                alert('Failed to load questions. Please try again.')
            }
        },
        async createQuestion() {
            try {
                const questionData = {
                    quiz_id: this.selectedQuiz.quiz_id,
                    question_statement: this.newQuestion.question_statement,
                    option_1: this.newQuestion.option_1,
                    option_2: this.newQuestion.option_2,
                    correct_option: this.newQuestion.correct_option
                }
                const response = await fetch('/api/admin/questions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(questionData)
                })
                const result = await response.json()
                if (response.ok) {
                    alert(result.message)
                    this.newQuestion = { question_statement: '', option_1: '', option_2: '', correct_option: '' }
                    this.fetchQuestions()
                } else {
                    alert(result.message)
                }
            } catch (error) {
                console.error('Error creating question:', error)
                alert('Failed to create question. Please try again.')
            }
        },
        editQuestion(question) {
            question.editing = true
        },
        async updateQuestion(question) {
            try {
                const response = await fetch(`/api/admin/questions/${question.question_id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        quiz_id: this.selectedQuiz.quiz_id,
                        question_statement: question.question_statement,
                        option_1: question.option_1,
                        option_2: question.option_2,
                        correct_option: question.correct_option
                    })
                })
                const result = await response.json()
                if (response.ok) {
                    alert(result.message)
                    question.editing = false
                } else {
                    alert(result.message)
                }
            } catch (error) {
                console.error('Error updating question:', error)
                alert('Failed to update question. Please try again.')
            }
        },
        async deleteQuestion(question_id) {
            if (confirm('Are you sure you want to delete this question?')) {
                try {
                    const response = await fetch(`/api/admin/questions/${question_id}`, {
                        method: 'DELETE'
                    })
                    const result = await response.json()
                    alert(result.message)
                    this.fetchQuestions()
                } catch (error) {
                    console.error('Error deleting question:', error)
                    alert('Failed to delete question. Please try again.')
                }
            }
        },
        updateCorrectOption() {
            if (this.newQuestion.correct_option &&
                ![this.newQuestion.option_1, this.newQuestion.option_2].includes(this.newQuestion.correct_option)) {
                this.newQuestion.correct_option = ''
            }
        },

        // Search and Summary Methods
        async search() {
            try {
                const response = await fetch(`/api/admin/search?query=${this.searchQuery}`)
                if (!response.ok) throw new Error('Failed to search')
                this.searchResults = await response.json()
            } catch (error) {
                console.error('Error searching:', error)
                alert('Failed to search. Please try again.')
            }
        },
        async fetchSummary() {
            try {
                const response = await fetch('/api/admin/summary')
                if (!response.ok) throw new Error('Failed to fetch summary')
                this.summary = await response.json()
                this.renderChart()
            } catch (error) {
                console.error('Error fetching summary:', error)
                alert('Failed to load summary. Please try again.')
            }
        },
        renderChart() {
            const ctx = document.getElementById('summaryChart')
            if (!ctx) {
                console.error('Canvas element not found')
                return
            }
            if (this.chart) {
                this.chart.destroy()
            }
            this.chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Users', 'Subjects', 'Quizzes'],
                    datasets: [{
                        label: 'Counts',
                        data: [this.summary.user_count, this.summary.subject_count, this.summary.quiz_count],
                        backgroundColor: ['#007bff', '#28a745', '#dc3545'],
                        borderColor: ['#0056b3', '#218838', '#c82333'],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    }
                }
            })
        }
    },
    mounted() {
        this.fetchSubjects()
        this.fetchChapters()
        this.fetchQuizzes()
        this.fetchQuestions()
    }
}

// Add styles
const style = document.createElement('style');
style.textContent = `
    body {
        background: linear-gradient(135deg, #4b6cb7, #182848, #6b48ff);
        min-height: 100vh;
        animation: gradientShift 15s ease infinite;
        background-size: 300% 300%;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .admin-dashboard {
        padding: 2rem 0;
    }

    .dashboard-title {
        font-weight: 800;
        background: linear-gradient(90deg, #3b82f6, #6b48ff);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 3px 6px rgba(0, 0, 0, 0.3);
        animation: fadeIn 1s ease-out;
    }

    .content-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(12px);
        border: 2px solid transparent;
        border-image: linear-gradient(45deg, #3b82f6, #6b48ff) 1;
        border-radius: 25px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        padding: 2rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: fadeIn 1s ease-out;
    }

    .content-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.5);
    }

    .custom-breadcrumb {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
    }

    .breadcrumb-item a {
        color: #3b82f6;
        text-decoration: none;
        transition: color 0.3s ease;
    }

    .breadcrumb-item a:hover {
        color: #6b48ff;
    }

    .breadcrumb-item.active {
        color: #ffffff;
    }

    h2, h3 {
        color: #ffffff;
        margin-bottom: 1.5rem;
        font-weight: 600;
    }

    .form-label {
        color: #ffffff;
        font-weight: 500;
    }

    /* Base form control styles */
    .form-control {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #ffffff;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
    }

    /* Style for non-edit mode form controls */
    form .form-control {
        background: rgba(255, 255, 255, 0.1);
        color: #ffffff;
    }

    form .form-control:focus {
        background: rgba(255, 255, 255, 0.2);
        color: #ffffff;
    }

    /* Style specifically for edit mode */
    td input.form-control,
    td textarea.form-control,
    td select.form-control {
        background-color: #ffffff !important;
        color: #333333 !important;
        border: 2px solid #3b82f6 !important;
        font-weight: 500 !important;
    }

    td input.form-control:focus,
    td textarea.form-control:focus,
    td select.form-control:focus {
        background-color: #ffffff !important;
        color: #333333 !important;
        border-color: #6b48ff !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.4) !important;
    }

    /* Style for table cells in non-edit mode */
    td span {
        color: #ffffff;
    }

    /* Make sure select options are visible */
    select.form-control option {
        background-color: #ffffff;
        color: #333333;
    }

    .table {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        overflow: hidden;
        margin-top: 1.5rem;
        color: #000000;
    }

    .table th {
        background: rgba(59, 130, 246, 0.2);
        color: #000000;
        font-weight: 600;
        border-color: rgba(0, 0, 0, 0.1);
    }

    .table td {
        border-color: rgba(0, 0, 0, 0.1);
        vertical-align: middle;
        color: #000000;
    }

    .btn {
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .btn-primary {
        background: linear-gradient(90deg, #3b82f6, #6b48ff);
        border: none;
    }

    .btn-primary:hover {
        background: linear-gradient(90deg, #2563eb, #5b3eff);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
    }

    .btn-warning {
        background: linear-gradient(90deg, #f59e0b, #d97706);
        border: none;
        color: #ffffff;
    }

    .btn-warning:hover {
        background: linear-gradient(90deg, #d97706, #b45309);
        color: #ffffff;
        transform: translateY(-2px);
    }

    .btn-danger {
        background: linear-gradient(90deg, #ef4444, #dc2626);
        border: none;
    }

    .btn-danger:hover {
        background: linear-gradient(90deg, #dc2626, #b91c1c);
        transform: translateY(-2px);
    }

    .btn-success {
        background: linear-gradient(90deg, #10b981, #059669);
        border: none;
    }

    .btn-success:hover {
        background: linear-gradient(90deg, #059669, #047857);
        transform: translateY(-2px);
    }

    @keyframes fadeIn {
        from { 
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .content-card {
            padding: 1.5rem;
        }

        .table {
            display: block;
            overflow-x: auto;
            white-space: nowrap;
        }
    }

    /* Make all text in table cells black */
    .table td span,
    .table td input.form-control,
    .table td textarea.form-control,
    .table td select.form-control {
        color: #000000 !important;
    }

    /* Style for edit mode inputs in table */
    td input.form-control,
    td textarea.form-control,
    td select.form-control {
        background-color: #ffffff !important;
        border: 2px solid #3b82f6 !important;
        font-weight: 500 !important;
    }

    td input.form-control:focus,
    td textarea.form-control:focus,
    td select.form-control:focus {
        background-color: #ffffff !important;
        border-color: #6b48ff !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.4) !important;
    }

    /* Keep form controls outside tables (create forms) with white text */
    form:not(.table) .form-control {
        background: rgba(255, 255, 255, 0.1);
        color: #ffffff;
    }

    form:not(.table) .form-control:focus {
        background: rgba(255, 255, 255, 0.2);
        color: #ffffff;
    }

    /* Make sure select options are visible */
    select.form-control option {
        background-color: #ffffff;
        color: #000000;
    }
`;

document.head.appendChild(style);

// Mount the app
const app = Vue.createApp(AdminDashboard);
app.mount('#app');