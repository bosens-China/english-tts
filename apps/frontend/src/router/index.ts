import { createRouter, createWebHistory } from 'vue-router'
import BookListView from '@/views/BookListView.vue'
import BookDetailView from '@/views/BookDetailView.vue'
import LessonDetailView from '@/views/LessonDetailView.vue'
import NoteEditView from '@/views/NoteEditView.vue'
import NoteView from '@/views/NoteView.vue'
import NoteListView from '@/views/NoteListView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'books',
      component: BookListView,
    },
    {
      path: '/books/:id',
      name: 'book-detail',
      component: BookDetailView,
    },
    {
      path: '/lessons/:id',
      name: 'lesson-detail',
      component: LessonDetailView,
    },
    {
      path: '/lessons/:lessonId/notes/new',
      name: 'note-create',
      component: NoteEditView,
    },
    {
      path: '/notes',
      name: 'note-list',
      component: NoteListView,
    },
    {
      path: '/notes/:id',
      name: 'note-view',
      component: NoteView,
    },
    {
      path: '/notes/:id/edit',
      name: 'note-edit',
      component: NoteEditView,
    },
    // 404 页面 - 放在最后匹配所有未定义的路径
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView,
    },
  ],
})

export default router
