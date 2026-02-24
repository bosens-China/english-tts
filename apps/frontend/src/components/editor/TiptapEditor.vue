<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { Editor, EditorContent, type JSONContent } from '@tiptap/vue-3'
import BubbleMenu from '@tiptap/extension-bubble-menu'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import Highlight from '@tiptap/extension-highlight'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import { Table } from '@tiptap/extension-table'
import { TableRow } from '@tiptap/extension-table-row'
import { TableCell } from '@tiptap/extension-table-cell'
import { TableHeader } from '@tiptap/extension-table-header'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import Underline from '@tiptap/extension-underline'

const props = defineProps<{
  modelValue: string
  placeholder?: string
  readonly?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'update:json': [value: JSONContent]
}>()

const editor = ref<Editor>()
const wordCount = ref(0)

onMounted(() => {
  editor.value = new Editor({
    extensions: [
      StarterKit,
      Underline,
      Placeholder.configure({
        placeholder: props.placeholder || '开始写作...',
      }),
      Highlight.configure({
        multicolor: true,
      }),
      TaskList,
      TaskItem.configure({
        nested: true,
      }),
      Table.configure({
        resizable: true,
      }),
      TableRow,
      TableHeader,
      TableCell,
      Image.configure({
        allowBase64: true,
      }),
      Link.configure({
        openOnClick: false,
      }),
    ],
    content: props.modelValue,
    editable: !props.readonly,
    onUpdate: ({ editor }) => {
      const html = editor.getHTML()
      const json = editor.getJSON()
      emit('update:modelValue', html)
      emit('update:json', json)

      // 计算字数
      const text = editor.getText()
      wordCount.value = text.trim().length
    },
    onCreate: ({ editor }) => {
      wordCount.value = editor.getText().trim().length
    },
  })
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})

watch(() => props.modelValue, (newValue) => {
  if (editor.value && newValue !== editor.value.getHTML()) {
    editor.value.commands.setContent(newValue)
  }
})

const insertTimestamp = () => {
  if (!editor.value) return
  const timestamp = new Date().toLocaleString('zh-CN')
  editor.value.chain().focus().insertContent(`<span class="timestamp">⏱ ${timestamp}</span>`).run()
}

const addImage = () => {
  const url = prompt('请输入图片 URL：')
  if (url && editor.value) {
    editor.value.chain().focus().setImage({ src: url }).run()
  }
}

const setLink = () => {
  if (!editor.value) return
  const previousUrl = editor.value.getAttributes('link').href
  const url = prompt('请输入链接 URL：', previousUrl)

  if (url === null) return
  if (url === '') {
    editor.value.chain().focus().extendMarkRange('link').unsetLink().run()
  } else {
    editor.value.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
  }
}

const insertTable = () => {
  if (!editor.value) return
  editor.value.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
}

defineExpose({
  editor,
  wordCount,
  insertTimestamp,
})
</script>

<template>
  <div class="editor-wrapper">
    <!-- 工具栏 -->
    <div v-if="!readonly && editor" class="editor-toolbar">
      <div class="toolbar-group">
        <button
          class="toolbar-btn"
          :class="{ active: editor.isActive('bold') }"
          @click="editor?.chain().focus().toggleBold().run()"
        >
          <div class="i-ph-text-b-bold" />
        </button>
        <button
          class="toolbar-btn"
          :class="{ active: editor.isActive('italic') }"
          @click="editor?.chain().focus().toggleItalic().run()"
        >
          <div class="i-ph-text-italic-bold" />
        </button>
        <button
          class="toolbar-btn"
          :class="{ active: editor.isActive('underline') }"
          @click="editor?.chain().focus().toggleUnderline().run()"
        >
          <div class="i-ph-text-underline-bold" />
        </button>
        <button
          class="toolbar-btn"
          :class="{ active: editor.isActive('strike') }"
          @click="editor?.chain().focus().toggleStrike().run()"
        >
          <div class="i-ph-text-strikethrough-bold" />
        </button>
        <button
          class="toolbar-btn"
          :class="{ active: editor.isActive('highlight') }"
          @click="editor?.chain().focus().toggleHighlight().run()"
        >
          <div class="i-ph-highlighter-bold" />
        </button>
      </div>

      <div class="toolbar-divider" />

      <div class="toolbar-group">
        <button
          class="toolbar-btn"
          :class="{ active: editor.isActive('heading', { level: 1 }) }"
          @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()"
        >
          <div class="i-ph-text-h-bold" />
        </button>
        <button
          class="toolbar-btn"
          :class="{ active: editor.isActive('heading', { level: 2 }) }"
          @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()"
        >
          <div class="i-ph-text-h-two-bold" />
        </button>
        <button
          class="toolbar-btn"
          :class="{ active: editor.isActive('heading', { level: 3 }) }"
          @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()"
        >
          <div class="i-ph-text-h-three-bold" />
        </button>
      </div>

      <div class="toolbar-divider" />

      <div class="toolbar-group">
        <button
          class="toolbar-btn"
          :class="{ active: editor.isActive('bulletList') }"
          @click="editor?.chain().focus().toggleBulletList().run()"
        >
          <div class="i-ph-list-bullets-bold" />
        </button>
        <button
          class="toolbar-btn"
          :class="{ active: editor.isActive('orderedList') }"
          @click="editor?.chain().focus().toggleOrderedList().run()"
        >
          <div class="i-ph-list-numbers-bold" />
        </button>
        <button
          class="toolbar-btn"
          :class="{ active: editor.isActive('taskList') }"
          @click="editor?.chain().focus().toggleTaskList().run()"
        >
          <div class="i-ph-check-square-bold" />
        </button>
        <button
          class="toolbar-btn"
          @click="insertTable"
        >
          <div class="i-ph-table-bold" />
        </button>
      </div>

      <div class="toolbar-divider" />

      <div class="toolbar-group">
        <button
          class="toolbar-btn"
          :class="{ active: editor.isActive('codeBlock') }"
          @click="editor?.chain().focus().toggleCodeBlock().run()"
        >
          <div class="i-ph-code-bold" />
        </button>
        <button
          class="toolbar-btn"
          :class="{ active: editor.isActive('blockquote') }"
          @click="editor?.chain().focus().toggleBlockquote().run()"
        >
          <div class="i-ph-quotes-bold" />
        </button>
        <button
          class="toolbar-btn"
          @click="setLink"
          :class="{ active: editor.isActive('link') }"
        >
          <div class="i-ph-link-bold" />
        </button>
        <button
          class="toolbar-btn"
          @click="addImage"
        >
          <div class="i-ph-image-bold" />
        </button>
        <button
          class="toolbar-btn"
          @click="insertTimestamp"
        >
          <div class="i-ph-clock-bold" />
        </button>
      </div>

      <div class="toolbar-divider" />

      <div class="toolbar-group">
        <button
          class="toolbar-btn"
          @click="editor?.chain().focus().undo().run()"
          :disabled="!editor.can().chain().focus().undo().run()"
        >
          <div class="i-ph-arrow-u-up-left-bold" />
        </button>
        <button
          class="toolbar-btn"
          @click="editor?.chain().focus().redo().run()"
          :disabled="!editor.can().chain().focus().redo().run()"
        >
          <div class="i-ph-arrow-u-up-right-bold" />
        </button>
      </div>
    </div>

    <!-- 编辑器内容 -->
    <div class="editor-content">
      <BubbleMenu
        v-if="editor && !readonly"
        :editor="editor"
        :tippy-options="{ duration: 100 }"
      >
        <div class="bubble-menu">
          <button
            class="bubble-btn"
            :class="{ active: editor.isActive('bold') }"
            @click="editor?.chain().focus().toggleBold().run()"
          >
            <div class="i-ph-text-b-bold" />
          </button>
          <button
            class="bubble-btn"
            :class="{ active: editor.isActive('italic') }"
            @click="editor?.chain().focus().toggleItalic().run()"
          >
            <div class="i-ph-text-italic-bold" />
          </button>
          <button
            class="bubble-btn"
            :class="{ active: editor.isActive('highlight') }"
            @click="editor?.chain().focus().toggleHighlight().run()"
          >
            <div class="i-ph-highlighter-bold" />
          </button>
          <button
            class="bubble-btn"
            @click="setLink"
            :class="{ active: editor.isActive('link') }"
          >
            <div class="i-ph-link-bold" />
          </button>
        </div>
      </BubbleMenu>

      <EditorContent :editor="editor" />
    </div>

    <!-- 底部状态栏 -->
    <div v-if="!readonly" class="editor-footer">
      <div class="flex items-center gap-4 text-sm text-gray-500">
        <span>{{ wordCount }} 字</span>
        <span v-if="editor?.isEmpty" class="text-gray-400">使用 / 触发快捷命令</span>
      </div>
    </div>
  </div>
</template>

<style>
/* 编辑器容器 */
.editor-wrapper {
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  background: white;
  overflow: hidden;
}

/* 工具栏 */
.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  overflow-x: auto;
  flex-wrap: wrap;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 0.125rem;
}

.toolbar-divider {
  width: 1px;
  height: 1.5rem;
  background: #d1d5db;
  margin: 0 0.25rem;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 0.375rem;
  color: #4b5563;
  transition: all 0.15s;
}

.toolbar-btn:hover {
  background: #e5e7eb;
  color: #111827;
}

.toolbar-btn.active {
  background: #dbeafe;
  color: #2563eb;
}

.toolbar-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 编辑器内容区 */
.editor-content {
  padding: 1.5rem;
  min-height: 400px;
}

.editor-content .ProseMirror {
  outline: none;
  min-height: 400px;
}

.editor-content .ProseMirror p.is-editor-empty:first-child::before {
  content: attr(data-placeholder);
  float: left;
  color: #9ca3af;
  pointer-events: none;
  height: 0;
}

/* 浮动菜单 */
.bubble-menu {
  display: flex;
  gap: 0.25rem;
  padding: 0.375rem;
  background: #1f2937;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.bubble-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 0.25rem;
  color: #e5e7eb;
  transition: all 0.15s;
}

.bubble-btn:hover {
  background: #374151;
  color: white;
}

.bubble-btn.active {
  background: #2563eb;
  color: white;
}

/* 底部状态栏 */
.editor-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 1rem;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

/* 编辑器样式 - 正文 */
.ProseMirror p {
  margin-bottom: 0.75rem;
  line-height: 1.75;
  color: #374151;
}

/* 标题 */
.ProseMirror h1 {
  font-size: 1.875rem;
  font-weight: 700;
  margin-bottom: 1rem;
  margin-top: 1.5rem;
  color: #111827;
  line-height: 1.3;
}

.ProseMirror h2 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  margin-top: 1.25rem;
  color: #1f2937;
  line-height: 1.35;
}

.ProseMirror h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  margin-top: 1rem;
  color: #1f2937;
}

/* 列表 */
.ProseMirror ul {
  list-style-type: disc;
  padding-left: 1.5rem;
  margin-bottom: 0.75rem;
}

.ProseMirror ol {
  list-style-type: decimal;
  padding-left: 1.5rem;
  margin-bottom: 0.75rem;
}

.ProseMirror li {
  margin-bottom: 0.25rem;
}

/* 任务列表 */
.ProseMirror ul[data-type="taskList"] {
  list-style: none;
  padding-left: 0;
}

.ProseMirror ul[data-type="taskList"] li {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.ProseMirror ul[data-type="taskList"] li > label {
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.ProseMirror ul[data-type="taskList"] li > div {
  flex: 1;
}

.ProseMirror ul[data-type="taskList"] input[type="checkbox"] {
  width: 1rem;
  height: 1rem;
  cursor: pointer;
}

/* 代码块 */
.ProseMirror pre {
  background: #1f2937;
  color: #f3f4f6;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin-bottom: 0.75rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.875rem;
}

.ProseMirror pre code {
  background: none;
  color: inherit;
  padding: 0;
  font-size: inherit;
}

.ProseMirror code {
  background: #f3f4f6;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  color: #db2777;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

/* 引用 */
.ProseMirror blockquote {
  border-left: 4px solid #3b82f6;
  padding-left: 1rem;
  margin-left: 0;
  margin-bottom: 0.75rem;
  color: #4b5563;
  font-style: italic;
}

/* 链接 */
.ProseMirror a {
  color: #2563eb;
  text-decoration: none;
}

.ProseMirror a:hover {
  text-decoration: underline;
}

/* 图片 */
.ProseMirror img {
  max-width: 100%;
  height: auto;
  border-radius: 0.5rem;
  margin: 1rem 0;
}

/* 高亮 */
.ProseMirror mark {
  background: #fef08a;
  padding: 0.125rem 0.25rem;
  border-radius: 0.125rem;
}

/* 表格 */
.ProseMirror table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

.ProseMirror th,
.ProseMirror td {
  border: 1px solid #e5e7eb;
  padding: 0.5rem 1rem;
  text-align: left;
}

.ProseMirror th {
  background: #f9fafb;
  font-weight: 600;
  color: #1f2937;
}

.ProseMirror tr:nth-child(even) {
  background: #f9fafb;
}

/* 选中状态 */
.ProseMirror ::selection {
  background: #bfdbfe;
}

/* 分割线 */
.ProseMirror hr {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 1.5rem 0;
}

/* 时间戳 */
.timestamp {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: #f0fdf4;
  color: #166534;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}
</style>
